"""Assembly and print contract for the removable blinds drive cassette."""

import pytest
from build123d import Cylinder, Pos, Rot


def test_layshaft_uses_a_real_5mm_rod_and_two_625zz_bearings():
    from blinds_cad.drivecassette import bearing_625zz, layshaft_rod
    from blinds_cad.params import P

    bearing_bounds = bearing_625zz().bounding_box()
    rod_bounds = layshaft_rod().bounding_box()

    assert P.lay_rod_d == 5.0
    assert P.lay_bearing_d == 16.0
    assert P.lay_bearing_w == 5.0
    assert P.lay_bearing_centers_x == (69.0, 89.0)
    assert tuple(bearing_bounds.size) == pytest.approx((5.0, 16.0, 16.0))
    assert tuple(rod_bounds.size) == pytest.approx((38.5, 5.0, 5.0))


def test_drive_cassette_is_removable_and_all_four_mounts_are_supported():
    from blinds_cad.drivecassette import bearing_caps, drive_cassette
    from blinds_cad.enclosure import frame
    from blinds_cad.params import P

    structure = frame()
    cassette = drive_cassette()
    caps = bearing_caps()

    assert len(structure.solids()) == 1
    assert len(cassette.solids()) == 1
    assert len(caps.solids()) == 2
    assert (structure & cassette).volume < 1e-6

    for x, y, z in P.drive_mount_points:
        screw = Pos(x, P.drive_tab_y1 + 0.5, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.drive_mount_clear_d / 2, P.drive_tab_y1 + 1)
        )
        frame_pad = Pos(x, y, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.drive_mount_boss_d / 2, P.drive_mount_face_y)
        )

        assert (structure & screw).volume < 1e-6, (x, z)
        assert (cassette & screw).volume < 1e-6, (x, z)
        assert (structure & frame_pad).volume >= 30.0, (x, z)
