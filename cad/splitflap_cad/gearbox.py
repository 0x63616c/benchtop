"""Compact 3:2 right-angle bevel gearbox, complete with housing.

The closed box is 45 x 36 x 43mm. Box coordinates start at the outer
back-left-bottom corner: +X right, +Y front, +Z up. A 5mm steel input
rod rises through the bottom at y=12.5, so its front-most edge is the
requested 15mm from the back. A 16T input and 24T output bevel pair turn
that axis 90 degrees with a 3:2 reduction: three input turns produce two
output turns. Both rods project 10mm beyond the box.

Four 625ZZ bearings (5 x 16 x 5mm) run as two-bearing stacks in pockets
that load from inside before the gears go on. A test-print variant swaps
them for four printable 16 x 5mm bushings with 5.4mm running bores. The
two gears have 5.2mm bores and round 2.2mm guides for 2mm cross pins;
drill each rod after clocking the mesh and retain it with a 2mm pin.
Both gears print heel-down with their hubs on the narrowing apex side,
so neither hub creates an umbrella overhang. The shallow 16T heel has a
55-degree bed-facing relief so its tooth ends are also self-supporting.
The top lid is a separate press-fit print, and printed spacers carry
each gear's axial load to its inner bearing.

Views: `just cad view gear-box` and `just cad view gear-box-test`.
"""

from functools import lru_cache
from math import atan2, pi
import warnings

from build123d import Align, Box, Cone, Cylinder, Pos, Rot
from py_gearworks import BevelGear, RIGHT

from . import frames as F
from .params import P
from .viewer import Scene


def _box_at(x: float, y: float, z: float, w: float, d: float, h: float):
    """Axis-aligned box from its minimum corner."""
    return Pos(x + w / 2, y + d / 2, z + h / 2) * Box(w, d, h)


