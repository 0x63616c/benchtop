"""Dimensional, clearance, and printer-envelope checks for the NAS bay."""

import pytest

from nas_cad.bay import bay_frame, caddy, drive_in_caddy_location, latch
from nas_cad.hdd import hdd_envelope
from nas_cad.nas import storage_frame
from nas_cad.params import P


def _dims(part):
    bb = part.bounding_box()
    return bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z


def _fits_p2s(part):
    return all(
        dimension <= limit
        for dimension, limit in zip(
            _dims(part), (P.printer_x, P.printer_y, P.printer_z), strict=True
        )
    )


def test_hdd_uses_maximum_sff_8301_envelope():
    assert _dims(hdd_envelope()) == pytest.approx((101.6, 147.0, 26.1), abs=0.01)


def test_caddy_and_bay_have_expected_clearance():
    assert P.caddy_inner_w - P.hdd_w == pytest.approx(2 * P.drive_side_clear)
    assert P.bay_w - P.caddy_w > 2 * P.bay_clear_x
    assert P.bay_h - P.caddy_h > 2 * P.bay_clear_z


@pytest.mark.parametrize("part", [caddy(), latch(), bay_frame()])
def test_every_printed_nas_part_fits_p2s(part):
    assert _fits_p2s(part)


def test_default_six_bay_storage_block_fits_p2s_envelope():
    assert P.bay_columns * P.bay_rows == 6
    assert _fits_p2s(storage_frame())


def test_drive_is_inside_closed_bay():
    drive = drive_in_caddy_location() * hdd_envelope()
    db, bb = drive.bounding_box(), bay_frame().bounding_box()
    assert db.min.X > bb.min.X
    assert db.max.X < bb.max.X
    assert db.min.Y >= bb.min.Y
    assert db.max.Y < bb.max.Y
    assert db.min.Z > bb.min.Z
    assert db.max.Z < bb.max.Z
