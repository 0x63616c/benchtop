"""Fit contract for the circular JGB37 bevel attachment."""

import pytest
from build123d import Pos

from splitflap_cad.gearbox import _cylinder
from splitflap_cad.motorbevel import housing, lid_print, motor_reference, scene
from splitflap_cad.params import P


def _parts():
    args = scene().show_args()
    return dict(zip(args["names"], args["objects"]))


def test_measured_motor_reference_matches_the_attachment_contract():
    motor_bb = motor_reference().bounding_box()

    assert P.gba_motor_d == 37
    assert P.gba_motor_ecc == 7
    assert P.gba_motor_boss_d == 12
    assert P.gba_motor_boss_h == 6
    assert P.gba_motor_shaft_d == 6
    assert P.gba_motor_shaft_flat == 5.4
    assert P.gba_motor_shaft_len == 15
    assert P.gba_motor_screw_n == 6
    assert P.gba_motor_screw_bcd == 32
    assert motor_bb.max.Z == pytest.approx(21)


def test_main_body_is_37mm_with_only_a_small_integrated_output_nose():
    bb = housing().bounding_box()

    assert bb.min.X == pytest.approx(-P.gba_outer_r)
    assert bb.max.X == pytest.approx(P.gba_outer_r)
    assert bb.min.Y == pytest.approx(-P.gba_outer_r)
    assert bb.max.Y == pytest.approx(P.gba_outer_r + P.gba_output_nose)
    assert P.gba_motor_screw_bcd / 2 + P.gba_mount_clear_d / 2 < P.gba_outer_r


def test_m3_head_windows_run_from_the_base_deck_to_the_open_top():
    body = housing()
    radial_probe = P.gba_motor_screw_bcd / 2 + 2
    lower_wall = Pos(radial_probe, 0, 0) * _cylinder(0.1, P.gba_base_t)
    upper_window = Pos(radial_probe, 0, P.gba_base_t) * _cylinder(
        0.1, P.gba_body_h - P.gba_base_t
    )

    assert (body & lower_wall).volume > 0
    assert (body & upper_window).volume < 1e-6


def test_m3_head_windows_have_square_corners():
    body = housing()
    square_corner = Pos(17.8, 2.8, P.gba_base_t) * _cylinder(
        0.1, P.gba_axis_z - P.gba_base_t
    )

    assert (body & square_corner).volume < 1e-6


def test_input_gear_hub_remains_fully_engaged_on_the_motor_shaft():
    parts = _parts()
    shaft_tip = P.gba_motor_boss_h + P.gba_motor_shaft_len
    input_gear_bb = parts["input-bevel"].bounding_box()

    assert input_gear_bb.min.Z > P.gba_motor_boss_h
    assert input_gear_bb.max.Z < shaft_tip
    assert (parts["motor"] & parts["input-bevel"]).volume < 1e-6
    assert (parts["motor"] & parts["input-spacer"]).volume < 1e-6


def test_compact_closed_attachment_is_38mm_tall():
    parts = _parts()

    assert P.gba_body_h == 35
    assert parts["housing"].bounding_box().max.Z == pytest.approx(P.gba_axis_z)
    assert parts["lid"].bounding_box().max.Z == pytest.approx(38)


def test_gears_and_running_stack_clear_the_circular_housing():
    parts = _parts()

    assert (parts["input-bevel"] & parts["output-bevel"]).volume < 1e-6
    assert (parts["housing"] & parts["motor"]).volume < 1e-6
    for name in (
        "input-bevel",
        "output-bevel",
        "input-spacer",
        "output-spacer",
        "output-bearings",
        "output-rod",
    ):
        assert (parts["housing"] & parts[name]).volume < 1e-6, name
        assert (parts["lid"] & parts[name]).volume < 1e-6, name

    assert (parts["housing"] & parts["lid"]).volume < 1e-6


def test_split_bearing_seats_close_directly_around_both_625zzs():
    parts = _parts()
    bearings = parts["output-bearings"]

    assert bearings.bounding_box().min.Z < P.gba_axis_z
    assert bearings.bounding_box().max.Z > P.gba_axis_z
    assert (parts["housing"] & bearings).volume < 1e-6
    assert (parts["lid"] & bearings).volume < 1e-6


def test_upper_enclosure_exports_roof_down_on_the_print_bed():
    printable = lid_print()

    assert printable.bounding_box().min.Z == pytest.approx(0)
    assert printable.volume == pytest.approx(_parts()["lid"].volume)


def test_spacers_locate_the_mesh_and_output_projects_10mm():
    parts = _parts()
    input_spacer_bb = parts["input-spacer"].bounding_box()
    input_gear_bb = parts["input-bevel"].bounding_box()
    output_spacer_bb = parts["output-spacer"].bounding_box()
    output_bearing_bb = parts["output-bearings"].bounding_box()

    assert input_spacer_bb.min.Z == pytest.approx(P.gba_motor_boss_h)
    assert input_gear_bb.min.Z - input_spacer_bb.max.Z == pytest.approx(P.gb_running_gap)
    assert output_bearing_bb.min.Y - output_spacer_bb.max.Y == pytest.approx(
        P.gb_running_gap
    )
    assert parts["output-rod"].bounding_box().max.Y == pytest.approx(
        P.gba_outer_r + P.gb_shaft_exposed
    )
