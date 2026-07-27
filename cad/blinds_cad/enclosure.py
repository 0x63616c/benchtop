"""Enclosure shell — the flush wall unit body, v2 center-drop. Printable.

Built in UNIT frame (see frames.py): back-left-bottom corner at the
origin. One print: outer skin + motor bulkhead rib + layshaft saddles
+ tail collar + sprocket wrap-guide block + french-cleat hook bar +
PCB floor bosses + carrier bosses. Back is open (rimmed) — it faces
the wall plate.

Cutouts: 2 chain slots (top, centered at x=49±11.5), 2 button holes +
USB-C slot (front wall, bottom), M5 axle bore (front wall -> cleat bar).

The layshaft U-saddles open toward the BACK: the layshaft drops in
through the opening, the gear mesh + a printed clip retain it.

View it: `just cad view blinds-shell`.
"""

import math

from build123d import Box, Cylinder, Polygon, Pos, Rot, Torus, extrude, fillet

from .params import P


def _box(x0, y0, z0, x1, y1, z1):
    """Axis-aligned box by min/max corners — layout reads as coordinates."""
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        x1 - x0, y1 - y0, z1 - z0
    )


def shell():
    w, d, h, t = P.enc_w, P.enc_d, P.enc_h, P.enc_wall

    body = _box(0, 0, 0, w, d, h)
    body = fillet(
        body.edges().filter_by(lambda e: abs(e.length - h) < 1e-6), P.enc_fillet
    )
    body -= _box(t, t, t, w - t, d - t, h - t)  # cavity
    # open back: rimmed opening onto the wall plate
    body -= _box(10, -1, 10, w - 10, t + 0.1, h - 10)

    body += _bulkhead()
    body += _right_saddle()
    body += _tail_collar()
    body += _wrap_guide()
    body += _cleat_hook()
    body += _floor_bosses()
    body += _carrier_bosses()

    # chain slots through the top face, over the two strands
    for x in P.strand_x:
        body -= _box(
            x - P.chain_slot / 2, P.spr_wy - P.chain_slot / 2, h - t - 1,
            x + P.chain_slot / 2, P.spr_wy + P.chain_slot / 2, h + 1,
        )
    # two buttons + USB-C, front wall bottom
    for x in (P.btn_x1, P.btn_x2):
        body -= Pos(x, d - t / 2, P.btn_z) * (
            Rot(90, 0, 0) * Cylinder(P.btn_d / 2, t + 2)
        )
    body -= _box(
        P.usb_x - P.usb_w / 2, d - t - 1, P.usb_z - P.usb_t / 2,
        P.usb_x + P.usb_w / 2, d + 1, P.usb_z + P.usb_t / 2,
    )
    # M5 sprocket axle: front wall -> guide cheeks -> cleat bar
    body -= Pos(P.drive_x, d / 2, P.spr_z) * (
        Rot(90, 0, 0) * Cylinder(P.axle_d / 2 + 0.1, d + 4)
    )
    # cleat rail corridor: hooking on raises the unit ~12, so the rail
    # overshoots its seat upward — clear everything above the rail top
    # in its y band (top-wall strip, bulkhead rib corner, bar sliver)
    body -= _box(
        10, -1, P.cleat_rail_top - 0.3,
        P.enc_w - 10, P.cleat_t + 0.4, h + 1,
    )
    return body


def _bulkhead():
    """Vertical motor-mount rib at the gearbox face: 6×M3 into the face,
    boss through-hole, and the layshaft's left U-saddle."""
    t = P.enc_wall
    rib = _box(P.bulkhead_x, t, P.bulkhead_z0, P.bulkhead_x + P.bulkhead_t, P.enc_d - t, P.enc_h - t)
    # boss through-hole on the SHAFT axis
    rib -= Pos(P.bulkhead_x + P.bulkhead_t / 2, P.drive_y, P.motor_z) * (
        Rot(0, 90, 0) * Cylinder(P.jgb_boss_d / 2 + 0.75, P.bulkhead_t + 2)
    )
    # 6×M3 tap holes on the GEARBOX axis (7 below the shaft — ecc down)
    for i in range(P.jgb_screw_n):
        a = math.radians(i * 360 / P.jgb_screw_n)
        r = P.jgb_screw_bcd / 2
        rib -= Pos(
            P.bulkhead_x + P.bulkhead_t / 2,
            P.drive_y + r * math.cos(a),
            P.motor_z - P.jgb_ecc + r * math.sin(a),
        ) * (Rot(0, 90, 0) * Cylinder(1.3, P.bulkhead_t + 2))  # M3 tap Ø2.6
    rib -= _saddle_cut(P.bulkhead_x - 1, P.bulkhead_x + P.bulkhead_t + 1)
    rib -= _rail_cut()  # the seated cleat rail passes through this x
    return rib


def _right_saddle():
    """Layshaft right U-saddle block, hung from the top face."""
    block = _box(P.saddle_x0, 13, 213, P.saddle_x1, 29, P.enc_h - P.enc_wall)
    return block - _saddle_cut(P.saddle_x0 - 1, P.saddle_x1 + 1)


