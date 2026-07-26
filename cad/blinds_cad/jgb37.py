"""JGB37-520B encoder gearmotor — reference model of the bought part.

Not printed; exists so the enclosure is fit-checked against verified
dims (ASLONG datasheet; caliper on arrival). Origin is the SHAFT axis
at the gearbox front face, shaft +Z, body -Z. The gearbox/motor axis
sits jgb_ecc away in local +Y — the 7mm eccentricity that tunes how
low the sprocket sits.

View it: `just cad view blinds-motor`.
"""

from build123d import Box, Cylinder, Pos

from .params import P


def jgb37():
    """Gearbox drum, can, encoder cap, boss, eccentric D-shaft, M3 holes."""
    gear_c = Pos(0, P.jgb_ecc)  # gearbox/motor axis in the shaft frame

    gearbox = gear_c * Pos(0, 0, -P.jgb_gear_len / 2) * Cylinder(
        P.jgb_gear_d / 2, P.jgb_gear_len
    )
    # 6×M3 on the face, around the GEARBOX axis
    for i in range(P.jgb_screw_n):
        gearbox -= gear_c * Pos(0, 0, -P.jgb_screw_depth / 2) * (
            _polar_z(P.jgb_screw_bcd / 2, i * 360 / P.jgb_screw_n)
            * Cylinder(P.jgb_screw_d / 2, P.jgb_screw_depth)
        )

    can_len = P.jgb_can_len + P.jgb_term_len
    can = gear_c * Pos(0, 0, -P.jgb_gear_len - can_len / 2) * Cylinder(
        P.jgb_can_d / 2, can_len
    )
    enc = gear_c * Pos(0, 0, -P.jgb_body_len + P.jgb_enc_len / 2) * Cylinder(
        P.jgb_can_d / 2, P.jgb_enc_len
    )

    boss = Pos(0, 0, P.jgb_boss_h / 2) * Cylinder(P.jgb_boss_d / 2, P.jgb_boss_h)
    shaft = Pos(0, 0, P.jgb_boss_h + P.jgb_shaft_len / 2) * Cylinder(
        P.jgb_shaft_d / 2, P.jgb_shaft_len
    )
    # single D-flat over the tip zone
    flat_z = P.jgb_boss_h + P.jgb_shaft_len - P.jgb_shaft_flat_len / 2
    cut_y = P.jgb_shaft_flat - P.jgb_shaft_d / 2  # flat plane -> box centre
    shaft -= Pos(0, cut_y + P.jgb_shaft_d / 2, flat_z) * Box(
        P.jgb_shaft_d * 2, P.jgb_shaft_d, P.jgb_shaft_flat_len
    )

    return gearbox + can + enc + boss + shaft


def _polar_z(r: float, deg: float):
    import math

    a = math.radians(deg)
    return Pos(r * math.cos(a), r * math.sin(a), 0)


def scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(jgb37(), "jgb37", color="silver")
