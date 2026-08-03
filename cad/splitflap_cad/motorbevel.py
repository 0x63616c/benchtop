"""Circular right-angle bevel attachment for the measured JGB37 motor.

The motor gearbox face is z=0 with its Ø37 centre at the origin. Its
6mm D-shaft is eccentric 7mm in -Y. The attachment stays within a Ø37
main circular body; only the integrated output nose, output rod, and M3
screw heads may project. The enclosure splits through the output-shaft
centreline, so each half contains an open semicircular 625ZZ seat and
prints without a horizontal tunnel. The 16T:24T pair gives a 3:2
reduction and directs the 5mm output rod inward along +Y.

View: `just cad view gear-box-motor`.
"""

from math import cos, radians, sin

from build123d import Pos, Rot

from . import frames as F
from .gearbox import (
    _box_at,
    _cylinder,
    _d_prism,
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


def _output_boss(axis_z: float):
    y0 = P.gba_output_bearing_y0 - 0.5
    y1 = P.gba_outer_r + P.gba_output_nose
    return (
        Pos(0, y0, axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(P.gba_output_boss_d / 2, y1 - y0)
    )


def _bearing_pocket(axis_z: float):
    y0 = P.gba_output_bearing_y0 - 0.5
    depth = P.gba_output_bearing_y1 - y0 + 0.2
    return (
        Pos(0, y0, axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(P.gb_bearing_pocket_d / 2, depth)
    )


def _shaft_passage(axis_z: float):
    y0 = P.gba_output_bearing_y1 - 0.1
    y1 = P.gba_outer_r + P.gba_output_nose + 0.1
    return (
        Pos(0, y0, axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(P.gb_gear_bore_d / 2, y1 - y0)
    )


def _split_boss_half(axis_z: float, upper: bool):
    boss = _output_boss(axis_z)
    radius = P.gba_output_boss_d / 2 + 0.5
    y0 = P.gba_output_bearing_y0 - 1
    depth = P.gba_outer_r + P.gba_output_nose + 1 - y0
    if upper:
        clip = _box_at(-radius, y0, axis_z, 2 * radius, depth, radius + 0.5)
    else:
        clip = _box_at(
            -radius,
            y0,
            axis_z - radius - 0.5,
            2 * radius,
            depth,
            radius + 0.5,
        )
    return boss & clip


def _cut_screw_windows(part, z0: float, height: float):
    for index in P.gba_mount_screw_indices:
        angle = index * 360 / P.gba_motor_screw_n
        window = Rot(0, 0, angle) * _box_at(
            P.gba_motor_screw_bcd / 2 - P.gba_screw_window_w / 2,
            -P.gba_screw_window_w / 2,
            z0,
            P.gba_screw_window_w,
            P.gba_screw_window_w,
            height,
        )
        part -= window
    return part


def _bearing_pedestal(height: float):
    """Solid print support from a flat face to a split bearing cradle."""
    y0 = P.gba_output_bearing_y0 - 0.5
    pedestal = _box_at(
        -P.gba_output_boss_d / 2,
        y0,
        0,
        P.gba_output_boss_d,
        P.gba_inner_r - y0 + 0.5,
        height,
    )
    return pedestal & _cylinder(P.gba_outer_r, height)


def housing():
    """Lower enclosure with integral lower 625ZZ bearing cradles."""
    body = _cylinder(P.gba_outer_r, P.gba_axis_z)
    body -= Pos(0, 0, P.gba_base_t) * _cylinder(
        P.gba_inner_r, P.gba_axis_z - P.gba_base_t + 1
    )
    seam_rebate = Pos(0, 0, P.gba_axis_z - P.gba_seam_step_h) * (
        _cylinder(P.gba_outer_r + 0.5, P.gba_seam_step_h + 0.5)
        - _cylinder(
            P.gba_outer_r - P.gba_seam_step_radial,
            P.gba_seam_step_h + 0.5,
        )
    )
    body -= seam_rebate

    # The eccentric motor boss passes through the mounting deck.
    body -= Pos(0, P.gba_input_y, -0.5) * _cylinder(
        P.gba_boss_clear_d / 2, P.gba_base_t + 1
    )

    # Six top-installed M3 screws remain reachable through both halves.
    for index in P.gba_mount_screw_indices:
        hole = _polar(
            P.gba_motor_screw_bcd / 2,
            index * 360 / P.gba_motor_screw_n,
        )
        body -= hole * Pos(0, 0, -0.5) * _cylinder(
            P.gba_mount_clear_d / 2, P.gba_base_t + 1
        )
    body = _cut_screw_windows(
        body, P.gba_base_t, P.gba_axis_z - P.gba_base_t + 0.5
    )
    body += _bearing_pedestal(P.gba_axis_z)
    body += _split_boss_half(P.gba_axis_z, upper=False)
    body -= seam_rebate
    body -= _bearing_pocket(P.gba_axis_z)
    body -= _shaft_passage(P.gba_axis_z)
    return body


def lid():
    """Upper enclosure and integral upper bearing seats, in assembly pose."""
    cap_h = P.gba_body_h - P.gba_axis_z
    cap = _cylinder(P.gba_outer_r, cap_h + P.gba_lid_t)
    cap -= Pos(0, 0, -0.5) * _cylinder(P.gba_inner_r, cap_h + 0.5)

    seam_skirt_inner_r = (
        P.gba_outer_r - P.gba_seam_step_radial + P.gba_seam_clear
    )
    seam_skirt = Pos(0, 0, -P.gba_seam_step_h) * (
        _cylinder(P.gba_outer_r, P.gba_seam_step_h)
        - _cylinder(seam_skirt_inner_r, P.gba_seam_step_h)
    )
    cap += seam_skirt
    cap = _cut_screw_windows(
        cap,
        -P.gba_seam_step_h - 0.5,
        cap_h + P.gba_lid_t + P.gba_seam_step_h + 1,
    )
    cap += _bearing_pedestal(cap_h + P.gba_lid_t)
    cap += _split_boss_half(0, upper=True)
    cap -= _bearing_pocket(0)
    cap -= _shaft_passage(0)
    return cap


def lid_print():
    """Upper enclosure flipped onto its flat roof for support-free printing."""
    oriented = Rot(180, 0, 0) * lid()
    return Pos(0, 0, -oriented.bounding_box().min.Z) * oriented


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
    result.add(_output_bearings(), "output-bearings", color="silver")
    result.add(_output_rod(), "output-rod", color="dimgray")
    return result
