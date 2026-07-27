"""Place, route and preview the blinds driver board.

Run with atopile's interpreter (it bundles faebryk):
    ~/.local/share/uv/tools/atopile/bin/python tools/place_and_render.py

Placement is address-keyed, so it survives `ato build` designator reshuffles.
Big parts are anchored by hand; the ~60 passives are laid out in BANKS next to
the chip they belong to, because hand-picking 60 coordinates is how you get a
board where C23 is four centimetres from the pin it decouples.

Routing is the A* grid router in tools/router.py — see its docstring for why
this board earns one. GND is never routed: In1/In2 are poured ground and every
ground pad gets a stitching via.

The panel is the 36x52 main board plus a 16x12 hall-sensor tab joined by a
4mm neck. The tab's three nets are deliberately SEPARATE nets from the main
board's (p3v3_tab etc), so nothing routes across the neck and snapping it off
breaks no copper — the two halves are joined by an XH-3 cable, because the
sprocket the sensor watches is 80mm away from where the board lives.
"""

import math
import re
from pathlib import Path

from faebryk.libs.kicad.fileformats import kicad

import router
from router import GRID, Grid

ROOT = Path(__file__).parent.parent
PCB = ROOT / "layouts/default/default.kicad_pcb"

BOARD_W, BOARD_H = 88.0, 32.0          # main board — flat on the v2 floor
TAB = (36.0, 35.0, 54.0, 47.0)         # snap-off hall tab, below the board
NECK = (43.0, 32.0, 47.0, 35.0)
EDGE_KEEP = 0.55                       # track CENTRELINE inset from any board
                                       # edge: 0.4mm of copper plus KiCad's
                                       # 0.25mm copper-to-edge rule

# The module's antenna half must see no copper on any layer, including the
# poured planes. Module body spans y 0.5..17.1 with the antenna at the low-y
# end, so this covers it plus a margin.
ANTENNA_KEEPOUT = (2.0, 0.0, 19.0, 8.5)

MIN_SILK_W = 0.15

# --- placement ---------------------------------------------------------------
# address -> (x, y, rot). Origin top-left, y down, mm.
ANCHORS = {
    # left block: MCU (antenna at the top/front edge) + protector — the
    # whole rev B top region survives the v2 reshape untouched
    "mcu": (10.5, 11.4, 0),  # 0.6 up: widens the pad-row -> bulk-row corridor
    "prot": (21.5, 6.0, 0),
    # front edge, matching the enclosure's wall holes (unit x 38/49/60)
    "sw_dn": (33.0, 3.4, 0),
    "j_usb": (44.0, 3.65, 180),
    "sw_up": (55.0, 3.4, 0),
    # PD sink under the USB
    "pd": (41.5, 14.0, 0),
    # charger, middle-left
    "chg": (33.0, 13.0, 180),  # SW pins face the inductor below; 0 aims them at sw_dn
    "l_chg": (33.0, 24.5, 0),
    # buck, center
    "buck": (54.0, 16.0, 0),
    "l_buck": (48.5, 24.5, 0),
    # boost, middle-right
    "boost": (68.0, 12.0, 0),
    "l_bst": (69.0, 22.5, 0),
    # H-bridge + connectors, right / back edge
    "drv": (81.5, 13.0, 0),
    "j_bat": (64.5, 30.7, 0),
    "j_mot": (80.0, 30.7, 0),
    "j_hall": (10.0, 30.7, 0),
    # the tab
    "hall": (45.0, 39.0, 0),
    "c_hall": (45.0, 42.0, 0),
    "j_hall_tab": (45.0, 45.1, 0),
}

# Right-angle connectors are meant to hang their housing off the board edge —
# only their pads have to land on copper. Everything else must sit fully inside.
EDGE_PARTS = {"j_bat", "j_mot", "j_hall", "j_usb", "j_hall_tab", "sw_up", "sw_dn"}

# M3 mounting holes (the enclosure's floor bosses match these — keep the CAD
# params in cad/blinds_cad in the same commit as any move). Ø3.2 cutout, and
# a square keep-out that placement AND routing both respect.
MOUNT_HOLES = [(85.0, 4.0), (4.0, 27.0), (85.0, 27.0)]
HOLE_D = 3.2
HOLE_KEEP = 2.6                        # centre -> edge of the keep-out square
# The 4th corner is the MCU + antenna — no screw there (steel in the antenna
# zone, no room either). Instead the enclosure puts a plain pillar under the
# USB edge to take plug insertion force; keep B.Cu clear where it presses.
PILLAR_KEEP = (41.0, 0.0, 47.0, 4.6)

# (x0, y0, cols, pitch_x, pitch_y, rot, [addr, ...]) — filled left to right,
# top to bottom. Keep each bank next to the chip it serves.
BANKS = [
    # protector network, right of the MCU (unchanged rev B cluster)
    (20.6, 10.4, 2, 3.4, 2.2, 0, ["r_vd", "r_cb2", "r_cb", "r_cb1",
                                 "c_prot_vdd", "c_cell1", "c_cell2", "c_cd"]),
    # Charger bulk: one 0805 row straight across, under the MCU. VBUS, PMID,
    # REGN, SYS and BAT are all quiet nodes — none of them is in a switching
    # loop — so a tidy spine beats scattering them around the chip.
    (2.4, 18.8, 6, 4.3, 2.4, 0, ["c_vbus1", "c_vbus2", "c_regn",
                                 "c_sys1", "c_sys2", "c_bat2"]),
    (2.4, 21.8, 1, 4.3, 2.4, 0, ["c_mcu_bulk"]),
    (7.0, 21.8, 2, 3.4, 2.0, 0, ["c_mcu_hf", "c_mcu_mid"]),
    (8.5, 24.5, 2, 3.2, 2.0, 0, ["r_en_mcu", "c_en_mcu", "r_io2"]),
    # bootstrap/drive caps hug the charger's right flank — sw_chg nets
    # must not cross the board
    (37.5, 7.5, 1, 3.2, 2.0, 0, ["c_btst1", "c_btst2", "c_sdrv"]),
    # charger small stuff, below the bulk row
    (15.0, 24.0, 4, 3.2, 2.0, 0, ["r_ts_hi", "r_ts_lo", "r_prog", "r_qon",
                                  "r_int", "r_sda", "r_scl", "r_ce_pd",
                                  "r_ce_ov"]),
    # PMID's pair sits under the charger's flank, next to the pin: it is the
    # input node of a switching converter, and 8mm of trace to the bulk cap
    # would be a loop worth avoiding even if it routed.
    (37.8, 17.6, 1, 3.0, 2.5, 0, ["c_pmid_hf"]),
    (38.5, 20.0, 1, 4.3, 2.4, 0, ["c_pmid"]),
    # BATP is a sense pin on the charger's right flank with nowhere to go —
    # give it battery copper 3mm away instead of across the board.
    (27.0, 16.2, 1, 4.3, 2.4, 90, ["c_bat1"]),  # BATP flank is LEFT at rot 180 —
                                                   # vertical, in the slot between the prot bank
                                                   # and the pin-18 escape stub
    # status LED out in the open
    (24.0, 29.5, 2, 3.4, 2.0, 0, ["d_stat", "r_stat"]),
    # PD sink straps, right of the PD chip under the USB
    (46.5, 8.2, 2, 3.2, 2.0, 0, ["r_vset", "r_iset", "r_hvdcp", "r_flgin",
                                 "c_pdvdd", "c_vbus_hf"]),
    # buck + 3V3, center
    (58.5, 12.0, 2, 3.2, 2.0, 0, ["r_en_buck", "r_fb_buck_hi", "r_fb_buck_lo",
                                  "c_ff", "c_buck_hf"]),
    (54.5, 22.5, 1, 4.3, 2.4, 0, ["c_buck_in", "c_buck_o"]),
    # boost small stuff, right of the boost
    (74.0, 16.0, 2, 3.2, 2.0, 0, ["c_boot", "c_vcc_bst", "c_ss", "c_comp",
                                  "r_comp", "r_fsw", "r_ilim_bst",
                                  "r_fb_bst_hi", "r_fb_bst_lo", "r_en_bst"]),
    (63.0, 27.5, 1, 4.3, 2.4, 0, ["c_bst_in"]),
    # 12V bulk, between the boost and the H-bridge
    (70.0, 26.5, 2, 4.1, 2.4, 0, ["c_bst_o1", "c_bst_o2", "c_bst_o3", "c_vm"]),
    (86.0, 18.0, 1, 3.2, 2.0, 0, ["c_bst_hf", "c_vm_hf", "r_ilim_mot"]),
]

