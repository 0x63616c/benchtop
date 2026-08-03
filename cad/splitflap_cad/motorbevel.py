"""Circular right-angle bevel attachment for the measured JGB37 motor.

The motor gearbox face is z=0 with its Ø37 centre at the origin. Its
6mm D-shaft is eccentric 7mm in -Y. The attachment stays within a Ø37
main circular body; only the horizontal output bearing nose, output rod,
and M3 screw heads may project. The 16T:24T pair gives a 3:2 reduction
and directs the 5mm output rod inward along +Y.

View: `just cad view gear-box-motor`.
"""

from math import cos, radians, sin

from build123d import Align, Cone, Pos, Rot

from . import frames as F
from .gearbox import (
    _cylinder,
    _d_prism,
    _box_at,
    _pair_parts,
    bearing_625zz,
)
from .params import P
from .viewer import Scene


def _polar(r: float, degrees: float):
    angle = radians(degrees)
    return Pos(r * cos(angle), r * sin(angle), 0)


def motor_reference():
    """Measured JGB37 envelope, centred on its Ø37 gearbox face."""
    gearbox = Pos(0, 0, -P.gba_motor_gear_len) * _cylinder(
        P.gba_motor_d / 2, P.gba_motor_gear_len
    )
    for index in range(P.gba_motor_screw_n):
        hole = _polar(
            P.gba_motor_screw_bcd / 2,
            index * 360 / P.gba_motor_screw_n,
        )
        gearbox -= hole * Pos(0, 0, -P.gba_motor_screw_depth) * _cylinder(
            P.gba_motor_screw_d / 2, P.gba_motor_screw_depth + 0.1
        )

    can = Pos(0, 0, -P.gba_motor_gear_len - P.gba_motor_can_len) * _cylinder(
        P.gba_motor_can_d / 2, P.gba_motor_can_len
    )
    encoder = Pos(0, 0, -P.gba_motor_body_len) * _cylinder(
        P.gba_motor_can_d / 2, P.gba_motor_encoder_len
    )
    boss = Pos(0, P.gba_input_y, 0) * _cylinder(
        P.gba_motor_boss_d / 2, P.gba_motor_boss_h
    )
    shaft = (
        Pos(0, P.gba_input_y, P.gba_motor_boss_h)
        * Rot(0, 0, 90)
        * _d_prism(
            P.gba_motor_shaft_d,
            P.gba_motor_shaft_flat,
            P.gba_motor_shaft_len,
        )
    )
    return gearbox + can + encoder + boss + shaft


def housing():
    """Ø37 mounting flange and shell with an outward bearing nose."""
    body = _cylinder(P.gba_outer_r, P.gba_body_h)
    body -= Pos(0, 0, P.gba_base_t) * _cylinder(
        P.gba_inner_r, P.gba_body_h - P.gba_base_t + 1
    )

    # The eccentric motor boss passes through the mounting deck.
    body -= Pos(0, P.gba_input_y, -0.5) * _cylinder(
        P.gba_boss_clear_d / 2, P.gba_base_t + 1
    )

    # Six top-installed M3 screws. Full-height channels intentionally open
    # through the Ø37 rim, keeping every screw visible and reachable from
    # the open top despite the tight 32mm bolt circle.
    for index in range(P.gba_motor_screw_n):
        hole = _polar(
            P.gba_motor_screw_bcd / 2,
            index * 360 / P.gba_motor_screw_n,
        )
        body -= hole * Pos(0, 0, -0.5) * _cylinder(
            P.gba_mount_clear_d / 2, P.gba_base_t + 1
        )
        body -= hole * Pos(0, 0, P.gba_base_t) * _cylinder(
            P.gba_screw_head_d / 2,
            P.gba_body_h - P.gba_base_t + 0.5,
        )

    # A top-open keyed saddle receives the separately printed bearing
    # cartridge. This avoids an unprintable horizontal bearing tunnel.
    cartridge_y0 = P.gba_output_bearing_y0 - 0.5
    main_slot_w = P.gba_bearing_cartridge_d + 2 * P.gba_cartridge_clear
    body -= _box_at(
        -main_slot_w / 2,
        cartridge_y0,
        P.gba_axis_z - main_slot_w / 2,
        main_slot_w,
        P.gba_outer_r + 1.5 - cartridge_y0,
        P.gba_body_h - (P.gba_axis_z - main_slot_w / 2) + 0.5,
    )
    flange_slot_w = P.gba_bearing_flange_d + 2 * P.gba_cartridge_clear
    flange_y0 = P.gba_outer_r + 1 - P.gba_bearing_flange_t
    body -= _box_at(
        -flange_slot_w / 2,
        flange_y0,
        P.gba_axis_z - flange_slot_w / 2,
        flange_slot_w,
        P.gba_bearing_flange_t + 0.6,
        P.gba_body_h - (P.gba_axis_z - flange_slot_w / 2) + 0.5,
    )
    return body