def _saddle_cut(x0, x1):
    """Layshaft bore + back-opening slot between the given x planes."""
    r = P.saddle_bore / 2
    cut = Pos((x0 + x1) / 2, P.drive_y, P.lay_z) * (
        Rot(0, 90, 0) * Cylinder(r, x1 - x0)
    )
    cut += _box(x0, P.enc_wall - 0.1, P.lay_z - r, x1, P.drive_y, P.lay_z + r)
    return cut


def _tail_collar():
    """Ring steadying the motor can near its encoder end."""
    gz = P.motor_z - P.jgb_ecc  # gearbox/can axis
    ring = Pos((P.collar_x0 + P.collar_x1) / 2, P.drive_y, gz) * (
        Rot(0, 90, 0)
        * (Cylinder(P.jgb_gear_d / 2 + 2.0, P.collar_x1 - P.collar_x0)
           - Cylinder(P.jgb_gear_d / 2 + 0.35, P.collar_x1 - P.collar_x0 + 2))
    )
    # clamp inside the cavity and tie it to the front wall
    ring &= _box(P.collar_x0, 2.5, P.bulkhead_z0 - 3, P.collar_x1, P.enc_d - P.enc_wall, P.enc_h)
    ring += _box(P.collar_x0, 38, gz - 8, P.collar_x1, P.enc_d - P.enc_wall + 0.1, gz + 8)
    return ring


def _wrap_guide():
    """Sprocket housing: block hung from the top face around the wheel —
    keeps the chain wrapped >=180° and strips it off the wheel (#16).
    Vertical run slots exit upward through the top-face chain slots."""
    cx, cz, wy = P.drive_x, P.spr_z, P.spr_wy
    r_ball = P.chain_ball_d / 2 + P.spr_ball_clear
    block = _box(cx - 10, 31, cz - P.guide_or, cx + 10, P.enc_d - P.enc_wall, P.enc_h - P.enc_wall)
    # wheel clearance
    block -= Pos(cx, wy, cz) * (
        Rot(90, 0, 0) * Cylinder(P.spr_od / 2 + 1.2, P.spr_w + 2)
    )
    # chain channel around the wrap
    block -= Pos(cx, wy, cz) * (Rot(90, 0, 0) * Torus(P.spr_pcd / 2, r_ball))
    # vertical run exits
    for x in P.strand_x:
        block -= _box(x - r_ball, wy - r_ball, cz - 1, x + r_ball, wy + r_ball, P.enc_h + 1)
    return block


def _cleat_hook():
    """Hook bar inside the top of the back opening; 45° notch receives
    the wall plate's cleat rail (0.3 clearance). Doubles as the back
    bearing for the sprocket's M5 axle. Kept to y<=7 so the sprocket
    ring gear (back face y 8.5) clears it, and to x<=76 so the
    layshaft's spur wheel does."""
    rail_top = P.cleat_rail_top
    bar = _box(P.cleat_x0, 0, rail_top - P.cleat_h - 4, P.cleat_x1, P.cleat_t + 1, P.enc_h - 10)
    return bar - _rail_cut()


def _rail_cut():
    """The seated rail's notch prism (0.3 clearance), across the whole
    opening span — the hook bar AND the bulkhead rib both clear it."""
    rail_top = P.cleat_rail_top
    # CCW winding — CW polygons extrude along -Z and flip the axis map
    notch = Polygon(
        (0, rail_top - P.cleat_h - 0.3),
        (P.cleat_t + 0.3, rail_top + 0.3),
        (0, rail_top + 0.3),
    )
    # Rot(0,90,90) is the cyclic axis map: sketch(x,y)+extrude(z) -> unit(y,z,x)
    return Rot(0, 90, 90) * extrude(notch, amount=P.enc_w)




def _floor_bosses():
    """3× M3 bosses under the flat main PCB's holes + the plain support
    pillar under the USB-C edge (plug insertion force)."""
    bosses = None
    for x, y in P.pcb_holes:
        b = Pos(x, y, (P.enc_wall + P.pcb_z0) / 2) * Cylinder(
            3.5, P.pcb_z0 - P.enc_wall
        )
        b -= Pos(x, y, P.pcb_z0 - 3) * Cylinder(1.3, 6.2)
        bosses = b if bosses is None else bosses + b
    px, py = P.pcb_pillar
    bosses += Pos(px, py, (P.enc_wall + P.pcb_z0) / 2) * Cylinder(
        3.0, P.pcb_z0 - P.enc_wall
    )
    return bosses


def _carrier_bosses():
    """4× M3 heat-set standoffs off the back wall for the battery
    carrier PCB (holders solder to it; it busses the 2S3P pack)."""
    w = P.holder_l + 0.4
    hgt = (P.cell_n - 1) * P.cell_pitch + P.holder_w + 2.0
    zc = P.bay_z0 + (P.cell_n - 1) * P.cell_pitch / 2
    bosses = None
    for sx in (-1, 1):
        for sz in (-1, 1):
            x = P.drive_x + sx * (w / 2 - 4)
            z = zc + sz * (hgt / 2 - 4)
            b = Pos(x, (P.enc_wall + P.carrier_y0) / 2, z) * (
                Rot(90, 0, 0) * Cylinder(4.0, P.carrier_y0 - P.enc_wall)
            )
            b -= Pos(x, P.carrier_y0 - 3, z) * (Rot(90, 0, 0) * Cylinder(2.3, 6.2))
            bosses = b if bosses is None else bosses + b
    return bosses


def scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(shell(), "shell", color="whitesmoke")
