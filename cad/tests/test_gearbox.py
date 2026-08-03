"""Fit contract for the compact right-angle gearbox."""

from math import sqrt

import pytest

from splitflap_cad import frames as F
from splitflap_cad.gearbox import housing, input_gear, lid, output_gear, scene
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
    unsupported_triangles = []
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
            unsupported_triangles.append((a, b, c))

    assert unsupported_triangles == []


def test_input_rod_edge_is_15mm_from_back_and_projections_are_10mm():
    args = scene().show_args()
    parts = dict(zip(args["names"], args["objects"]))
    input_bb = parts["input-rod"].bounding_box()
    output_bb = parts["output-rod"].bounding_box()

    assert input_bb.max.Y == pytest.approx(P.gb_shaft_far_from_back)
    assert input_bb.min.Z == pytest.approx(-P.gb_shaft_exposed)
    assert output_bb.max.Y == pytest.approx(P.gb_outer_d + P.gb_shaft_exposed)
    assert input_bb.max.X - input_bb.min.X == pytest.approx(P.gb_shaft_d)
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
        "input-bearings",
        "output-bearings",
        "input-rod",
        "output-rod",
    ):
        assert (parts["housing"] & parts[name]).volume < 1e-6, name


def test_bearing_contract_is_625zz_on_both_axes():
    assert P.gb_shaft_d == 5
    assert P.gb_bearing_d == 16
    assert P.gb_bearing_w == 5
    assert P.gb_bearing_n == 2


def test_bevel_pair_is_three_input_turns_to_two_output_turns():
    assert P.gb_input_teeth == 16
    assert P.gb_output_teeth == 24
    assert P.gb_output_teeth / P.gb_input_teeth == pytest.approx(3 / 2)