# Board-level silk: (text, x, y, size, rot)
SILK = [
    ("BLINDS DRIVER rev C", 62.0, 5.0, 0.9, 0),
    ("0x63616c", 62.0, 7.5, 0.8, 0),
    ("BAT 2S  + M -", 64.5, 28.6, 0.7, 0),
    ("MOTOR", 78.0, 28.6, 0.7, 0),
    ("HALL", 10.0, 28.6, 0.7, 0),
    ("USB-C PD", 44.0, 6.2, 0.7, 0),
    ("DOWN", 33.0, 7.8, 0.8, 0),
    ("UP", 55.0, 7.8, 0.8, 0),
    ("HALL TAB - snap off", 45.0, 36.5, 0.7, 0),
]

# Track width by net. atopile's net NAMES are whatever pad it happened to name
# them after ("2", "MODE", "1-3"), so nets are identified by a pad that can
# only belong to them — a pin number off a datasheet, which does not drift.
# 0.15mm signal traces: the BQ25798's 0.4mm-pitch pads leave 0.2mm between
# neighbours, so a wider escape simply does not fit. JLC's 4-layer floor is 0.09.
W_SIG, W_PWR, W_BIG = 0.15, 0.3, 0.4
W_FINE, CLEAR_FINE = 0.1, 0.1     # last-resort hop, still inside JLC's floor
HAIRLINE = False                  # searching the whole board at 0.1mm clearance
                                  # costs 20+ minutes and has never been what
                                  # closed a net — kept for the day it is
NET_BY_PAD = {
    "gnd": "chg.27", "gnd_tab": "hall.3",
    "vbus": "chg.2", "pmid": "chg.29", "sys": "chg.25", "bat": "chg.22",
    "regn": "chg.5", "batmid": "j_bat.2",
    "sw_chg1": "chg.28", "sw_chg2": "chg.26",
    "v12": "drv.5", "sw_bst": "boost.4", "mot_a": "drv.6", "mot_b": "drv.8",
    "p3v3": "mcu.3", "sw_buck": "buck.3", "p3v3_tab": "hall.1",
    "prot_vdd": "prot.7", "prot_vc1": "prot.2", "prot_vc2": "prot.1",
    "prot_cb": "prot.3", "stat_a": "d_stat.2",
}
WIDTH_BY_NAME = {
    "vbus": W_BIG, "pmid": W_BIG, "sys": W_BIG, "bat": W_BIG, "v12": W_BIG,
    "p3v3": W_BIG, "batmid": W_PWR,
    "sw_chg1": W_BIG, "sw_chg2": W_BIG, "sw_bst": W_BIG, "sw_buck": W_BIG,
    "mot_a": W_BIG, "mot_b": W_BIG,
    "regn": W_PWR, "prot_vdd": W_PWR, "prot_vc1": W_PWR, "prot_vc2": W_PWR,
    "prot_cb": W_PWR, "stat_a": W_PWR, "p3v3_tab": W_PWR,
}
GND_NETS = {"gnd", "gnd_tab"}

# The charger is the tightest corner of the board — 29 pins on a 4mm QFN with
# its passive bank on one side and the board edge on the other. These nets go
# down before anything else competes for that space; found by watching which
# ones the retry loop kept rescuing.
PRIORITY_PADS = ["chg.26", "chg.14", "chg.29", "chg.22", "chg.5", "chg.20", "mcu.19", "chg.15", "chg.25",
                 "chg.19", "chg.4", "chg.21"]

VIA_SIZE, VIA_DRILL = 0.6, 0.3

# Six layers: F / In1 GND / In2 route / In3 route / In4 GND / B. Two routing
# layers could not finish this board and three only got within a few nets of
# it — 24 nets have to escape a 4mm 29-pin QFN, and no amount of net ordering
# invents room that is not there. The extra pair costs about $30 across the
# whole ten-board run, which is less than one more evening of shuffling parts.
ROUTE_LAYERS = ["F.Cu", "In2.Cu", "In3.Cu", "B.Cu"]
GND_LAYERS = ["F.Cu", "In1.Cu", "In4.Cu", "B.Cu"]


def pad_layers(pad):
    """Which routing layers a pad's copper is on. THT pads reach all of them.

    pad.layers is a pyzig list, and str() on it gives "<pyzig.MutableList object
    at 0x...>" — no layer names, no "*". Formatting it instead of iterating it
    silently put EVERY pad on F.Cu alone, so the router happily ran tracks
    through every through-hole pad on the inner and bottom layers. That was
    ~100 DRC shorts wearing a hundred different disguises.
    """
    names = [str(x) for x in pad.layers]
    if any(n.startswith("*") for n in names):
        return list(ROUTE_LAYERS)
    out = [ly for ly in ROUTE_LAYERS if ly in names]
    return out or ["F.Cu"]