def _cylinder(radius: float, height: float):
    """Axis +Z cylinder from z=0; build123d otherwise centres it."""
    return Cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _self_supporting_heel(part):
    """Trim a shallow bevel heel to a support-free printable envelope."""
    heel_z = part.bounding_box().min.Z
    heel_faces = [
        face
        for face in part.faces()
        if abs(face.bounding_box().min.Z - heel_z) < 1e-6
        and abs(face.bounding_box().max.Z - heel_z) < 1e-6
    ]
    heel_bb = max(heel_faces, key=lambda face: face.area).bounding_box()
    heel_r = max(abs(heel_bb.min.X), abs(heel_bb.max.X))
    height = part.bounding_box().max.Z - heel_z + 0.1
    radial_growth = 0.7  # 55 degrees from the bed, safely above 45
    envelope = Pos(0, 0, heel_z) * Cone(
        heel_r,
        heel_r + radial_growth * height,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return part & envelope


@lru_cache(maxsize=1)
def _pair_parts():
    """The meshed pair in py_gearworks coordinates, built only once."""
    input_angle = atan2(P.gb_input_teeth, P.gb_output_teeth)
    output_angle = pi / 2 - input_angle
    common = dict(
        module=P.gb_gear_module,
        height=P.gb_gear_face,
        backlash=P.gb_gear_backlash,
    )
    input_definition = BevelGear(
        number_of_teeth=P.gb_input_teeth,
        cone_angle=2 * input_angle,
        **common,
    )
    output_definition = BevelGear(
        number_of_teeth=P.gb_output_teeth,
        cone_angle=2 * output_angle,
        **common,
    )
    output_definition.mesh_to(input_definition, target_dir=RIGHT)

    # scipy warns about a harmless Euler-angle ambiguity when a right-angle
    # pair is converted to a build123d Location.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Gimbal lock detected.*")
        input_part = input_definition.build_part(n_vert=4)
        output_part = output_definition.build_part(n_vert=4)

    hub_r = P.gb_gear_hub_d / 2
    bore_r = P.gb_gear_bore_d / 2
    pin_r = P.gb_pin_guide_d / 2

    # Put each hub on the narrowing pitch-apex side. In the printable
    # orientations below that means the wide heel face sits on the bed
    # and the hub grows upward, rather than supporting an umbrella.
    input_hub_z0 = 2.0
    input_part += Pos(0, 0, input_hub_z0) * _cylinder(
        hub_r, P.gb_gear_hub_len
    )
    input_part = _self_supporting_heel(input_part)
    input_part -= Pos(0, 0, -2) * _cylinder(bore_r, 10)
    input_part -= (
        Pos(-6, 0, input_hub_z0 + P.gb_gear_hub_len / 2)
        * Rot(0, 90, 0)
        * _cylinder(pin_r, 12)
    )

    # Output gear is already meshed: its axis is +X through
    # (0, 0, output_pitch_r), and its apex points toward -X.
    ri, ro = P.gb_input_pitch_r, P.gb_output_pitch_r
    output_hub_x0 = ri - 0.5
    output_part += (
        Pos(output_hub_x0, 0, ro)
        * Rot(0, -90, 0)
        * _cylinder(hub_r, P.gb_gear_hub_len)
    )
    output_part -= (
        Pos(ri + 2, 0, ro) * Rot(0, -90, 0) * _cylinder(bore_r, 10)
    )
    output_part -= (
        Pos(output_hub_x0 - P.gb_gear_hub_len / 2, 6, ro)
        * Rot(90, 0, 0)
        * _cylinder(pin_r, 12)
    )
    return input_part, output_part


def input_gear():
    """Printable input gear, wide heel face down and apex hub up."""
    part = _pair_parts()[0]
    return Pos(0, 0, -part.bounding_box().min.Z) * part


def output_gear():
    """Printable output gear, wide heel face down and apex hub up."""
    to_print = Rot(0, 90, 0) * Pos(
        -P.gb_input_pitch_r, 0, -P.gb_output_pitch_r
    )
    part = to_print * _pair_parts()[1]
    return Pos(0, 0, -part.bounding_box().min.Z) * part


def input_spacer():
    """Printed tube between the input gear heel and upper bearing."""
    gear_heel_z = P.gb_pair_z0 + _pair_parts()[0].bounding_box().min.Z
    length = gear_heel_z - P.gb_running_gap - P.gb_input_bearing_z1
    return _cylinder(4, length) - Pos(0, 0, -0.5) * _cylinder(
        P.gb_gear_bore_d / 2, length + 1
    )


def output_spacer():
    """Printed tube between the output gear heel and inner bearing."""
    gear_heel_front = P.gb_input_y + _pair_parts()[1].bounding_box().max.X
    length = P.gb_output_bearing_y0 - P.gb_running_gap - gear_heel_front
    return _cylinder(4, length) - Pos(0, 0, -0.5) * _cylinder(
        P.gb_gear_bore_d / 2, length + 1
    )


def housing():
    """Open-top box with two shouldered, two-bearing pockets."""
    w, d, h, wall = P.gb_outer_w, P.gb_outer_d, P.gb_housing_h, P.gb_wall
    body = _box_at(0, 0, 0, w, d, h)
    body -= _box_at(wall, wall, wall, w - 2 * wall, d - 2 * wall, h + 1)

    # The input stack loads from inside and stops on a bottom shoulder.
    input_boss_h = P.gb_input_bearing_z1 + 0.7
    body += Pos(P.gb_center_x, P.gb_input_y, 0) * _cylinder(
        P.gb_bearing_boss_d / 2, input_boss_h
    )
    body -= Pos(P.gb_center_x, P.gb_input_y, P.gb_input_bearing_z0) * _cylinder(
        P.gb_bearing_pocket_d / 2, P.gb_bearing_stack + 0.8
    )
    body -= Pos(P.gb_center_x, P.gb_input_y, -0.5) * _cylinder(
        P.gb_gear_bore_d / 2, P.gb_input_bearing_z0 + 1
    )

    # The output stack loads from inside and stops on the front shoulder.
    output_boss_y0 = P.gb_output_bearing_y0 - 0.5
    body += (
        Pos(P.gb_center_x, output_boss_y0, P.gb_axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(P.gb_bearing_boss_d / 2, d - output_boss_y0)
    )
    body -= (
        Pos(P.gb_center_x, output_boss_y0, P.gb_axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(
            P.gb_bearing_pocket_d / 2,
            P.gb_output_bearing_y1 - output_boss_y0 + 0.2,
        )
    )
    body -= (
        Pos(P.gb_center_x, P.gb_output_bearing_y1 - 0.2, P.gb_axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(P.gb_gear_bore_d / 2, P.gb_bearing_shoulder + 0.7)
    )
    return body


def lid():
    """Press-fit top lid; local z=0 is the housing's top rim."""
    plate = _box_at(0, 0, 0, P.gb_outer_w, P.gb_outer_d, P.gb_lid_t)
    plug = _box_at(
        P.gb_wall + P.gb_lid_clear,
        P.gb_wall + P.gb_lid_clear,
        -P.gb_lid_plug,
        P.gb_lid_plug_w,
        P.gb_lid_plug_d,
        P.gb_lid_plug,
    )
    return plate + plug


def bearing_625zz():
    """Display-only 625ZZ envelope, axis +Z, z=0..5."""
    return _cylinder(P.gb_bearing_d / 2, P.gb_bearing_w) - Pos(0, 0, -0.5) * _cylinder(
        P.gb_shaft_d / 2, P.gb_bearing_w + 1
    )


def test_bushing():
    """Printed 625ZZ substitute for low-load test assembly."""
    return _cylinder(P.gb_bearing_d / 2, P.gb_bearing_w) - Pos(0, 0, -0.5) * _cylinder(
        P.gb_test_bushing_bore_d / 2, P.gb_bearing_w + 1
    )


def test_bushings():
    """Four printed test bushings arranged as one STL build plate."""
    bushing = test_bushing()
    pitch = P.gb_bearing_d + 2
    return (
        Pos(-pitch / 2, -pitch / 2, 0) * bushing
        + Pos(pitch / 2, -pitch / 2, 0) * bushing
        + Pos(-pitch / 2, pitch / 2, 0) * bushing
        + Pos(pitch / 2, pitch / 2, 0) * bushing
    )


def _input_supports(support):
    return (
        Pos(P.gb_center_x, P.gb_input_y, P.gb_input_bearing_z0) * support
        + Pos(
            P.gb_center_x,
            P.gb_input_y,
            P.gb_input_bearing_z0 + P.gb_bearing_w,
        )
        * support
    )


def _output_supports(support):
    outer = Pos(P.gb_center_x, P.gb_output_bearing_y1, P.gb_axis_z) * Rot(90, 0, 0)
    inner = Pos(
        P.gb_center_x, P.gb_output_bearing_y1 - P.gb_bearing_w, P.gb_axis_z
    ) * Rot(90, 0, 0)
    return outer * support + inner * support


def _input_rod():
    z0 = -P.gb_shaft_exposed
    z1 = P.gb_pair_z0 + _pair_parts()[0].bounding_box().max.Z
    return Pos(P.gb_center_x, P.gb_input_y, z0) * _cylinder(P.gb_shaft_d / 2, z1 - z0)


def _output_rod():
    y0 = P.gb_input_y + _pair_parts()[1].bounding_box().min.X
    y1 = P.gb_outer_d + P.gb_shaft_exposed
    return (
        Pos(P.gb_center_x, y0, P.gb_axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(P.gb_shaft_d / 2, y1 - y0)
    )


def _posed_input_spacer():
    return Pos(P.gb_center_x, P.gb_input_y, P.gb_input_bearing_z1) * input_spacer()


def _posed_output_spacer():
    gear_heel_front = P.gb_input_y + _pair_parts()[1].bounding_box().max.X
    return (
        Pos(P.gb_center_x, gear_heel_front, P.gb_axis_z)
        * Rot(-90, 0, 0)
        * output_spacer()
    )


def _scene(test_print: bool) -> Scene:
    input_part, output_part = _pair_parts()
    s = Scene()
    s.add(housing(), "housing", color="lightblue", alpha=0.28)
    s.add(lid(), "lid", color="lightskyblue", alpha=0.22, loc=F.GEARBOX_LID_IN_BOX)
    s.add(
        input_part,
        "input-bevel",
        color="orange",
        loc=F.GEARBOX_PAIR_IN_BOX,
    )
    s.add(
        output_part,
        "output-bevel",
        color="gold",
        loc=F.GEARBOX_PAIR_IN_BOX,
    )
    s.add(_posed_input_spacer(), "input-spacer", color="darkorange")
    s.add(_posed_output_spacer(), "output-spacer", color="goldenrod")
    if test_print:
        s.add(_input_supports(test_bushing()), "input-bushings", color="coral")
        s.add(_output_supports(test_bushing()), "output-bushings", color="coral")
    else:
        s.add(_input_supports(bearing_625zz()), "input-bearings", color="silver")
        s.add(_output_supports(bearing_625zz()), "output-bearings", color="silver")
    s.add(_input_rod(), "input-rod", color="dimgray")
    s.add(_output_rod(), "output-rod", color="dimgray")
    return s


def scene() -> Scene:
    """Production assembly with four 625ZZ bearings."""
    return _scene(test_print=False)


def test_scene() -> Scene:
    """Test-print assembly with four printed bushings instead of bearings."""
    return _scene(test_print=True)
