"""Flatbed calibration geometry and print-envelope checks."""

import pytest

from flatbed_cad.calibration import calibration_kit, fastener_coupon
from flatbed_cad.params import P


def test_calibration_kit_is_palm_scale_and_flat_on_bed():
    kit = calibration_kit()
    bounds = kit.bounding_box()

    assert bounds.min.Z == pytest.approx(0)
    assert bounds.max.Z == pytest.approx(P.fastener_t)
    assert bounds.max.X - bounds.min.X <= 80
    assert bounds.max.Y - bounds.min.Y <= 130
    assert len(kit.solids()) == 7


def test_fit_ladder_brackets_the_nominal_dimensions():
    assert P.lap_clearances == (0.10, 0.20, 0.30)
    assert P.insert_bore_ds == (4.0, 4.2, 4.4)
    assert P.clearance_hole_ds == (3.2, 3.4, 3.6)


def test_insert_bores_leave_a_floor():
    assert P.fastener_t - P.insert_bore_depth > 0
    assert fastener_coupon().bounding_box().max.Z == pytest.approx(P.fastener_t)
