"""Fit contract for the circular JGB37 bevel attachment."""

import pytest

from splitflap_cad.motorbevel import bearing_cartridge, housing, motor_reference, scene
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


def test_main_body_is_37mm_and_cartridge_is_the_only_output_nose():
    bb = housing().bounding_box()
    cartridge_bb = _parts()["bearing-cartridge"].bounding_box()

    assert bb.min.X == pytest.approx(-P.gba_outer_r)
    assert bb.max.X == pytest.approx(P.gba_outer_r)
    assert bb.min.Y == pytest.approx(-P.gba_outer_r)
    assert bb.max.Y == pytest.approx(P.gba_outer_r)
    assert cartridge_bb.max.Y == pytest.approx(P.gba_outer_r + 1)
    assert P.gba_motor_screw_bcd / 2 + P.gba_mount_clear_d / 2 < P.gba_outer_r


def test_motor_shaft_tip_and_input_gear_hub_finish_flush():
    parts = _parts()
    shaft_tip = P.gba_motor_boss_h + P.gba_motor_shaft_len

    assert parts["input-bevel"].bounding_box().max.Z == pytest.approx(shaft_tip)
    assert (parts["motor"] & parts["input-bevel"]).volume < 1e-6
    assert (parts["motor"] & parts["input-spacer"]).volume < 1e-6


def test_gears_and_running_stack_clear_the_circular_housing():
    parts = _parts()

    assert (parts["input-bevel"] & parts["output-bevel"]).volume < 1e-6
    assert (parts["housing"] & parts["motor"]).volume < 1e-6
    for name in (
        "input-bevel",
        "output-bevel",
        "input-spacer",
        "output-spacer",
        "bearing-cartridge",
        "output-bearings",
        "output-rod",
    ):
        assert (parts["housing"] & parts[name]).volume < 1e-6, name
        assert (parts["lid"] & parts[name]).volume < 1e-6, name

    assert (parts["bearing-cartridge"] & parts["output-bearings"]).volume < 1e-6
    assert (parts["bearing-cartridge"] & parts["output-rod"]).volume < 1e-6


def test_bearing_cartridge_prints_upright_with_a_45_degree_flange_ramp():
    bb = bearing_cartridge().bounding_box()
    radial_growth = (P.gba_bearing_flange_d - P.gba_bearing_cartridge_d) / 2

    assert bb.min.Z == pytest.approx(0)
    assert radial_growth <= P.gba_bearing_flange_t
    assert bb.size.Z == pytest.approx(
        P.gba_outer_r + 1 - (P.gba_output_bearing_y0 - 0.5)
    )


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
