"""JGB37-520 encoder gearmotor reference for the enclosed Flatbed gearbox.

Local origin is the output-shaft axis on the gearbox front face. The shaft
points +Y, the motor body points -Y, and the Ø37 gearbox/motor axis is offset
7 mm in +Z. The mechanical envelope reuses the repo's 24 mm ``L`` variant.
The rear encoder is conservative envelope geometry: measure the exact PCB and
connector before using it as anything tighter than a collision keepout.
"""

from math import cos, radians, sin

from build123d import Align, Box, Cylinder, Pos, Rot

from splitflap_cad.viewer import Scene

from .params import P


def _cylinder_y(radius: float, length: float):
    cylinder = Cylinder(
        radius,
        length,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return Rot(-90, 0, 0) * cylinder


def _polar_xz(radius: float, degrees: float):
    angle = radians(degrees)
    return Pos(radius * cos(angle), 0, radius * sin(angle))


def _d_shaft_y():
    radius = P.fg_motor_shaft_d / 2
    shaft = _cylinder_y(radius, P.fg_motor_shaft_len)
    flat_z = P.fg_motor_shaft_flat - radius
    keep = Pos(0, P.fg_motor_shaft_len / 2, (-radius + flat_z) / 2) * Box(
        P.fg_motor_shaft_d + 0.2,
        P.fg_motor_shaft_len + 0.2,
        P.fg_motor_shaft_flat + 0.2,
    )
    return shaft & keep


def motor_reference():
    """Bought motor envelope including face holes, boss, shaft, and encoder."""
    centre = Pos(0, 0, P.fg_motor_ecc)
    gearbox = centre * Pos(0, -P.fg_motor_gear_len, 0) * _cylinder_y(
        P.fg_motor_gear_d / 2,
        P.fg_motor_gear_len,
    )
    for index in range(P.fg_motor_screw_n):
        hole = centre * _polar_xz(
            P.fg_motor_screw_bcd / 2,
            index * 360 / P.fg_motor_screw_n,
        )
        gearbox -= hole * Pos(0, -P.fg_motor_screw_depth, 0) * _cylinder_y(
            P.fg_motor_screw_d / 2,
            P.fg_motor_screw_depth + 0.1,
        )

    can_y0 = -P.fg_motor_gear_len - P.fg_motor_can_len
    can = centre * Pos(0, can_y0, 0) * _cylinder_y(
        P.fg_motor_can_d / 2,
        P.fg_motor_can_len,
    )
    encoder_y0 = -P.fg_motor_body_len
    encoder = centre * Pos(0, encoder_y0, 0) * _cylinder_y(
        P.fg_motor_can_d / 2,
        P.fg_motor_encoder_len,
    )
    boss = _cylinder_y(P.fg_motor_boss_d / 2, P.fg_motor_boss_h)
    shaft = Pos(0, P.fg_motor_boss_h, 0) * _d_shaft_y()
    return gearbox + can + encoder + boss + shaft


def scene() -> Scene:
    return Scene().add(motor_reference(), "jgb37-520-encoder", "silver")
