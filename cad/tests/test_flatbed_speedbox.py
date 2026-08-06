"""Geometry and interface checks for the enclosed Flatbed JGB37 speedbox."""

from math import sqrt

import pytest
from build123d import Align, Box, Cylinder, Pos

from flatbed_cad import frames as F
from flatbed_cad.motor_reference import motor_reference
from flatbed_cad.params import P
from flatbed_cad.speedbox import (
    input_gear,
    output_axis_y,
    output_bearings,
    output_gear,
    output_rod,
    output_spacer,
    pair_in_box,
    pair_parts,
    posed_output_spacer,
)
from flatbed_cad.speedbox_assembly import scene as assembly_scene
from flatbed_cad.speedbox_panels import (
    bottom_panel,
    front_panel,
    left_panel,
    motor_bulkhead,
    rear_panel,
    right_panel,
    top_panel,
)


def test_ratio_is_a_one_point_three_three_times_speed_increase():
    assert P.fg_input_teeth == 24
    assert P.fg_output_teeth == 18
    assert P.fg_output_speed_ratio == pytest.approx(4 / 3)


def test_box_uses_physically_selected_flatbed_joint():
    assert P.fg_panel_t == 2.0
    assert P.fg_side_t == 2.0
    assert P.fg_joint_boss_t == 8.0
    assert P.fg_joint_clear == 0.20
    assert P.fg_joint_hole_d == 3.4
    assert (P.fg_joint_nut_w, P.fg_joint_nut_d) == (5.8, 2.7)
    assert P.fg_joint_stem_w == 3.5
    assert P.fg_joint_head_d == 6.0
    assert P.fg_joint_edge_ligament == 2.0


def test_motor_is_fully_inside_six_side_envelope():
    motor = F.FG_MOTOR_IN_BOX * motor_reference()
    bounds = motor.bounding_box()

    assert bounds.min.X >= P.fg_panel_t
    assert bounds.max.X <= P.fg_box_w - P.fg_panel_t
    assert bounds.min.Y >= P.fg_panel_t
    assert bounds.max.Y <= P.fg_box_d - P.fg_panel_t
    assert bounds.min.Z >= P.fg_panel_t
    assert bounds.max.Z <= P.fg_box_h - P.fg_panel_t


def test_gears_fit_inside_box_and_output_axis_clears_front():
    for gear in pair_parts():
        bounds = (pair_in_box() * gear).bounding_box()
        assert bounds.min.X > P.fg_panel_t
        assert bounds.max.X < P.fg_box_w - P.fg_panel_t
        assert bounds.min.Y > P.fg_motor_face_y
        assert bounds.max.Y < P.fg_box_d - P.fg_panel_t
        assert bounds.min.Z > P.fg_panel_t
        assert bounds.max.Z < P.fg_box_h - P.fg_panel_t

    assert output_axis_y() < P.fg_box_d - P.fg_bearing_carrier_d / 2


@pytest.mark.parametrize(
    "builder,max_height",
    (
        (bottom_panel, P.fg_front_center_boss_t),
        (top_panel, P.fg_bearing_carrier_t),
        (front_panel, P.fg_panel_t),
        (rear_panel, P.fg_panel_t),
        (left_panel, P.fg_joint_boss_t),
        (right_panel, P.fg_joint_boss_t),
        (
            motor_bulkhead,
            P.fg_bulkhead_t + P.fg_bulkhead_reinforce,
        ),
        (input_gear, None),
        (output_gear, None),
        (output_spacer, None),
    ),
)
def test_every_printable_starts_flat_on_bed(builder, max_height):
    bounds = builder().bounding_box()
    assert bounds.min.Z == pytest.approx(0, abs=1e-6)
    if max_height is not None:
        assert bounds.max.Z == pytest.approx(max_height)


def test_output_spacer_has_positive_length():
    bounds = output_spacer().bounding_box()
    assert bounds.max.Z > 3.5


def test_output_has_two_distinct_bearings():
    assert len(output_bearings().solids()) == 2


def test_printable_gears_are_each_one_connected_solid():
    assert len(input_gear().solids()) == 1
    assert len(output_gear().solids()) == 1


