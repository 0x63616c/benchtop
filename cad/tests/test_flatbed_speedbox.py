"""Geometry and interface checks for the enclosed Flatbed JGB37 speedbox."""

import pytest

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


def test_ratio_is_a_two_times_speed_increase():
    assert P.fg_input_teeth == 24
    assert P.fg_output_teeth == 12
    assert P.fg_output_speed_ratio == pytest.approx(2.0)


def test_box_uses_physically_selected_flatbed_joint():
    assert P.fg_panel_t == 2.0
    assert P.fg_joint_clear == 0.20
    assert P.fg_joint_hole_d == 3.4
    assert (P.fg_joint_nut_w, P.fg_joint_nut_d) == (5.8, 2.7)


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
        (bottom_panel, P.fg_panel_t),
        (top_panel, P.fg_panel_t),
        (front_panel, P.fg_panel_t),
        (rear_panel, P.fg_panel_t),
        (left_panel, P.fg_panel_t),
        (right_panel, P.fg_bearing_carrier_t),
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
    assert bounds.max.Z > 0.6


def test_printable_gears_are_each_one_connected_solid():
    assert len(input_gear().solids()) == 1
    assert len(output_gear().solids()) == 1


def test_compact_envelope_and_large_encoder_exit_are_locked_in():
    assert (P.fg_box_w, P.fg_box_d, P.fg_box_h) == (43.0, 91.0, 43.0)
    assert (P.fg_wire_exit_w, P.fg_wire_exit_h) == (24.0, 14.0)
    assert P.fg_motor_face_y == pytest.approx(65.0)


def test_one_sided_output_shaft_does_not_touch_motor():
    motor = F.FG_MOTOR_IN_BOX * motor_reference()
    assert (motor & output_rod()).volume == pytest.approx(0, abs=1e-6)


def test_output_shaft_starts_beyond_input_gear_and_gears_do_not_overlap():
    input_part, output_part = pair_parts()
    input_in_box = pair_in_box() * input_part
    output_in_box = pair_in_box() * output_part
    assert output_rod().bounding_box().min.X > input_in_box.bounding_box().max.X
    assert (input_in_box & output_in_box).volume == pytest.approx(0, abs=1e-6)


def test_top_and_bottom_hardware_stays_behind_motor_bulkhead():
    furthest_hardware_y = max(
        P.fg_box_d / 2 + station + P.fg_joint_nut_w / 2
        for station in P.fg_long_joint_positions
    )
    assert furthest_hardware_y < P.fg_motor_face_y


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
    assert {"jgb37-520", "24T-input", "12T-output", "625ZZ-bearing"} <= set(
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
