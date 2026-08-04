"""Dimensional, clearance, and printer-envelope checks for the NAS bay."""

import pytest

from nas_cad.bay import (
    bay_frame,
    caddy,
    caddy_location,
    door,
    drive_in_caddy_location,
)
from nas_cad.hdd import hdd_envelope
from nas_cad.nas import scene as storage_scene
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


@pytest.mark.parametrize("part", [caddy(), door(), bay_frame()])
def test_every_printed_nas_part_fits_p2s(part):
    assert _fits_p2s(part)


def test_default_six_bay_storage_block_is_six_upright_doors_across():
    assert P.bay_columns * P.bay_rows == 6
    assert (P.bay_columns, P.bay_rows) == (6, 1)
    assert _dims(storage_frame()) == pytest.approx((226.0, 174.0, 116.4))
    assert _fits_p2s(storage_frame())


def test_drive_is_inside_closed_bay():
    drive = caddy_location() * drive_in_caddy_location() * hdd_envelope()
    db, bb = drive.bounding_box(), bay_frame().bounding_box()
    assert db.min.X > bb.min.X
    assert db.max.X < bb.max.X
    assert db.min.Y >= bb.min.Y
    assert db.max.Y < bb.max.Y
    assert db.min.Z > bb.min.Z
    assert db.max.Z < bb.max.Z


def test_tool_less_pins_enter_hdd_holes_without_body_collision():
    drive = drive_in_caddy_location() * hdd_envelope()
    assert (caddy() & drive).volume == pytest.approx(0.0, abs=1e-6)


def test_storage_scene_groups_each_bay_and_its_moving_parts():
    model = storage_scene()
    root = model.show_args()["objects"][0]
    assert root.name == "nas-storage"
    assert [bay.name for bay in root] == [f"bay-{i}" for i in range(1, 7)]
    assert [group.name for group in root[0]] == ["fixed", "moving"]
    moving = root[0][1]
    assert moving[-1].name == "push-door"


def test_storage_scene_animates_press_door_and_caddy_per_bay():
    model = storage_scene()
    assert len(model._tracks) == 6 * 3
    for index in range(1, 7):
        prefix = f"nas-storage/bay-{index}/moving"
        tracks = [track for track in model._tracks if track.target.startswith(prefix)]
        assert {track.action for track in tracks} == {"ty", "rz"}
        assert any(track.target == prefix for track in tracks)
        assert any(track.target == f"{prefix}/push-door" for track in tracks)