def test_output_gear_has_support_free_wide_heel_down_geometry():
    gear = output_gear()
    bed_faces = [
        face
        for face in gear.faces()
        if face.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
        and face.bounding_box().max.Z == pytest.approx(0, abs=1e-6)
        and face.normal_at().Z < -0.99
    ]
    assert bed_faces
    assert max(face.bounding_box().size.X for face in bed_faces) > P.fg_gear_hub_d

    vertices, triangles = gear.tessellate(0.1, 0.1)
    unsupported = []
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
            unsupported.extend((p0, p1, p2))
    assert unsupported == []


def test_output_gear_d_bore_matches_a_short_flat_filed_into_five_mm_rod():
    gear = output_gear()
    probe_z = gear.bounding_box().max.Z - 1.0
    flat_probe = Pos(0, -2.25, probe_z - 0.25) * Cylinder(
        0.12,
        0.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    open_probe = Pos(0, 2.25, probe_z - 0.25) * Cylinder(
        0.12,
        0.5,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    assert (gear & flat_probe).volume == pytest.approx(flat_probe.volume)
    assert (gear & open_probe).volume == pytest.approx(0, abs=1e-6)
    assert P.fg_output_shaft_d - P.fg_output_shaft_flat == pytest.approx(0.6)


def test_compact_envelope_and_large_encoder_exit_are_locked_in():
    assert (P.fg_box_w, P.fg_box_d, P.fg_box_h) == (55.0, 95.0, 43.0)
    assert (P.fg_wire_exit_w, P.fg_wire_exit_h) == (24.0, 14.0)
    assert P.fg_motor_face_y == pytest.approx(65.0)


def test_one_sided_output_shaft_does_not_touch_motor():
    motor = F.FG_MOTOR_IN_BOX * motor_reference()
    assert (motor & output_rod()).volume == pytest.approx(0, abs=1e-6)


def test_output_shaft_engages_d_bore_without_touching_input_gear():
    input_part, output_part = pair_parts()
    input_in_box = pair_in_box() * input_part
    output_in_box = pair_in_box() * output_part
    rod = output_rod()
    assert rod.bounding_box().min.Z == pytest.approx(
        output_in_box.bounding_box().min.Z
    )
    assert (rod & input_in_box).volume == pytest.approx(0, abs=1e-6)
    assert (rod & output_in_box).volume == pytest.approx(0, abs=1e-6)
    assert (input_in_box & output_in_box).volume == pytest.approx(0, abs=1e-6)


def test_output_shaft_is_centered_and_gear_clears_front_skin():
    rod_bounds = output_rod().bounding_box()
    assert (rod_bounds.min.X + rod_bounds.max.X) / 2 == pytest.approx(
        P.fg_box_w / 2
    )
    output_bounds = (pair_in_box() * pair_parts()[1]).bounding_box()
    front_clearance = P.fg_box_d - P.fg_panel_t - output_bounds.max.Y
    assert front_clearance >= 1.0


def test_top_and_bottom_hardware_stays_behind_motor_bulkhead():
    furthest_hardware_y = max(
        P.fg_box_d / 2 + station + P.fg_joint_nut_w / 2
        for station in P.fg_long_joint_positions
    )
    assert furthest_hardware_y < P.fg_motor_face_y


@pytest.mark.parametrize(
    "builder,hole_ys",
    (
        (bottom_panel, P.fg_long_joint_positions),
        (top_panel, tuple(-u for u in P.fg_long_joint_positions)),
        (rear_panel, (0.0,)),
        (front_panel, (P.fg_front_joint_z,)),
    ),
)
def test_every_face_has_full_m3_holes_and_complete_head_seats(builder, hole_ys):
    part = builder()
    hole_xs = (
        -P.fg_box_w / 2 + P.fg_joint_axis_inset,
        P.fg_box_w / 2 - P.fg_joint_axis_inset,
    )
    for hole_x in hole_xs:
        for hole_y in hole_ys:
            through_probe = Pos(hole_x, hole_y, -0.1) * Cylinder(
                P.fg_joint_hole_d / 2 - 0.1,
                P.fg_panel_t + 0.2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            assert (part & through_probe).volume == pytest.approx(0, abs=1e-6)

            head_disk = Pos(hole_x, hole_y, 0) * Cylinder(
                P.fg_joint_head_d / 2,
                P.fg_panel_t,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            hole_disk = Pos(hole_x, hole_y, 0) * Cylinder(
                P.fg_joint_hole_d / 2,
                P.fg_panel_t,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            seat = head_disk - hole_disk
            assert (seat - (part & seat)).volume == pytest.approx(0, abs=1e-6)


def test_front_has_centered_third_m3_hole_on_opposite_long_edge():
    front = front_panel()
    center_v = P.fg_front_center_axis_z - P.fg_box_h / 2
    through_probe = Pos(0, center_v, -0.1) * Cylinder(
        P.fg_joint_hole_d / 2 - 0.1,
        P.fg_panel_t + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    assert (front & through_probe).volume == pytest.approx(0, abs=1e-6)

    head_disk = Pos(0, center_v, 0) * Cylinder(
        P.fg_joint_head_d / 2,
        P.fg_panel_t,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    hole_disk = Pos(0, center_v, 0) * Cylinder(
        P.fg_joint_hole_d / 2,
        P.fg_panel_t,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    seat = head_disk - hole_disk
    assert (seat - (front & seat)).volume == pytest.approx(0, abs=1e-6)
    lower_edge_ligament = (
        center_v + P.fg_inner_h / 2 - P.fg_joint_head_d / 2
    )
    assert lower_edge_ligament >= P.fg_joint_edge_ligament


def test_third_front_bolt_has_aligned_top_loading_nut_boss_on_bottom():
    bottom = bottom_panel()
    pocket_y = P.fg_box_d / 2 - P.fg_joint_nut_inset
    cavity_floor = P.fg_front_center_axis_z - P.fg_joint_nut_w / 2
    bottomed_nut_center = cavity_floor + P.fg_joint_nut_w / 2
    assert bottomed_nut_center == pytest.approx(P.fg_front_center_axis_z)

    solid_floor = Pos(0, pocket_y, cavity_floor / 2) * Box(
        3.0, 2.0, cavity_floor - 0.2
    )
    open_cavity = Pos(0, pocket_y, 7.0) * Box(3.0, 2.0, 5.0)
    assert (bottom & solid_floor).volume == pytest.approx(solid_floor.volume)
    assert (bottom & open_cavity).volume == pytest.approx(0, abs=1e-6)


def test_m3_head_and_slot_ligaments_are_at_least_two_mm():
    edge_ligament = P.fg_joint_axis_inset - P.fg_joint_head_d / 2
    slot_ligament = (
        P.fg_joint_tab_pitch / 2
        - (P.fg_joint_tab_w + P.fg_joint_tab_end_clear) / 2
        - P.fg_joint_head_d / 2
    )
    assert edge_ligament >= P.fg_joint_edge_ligament
    assert slot_ligament >= P.fg_joint_edge_ligament


def test_side_nut_traps_open_inside_but_keep_solid_outside_wall():
    side = left_panel()
    u = P.fg_long_joint_positions[0]
    pocket_v = P.fg_inner_h / 2 - P.fg_joint_nut_inset
    outer_wall = Pos(u, pocket_v, 1.0) * Box(3.0, 2.0, 1.5)
    inner_cavity = Pos(u, pocket_v, 6.0) * Box(3.0, 2.0, 3.0)
    assert (side & outer_wall).volume == pytest.approx(outer_wall.volume)
    assert (side & inner_cavity).volume == pytest.approx(0, abs=1e-6)


def test_side_nut_traps_align_a_bottomed_m3_nut_with_the_bolt_axis():
    cavity_floor = P.fg_joint_boss_t - P.fg_joint_nut_access_depth
    bottomed_nut_center = cavity_floor + P.fg_joint_nut_w / 2
    assert cavity_floor == P.fg_side_t
    assert bottomed_nut_center == pytest.approx(P.fg_joint_axis_inset, abs=0.15)


def test_large_panels_use_connected_ladder_frames_without_x_braces():
    side = left_panel()
    bottom = bottom_panel()
    front = front_panel()

    old_thick_side = P.fg_inner_d * P.fg_inner_h * P.fg_joint_boss_t
    bottom_full = P.fg_box_w * P.fg_box_d * P.fg_panel_t
    front_full = P.fg_box_w * P.fg_inner_h * P.fg_panel_t
    assert side.volume < old_thick_side * 0.35
    assert bottom.volume < bottom_full * 0.70
    assert front.volume < front_full * 0.75

    for part in (side, bottom, front):
        assert len(part.solids()) == 1

    side_window_w = (
        P.fg_inner_d - 2 * P.fg_side_frame_x - P.fg_side_rib_w
    ) / 2
    side_window_x = P.fg_side_rib_w / 2 + side_window_w / 2
    side_open = Pos(side_window_x, 0, P.fg_side_t / 2) * Box(
        2, 2, P.fg_side_t + 0.2
    )
    side_rib = Pos(0, 0, P.fg_side_t / 2) * Box(2, 2, P.fg_side_t)
    skin_center_y = (P.fg_skin_window_y0 + P.fg_skin_window_y1) / 2
    bottom_open = Pos(0, skin_center_y + 15, P.fg_panel_t / 2) * Box(
        2, 2, P.fg_panel_t + 0.2
    )
    bottom_rib = Pos(0, skin_center_y, P.fg_panel_t / 2) * Box(
        2, 2, P.fg_panel_t
    )
    assert (side & side_open).volume == pytest.approx(0, abs=1e-6)
    assert (side & side_rib).volume > 0
    assert (bottom & bottom_open).volume == pytest.approx(0, abs=1e-6)
    assert (bottom & bottom_rib).volume > 0


def test_assembly_scene_contains_closed_box_and_drivetrain():
    names = assembly_scene().show_args()["names"]
    assert names[:7] == [
        "bottom",
        "top",
        "left",
        "right",
        "rear",
        "front",
        "motor-bulkhead",
    ]
    assert {"jgb37-520", "24T-input", "18T-output", "625ZZ-bearings"} <= set(
        names
    )


@pytest.mark.slow
def test_structural_panels_do_not_overlap_when_assembled():
    parts = (
        (bottom_panel(), F.FG_BOTTOM_IN_BOX),
        (top_panel(), F.FG_TOP_IN_BOX),
        (left_panel(), F.FG_LEFT_IN_BOX),
        (right_panel(), F.FG_RIGHT_IN_BOX),
        (rear_panel(), F.FG_REAR_IN_BOX),
        (front_panel(), F.FG_FRONT_IN_BOX),
        (motor_bulkhead(), F.FG_BULKHEAD_IN_BOX),
    )
    posed = [location * part for part, location in parts]
    for index, first in enumerate(posed):
        for second in posed[index + 1 :]:
            assert (first & second).volume == pytest.approx(0, abs=1e-6)


@pytest.mark.slow
def test_motor_shaft_clears_input_gear_bore():
    motor = F.FG_MOTOR_IN_BOX * motor_reference()
    input_gear_in_box = pair_in_box() * pair_parts()[0]
    assert (motor & input_gear_in_box).volume == pytest.approx(0, abs=1e-6)


@pytest.mark.slow
def test_complete_assembly_has_no_solid_collisions():
    input_part, output_part = pair_parts()
    gear_frame = pair_in_box()
    parts = (
        F.FG_BOTTOM_IN_BOX * bottom_panel(),
        F.FG_TOP_IN_BOX * top_panel(),
        F.FG_LEFT_IN_BOX * left_panel(),
        F.FG_RIGHT_IN_BOX * right_panel(),
        F.FG_REAR_IN_BOX * rear_panel(),
        F.FG_FRONT_IN_BOX * front_panel(),
        F.FG_BULKHEAD_IN_BOX * motor_bulkhead(),
        F.FG_MOTOR_IN_BOX * motor_reference(),
        gear_frame * input_part,
        gear_frame * output_part,
        output_bearings(),
        posed_output_spacer(),
        output_rod(),
    )
    for index, first in enumerate(parts):
        for second in parts[index + 1 :]:
            assert (first & second).volume == pytest.approx(0, abs=1e-6)
