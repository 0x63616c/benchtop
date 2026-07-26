"""A* grid router for two signal layers over solid ground planes.

Rev B has 87 footprints and 78 nets — an order of magnitude past what the
split-flap boards route from a hand-written waypoint table. So the waypoints
become a search instead: every pad and every finished track is stamped into a
0.1mm occupancy grid, and each net is grown pad-by-pad with A* over
{F.Cu, B.Cu} x grid, paying a fixed penalty per via.

Ground is NOT routed. In1/In2 are poured GND, so a GND pad only needs a via,
which is what `stitch_vias` does.

Clearance is baked into the grid rather than checked afterwards: a pad or
track owns not just its own cells but a halo of (clearance + track/2) around
them, so any centreline the search returns is legal by construction. Where two
different nets' halos overlap, the cell is locked out for everyone — slightly
conservative, and much easier to trust than a post-hoc DRC loop.
"""

import heapq
from array import array

GRID = 0.1          # mm per cell
CLEAR = 0.13        # copper-to-copper. JLC's 4-layer floor is 0.09, and
                    # anything looser cannot escape a 0.4mm-pitch QFN pin at all
VIA_COST = 12       # in grid steps. B.Cu is nearly empty — going there is cheap
VIA_SIZE = 0.6      # kept here too: the router has to know how fat a via is
BEND_COST = 6       # without this the search returns staircases, not tracks

FREE = 0
LOCKED = -1


class Grid:
    """Occupancy for one board, all routing layers."""

    def __init__(self, w, h, layers, regions):
        self.nx = int(round(w / GRID)) + 1
        self.ny = int(round(h / GRID)) + 1
        self.layers = list(layers)
        self.cells = {ly: array("i", [LOCKED]) * (self.nx * self.ny) for ly in layers}
        self.is_core = {ly: bytearray(self.nx * self.ny) for ly in layers}
        # only inside a declared region is copper allowed
        for x0, y0, x1, y1 in regions:
            for ly in layers:
                c = self.cells[ly]
                for gy in range(self._gy(y0), self._gy(y1) + 1):
                    row = gy * self.nx
                    for gx in range(self._gx(x0), self._gx(x1) + 1):
                        c[row + gx] = FREE

    def _gx(self, x):
        return max(0, min(self.nx - 1, int(round(x / GRID))))

    def _gy(self, y):
        return max(0, min(self.ny - 1, int(round(y / GRID))))

    def idx(self, gx, gy):
        return gy * self.nx + gx

    def block(self, x0, y0, x1, y1, layers=None):
        """Hard keep-out (antenna, edges, mount holes) — nobody routes here."""
        for ly in (layers or self.layers):
            c = self.cells[ly]
            for gy in range(self._gy(y0), self._gy(y1) + 1):
                row = gy * self.nx
                for gx in range(self._gx(x0), self._gx(x1) + 1):
                    c[row + gx] = LOCKED

    def core(self, layer, x0, y0, x1, y1, net):
        """Copper that IS the net: a pad, or a track already laid.

        Cores are absolute — a halo may never take one away, or a pad whose
        neighbour crowds it would become unreachable and its net unroutable.
        """
        c, k = self.cells[layer], self.is_core[layer]
        for gy in range(self._gy(y0), self._gy(y1) + 1):
            row = gy * self.nx
            for gx in range(self._gx(x0), self._gx(x1) + 1):
                c[row + gx] = net
                k[row + gx] = 1

    def halo(self, layer, x0, y0, x1, y1, net, halo):
        """The exclusion ring: free cells become this net's, contested ones lock."""
        c, k = self.cells[layer], self.is_core[layer]
        for gy in range(self._gy(y0 - halo), self._gy(y1 + halo) + 1):
            row = gy * self.nx
            for gx in range(self._gx(x0 - halo), self._gx(x1 + halo) + 1):
                i = row + gx
                if k[i]:
                    continue
                v = c[i]
                if v == FREE:
                    c[i] = net
                elif v != net and v != LOCKED:
                    c[i] = LOCKED

    def stamp(self, layer, x0, y0, x1, y1, net, halo):
        self.core(layer, x0, y0, x1, y1, net)
        self.halo(layer, x0, y0, x1, y1, net, halo)

    def passable(self, layer, i, net):
        v = self.cells[layer][i]
        return v == FREE or v == net

    def cells_of(self, layer, net):
        c = self.cells[layer]
        return {i for i, v in enumerate(c) if v == net}


def clear_at(g, layer, i, net, extra):
    """Is a wider-than-baseline object legal centred on this cell?

    Halos are stamped for a baseline W_SIG track. Anything fatter — a power
    trace, or a via, which is 0.6mm of copper on a 0.15mm path — has to prove
    the extra radius is free as well, or DRC finds it later as a short.
    """
    if extra <= 0:
        return True
    r = int(round(extra / GRID))
    gx, gy = i % g.nx, i // g.nx
    c = g.cells[layer]
    for y in range(max(0, gy - r), min(g.ny - 1, gy + r) + 1):
        row = y * g.nx
        for x in range(max(0, gx - r), min(g.nx - 1, gx + r) + 1):
            v = c[row + x]
            if v != FREE and v != net:
                return False
    return True


def via_fits(g, i, net, extra):
    return all(clear_at(g, ly, i, net, extra) for ly in g.layers)


