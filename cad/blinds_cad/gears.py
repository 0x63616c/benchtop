"""Printed gear train for the v2 center-drop drive. Printable ×2.

Two parts:
  * `pinion()`   — m2 z14 spur on the motor's 6mm D-shaft.
  * `layshaft()` — ONE print: m2 z17 spur + Ø8 shaft + m2 z10 bevel
                   at the far end. Rides in two U-saddles (bulkhead
                   rib + right block), retained by the mesh + clips.

Tooth geometry: proper involute flanks (20° PA) computed as a point
polyline; the bevel is the same outline lofted toward its 45° cone
apex — a straight-bevel approximation that prints clean and meshes
the sprocket's identical z10 ring. Steel bevels can replace the pair
later; bores stay standard (Ø6 D / Ø5 axle on the sprocket side).

Local frames: gear axis +Z. The layshaft's bevel HEEL plane is z=0
with the cone apex at +Z (z=+bevel_r); shaft and spur extend -Z.

View: `just cad view blinds-gears`.
"""

import math

from build123d import Box, Cylinder, Polygon, Pos, Rot, extrude, loft

from .params import P


def _inv(t: float) -> float:
    return t - math.atan(t)


def gear_outline(m: float, z: int, pa_deg: float = 20.0) -> list:
    """Full involute gear outline as a closed point loop (CCW)."""
    pa = math.radians(pa_deg)
    r_p = m * z / 2
    r_b = r_p * math.cos(pa)
    r_a = r_p + m            # addendum
    r_r = r_p - 1.25 * m     # dedendum
    beta = math.pi / (2 * z) + _inv(math.tan(pa))  # base half-thickness angle
    t_a = math.sqrt((r_a / r_b) ** 2 - 1)          # roll param at the tip
    theta_tip = beta - _inv(t_a)
    pitch = 2 * math.pi / z

    pts = []
    for i in range(z):
        c = i * pitch
        # root arc from the previous gap into this tooth
        for k in range(3):
            a = c - pitch / 2 + k * (pitch / 2 - beta) / 2
            pts.append((r_r * math.cos(a), r_r * math.sin(a)))
        # leading flank, root -> tip
        for k in range(6):
            t = t_a * k / 5
            r = r_b * math.sqrt(1 + t * t)
            a = c - beta + _inv(t)
            pts.append((max(r, r_r) * math.cos(a), max(r, r_r) * math.sin(a)))
        # tip arc
        for k in range(3):
            a = c - theta_tip + k * theta_tip
            pts.append((r_a * math.cos(a), r_a * math.sin(a)))
        # trailing flank, tip -> root
        for k in range(6):
            t = t_a * (5 - k) / 5
            r = r_b * math.sqrt(1 + t * t)
            a = c + beta - _inv(t)
            pts.append((max(r, r_r) * math.cos(a), max(r, r_r) * math.sin(a)))
        # root arc out of this tooth
        for k in range(3):
            a = c + beta + (k + 1) * (pitch / 2 - beta) / 3
            pts.append((r_r * math.cos(a), r_r * math.sin(a)))
    return pts


def spur(m: float, z: int, width: float):
    """Spur gear blank, z=0..width, no bore."""
    return extrude(Polygon(*gear_outline(m, z)), amount=width)


def bevel(m: float, z: int, face: float):
    """Straight 45° miter bevel: heel outline at z=0 lofted toward the
    cone apex at z=+pitch_r. Toe scale follows the cone distance."""
    r_p = m * z / 2
    cone = r_p * math.sqrt(2)          # heel cone distance
    s = (cone - face) / cone           # toe scale about the apex
    dz = face / math.sqrt(2)
    heel = gear_outline(m, z)
    toe = [(x * s, y * s) for x, y in heel]
    return loft([Polygon(*heel), Pos(0, 0, dz) * Polygon(*toe)])


def _d_bore(length: float):
    """Ø6.2 D-bore matching the motor shaft (flat toward +Y local)."""
    bore = Cylinder(3.1, length)
    flat_y = 5.55 - 3.1
    bore -= Pos(0, flat_y + 3.1) * Box(6.2 * 2, 6.2, length + 2)
    return bore


def pinion():
    """Motor spur pinion, centered on z=0 (rides the shaft flat)."""
    g = Pos(0, 0, -P.spur_w / 2) * spur(P.gear_m, P.spur_pinion_z, P.spur_w)
    return g - _d_bore(P.spur_w + 2)


def layshaft():
    """Bevel (heel z=0, apex +Z) + Ø8 shaft + z17 spur, one print."""
    body = bevel(P.gear_m, P.bevel_z, P.bevel_face)
    body += Pos(0, 0, -2.5) * Cylinder(P.lay_hub_d / 2, 5)  # bevel hub, z -5..0
    # (kept short: the hub must stay left of the bulkhead rib at x 67)
    shaft_len = 33.0  # unit x 59..92: through both saddles
    body += Pos(0, 0, -shaft_len / 2) * Cylinder(P.lay_shaft_d / 2, shaft_len)
    # spur wheel over the pinion: unit x = bevel_heel_x - local z, so the
    # teeth at unit x 78..85 live at local z -26..-19
    z_far = P.bevel_heel_x - (P.pinion_x + P.spur_w / 2)  # -26
    body += Pos(0, 0, z_far) * spur(P.gear_m, P.spur_wheel_z, P.spur_w)
    return body


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    s.add(pinion(), "pinion", color="orange")
    s.add(layshaft(), "layshaft", color="goldenrod", loc=Pos(45, 0, 0))
    return s
