"""Compact 1:1 right-angle bevel gearbox, complete with housing.

The closed box is 45 x 45 x 36mm. Box coordinates start at the outer
back-left-bottom corner: +X right, +Y front, +Z up. A 5mm steel input
rod rises through the bottom at y=12.5, so its front-most edge is the
requested 15mm from the back. An equal bevel pair turns that axis 90
degrees and sends a second 5mm rod through the front face. Both rods
project 10mm beyond the box.

Four 625ZZ bearings (5 x 16 x 5mm) run as two-bearing stacks in pockets
that load from inside before the gears go on. The two gears have 5.2mm
bores and 2.2mm cross-pin drill guides; drill each rod after clocking the
mesh and retain it with a 2mm pin. The top lid is a separate press-fit
print, and a short printed spacer carries the output gear's axial load
to its inner bearing.

View: `just cad view gear-box`.
"""

from functools import lru_cache
from math import pi
import warnings

from build123d import Align, Box, Cylinder, Pos, Rot
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


@lru_cache(maxsize=1)
def _pair_parts():
    """The meshed pair in py_gearworks coordinates, built only once."""
    kwargs = dict(
        number_of_teeth=P.gb_gear_teeth,
        module=P.gb_gear_module,
        height=P.gb_gear_face,
        cone_angle=pi / 2,
        backlash=P.gb_gear_backlash,
    )
    input_definition = BevelGear(**kwargs)
    output_definition = BevelGear(**kwargs)
    output_definition.mesh_to(input_definition, target_dir=RIGHT)

    # scipy warns about a harmless Euler-angle ambiguity when a right-angle
    # pair is converted to a build123d Location.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Gimbal lock detected.*")
        input_part = input_definition.build_part(n_vert=4)
        output_part = output_definition.build_part(n_vert=4)

    hub_r = P.gb_gear_hub_d / 2
    bore_r = P.gb_gear_bore_d / 2
    pin_r = 1.1  # Ø2.2 drill guide for a Ø2 cross pin

    # Input gear: axis +Z, nominal heel at z=0. The hub reaches down to
    # the upper input bearing once the pair is posed in the box.
    input_part += Pos(0, 0, -3) * _cylinder(hub_r, 4)
    input_part -= Pos(0, 0, -4) * _cylinder(bore_r, 9)
    input_part -= Pos(-6, 0, -1) * Rot(0, 90, 0) * _cylinder(pin_r, 12)

    # Output gear is already meshed: its axis is +X through (0, 0, pitch_r)
    # and its heel is x=pitch_r. Give it the same short hub and pin guide.
    r = P.gb_pitch_r
    output_part += Pos(r, 0, r) * Rot(0, 90, 0) * _cylinder(hub_r, 4)
    output_part -= Pos(r - 4, 0, r) * Rot(0, 90, 0) * _cylinder(bore_r, 9)
    output_part -= Pos(r + 2, 6, r) * Rot(90, 0, 0) * _cylinder(pin_r, 12)
    return input_part, output_part


def input_gear():
    """Printable input miter gear in its native heel-at-z=0 frame."""
    return _pair_parts()[0]


def output_gear():
    """Printable output gear, normalized upright onto a Z-axis."""
    r = P.gb_pitch_r
    to_print = Rot(0, -90, 0) * Pos(-r, 0, -r)
    return to_print * _pair_parts()[1]


def output_spacer():
    """Printed tube between the output hub and inner bearing race."""
    gear_hub_front = P.gb_input_y + P.gb_pitch_r + 4
    length = P.gb_output_bearing_y0 - P.gb_running_gap - gear_hub_front
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


def _input_bearings():
    b = bearing_625zz()
    return (
        Pos(P.gb_center_x, P.gb_input_y, P.gb_input_bearing_z0) * b
        + Pos(
            P.gb_center_x,
            P.gb_input_y,
            P.gb_input_bearing_z0 + P.gb_bearing_w,
        )
        * b
    )


def _output_bearings():
    b = bearing_625zz()
    outer = Pos(P.gb_center_x, P.gb_output_bearing_y1, P.gb_axis_z) * Rot(90, 0, 0)
    inner = Pos(
        P.gb_center_x, P.gb_output_bearing_y1 - P.gb_bearing_w, P.gb_axis_z
    ) * Rot(90, 0, 0)
    return outer * b + inner * b


def _input_rod():
    z0 = -P.gb_shaft_exposed
    z1 = P.gb_pair_z0 + 4
    return Pos(P.gb_center_x, P.gb_input_y, z0) * _cylinder(P.gb_shaft_d / 2, z1 - z0)


def _output_rod():
    y0 = P.gb_input_y + P.gb_pitch_r - 4
    y1 = P.gb_outer_d + P.gb_shaft_exposed
    return (
        Pos(P.gb_center_x, y0, P.gb_axis_z)
        * Rot(-90, 0, 0)
        * _cylinder(P.gb_shaft_d / 2, y1 - y0)
    )


def _posed_spacer():
    gear_hub_front = P.gb_input_y + P.gb_pitch_r + 4
    return (
        Pos(P.gb_center_x, gear_hub_front, P.gb_axis_z)
        * Rot(-90, 0, 0)
        * output_spacer()
    )


def scene() -> Scene:
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
    s.add(_posed_spacer(), "output-spacer", color="goldenrod")
    s.add(_input_bearings(), "input-bearings", color="silver")
    s.add(_output_bearings(), "output-bearings", color="silver")
    s.add(_input_rod(), "input-rod", color="dimgray")
    s.add(_output_rod(), "output-rod", color="dimgray")
    return s
