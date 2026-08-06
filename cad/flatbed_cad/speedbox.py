"""Modular 1.333x-speed right-angle drivetrain for the enclosed JGB37 box.

A 24T motor bevel drives an 18T output bevel, so one motor-shaft revolution
produces 1.333 output-shaft revolutions. The pair is a replaceable cartridge:
to explore a different ratio, change only the tooth counts and derived box
clearances rather than coupling gear construction to panel construction.
"""

from functools import lru_cache
from math import atan2, pi
import warnings

from build123d import Align, Box, Cylinder, Plane, Pos, Rot
from py_gearworks import BevelGear, RIGHT

from splitflap_cad.geo import self_supporting_heel
from splitflap_cad.viewer import Scene

from . import frames as F
from .motor_reference import motor_reference
from .params import P


def _cylinder(radius: float, height: float):
    return Cylinder(
        radius,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def _d_prism(diameter: float, flat_span: float, height: float):
    radius = diameter / 2
    flat_y = radius - flat_span
    keep = Pos(0, (flat_y + radius) / 2, height / 2) * Box(
        diameter + 0.2,
        flat_span + 0.2,
        height + 0.2,
    )
    return _cylinder(radius, height) & keep


@lru_cache(maxsize=1)
def pair_parts():
    """Motor and output bevels in py_gearworks' common local frame."""
    input_angle = atan2(P.fg_input_teeth, P.fg_output_teeth)
    output_angle = pi / 2 - input_angle
    common = dict(
        module=P.fg_gear_module,
        height=P.fg_gear_face,
        backlash=P.fg_gear_backlash,
    )
    input_definition = BevelGear(
        number_of_teeth=P.fg_input_teeth,
        cone_angle=2 * input_angle,
        **common,
    )
    output_definition = BevelGear(
        number_of_teeth=P.fg_output_teeth,
        cone_angle=2 * output_angle,
        **common,
    )
    output_definition.mesh_to(input_definition, target_dir=RIGHT)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Gimbal lock detected.*")
        input_part = input_definition.build_part(n_vert=4)
        output_part = output_definition.build_part(n_vert=4)

    hub_r = P.fg_gear_hub_d / 2
    # The bevel body is shallow around its bore. Start the hub at z=0 so it
    # overlaps that body; starting at z=2 leaves a disconnected floating solid.
    input_part += _cylinder(hub_r, P.fg_gear_hub_len + 2.0)
    input_part = self_supporting_heel(
        input_part,
        P.fg_gear_print_radial_growth,
    )
    input_part -= Pos(0, 0, -2) * _d_prism(
        P.fg_motor_shaft_d + 0.2,
        P.fg_motor_shaft_flat + 0.2,
        12,
    )

    # Put the output hub on the narrowing apex side. In print orientation the
    # wide heel then sits on the bed and the hub grows upward, rather than the
    # old heel-side hub supporting an umbrella of teeth.
    output_hub_x0 = P.fg_input_pitch_r - 0.6
    output_part += (
        Pos(output_hub_x0, 0, P.fg_output_pitch_r)
        * Rot(0, -90, 0)
        * _cylinder(hub_r, P.fg_output_hub_len)
    )

    output_to_print = Rot(0, 90, 0) * Pos(
        -P.fg_input_pitch_r,
        0,
        -P.fg_output_pitch_r,
    )
    printable_output = output_to_print * output_part
    printable_output = self_supporting_heel(
        printable_output,
        P.fg_gear_print_radial_growth,
    )
    output_part = output_to_print.inverse() * printable_output
    output_part -= (
        Pos(P.fg_input_pitch_r - 10, 0, P.fg_output_pitch_r)
        * Rot(0, 90, 0)
        * _cylinder(P.fg_output_bore_d / 2, 25)
    )
    return input_part, output_part


def pair_origin_y() -> float:
    """Place the input heel beyond the motor boss and axial spacer."""
    input_min = pair_parts()[0].bounding_box().min.Z
    return (
        P.fg_motor_face_y
        + P.fg_motor_boss_h
        + P.fg_motor_gear_gap
        + P.fg_input_spacer_len
        - input_min
    )


def pair_in_box():
    """Local pair frame: input +Y, output +X through the side walls."""
    return Plane(
        origin=(P.fg_motor_axis_x, pair_origin_y(), P.fg_shaft_z),
        x_dir=(1, 0, 0),
        z_dir=(0, 1, 0),
    ).location


def output_axis_y() -> float:
    return pair_origin_y() + P.fg_output_pitch_r


def input_gear():
    """24T D-bore gear, heel-down print orientation."""
    part = pair_parts()[0]
    return Pos(0, 0, -part.bounding_box().min.Z) * part


def input_spacer():
    """Printed sleeve that locates the shifted input gear on the motor shaft."""
    return _cylinder(P.fg_gear_hub_d / 2, P.fg_input_spacer_len) - Pos(
        0, 0, -0.1
    ) * _cylinder(
        (P.fg_motor_shaft_d + 0.2) / 2,
        P.fg_input_spacer_len + 0.2,
    )


def output_gear():
    """18T round-bore output gear, self-supporting heel-down orientation."""
    orient = Rot(0, 90, 0) * Pos(
        -P.fg_input_pitch_r,
        0,
        -P.fg_output_pitch_r,
    )
    part = orient * pair_parts()[1]
    return Pos(0, 0, -part.bounding_box().min.Z) * part


def output_spacer():
    """Short right-side thrust sleeve between output gear and bearing."""
    posed_output = pair_in_box() * pair_parts()[1]
    right_length = (
        P.fg_box_w
        - P.fg_bearing_carrier_t
        - P.fg_gear_running_gap
        - posed_output.bounding_box().max.X
    )

    def sleeve(length: float):
        return _cylinder(4.0, length) - Pos(0, 0, -0.1) * _cylinder(
            P.fg_output_spacer_bore_d / 2,
            length + 0.2,
        )

    return sleeve(right_length)


def bearing_625zz():
    """Display-only 5 x 16 x 5 mm bearing envelope."""
    return _cylinder(P.fg_bearing_d / 2, P.fg_bearing_w) - Pos(
        0, 0, -0.1
    ) * _cylinder(P.fg_output_shaft_d / 2, P.fg_bearing_w + 0.2)


def output_rod():
    """Unmodified round 5 mm rod through both side bearings."""
    return Pos(0, output_axis_y(), P.fg_shaft_z) * Rot(
        0, 90, 0
    ) * _cylinder(
        P.fg_output_shaft_d / 2,
        P.fg_box_w + P.fg_output_exposed,
    )


def output_bearings():
    left_x = P.fg_bearing_shoulder
    right_x = P.fg_box_w - P.fg_bearing_shoulder - P.fg_bearing_w
    left = Pos(left_x, output_axis_y(), P.fg_shaft_z) * Rot(
        0, 90, 0
    ) * bearing_625zz()
    right = Pos(right_x, output_axis_y(), P.fg_shaft_z) * Rot(
        0, 90, 0
    ) * bearing_625zz()
    return left + right


def posed_output_spacer():
    posed_output = pair_in_box() * pair_parts()[1]
    right_x0 = posed_output.bounding_box().max.X + P.fg_gear_running_gap
    right_length = P.fg_box_w - P.fg_bearing_carrier_t - right_x0

    def sleeve_at(x0: float, length: float):
        return Pos(x0, output_axis_y(), P.fg_shaft_z) * Rot(
            0, 90, 0
        ) * (
            _cylinder(4.0, length)
            - Pos(0, 0, -0.1)
            * _cylinder(P.fg_output_spacer_bore_d / 2, length + 0.2)
        )

    return sleeve_at(right_x0, right_length)


def posed_input_spacer():
    posed_input = pair_in_box() * pair_parts()[0]
    y1 = posed_input.bounding_box().min.Y
    return Pos(
        P.fg_motor_axis_x,
        y1 - P.fg_input_spacer_len,
        P.fg_shaft_z,
    ) * Rot(-90, 0, 0) * input_spacer()


def drivetrain_scene() -> Scene:
    input_part, output_part = pair_parts()
    frame = pair_in_box()
    return (
        Scene()
        .add(input_part, "24T-input", "orange", loc=frame)
        .add(posed_input_spacer(), "input-spacer", "darkorange")
        .add(output_part, "18T-output", "gold", loc=frame)
        .add(posed_output_spacer(), "output-spacer", "goldenrod")
        .add(output_bearings(), "625ZZ-bearings", "silver")
        .add(output_rod(), "5mm-output-shaft", "dimgray")
    )


def scene() -> Scene:
    result = Scene().add(
        motor_reference(),
        "jgb37-520",
        "silver",
        loc=F.FG_MOTOR_IN_BOX,
    )
    drive = drivetrain_scene()
    for obj, name, color, alpha in zip(
        drive._objects,
        drive._names,
        drive._colors,
        drive._alphas,
        strict=True,
    ):
        result.add(obj, name, color, alpha)
    return result
