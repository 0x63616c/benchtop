"""Dimensional, fit, and printer-envelope checks for the Retro Mac."""

import pytest

from retro_mac_cad.cradle import (
    cradle_left,
    cradle_right,
    slot_cap_left,
    slot_cap_right,
)
from retro_mac_cad.ipad import ipad_body, ipad_envelope
from retro_mac_cad.params import P
from retro_mac_cad.shell import SKIN_BUILDERS, full_shell


def _dims(part):
    bb = part.bounding_box()
    return bb.size.X, bb.size.Y, bb.size.Z


def _fits_p2s(part):
    return all(
        dim <= limit + 1e-6
        for dim, limit in zip(
            _dims(part), (P.printer_x, P.printer_y, P.printer_z), strict=True
        )
    )


def test_ipad_body_matches_published_fourth_generation_envelope():
    assert _dims(ipad_body()) == pytest.approx((280.6, 5.9, 214.9), abs=0.01)


def test_display_opening_is_derived_from_resolution_and_ppi():
    assert P.display_w == pytest.approx(262.852, abs=0.001)
    assert P.display_h == pytest.approx(197.042, abs=0.001)


def test_case_preserves_macintosh_plus_scale():
    assert P.scale == pytest.approx(12.9 / 9.0)
    assert (P.case_w, P.case_h, P.case_d) == pytest.approx(
        (349.504, 495.131, 396.833), abs=0.001
    )
    assert _dims(full_shell()) == pytest.approx(
        (P.case_w, P.case_d, P.case_h), abs=0.01
    )


@pytest.mark.parametrize(
    "part",
    [
        *(builder() for builder in SKIN_BUILDERS),
        cradle_left(),
        cradle_right(),
        slot_cap_left(),
        slot_cap_right(),
    ],
)
def test_every_printed_part_fits_p2s(part):
    assert _fits_p2s(part), _dims(part)


def test_cradle_does_not_intersect_ipad_envelope():
    cradle = cradle_left() + cradle_right()
    assert (cradle & ipad_envelope()).volume == pytest.approx(0.0, abs=1e-5)


def test_slot_clears_body_and_camera_depth():
    assert 2 * P.pocket_half_w > P.ipad_w
    assert P.slot_y0 < P.camera_back_y
    assert P.slot_y1 > P.ipad_front_y


def test_screen_is_centred_on_display_opening():
    assert P.ipad_bottom_z > 0
    assert P.ipad_top_z < P.case_h
    assert P.screen_z == pytest.approx(
        P.case_h - P.screen_top_margin - P.display_h / 2
    )