def lid():
    """Circular press-fit lid with a bearing-cartridge capture rib."""
    plate = _cylinder(P.gba_outer_r, P.gba_lid_t)
    plug = Pos(0, 0, -P.gba_lid_plug) * _cylinder(
        P.gba_lid_plug_r, P.gba_lid_plug
    )
    cartridge_top = P.gba_axis_z + P.gba_bearing_flange_d / 2
    capture_h = P.gba_body_h - cartridge_top - P.gba_lid_capture_gap
    capture = _box_at(
        -3,
        P.gba_outer_r - 1.1,
        -capture_h,
        6,
        1.1,
        capture_h,
    )
    return plate + plug + capture


def bearing_cartridge():
    """Support-free upright print carrying the two horizontal 625ZZs."""
    y0 = P.gba_output_bearing_y0 - 0.5
    length = P.gba_outer_r + 1 - y0
    body_r = P.gba_bearing_cartridge_d / 2
    flange_r = P.gba_bearing_flange_d / 2
    ramp_h = flange_r - body_r
    ramp_z = length - P.gba_bearing_flange_t

    body = _cylinder(body_r, ramp_z)
    body += Pos(0, 0, ramp_z) * Cone(
        body_r,
        flange_r,
        ramp_h,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    body += Pos(0, 0, ramp_z + ramp_h) * _cylinder(
        flange_r, P.gba_bearing_flange_t - ramp_h
    )

    pocket_depth = P.gba_output_bearing_y1 - y0 + 0.2
    body -= Pos(0, 0, -0.1) * _cylinder(
        P.gb_bearing_pocket_d / 2, pocket_depth + 0.1
    )
    body -= Pos(0, 0, pocket_depth - 0.1) * _cylinder(
        P.gb_gear_bore_d / 2, length - pocket_depth + 0.2
    )
    return body


def input_spacer():
    """Sleeve from the motor boss to the heel of the D-bore input gear."""
    gear_heel_z = P.gba_pair_z0 + _pair_parts()[0].bounding_box().min.Z
    length = gear_heel_z - P.gb_running_gap - P.gba_motor_boss_h
    return _cylinder(5, length) - Pos(0, 0, -0.5) * _cylinder(
        P.gb_input_bore_d / 2, length + 1
    )


def output_spacer():
    """Sleeve from the output gear heel to the inner 625ZZ bearing."""
    gear_heel_y = P.gba_input_y + _pair_parts()[1].bounding_box().max.X
    length = P.gba_output_bearing_y0 - P.gb_running_gap - gear_heel_y
    return _cylinder(4, length) - Pos(0, 0, -0.5) * _cylinder(
        P.gb_gear_bore_d / 2, length + 1
    )


def _output_bearings():
    bearing = bearing_625zz()
    outer = Pos(0, P.gba_output_bearing_y1, P.gba_axis_z) * Rot(90, 0, 0)
    inner = Pos(
        0,
        P.gba_output_bearing_y1 - P.gb_bearing_w,
        P.gba_axis_z,
    ) * Rot(90, 0, 0)
    return outer * bearing + inner * bearing


def _posed_bearing_cartridge():
    y0 = P.gba_output_bearing_y0 - 0.5
    return Pos(0, y0, P.gba_axis_z) * Rot(-90, 0, 0) * bearing_cartridge()


def _output_rod():
    y0 = P.gba_input_y + _pair_parts()[1].bounding_box().min.X
    y1 = P.gba_outer_r + P.gb_shaft_exposed
    return (
        Pos(0, y0, P.gba_axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(P.gb_shaft_d / 2, y1 - y0)
    )


def _posed_input_spacer():
    return Pos(0, P.gba_input_y, P.gba_motor_boss_h) * input_spacer()


def _posed_output_spacer():
    gear_heel_y = P.gba_input_y + _pair_parts()[1].bounding_box().max.X
    return (
        Pos(0, gear_heel_y, P.gba_axis_z)
        * Rot(-90, 0, 0)
        * output_spacer()
    )


def scene() -> Scene:
    """Measured motor, circular attachment, bevel pair, and output stack."""
    input_part, output_part = _pair_parts()
    result = Scene()
    result.add(motor_reference(), "motor", color="silver")
    result.add(housing(), "housing", color="lightblue", alpha=0.25)
    result.add(lid(), "lid", color="lightskyblue", alpha=0.2, loc=F.GBA_LID_ON_HOUSING)
    result.add(input_part, "input-bevel", color="orange", loc=F.GBA_PAIR_ON_MOTOR)
    result.add(output_part, "output-bevel", color="gold", loc=F.GBA_PAIR_ON_MOTOR)
    result.add(_posed_input_spacer(), "input-spacer", color="darkorange")
    result.add(_posed_output_spacer(), "output-spacer", color="goldenrod")
    result.add(_posed_bearing_cartridge(), "bearing-cartridge", color="deepskyblue")
    result.add(_output_bearings(), "output-bearings", color="silver")
    result.add(_output_rod(), "output-rod", color="dimgray")
    return result