def strict_ok(g, layer, i, net, radius):
    """Exact clearance test: no FOREIGN copper within `radius` of this cell.

    The halo grid is an approximation — a cell claimed by two nets' halos is
    locked for everyone, even when a centreline there would still clear both
    of them. That is fine while there is room and wrong once there is not, so
    the last few nets get the real test instead: distance to actual copper.
    """
    r = int(round(radius / GRID))
    gx, gy = i % g.nx, i // g.nx
    c, k = g.cells[layer], g.is_core[layer]
    if c[i] == LOCKED and not k[i]:
        pass                      # locked-by-halo is exactly what we re-judge
    for y in range(max(0, gy - r), min(g.ny - 1, gy + r) + 1):
        row = y * g.nx
        for x in range(max(0, gx - r), min(g.nx - 1, gx + r) + 1):
            j = row + x
            if k[j] and c[j] != net:
                return False
    return True


def _neighbours(g, i):
    gx, gy = i % g.nx, i // g.nx
    if gx > 0:
        yield i - 1
    if gx < g.nx - 1:
        yield i + 1
    if gy > 0:
        yield i - g.nx
    if gy < g.ny - 1:
        yield i + g.nx


def route_net(g, net, sources, targets, width, base_width, strict=False):
    """A* from any source cell to any target cell. Returns [(layer, i), ...].

    sources/targets are {layer: set(index)}. The path is stamped by the caller
    so a failed net leaves the grid untouched.
    """
    extra = max(0.0, (width - base_width) / 2)
    via_extra = max(0.0, (VIA_SIZE - base_width) / 2)
    if strict:
        rad, via_rad = CLEAR + width / 2, CLEAR + VIA_SIZE / 2

        def free(layer, cell):
            return strict_ok(g, layer, cell, net, rad)

        def via_free(cell):
            return all(strict_ok(g, ly, cell, net, via_rad) for ly in g.layers)
    else:
        def free(layer, cell):
            return g.passable(layer, cell, net) and clear_at(g, layer, cell, net, extra)

        def via_free(cell):
            return via_fits(g, cell, net, via_extra)
    tgt = {(ly, i) for ly, s in targets.items() for i in s}
    if not tgt:
        return None
    tx = sum((i % g.nx) for _, i in tgt) / len(tgt)
    ty = sum((i // g.nx) for _, i in tgt) / len(tgt)

    def h(i):
        return abs(i % g.nx - tx) + abs(i // g.nx - ty)

    open_q = []
    best = {}
    for ly, s in sources.items():
        for i in s:
            st = (ly, i)
            best[st] = 0
            heapq.heappush(open_q, (h(i), 0, st, None))
    came = {}
    while open_q:
        _, cost, state, prev = heapq.heappop(open_q)
        if state in came:
            continue
        came[state] = prev
        if state in tgt:
            path = []
            while state is not None:
                path.append(state)
                state = came[state]
            return path[::-1]
        ly, i = state
        for j in _neighbours(g, i):
            if not free(ly, j):
                continue
            nc = cost + 1
            if prev is not None and prev[0] == ly:
                # cheap straightness bias: turning costs a little
                if (j - i) != (i - prev[1]):
                    nc += BEND_COST
            if best.get((ly, j), 1 << 30) > nc:
                best[(ly, j)] = nc
                heapq.heappush(open_q, (nc + h(j), nc, (ly, j), state))
        for other in g.layers:
            if other == ly or not free(other, i):
                continue
            if not via_free(i):
                continue
            nc = cost + VIA_COST
            if best.get((other, i), 1 << 30) > nc:
                best[(other, i)] = nc
                heapq.heappush(open_q, (nc + h(i), nc, (other, i), state))
    return None


def path_to_geometry(g, path):
    """Collapse a cell path into (segments, vias) in mm."""
    segs, vias = [], []
    run = [path[0]]
    for state in path[1:]:
        ly, i = state
        ply, pi = run[-1]
        if ly != ply:                       # layer change = via
            _emit_run(g, run, segs)
            vias.append(_xy(g, i))
            run = [state]
            continue
        run.append(state)
    _emit_run(g, run, segs)
    return segs, vias


def _xy(g, i):
    return ((i % g.nx) * GRID, (i // g.nx) * GRID)


def _emit_run(g, run, segs):
    """One layer's worth of cells -> as few straight segments as possible."""
    if len(run) < 2:
        return
    ly = run[0][0]
    pts = [_xy(g, i) for _, i in run]
    start = pts[0]
    for k in range(1, len(pts) - 1):
        a, b, c = pts[k - 1], pts[k], pts[k + 1]
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            segs.append((ly, start, b))
            start = b
    segs.append((ly, start, pts[-1]))


def stamp_path(g, path, net, width, base_width):
    """Lay the finished path into the grid: track copper, plus via pads.

    Halos go down at the BASELINE width, not this net's: a halo's job is to
    keep the next net's centreline out, and that next net proves its own extra
    radius at query time.
    """
    halo = CLEAR + base_width / 2
    half = width / 2
    vhalf = VIA_SIZE / 2
    prev = None
    for ly, i in path:
        x, y = _xy(g, i)
        g.stamp(ly, x - half, y - half, x + half, y + half, net, halo)
        if prev is not None and prev[0] != ly:
            for lay in g.layers:
                g.stamp(lay, x - vhalf, y - vhalf, x + vhalf, y + vhalf, net, halo)
        prev = (ly, i)
