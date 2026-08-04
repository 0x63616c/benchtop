"""Separate printable gears for the removable blinds drive cassette.

The motor pinion, layshaft spur, and layshaft bevel are independent
prints.  The two layshaft gears run on a bought 5 mm rod rather than a
printed shaft.  The round-bore gears include 2.2 mm cross-pin drilling
guides; the motor pinion uses the JGB37's measured D-flat plus an M3
grub-screw pilot.

Every exported gear has a deliberate flat print pose: spur faces or the
bevel heel on the bed, with any hub growing upward.
"""

from functools import lru_cache
from math import pi
import warnings

from build123d import Align, Box, Cone, Cylinder, Pos, Rot
from py_gearworks import BevelGear, RIGHT, SpurGear

from .params import P


def _cylinder(radius: float, height: float):
    return Cylinder(
        radius,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


@lru_cache(maxsize=1)
def _spur_pair_parts():
    """Meshed py_gearworks spur pair, each returned on its own axis."""
    common = dict(
        module=P.gear_m,
        height=P.spur_w,
        backlash=P.gear_backlash,
    )
    pinion_definition = SpurGear(number_of_teeth=P.spur_pinion_z, **common)
    wheel_definition = SpurGear(number_of_teeth=P.spur_wheel_z, **common)
    wheel_definition.mesh_to(pinion_definition, target_dir=RIGHT)

    pinion_part = pinion_definition.build_part(n_vert=2)
    wheel_part = wheel_definition.build_part(n_vert=2)
    wheel_part = Pos(
        -(P.spur_pinion_r + P.spur_wheel_r), 0, 0
    ) * wheel_part
    return pinion_part, wheel_part


@lru_cache(maxsize=1)
def _bevel_pair_parts():
    """Matched py_gearworks 1:1 miter pair in layshaft/ring frames."""
    common = dict(
        number_of_teeth=P.bevel_z,
        module=P.gear_m,
        height=P.bevel_face,
        cone_angle=pi / 2,
        backlash=P.gear_backlash,
    )
    layshaft_definition = BevelGear(**common)
    ring_definition = BevelGear(**common)
    ring_definition.mesh_to(layshaft_definition, target_dir=RIGHT)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Gimbal lock detected.*")
        layshaft_part = layshaft_definition.build_part(n_vert=4)
        ring_part = ring_definition.build_part(n_vert=4)

    ring_part = Pos(P.bevel_r, 0, -P.bevel_r) * Rot(0, -90, 0) * ring_part
    return layshaft_part, ring_part


def bevel_ring():
    """Matched sprocket-side bevel, heel plane at local z=0."""
    return _bevel_pair_parts()[1]


def _d_bore(length: float):
    """Ø6.2 D-bore matching the motor shaft, centred on local z=0."""
    bore = Cylinder(3.1, length)
    flat_y = 5.55 - 3.1
    bore -= Pos(0, flat_y + 3.1) * Box(6.2 * 2, 6.2, length + 2)
    return bore


def _round_bore(z0: float, length: float):
    return Pos(0, 0, z0) * _cylinder(
        (P.lay_rod_d + P.lay_rod_clear) / 2,
        length,
    )


def _cross_pin(z: float, outer_d: float):
    """Transverse 2.2 mm drilling guide through a round-shaft gear."""
    return Pos(0, outer_d / 2 + 1, z) * Rot(90, 0, 0) * _cylinder(
        P.lay_pin_guide_d / 2,
        outer_d + 2,
    )


def _self_supporting_heel(part):
    """Trim shallow heel tooth ends to the proven 55-degree envelope."""
    heel_z = part.bounding_box().min.Z
    heel_faces = [
        face
        for face in part.faces()
        if abs(face.bounding_box().min.Z - heel_z) < 1e-6
        and abs(face.bounding_box().max.Z - heel_z) < 1e-6
    ]
    heel_bounds = max(heel_faces, key=lambda face: face.area).bounding_box()
    heel_radius = max(abs(heel_bounds.min.X), abs(heel_bounds.max.X))
    height = part.bounding_box().max.Z - heel_z + 0.1
    envelope = Pos(0, 0, heel_z) * Cone(
        heel_radius,
        heel_radius + 0.7 * height,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return part & envelope


def pinion():
    """Motor D-shaft pinion in its centred assembly frame."""
    gear = (
        Rot(0, 0, P.spur_pinion_phase)
        * Pos(0, 0, -P.spur_w / 2)
        * _spur_pair_parts()[0]
    )
    hub_z0 = -P.spur_w / 2 - P.gear_hub_len
    body = gear + Pos(0, 0, hub_z0) * _cylinder(
        P.gear_hub_d / 2,
        P.gear_hub_len,
    )
    body -= _d_bore(P.spur_w + 2 * P.gear_hub_len + 2)
    # Drill/tap this pilot M3 after printing; it lands on the motor flat.
    body -= Pos(0, P.gear_hub_d / 2 + 1, hub_z0 + P.gear_hub_len / 2) * (
        Rot(90, 0, 0)
        * _cylinder(P.pinion_grub_pilot_d / 2, P.gear_hub_d + 2)
    )
    return body


def spur_gear():
    """Layshaft z17 spur with round bore and cross-pin guide."""
    gear = Pos(0, 0, -P.spur_w / 2) * _spur_pair_parts()[1]
    hub_z0 = P.spur_w / 2
    body = gear + Pos(0, 0, hub_z0) * _cylinder(
        P.gear_hub_d / 2,
        P.gear_hub_len,
    )
    body -= _round_bore(-P.spur_w / 2 - 1, P.spur_w + P.gear_hub_len + 2)
    body -= _cross_pin(hub_z0 + P.gear_hub_len / 2, P.gear_hub_d)
    return body


def bevel_gear():
    """Layshaft miter gear; hubless so its wide heel prints on the bed."""
    body = _self_supporting_heel(_bevel_pair_parts()[0])
    bounds = body.bounding_box()
    body -= _round_bore(bounds.min.Z - 1, bounds.size.Z + 2)
    body -= _cross_pin(1.0, P.lay_bevel_pin_span)
    return body


def _on_bed(part):
    return Pos(0, 0, -part.bounding_box().min.Z) * part


def pinion_print():
    """Motor pinion face-down, hub upward."""
    return _on_bed(Rot(180, 0, 0) * pinion())


def spur_gear_print():
    """Layshaft spur face-down, hub upward."""
    return _on_bed(spur_gear())


def bevel_gear_print():
    """Layshaft bevel wide-heel-down."""
    return _on_bed(bevel_gear())


def scene():
    from splitflap_cad.viewer import Scene

    return (
        Scene()
        .add(pinion_print(), "pinion", color="orange", loc=Pos(-38, 0, 0))
        .add(spur_gear_print(), "layshaft-spur", color="goldenrod")
        .add(bevel_gear_print(), "layshaft-bevel", color="gold", loc=Pos(38, 0, 0))
    )