# Fine-pitch parts get a fanout stub per pad before anything else is routed:
# a straight run outward, on the pad's own centreline, to clear the ring of
# neighbouring pads. Nothing can escape a 0.4mm-pitch QFN otherwise — between
# two neighbours there is 0.2mm, and the narrowest legal trace plus its two
# clearances needs more than that. addr -> stub length past the pad edge, mm.
FANOUT = {"chg": 1.2, "boost": 1.0, "pd": 0.8, "prot": 0.7, "drv": 0.7,
          "buck": 0.6, "mcu": 0.6, "hall": 0.6, "j_usb": 0.8}
# Per-pad override, for the one or two pins whose lane the rest of the fanout
# closes off. BATP only senses the battery, so its run is long by nature —
# reaching past the traffic beats fighting it.
FANOUT_PAD = {"chg.26": 2.0, "chg.18": 3.6, "chg.14": 2.9, "chg.21": 3.3}  # staggered lengths so tips of
                                  # neighbouring escape stubs don't seal each other;
                                  # rev B's rot-0 values re-derived for the 180 charger


def rot(x, y, deg):
    a = math.radians(-deg)  # kicad rotation is CCW in a y-down world
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def placement():
    """ANCHORS plus the expanded BANKS, as one address -> (x, y, rot) map."""
    out = dict(ANCHORS)
    for x0, y0, cols, px, py, r, addrs in BANKS:
        for n, addr in enumerate(addrs):
            out[addr] = (x0 + (n % cols) * px, y0 + (n // cols) * py, r)
    return out


def pad_rects(pad, fx, fy, fr):
    """A pad's copper as axis-aligned rectangles, in board coords.

    A plain pad is one rectangle. The BQ25798's four corner pads are L-shaped
    polygons, and taking their bounding box instead fills in the notch — which
    is exactly where the neighbouring pin's escape lane runs. Those pins then
    report "no way out" and their nets never route, which is a long way from
    the actual cause.
    """
    if pad.primitives is None or not len(pad.primitives.gr_polys):
        return [pad_box(pad, fx, fy, fr)]
    pts = [(pt.x, pt.y) for poly in pad.primitives.gr_polys for pt in poly.pts.xys]
    ys = sorted({round(y, 3) for _, y in pts})
    rects = []
    for y0, y1 in zip(ys, ys[1:]):
        ym = (y0 + y1) / 2
        xs = _crossings(pts, ym)
        for x0, x1 in zip(xs[0::2], xs[1::2]):
            rects.append(_local_rect(pad, fx, fy, fr, x0, y0, x1, y1))
    return rects or [pad_box(pad, fx, fy, fr)]


def _crossings(pts, ym):
    """x where the closed polygon crosses the horizontal line y = ym."""
    xs = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 <= ym < y1) or (y1 <= ym < y0):
            xs.append(x0 + (ym - y0) * (x1 - x0) / (y1 - y0))
    return sorted(xs)


def _local_rect(pad, fx, fy, fr, lx0, ly0, lx1, ly1):
    xs, ys = [], []
    for cx, cy in ((lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1)):
        px, py = rot(pad.at.x + cx, pad.at.y + cy, fr)
        xs.append(fx + px)
        ys.append(fy + py)
    return (min(xs), min(ys), max(xs), max(ys))


def pad_box(pad, fx, fy, fr):
    """A pad's bounding box in board coords.

    The BQ25798's four corner pads are `custom` shapes whose (size) field is a
    0.01mm placeholder — their real copper is in the primitives polygon. Taking
    (size) at face value makes those pads one grid cell wide and their nets
    unroutable, which is a very confusing way to find this out.
    """
    if pad.primitives is not None and len(pad.primitives.gr_polys):
        xs, ys = [], []
        for poly in pad.primitives.gr_polys:
            for pt in poly.pts.xys:
                xs.append(pt.x)
                ys.append(pt.y)
        lx0, ly0, lx1, ly1 = min(xs), min(ys), max(xs), max(ys)
    else:
        w, h = pad.size.w, (pad.size.h or pad.size.w)
        if round((pad.at.r or 0) % 180) == 90:
            w, h = h, w
        lx0, ly0, lx1, ly1 = -w / 2, -h / 2, w / 2, h / 2
    xs, ys = [], []
    for cx, cy in ((lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1)):
        px, py = rot(pad.at.x + cx, pad.at.y + cy, fr)
        xs.append(fx + px)
        ys.append(fy + py)
    return (min(xs), min(ys), max(xs), max(ys))


def fp_boxes(k):
    """(addr, pad_boxes, body_box) in board coords, honouring pad rotation."""
    out = []
    for fp in k.footprints:
        addr = next(p.value for p in fp.propertys if p.name == "atopile_address").split(".")[-1]
        fx, fy, fr = fp.at.x, fp.at.y, fp.at.r or 0
        pads, xs, ys = [], [], []
        for pad in fp.pads:
            box = pad_box(pad, fx, fy, fr)
            pads.append((pad.name, box, pad))
            xs += [box[0], box[2]]
            ys += [box[1], box[3]]
        for ln in list(fp.fp_lines) + list(fp.fp_rects):
            if "SilkS" not in str(ln.layer) and "CrtYd" not in str(ln.layer):
                continue
            for px, py in (rot(ln.start.x, ln.start.y, fr), rot(ln.end.x, ln.end.y, fr)):
                xs.append(fx + px)
                ys.append(fy + py)
        out.append((addr, pads, (min(xs), min(ys), max(xs), max(ys))))
    return out


def thicken_silk(k):
    """Raise every footprint silk stroke and text to at least MIN_SILK_W."""
    bumped = 0
    for fp in k.footprints:
        graphics = (list(fp.fp_lines) + list(fp.fp_rects)
                    + list(fp.fp_circles) + list(fp.fp_arcs) + list(fp.fp_poly))
        for g in graphics:
            if "SilkS" not in str(getattr(g, "layer", "")):
                continue
            if g.stroke and g.stroke.width < MIN_SILK_W:
                g.stroke.width = MIN_SILK_W
                bumped += 1
        for t in list(fp.fp_texts) + list(fp.propertys):
            if "SilkS" not in str(getattr(t, "layer", "")):
                continue
            if t.effects and t.effects.font and (t.effects.font.thickness or 0) < MIN_SILK_W:
                t.effects.font.thickness = MIN_SILK_W
                bumped += 1
    print(f"silk: raised {bumped} strokes/texts to >= {MIN_SILK_W}mm")


def in_region(box):
    """Is this box inside the main board or inside the tab?"""
    for x0, y0, x1, y1 in ((0, 0, BOARD_W, BOARD_H), TAB):
        if box[0] >= x0 and box[1] >= y0 and box[2] <= x1 and box[3] <= y1:
            return True
    return False


def check(k):
    """Body overlap / off-board / pad clearance, numerically. Raises on failure."""
    boxes = fp_boxes(k)
    errs = []

    def overlap(a, b, gap=0.0):
        return (a[0] < b[2] - gap and b[0] < a[2] - gap
                and a[1] < b[3] - gap and b[1] < a[3] - gap)

    for addr, pads, body in boxes:
        for _, pb, _ in pads:
            if not in_region(pb):
                errs.append(f"{addr}: pad off-board {tuple(round(v, 2) for v in pb)}")
        if addr not in EDGE_PARTS and not in_region(body):
            errs.append(f"{addr}: body off-board {tuple(round(v, 2) for v in body)}")
        if overlap(body, ANTENNA_KEEPOUT) and addr != "mcu":
            errs.append(f"{addr}: body inside the antenna keepout")
        for hx, hy in MOUNT_HOLES:
            hole = (hx - HOLE_KEEP, hy - HOLE_KEEP, hx + HOLE_KEEP, hy + HOLE_KEEP)
            if overlap(body, hole):
                errs.append(f"{addr}: body inside the mount-hole keepout at ({hx},{hy})")

    for i, (a_addr, a_pads, a_body) in enumerate(boxes):
        for b_addr, b_pads, b_body in boxes[i + 1:]:
            if overlap(a_body, b_body, gap=0.01):
                errs.append(f"{a_addr} <-> {b_addr}: bodies overlap")
            for an, ab, _ in a_pads:
                for bn, bb, _ in b_pads:
                    if overlap(ab, bb, gap=-0.2):
                        errs.append(f"{a_addr}.{an} <-> {b_addr}.{bn}: pads < 0.2mm apart")

    if errs:
        raise SystemExit("PLACEMENT CHECK FAILED:\n  " + "\n  ".join(sorted(set(errs))))
    print(f"placement check ok: {len(boxes)} footprints, none overlapping or off-board")


# --- 4-layer stackup ---------------------------------------------------------
# atopile emits a 2-layer board. Three switchers, a 0.4mm-pitch QFN and 78 nets
# on two layers is not a fight worth having, so the inner layers are added here
# and poured solid with ground.
def ensure_4_layers(text):
    if '"In1.Cu"' in text:
        return text
    text = text.replace('\t\t(0 "F.Cu" signal)\n',
                        '\t\t(0 "F.Cu" signal)\n\t\t(1 "In1.Cu" signal)\n'
                        '\t\t(2 "In2.Cu" signal)\n\t\t(3 "In3.Cu" signal)\n'
                        '\t\t(4 "In4.Cu" signal)\n')
    stack = "".join(
        f'\t\t\t(layer "In{n}.Cu"\n\t\t\t\t(type "copper")\n\t\t\t\t(thickness 0.0175)\n\t\t\t)\n'
        f'\t\t\t(layer "dielectric {n + 1}"\n\t\t\t\t(type "{"core" if n % 2 else "prepreg"}")\n'
        f'\t\t\t\t(thickness 0.3)\n\t\t\t\t(material "FR4")\n'
        f'\t\t\t\t(epsilon_r 4.5)\n\t\t\t\t(loss_tangent 0.02)\n\t\t\t)\n'
        for n in (1, 2, 3, 4)
    )
    # the existing single dielectric sits between F.Cu and B.Cu; the two inner
    # copper layers and their dielectrics go in right after F.Cu's dielectric
    m = re.search(r'(\(layer "dielectric 1"[\s\S]*?\n\t\t\t\)\n)', text)
    if not m:
        raise SystemExit("could not find dielectric 1 in the stackup")
    text = text[:m.end(1)] + stack + text[m.end(1):]
    print("stackup: promoted to 6 layers (In1/In4 GND, In2/In3 routing)")
    return text


def main():
    text = ensure_4_layers(PCB.read_text())
    pcb = kicad.loads(kicad.pcb.PcbFile, text)
    k = pcb.kicad_pcb
    place = placement()

    missing = []
    for fp in k.footprints:
        for p in fp.propertys:
            if p.at is None:
                p.at = kicad.pcb.Xyr(x=0, y=0, r=0)
            elif p.at.r is None:
                p.at.r = 0
        for t in fp.fp_texts:
            if t.at.r is None:
                t.at.r = 0

        addr = next(p.value for p in fp.propertys if p.name == "atopile_address").split(".")[-1]
        if addr not in place:
            missing.append(addr)
            continue
        x, y, r = place[addr]
        cur = fp.at.r or 0
        fp.at.x, fp.at.y = x, y
        fp.at.r = r
        delta = (r - cur) % 360
        if delta:
            for obj in list(fp.pads) + list(fp.fp_texts) + list(fp.propertys):
                obj.at.r = ((obj.at.r or 0) + delta) % 360
        # refdes text off the pads; the placement check reads bodies, and a
        # rotated right-justified field skews KiCad's own extent maths
        ref = next(p for p in fp.propertys if p.name == "Reference")
        if ref.effects:
            ref.effects.justify = None
    if missing:
        raise SystemExit("no placement for: " + ", ".join(sorted(missing)))

    clean_custom_pads(k)
    outline(k)
    silkscreen(k)
    thicken_silk(k)
    check(k)

    route(k)
    kicad.dumps(pcb, PCB)
    set_mask_expansion()
    render(pcb)


def clean_custom_pads(k):
    """Drop repeated vertices from custom pad polygons.

    EasyEDA's L-shaped QFN corner pads come out with consecutive duplicate
    points. KiCad rejects the padstack outright ("must resolve to a single
    polygon"), and it is a pure geometry defect — the outline is unchanged.
    Done on the board rather than the library so it also survives a rebuild.
    """
    fixed = 0
    for fp in k.footprints:
        for pad in fp.pads:
            if pad.primitives is None:
                continue
            for poly in pad.primitives.gr_polys:
                pts = [(pt.x, pt.y) for pt in poly.pts.xys]
                keep = [pts[0]]
                for xy in pts[1:]:
                    if xy != keep[-1]:
                        keep.append(xy)
                if len(keep) > 1 and keep[0] == keep[-1]:
                    keep.pop()
                if len(keep) == len(pts):
                    continue
                while len(poly.pts.xys):
                    poly.pts.xys.pop(len(poly.pts.xys) - 1)
                for x, y in keep:
                    poly.pts.xys.append(kicad.pcb.Xy(x=x, y=y))
                fixed += 1
    if fixed:
        print(f"padstacks: de-duplicated {fixed} custom pad polygons")


def outline(k):
    """One closed polygon: main board, neck, tab."""
    while len(k.gr_lines):
        k.gr_lines.pop(len(k.gr_lines) - 1)
    tx0, ty0, tx1, ty1 = TAB
    nx0, ny0, nx1, ny1 = NECK
    pts = [
        (0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H),
        (nx1, ny0), (nx1, ny1), (tx1, ty0), (tx1, ty1), (tx0, ty1), (tx0, ty0),
        (nx0, ny1), (nx0, ny0), (0, BOARD_H),
    ]
    loops = [pts]
    for hx, hy in MOUNT_HOLES:
        r = HOLE_D / 2
        loops.append([(hx + r * math.cos(a), hy + r * math.sin(a))
                      for a in (i * 2 * math.pi / 16 for i in range(16))])
    for loop in loops:
        for (x1, y1), (x2, y2) in zip(loop, loop[1:] + loop[:1]):
            k.gr_lines.append(kicad.pcb.Line(
                start=kicad.pcb.Xy(x=x1, y=y1),
                end=kicad.pcb.Xy(x=x2, y=y2),
                stroke=kicad.pcb.Stroke(width=0.1, type="default"),
                layer="Edge.Cuts",
            ))


def silkscreen(k):
    while len(k.gr_texts):
        k.gr_texts.pop(len(k.gr_texts) - 1)
    for text, tx, ty, size, r in SILK:
        k.gr_texts.append(kicad.pcb.Text(
            text=text,
            at=kicad.pcb.Xyr(x=tx, y=ty, r=r),
            layer=kicad.pcb.TextLayer(layer="F.SilkS"),
            effects=kicad.pcb.Effects(
                font=kicad.pcb.Font(size=kicad.pcb.Wh(w=size, h=size),
                                    thickness=max(MIN_SILK_W, round(size * 0.15, 3))),
            ),
        ))


def fanout(k, g, boxes, pads_by_net):
    """Straight escape stubs off every fine-pitch pad, before any routing.

    Each stub runs outward along its pad's own centreline, so neighbouring
    stubs stay one pad-pitch apart and legal. Once they are down, the search
    starts from copper that is already outside the chip's pad ring, which is
    the difference between "routes in a second" and "cannot leave pin 16".
    """
    by_addr = {addr: (pads, body) for addr, pads, body in boxes}
    stub_rects = []
    pending = []
    made = 0
    for addr, length in FANOUT.items():
        if addr not in by_addr:
            continue
        pads, body = by_addr[addr]
        cx, cy = (body[0] + body[2]) / 2, (body[1] + body[3]) / 2
        for i, (name, box, pad) in enumerate(pads):
            if not pad.net or not pad.net.number:
                continue
            n = pad.net.number
            if len(pads_by_net.get(n, [])) < 2:
                continue
            # Staggered lengths: if every stub on an edge ended on the same
            # line, every escaping track would have to turn at the same radius
            # and they would all jam. Four depths, 0.7mm apart, also space the
            # end-of-stub vias far enough apart to be legal (0.6mm pads at
            # 0.4mm pitch need 0.73mm centre to centre; the diagonal gives
            # 0.81mm).
            # Depth order 0,2,1,3 repeating. A stub can only END in a via if
            # it is longer than BOTH its neighbours — otherwise a neighbour's
            # stub runs 0.4mm past the via pad, which is a short. This order
            # makes that true for half the pins instead of a quarter.
            level = (0, 2, 1, 3)[i % 4]
            can_via = level >= 2 and (0, 2, 1, 3)[(i + 1) % 4] < level \
                and (0, 2, 1, 3)[(i - 1) % 4] < level
            length_i = FANOUT_PAD.get(f"{addr}.{name}", length + level * 0.7)
            px, py = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            dx, dy = px - cx, py - cy
            if abs(dx) < 0.5 and abs(dy) < 0.5:
                continue                        # centre thermal land: no way out
            w = W_SIG / 2
            if abs(dx) >= abs(dy):
                sx = box[2] + length_i if dx > 0 else box[0] - length_i
                stub = (min(sx, box[2]), py - w, max(sx, box[0]), py + w)
                end = (sx, py)
            else:
                sy = box[3] + length_i if dy > 0 else box[1] - length_i
                stub = (px - w, min(sy, box[3]), px + w, max(sy, box[1]))
                end = (px, sy)
            layers = pad_layers(pad)
            for ly in layers:
                g.core(ly, stub[0], stub[1], stub[2], stub[3], n)
            stub_rects.append((layers, stub, n))
            k.segments.append(kicad.pcb.Segment(
                start=kicad.pcb.Xy(x=round(px, 3), y=round(py, 3)),
                end=kicad.pcb.Xy(x=round(end[0], 3), y=round(end[1], 3)),
                width=W_SIG, layer=layers[0], net=n,
            ))
            # the pad's routable footprint is now pad + stub
            pending.append((f"{addr}.{name}", n, stub, end, can_via))
            made += 1

    # Vias go down only once EVERY stub is on the grid. Placed inline, a via
    # was judged against the stubs that happened to exist already, and the next
    # pin's stub then ran 0.4mm past it — which DRC calls a short.
    vias = 0
    for key, n, stub, end, can_via in pending:
        vhalf = VIA_SIZE / 2
        box, layers = stub, None
        if can_via and router.via_fits(g, g.idx(g._gx(end[0]), g._gy(end[1])), n,
                           vhalf + router.CLEAR + W_BIG / 2):
            for ly in ROUTE_LAYERS:
                g.stamp(ly, end[0] - vhalf, end[1] - vhalf,
                        end[0] + vhalf, end[1] + vhalf, n, router.CLEAR + W_BIG / 2)
            k.vias.append(kicad.pcb.Via(
                at=kicad.pcb.Xy(x=round(end[0], 3), y=round(end[1], 3)),
                size=VIA_SIZE, drill=VIA_DRILL,
                layers=["F.Cu", "B.Cu"], net=n,
            ))
            box = (min(stub[0], end[0] - vhalf), min(stub[1], end[1] - vhalf),
                   max(stub[2], end[0] + vhalf), max(stub[3], end[1] + vhalf))
            layers = list(ROUTE_LAYERS)
            vias += 1
        for j, (pn, pb, pl) in enumerate(pads_by_net[n]):
            if pn == key:
                pads_by_net[n][j] = (pn, (min(pb[0], box[0]), min(pb[1], box[1]),
                                          max(pb[2], box[2]), max(pb[3], box[3])),
                                     sorted(set(pl) | set(layers)) if layers else pl)
    print(f"fanout: {made} escape stubs, {vias} of them dropping to a via")
    return stub_rects


# --- routing -----------------------------------------------------------------
def route(k):
    """Route the board, retrying with the losers promoted to the front.

    One pass leaves a handful of nets stranded behind copper that earlier nets
    laid across their only exit. Rather than hand-tuning the order, the whole
    board is ripped up and re-routed with every failed net promoted to first
    place; three passes has been enough to close it out.
    """
    priority, best = set(), None
    for attempt in range(3):
        failed = route_pass(k, priority)
        if best is None or len(failed) < len(best[1]):
            best = (set(priority), list(failed))
        if not failed:
            return
        print(f"  pass {attempt + 1}: {len(failed)} unrouted, retrying with them first")
        # Alternate between remembering every net that has ever been stranded
        # and only the last pass's. The union converges on a good order; the
        # reset shakes it out of a local minimum where two nets keep swapping
        # which one gets the last corridor.
        if attempt % 2:
            priority = {n for n, _ in failed}
        else:
            priority |= {n for n, _ in failed}
    route_pass(k, best[0], report=True, strict=True)


def route_pass(k, priority, report=False, strict=False):
    for coll in (k.segments, k.vias):
        while len(coll):
            coll.pop(len(coll) - 1)

    boxes = fp_boxes(k)
    pad_net = {}
    for addr, pads, _ in boxes:
        for name, _, pad in pads:
            if pad.net and pad.net.number:
                pad_net[f"{addr}.{name}"] = pad.net.number
    net_name = {}
    for label, ref in NET_BY_PAD.items():
        if ref not in pad_net:
            raise SystemExit(f"net anchor {ref} ({label}) is not a pad on this board")
        net_name[pad_net[ref]] = label
    priority = set(priority) | {pad_net[r] for r in PRIORITY_PADS if r in pad_net}

    regions = [
        (EDGE_KEEP, EDGE_KEEP, BOARD_W - EDGE_KEEP, BOARD_H - EDGE_KEEP),
        (TAB[0] + EDGE_KEEP, TAB[1] + EDGE_KEEP, TAB[2] - EDGE_KEEP, TAB[3] - EDGE_KEEP),
    ]
    g = Grid(BOARD_W, TAB[3], ROUTE_LAYERS, regions)
    g.block(*ANTENNA_KEEPOUT)
    for hx, hy in MOUNT_HOLES:
        g.block(hx - HOLE_KEEP, hy - HOLE_KEEP, hx + HOLE_KEEP, hy + HOLE_KEEP)
    g.block(*PILLAR_KEEP, layers=["B.Cu"])

    # Every pad's copper goes down before any halo does. The other order lets a
    # crowded neighbour's clearance ring lock out a pad's own cells, which
    # presents as "every net failed to route".
    fp_pose = {}
    for fp in k.footprints:
        a = next(p.value for p in fp.propertys
                 if p.name == "atopile_address").split(".")[-1]
        fp_pose[a] = (fp.at.x, fp.at.y, fp.at.r or 0)
    pad_shape = {}
    pads_by_net = {}
    for addr, pads, _ in boxes:
        for name, box, pad in pads:
            if not pad.net or not pad.net.number:
                # Netless copper is still copper: the TPS61088 footprint carries
                # eight thermal vias and the USB-C two mounting posts, none of
                # them on a net. Left unstamped they are invisible to the router
                # and it lays tracks straight over them.
                # Wide enough that a VIA hole next to netless copper still
                # meets the 0.2 hole-clearance rule, not just a track.
                pad_r = router.CLEAR + W_BIG / 2 + 0.2
                for ly in ROUTE_LAYERS:
                    g.block(box[0] - pad_r, box[1] - pad_r,
                            box[2] + pad_r, box[3] + pad_r, [ly])
                continue
            n = pad.net.number
            layers = pad_layers(pad)
            rects = pad_rects(pad, *fp_pose[addr])
            for ly in layers:
                for r in rects:
                    g.core(ly, r[0], r[1], r[2], r[3], n)
            pads_by_net.setdefault(n, []).append((f"{addr}.{name}", box, layers))
            pad_shape.setdefault(f"{addr}.{name}", []).extend(rects)
    stub_rects = fanout(k, g, boxes, pads_by_net)

    for n, pads in pads_by_net.items():
        for name, box, layers in pads:
            for ly in layers:
                for r in pad_shape[name]:
                    g.halo(ly, r[0], r[1], r[2], r[3], n, router.CLEAR + W_SIG / 2)
    for layers, stub, n in stub_rects:
        for ly in layers:
            g.halo(ly, stub[0], stub[1], stub[2], stub[3], n, router.CLEAR + W_SIG / 2)

    def span(n):
        pads = pads_by_net[n]
        xs = [p[1][0] for p in pads] + [p[1][2] for p in pads]
        ys = [p[1][1] for p in pads] + [p[1][3] for p in pads]
        return (max(xs) - min(xs)) + (max(ys) - min(ys))

    # Shortest nets first: a two-pad net between neighbouring parts has exactly
    # one sensible route and no slack, while a rail with a dozen pads can go
    # almost anywhere. Ties broken by pad count.
    ordered = sorted(pads_by_net,
                     key=lambda n: (n not in priority, span(n), len(pads_by_net[n])))
    routed, failed, narrowed, squeezed, hairline = 0, [], [], [], []
    for n in ordered:
        name = net_name.get(n, str(n))
        if name in GND_NETS:
            continue
        pads = pads_by_net[n]
        if len(pads) < 2:
            continue
        width = WIDTH_BY_NAME.get(name, W_SIG)
        pads = nearest_first(pads)
        grown = _pad_cells(g, pads[0], n)
        for pad in pads[1:]:
            target = _pad_cells(g, pad, n)
            path = router.route_net(g, n, grown, target, width, W_SIG)
            w = width
            if path is None and width > W_SIG:
                # A power net that cannot get through at full width still has
                # to connect. Falling back to a signal-width run is the honest
                # trade: less copper on one leg, versus an open circuit.
                w = W_SIG
                path = router.route_net(g, n, grown, target, w, W_SIG)
                if path is not None:
                    narrowed.append(f"{name} -> {pad[0]}")
            if path is None and strict:
                # Last resort: re-judge the locked seams with the exact
                # clearance test instead of the halo approximation. A cell
                # both nets' halos claim is often still legal for one of them.
                path = router.route_net(g, n, grown, target, W_SIG, W_SIG, strict=True)
                if path is not None:
                    w = W_SIG
                    squeezed.append(f"{name} -> {pad[0]}")
                elif strict and HAIRLINE:
                    # Only for a net the retry loop has already singled out:
                    # drop to JLC's finest process for this one hop — 0.1mm at
                    # 0.1mm, inside their 0.09/0.09 floor. Searching the whole
                    # board at that clearance for every straggler costs more
                    # time than it is worth, so it is not the default.
                    path = router.route_net(g, n, grown, target, W_FINE, W_FINE,
                                            strict=True, clear=CLEAR_FINE)
                    if path is not None:
                        w = W_FINE
                        hairline.append(f"{name} -> {pad[0]}")
            if path is None:
                failed.append((n, f"{name} -> {pad[0]} "
                              f"(src {sum(len(s) for s in grown.values())} cells/"
                              f"{_open(g, grown, n)} open, "
                              f"dst {sum(len(s) for s in target.values())} cells/"
                              f"{_open(g, target, n)} open)"))
                continue
            router.stamp_path(g, path, n, w, W_SIG)
            _emit(k, g, path, n, w)
            for ly, i in path:
                grown.setdefault(ly, set()).add(i)
            for ly, cells in target.items():
                grown.setdefault(ly, set()).update(cells)
        routed += 1

    if DEBUG_MAP:
        dump_map(g, pads_by_net, *DEBUG_MAP)
    kicad_names = {n.number: n.name for n in k.nets}
    gnd_net = next(n for n, v in net_name.items() if v == "gnd")
    gnd_tab_net = next(n for n, v in net_name.items() if v == "gnd_tab")
    pour_ground(k, (gnd_net, kicad_names[gnd_net]),
                (gnd_tab_net, kicad_names[gnd_tab_net]))
    stitch_vias(k, g, pads_by_net, net_name)
    if report or not failed:
        print(f"routed {routed} nets, {len(k.segments)} segments, {len(k.vias)} vias")
        if narrowed:
            print(f"narrowed to {W_SIG}mm: " + ", ".join(narrowed))
        if squeezed:
            print("threaded on exact clearance: " + ", ".join(squeezed))
        if hairline:
            print(f"hairline ({W_FINE}mm/{CLEAR_FINE}mm): " + ", ".join(hairline))
        if failed:
            print("UNROUTED:\n  " + "\n  ".join(m for _, m in failed))
    return failed


DEBUG_MAP = None  # # ("addr.pad", half_window_mm) — prints the occupancy grid


def dump_map(g, pads_by_net, key, half):
    for n, pads in pads_by_net.items():
        for name, box, layers in pads:
            if name != key:
                continue
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            print(f"--- {key} net {n} box {[round(v,2) for v in box]}")
            for ly in ("F.Cu", "B.Cu"):
                print(f"  [{ly}]")
                for gy in range(g._gy(cy - half), g._gy(cy + half) + 1):
                    row = ""
                    for gx in range(g._gx(cx - half), g._gx(cx + half) + 1):
                        v = g.cells[ly][g.idx(gx, gy)]
                        row += "#" if v == -1 else ("." if v == 0 else
                                                    ("@" if v == n else "o"))
                    print("   ", row)
            return


def nearest_first(pads):
    """Order a net's pads so each one is the closest still-unconnected pad.

    Routing them in declaration order gives a net that criss-crosses the board;
    on a board this full, that copper is exactly what the next net needed.
    """
    def centre(p):
        return ((p[1][0] + p[1][2]) / 2, (p[1][1] + p[1][3]) / 2)

    rest = list(pads)
    out = [rest.pop(0)]
    while rest:
        best, bi = None, 0
        for i, p in enumerate(rest):
            px, py = centre(p)
            d = min((px - cx) ** 2 + (py - cy) ** 2
                    for cx, cy in (centre(q) for q in out))
            if best is None or d < best:
                best, bi = d, i
        out.append(rest.pop(bi))
    return out


def _open(g, cells, net):
    """How many free cells this island can step into — 0 means walled in."""
    n = 0
    for ly, s in cells.items():
        for i in s:
            for j in router._neighbours(g, i):
                if j not in s and g.passable(ly, j, net):
                    n += 1
    return n


def _pad_cells(g, pad, net):
    """The grid cells a pad actually owns, per layer."""
    _, box, layers = pad
    out = {}
    for ly in layers:
        s = set()
        for gy in range(g._gy(box[1]), g._gy(box[3]) + 1):
            for gx in range(g._gx(box[0]), g._gx(box[2]) + 1):
                i = g.idx(gx, gy)
                if g.cells[ly][i] == net and g.is_core[ly][i]:
                    s.add(i)
        if s:
            out[ly] = s
    return out


def _emit(k, g, path, net, width):
    segs, vias = router.path_to_geometry(g, path)
    for layer, (x1, y1), (x2, y2) in segs:
        if (x1, y1) == (x2, y2):
            continue
        k.segments.append(kicad.pcb.Segment(
            start=kicad.pcb.Xy(x=round(x1, 3), y=round(y1, 3)),
            end=kicad.pcb.Xy(x=round(x2, 3), y=round(y2, 3)),
            width=width, layer=layer, net=net,
        ))
    for x, y in vias:
        k.vias.append(kicad.pcb.Via(
            at=kicad.pcb.Xy(x=round(x, 3), y=round(y, 3)),
            size=VIA_SIZE, drill=VIA_DRILL,
            layers=["F.Cu", "B.Cu"], net=net,
        ))


def stitch_vias(k, g, pads_by_net, net_name):
    """A via per ground pad, tying it to the In1/In2 planes.

    The F.Cu pour would connect most of them anyway, but a QFN's ground pad
    with three neighbours 0.4mm away can end up an island after fill, and a
    switching converter with an islanded ground pad is a boat anchor.
    """
    added = 0
    for n, pads in pads_by_net.items():
        if net_name.get(n) not in GND_NETS:
            continue
        for _, box, _ in pads:
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            for dx, dy in ((0, 0), (0.7, 0), (-0.7, 0), (0, 0.7), (0, -0.7),
                           (0.7, 0.7), (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7),
                           (1.1, 0), (-1.1, 0), (0, 1.1), (0, -1.1)):
                x, y = cx + dx, cy + dy
                if _via_fits(g, x, y, n):
                    for ly in ROUTE_LAYERS:
                        g.stamp(ly, x - 0.3, y - 0.3, x + 0.3, y + 0.3, n,
                                router.CLEAR + W_BIG / 2)
                    k.vias.append(kicad.pcb.Via(
                        at=kicad.pcb.Xy(x=round(x, 3), y=round(y, 3)),
                        size=VIA_SIZE, drill=VIA_DRILL,
                        layers=["F.Cu", "B.Cu"], net=n,
                    ))
                    added += 1
                    break
    print(f"stitching: {added} ground vias")


def _via_fits(g, x, y, net):
    # Stitching happens after every track is down, so a stitch via only has to
    # clear what already exists — no need to reserve room for a future rail.
    # The stricter margin was leaving ground pads stranded off the pour.
    r = VIA_SIZE / 2 + router.CLEAR
    for gy in range(g._gy(y - r), g._gy(y + r) + 1):
        for gx in range(g._gx(x - r), g._gx(x + r) + 1):
            i = g.idx(gx, gy)
            for ly in g.layers:
                if not g.passable(ly, i, net):
                    return False
    return True


def pour_ground(k, gnd, gnd_tab):
    """Ground pours on all four layers, for both halves of the panel.

    The main-board polygon is the board minus the module's antenna corner — a
    pour under a PCB antenna detunes it, and no amount of via stitching makes
    up for that.
    """
    while len(k.zones):
        k.zones.pop(len(k.zones) - 1)
    e = 0.35        # pours only need their own edge clearance
    ax0, ay0, ax1, ay1 = ANTENNA_KEEPOUT
    main = [
        (e, e), (ax0, e), (ax0, ay1), (ax1, ay1), (ax1, e),
        (BOARD_W - e, e), (BOARD_W - e, BOARD_H - e), (e, BOARD_H - e),
    ]
    tab = [(TAB[0] + e, TAB[1] + e), (TAB[2] - e, TAB[1] + e),
           (TAB[2] - e, TAB[3] - e), (TAB[0] + e, TAB[3] - e)]
    for (net, name), pts in ((gnd, main), (gnd_tab, tab)):
        for layer in GND_LAYERS:
            k.zones.append(kicad.pcb.Zone(
                net=net, net_name=name, layer=layer,
                hatch=kicad.pcb.Hatch(mode="edge", pitch=0.5),
                connect_pads=kicad.pcb.ConnectPads(clearance=0.2),
                min_thickness=0.2,
                filled_areas_thickness="no",
                fill=kicad.pcb.ZoneFill(enable="yes", thermal_gap=0.2,
                                        thermal_bridge_width=0.4),
                polygon=kicad.pcb.Polygon(
                    pts=kicad.pcb.Pts(xys=[kicad.pcb.Xy(x=x, y=y) for x, y in pts])),
                uuid=kicad.gen_uuid(),
            ))
    print(f"pours: {len(k.zones)} ground zones over {len(GND_LAYERS)} layers")


def set_mask_expansion():
    """0.05mm of mask expansion — the usual house value."""
    text = PCB.read_text()
    new, n = re.subn(r"\(pad_to_mask_clearance [\d.]+\)",
                     "(pad_to_mask_clearance 0.05)", text, count=1)
    assert n == 1, "pad_to_mask_clearance not found in the board setup block"
    PCB.write_text(new)


def render(pcb):
    k = pcb.kicad_pcb
    S = 12  # px per mm
    H = TAB[3]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'viewBox="-40 -50 {BOARD_W * S + 80} {H * S + 90}" font-family="monospace">',
           f'<rect x="-40" y="-50" width="{BOARD_W * S + 80}" height="{H * S + 90}" fill="#10141a"/>',
           f'<rect x="0" y="0" width="{BOARD_W * S}" height="{BOARD_H * S}" rx="6" '
           f'fill="#173425" stroke="#c8a038" stroke-width="2"/>',
           f'<rect x="{TAB[0] * S}" y="{TAB[1] * S}" width="{(TAB[2] - TAB[0]) * S}" '
           f'height="{(TAB[3] - TAB[1]) * S}" rx="6" fill="#173425" stroke="#c8a038" stroke-width="2"/>']

    for want, color in (("B.Cu", "#3b6ea5"), ("F.Cu", "#b0433b")):
        for seg in k.segments:
            if str(seg.layer) != want:
                continue
            out.append(f'<line x1="{seg.start.x * S:.1f}" y1="{seg.start.y * S:.1f}" '
                       f'x2="{seg.end.x * S:.1f}" y2="{seg.end.y * S:.1f}" '
                       f'stroke="{color}" stroke-width="{seg.width * S:.1f}" '
                       f'stroke-linecap="round" opacity="0.9"/>')

    net_pads = {}
    routed_nets = {seg.net for seg in k.segments}
    for fp in k.footprints:
        fx, fy, fr = fp.at.x, fp.at.y, fp.at.r or 0
        ref = next(p.value for p in fp.propertys if p.name == "Reference")
        for ln in fp.fp_lines:
            if "SilkS" not in str(ln.layer):
                continue
            x1, y1 = rot(ln.start.x, ln.start.y, fr)
            x2, y2 = rot(ln.end.x, ln.end.y, fr)
            out.append(f'<line x1="{(fx + x1) * S:.1f}" y1="{(fy + y1) * S:.1f}" '
                       f'x2="{(fx + x2) * S:.1f}" y2="{(fy + y2) * S:.1f}" '
                       f'stroke="#8fa3b8" stroke-width="0.8"/>')
        for pad in fp.pads:
            lx, ly_ = rot(pad.at.x, pad.at.y, fr)
            px, py = (fx + lx) * S, (fy + ly_) * S
            w, h = pad.size.w * S, (pad.size.h or pad.size.w) * S
            if (pad.at.r or 0) % 360 in (90, 270):
                w, h = h, w
            tht = str(pad.type) == "thru_hole"
            color = "#d4b03c" if tht else "#c87533"
            out.append(f'<rect x="{px - w / 2:.1f}" y="{py - h / 2:.1f}" width="{w:.1f}" '
                       f'height="{h:.1f}" rx="1" fill="{color}"/>')
            if pad.net and pad.net.number and pad.net.number not in routed_nets:
                net_pads.setdefault(pad.net.name, []).append((px, py))
        out.append(f'<text x="{fx * S:.1f}" y="{fy * S - 3:.1f}" fill="#e8e0d0" '
                   f'font-size="7" text-anchor="middle">{ref}</text>')

    for via in k.vias:
        out.append(f'<circle cx="{via.at.x * S:.1f}" cy="{via.at.y * S:.1f}" '
                   f'r="{via.size * S / 2:.1f}" fill="#d4b03c" opacity="0.8"/>')

    for name, pads in net_pads.items():
        for (x1, y1), (x2, y2) in zip(pads, pads[1:]):
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                       f'stroke="#4fd1c5" stroke-width="0.7" opacity="0.55"/>')

    out.append(f'<text x="{BOARD_W * S / 2}" y="-20" fill="#e8e0d0" font-size="13" '
               f'text-anchor="middle">blinds driver rev B — {BOARD_W:.0f}x{BOARD_H:.0f}mm '
               f'+ hall tab — red=F.Cu blue=B.Cu</text>')
    out.append("</svg>")
    (ROOT / "preview.svg").write_text("\n".join(out))
    print("wrote", ROOT / "preview.svg")


if __name__ == "__main__":
    main()
