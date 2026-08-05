"""Flatbed captive-nut calibration geometry and print-envelope checks."""

import pytest

from flatbed_cad.calibration import base_coupon, calibration_kit, upright_coupon
from flatbed_cad.frames import UPRIGHT_ON_BASE
from flatbed_cad.params import P


def test_calibration_kit_is_palm_scale_and_flat_on_bed():
    kit = calibration_kit()
    bounds = kit.bounding_box()

    assert bounds.min.Z == pytest.approx(0)
    assert bounds.max.Z == pytest.approx(P.panel_t)
    assert bounds.max.X - bounds.min.X <= 140
    assert bounds.max.Y - bounds.min.Y <= 60
    assert len(kit.solids()) == 10


def test_five_step_ladders_cover_requested_ranges():
    assert P.panel_clearances == (0.10, 0.15, 0.20, 0.25, 0.30)
    assert P.clearance_hole_ds == (3.2, 3.3, 3.4, 3.5, 3.6)
    assert P.nut_pocket_ws == (5.6, 5.7, 5.8, 5.9, 6.0)
    assert P.nut_pocket_ds == (2.5, 2.6, 2.7, 2.8, 2.9)
    assert 0 < P.label_depth < P.panel_t


def test_every_base_and_upright_has_the_same_interchangeable_envelope():
    base_bounds = [base_coupon(i).bounding_box().size for i in range(5)]
    upright_bounds = [upright_coupon(i).bounding_box().size for i in range(5)]

    assert all(size == base_bounds[0] for size in base_bounds)
    assert all(size == upright_bounds[0] for size in upright_bounds)


def test_nut_pocket_is_reached_by_bolt_stem():
    for pocket_d in P.nut_pocket_ds:
        pocket_bottom = P.nut_center_y - pocket_d / 2
        assert pocket_bottom > 0
        assert P.bolt_stem_w > max(P.clearance_hole_ds)


def test_assembled_tabs_finish_flush_without_interference():
    base = base_coupon(2)
    upright = UPRIGHT_ON_BASE * upright_coupon(2)

    assert (base & upright).volume == pytest.approx(0, abs=1e-6)
    assert upright.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
    assert upright.bounding_box().max.Z == pytest.approx(P.panel_t + P.upright_h)
