"""Fit contract for the compact right-angle gearbox."""

from math import sqrt

import pytest

from splitflap_cad import frames as F
from splitflap_cad.gearbox import (
    housing,
    input_gear,
    jig_scene as gearbox_jig_scene,
    lid,
    mesh_jig,
    output_gear,
    scene,
    test_bushing as gearbox_test_bushing,
    test_bushings as gearbox_test_bushings,
    test_scene as gearbox_test_scene,
)
from splitflap_cad.params import P


def _bbox_tuple(part):
    bb = part.bounding_box()
    return (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)


def test_closed_box_uses_compact_45_by_36mm_footprint():
    assert _bbox_tuple(housing()) == pytest.approx(
        (0, 0, 0, P.gb_outer_w, P.gb_outer_d, P.gb_housing_h)
    )
    closed_lid = F.GEARBOX_LID_IN_BOX * lid()
    assert _bbox_tuple(closed_lid) == pytest.approx(
        (0, 0, P.gb_housing_h - P.gb_lid_plug, P.gb_outer_w, P.gb_outer_d, P.gb_outer_h)
    )
    assert P.gb_outer_w == 45
    assert P.gb_outer_d == 36
    assert P.gb_outer_h <= 45


def test_output_stack_retains_running_clearance_at_compact_depth():
    args = scene().show_args()
    parts = dict(zip(args["names"], args["objects"]))
    gear_front = parts["output-bevel"].bounding_box().max.Y
    bearing_back = parts["output-bearings"].bounding_box().min.Y

    assert bearing_back - gear_front >= P.gb_running_gap


@pytest.mark.parametrize("gear", [input_gear, output_gear])
def test_printable_gears_have_support_free_heel_down_geometry(gear):
    part = gear()
    bb = part.bounding_box()
    bed_faces = [
        face
        for face in part.faces()
        if face.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
        and face.bounding_box().max.Z == pytest.approx(0, abs=1e-6)
        and face.normal_at().Z < -0.99
    ]

    assert bb.min.Z == pytest.approx(0, abs=1e-6)
    assert bed_faces
    assert max(face.bounding_box().size.X for face in bed_faces) > P.gb_gear_hub_d

    vertices, triangles = part.tessellate(0.1, 0.1)
    unsupported_vertices = []
    for a, b, c in triangles:
        p0, p1, p2 = vertices[a], vertices[b], vertices[c]
        ux, uy, uz = p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z
        vx, vy, vz = p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        magnitude = sqrt(nx * nx + ny * ny + nz * nz)
        normal_z = nz / magnitude if magnitude else 0
        if normal_z < -0.71 and min(p0.Z, p1.Z, p2.Z) > 1e-4:
            unsupported_vertices.extend((p0, p1, p2))

    # The D-bore input has no bridge. The round-bore output retains one
    # deliberately tiny Ø2.2 pin-guide bridge, entirely inside its hub.
    if gear is input_gear:
        assert unsupported_vertices == []
    else:
        assert unsupported_vertices
        assert max(sqrt(p.X * p.X + p.Y * p.Y) for p in unsupported_vertices) <= (
            P.gb_gear_hub_d / 2 + 1e-5
        )
        assert any(
            getattr(face, "radius", None) == pytest.approx(P.gb_pin_guide_d / 2)
            for face in part.faces()
        )


def test_test_print_variant_replaces_output_bearings_with_two_printed_bushings():
    args = gearbox_test_scene().show_args()
    parts = dict(zip(args["names"], args["objects"]))
    bushing_plate = gearbox_test_bushings()

    assert "input-bearings" not in parts
    assert "output-bearings" not in parts
    assert "output-bushings" in parts
    assert len(bushing_plate.solids()) == 2
    assert bushing_plate.volume == pytest.approx(2 * gearbox_test_bushing().volume)
    assert tuple(bushing_plate.bounding_box().size) == pytest.approx((34, 16, 5))
    assert (parts["housing"] & parts["output-bushings"]).volume < 1e-6
    assert (parts["input-rod"] & parts["output-bushings"]).volume < 1e-6
    assert (parts["output-rod"] & parts["output-bushings"]).volume < 1e-6


def test_open_l_jig_holds_rods_on_the_mesh_axes_without_extra_hardware():
    assert _bbox_tuple(mesh_jig()) == pytest.approx(
        (0, 0, 0, P.gb_jig_w, P.gb_outer_d, P.gb_jig_h)
    )

    args = gearbox_jig_scene().show_args()
    parts = dict(zip(args["names"], args["objects"]))
    assert set(parts) == {
        "mesh-jig",
        "input-bevel",
        "output-bevel",
        "input-spacer",
        "output-spacer",
        "input-rod",
        "output-rod",
    }
    for name in set(parts) - {"mesh-jig"}:
        assert (parts["mesh-jig"] & parts[name]).volume < 1e-6, name


def test_input_rod_edge_is_15mm_from_back_and_projections_are_10mm():
    args = scene().show_args()
    parts = dict(zip(args["names"], args["objects"]))
    input_bb = parts["input-rod"].bounding_box()
    output_bb = parts["output-rod"].bounding_box()

    assert input_bb.max.Y == pytest.approx(P.gb_shaft_far_from_back)
    assert input_bb.min.Z == pytest.approx(-P.gb_shaft_exposed)
    assert output_bb.max.Y == pytest.approx(P.gb_outer_d + P.gb_shaft_exposed)
    assert input_bb.max.X - input_bb.min.X == pytest.approx(P.gb_motor_shaft_flat)
    assert input_bb.max.Y - input_bb.min.Y == pytest.approx(P.gb_motor_shaft_d)
    assert output_bb.max.Z - output_bb.min.Z == pytest.approx(P.gb_shaft_d)


def test_gears_mesh_without_solid_overlap_and_running_parts_clear_box():
    args = scene().show_args()
    parts = dict(zip(args["names"], args["objects"]))

    assert (parts["input-bevel"] & parts["output-bevel"]).volume < 1e-6
    for name in (
        "input-bevel",
        "output-bevel",
        "input-spacer",
        "output-spacer",
        "output-bearings",
        "input-rod",
        "output-rod",
    ):
        assert (parts["housing"] & parts[name]).volume < 1e-6, name
    assert (parts["input-bevel"] & parts["input-rod"]).volume < 1e-6
    assert (parts["output-bevel"] & parts["output-rod"]).volume < 1e-6


def test_input_motor_shaft_and_output_bearing_contracts():
    assert P.gb_motor_shaft_d == 6
    assert P.gb_motor_shaft_flat == 5.4
    assert P.gb_shaft_d == 5
    assert P.gb_bearing_d == 16
    assert P.gb_bearing_w == 5
    assert P.gb_bearing_n == 2


def test_bevel_pair_is_three_input_turns_to_two_output_turns():
    assert P.gb_input_teeth == 16
    assert P.gb_output_teeth == 24
    assert P.gb_output_teeth / P.gb_input_teeth == pytest.approx(3 / 2)
