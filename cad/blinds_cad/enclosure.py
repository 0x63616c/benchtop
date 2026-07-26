"""Enclosure shell — the flush wall unit body. Printable.

Built in UNIT frame (see frames.py): back-left-bottom corner at the
origin. One print: outer skin + motor bulkhead + sprocket wrap-guide
block + french-cleat hook bar. Back is open (rimmed) — it faces the
wall plate; a dedicated back/service panel is a later refinement.

Cutouts: 2 chain slots (top), 2 button holes (left), USB-C (bottom).

View it: `just cad view blinds-shell`.
"""

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
    body += _wrap_guide()
    body += _cleat_hook()

    # chain slots through the top face, over the two strands
    for y in P.strand_y:
        body -= _box(
            P.spr_x - P.chain_slot / 2, y - P.chain_slot / 2, h - t - 1,
            P.spr_x + P.chain_slot / 2, y + P.chain_slot / 2, h + 1,
        )
    # two buttons, left wall
    for z in (P.btn_z1, P.btn_z2):
        body -= Pos(t / 2, P.axis_y, z) * (
            Rot(0, 90, 0) * Cylinder(P.btn_d / 2, t + 2)
        )
    # USB-C, bottom face
    body -= _box(
        P.usb_x - P.usb_w / 2, P.axis_y - P.usb_t / 2, -1,
        P.usb_x + P.usb_w / 2, P.axis_y + P.usb_t / 2, t + 1,
    )
    return body


def _bulkhead():
    """Motor-mount rib: gearbox face screws into it; boss passes through."""
    t = P.enc_wall
    rib = _box(P.bulkhead_x, t, t, P.bulkhead_x + P.bulkhead_t, P.enc_d - t, P.bulkhead_top)
    # boss through-hole on the SHAFT axis
    rib -= Pos(P.bulkhead_x + P.bulkhead_t / 2, P.axis_y, P.axis_z) * (
        Rot(0, 90, 0) * Cylinder(P.jgb_boss_d / 2 + 0.5, P.bulkhead_t + 2)
    )
    # 6×M3 tap holes on the GEARBOX axis (7 above the shaft)
    import math

    for i in range(P.jgb_screw_n):
        a = math.radians(i * 360 / P.jgb_screw_n)
        r = P.jgb_screw_bcd / 2
        rib -= Pos(
            P.bulkhead_x + P.bulkhead_t / 2,
            P.axis_y + r * math.cos(a),
            P.axis_z + P.jgb_ecc + r * math.sin(a),
        ) * (Rot(0, 90, 0) * Cylinder(1.3, P.bulkhead_t + 2))  # M3 tap Ø2.6
    return rib


def _wrap_guide():
    """Sprocket housing: lower-half drum with the chain channel cut —
    outer wall + side cheeks keep the chain wrapped >=180° and strip it
    off the wheel (#16). Vertical run slots exit upward."""
    cx, cy, cz = P.spr_x, P.axis_y, P.axis_z
    r_ball = P.chain_ball_d / 2 + P.spr_ball_clear
    block = Pos(cx, cy, cz) * (Rot(0, 90, 0) * Cylinder(P.guide_or, 12))
    block -= _box(cx - 7, cy - P.guide_or - 1, cz, cx + 7, cy + P.guide_or + 1,
                  cz + P.guide_or + 1)  # keep lower half only
    # wheel clearance
    block -= Pos(cx, cy, cz) * (Rot(0, 90, 0) * Cylinder(P.spr_od / 2 + 1.2, 9.5))
    # hub + shaft bore through the side cheeks
    block -= Pos(cx, cy, cz) * (Rot(0, 90, 0) * Cylinder(P.spr_hub_d / 2 + 1, 14))
    # chain channel around the wrap
    block -= Pos(cx, cy, cz) * (Rot(0, 90, 0) * Torus(P.spr_pcd / 2, r_ball))
    # vertical run exits
    for y in P.strand_y:
        block -= _box(cx - 3.5, y - r_ball, cz - 1, cx + 3.5, y + r_ball, cz + P.guide_or + 1)
    return block


def _cleat_hook():
    """Hook bar inside the top of the back opening; 45° notch receives
    the wall plate's cleat rail (0.3 clearance)."""
    rail_top = 170.0
    # CCW winding — CW polygons extrude along -Z and flip the axis map
    notch = Polygon(
        (0, rail_top - P.cleat_h - 0.3),
        (P.cleat_t + 0.3, rail_top + 0.3),
        (0, rail_top + 0.3),
    )
    bar = _box(11, 0, rail_top - P.cleat_h - 4, P.enc_w - 11, P.cleat_t + 2, P.enc_h - 10)
    # Rot(0,90,90) is the cyclic axis map: sketch(x,y)+extrude(z) -> unit(y,z,x)
    cut = Rot(0, 90, 90) * extrude(notch, amount=P.enc_w)
    return bar - cut


def scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(shell(), "shell", color="whitesmoke")
