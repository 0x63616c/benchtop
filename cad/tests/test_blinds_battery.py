"""Public contract for the removable 2S3P battery assembly.

The bought parts are two Bistook three-slot 21700 holders.  Each holder
mounts directly to the wall frame through its three moulded 4.2 mm holes;
there is no structural carrier PCB.
"""

import pytest
from build123d import Cylinder, Pos, Rot


def test_two_owned_holders_match_the_supplied_plastic_envelope():
    from blinds_cad.cells21700 import holder_stack

    bounds = holder_stack().bounding_box()

    assert bounds.size.X == pytest.approx(83.00)
    assert bounds.size.Y == pytest.approx(14.51)
    assert bounds.size.Z == pytest.approx(136.18)


def test_holders_fit_the_bay_with_a_room_side_wiring_cavity():
    from blinds_cad import frames as F
    from blinds_cad.cells21700 import holder_stack
    from blinds_cad.params import P

    bounds = (F.BAY_IN_UNIT * holder_stack()).bounding_box()

    assert bounds.min.X == pytest.approx(7.5)
    assert bounds.max.X == pytest.approx(90.5)
    assert bounds.min.Y == pytest.approx(8.5)
    assert bounds.min.Z == pytest.approx(17.0)
    assert bounds.max.Z == pytest.approx(153.18)

    contact_front = bounds.min.Y + 21.80
    sleeve_inner_front = P.enc_d - P.sleeve_t
    assert sleeve_inner_front - contact_front >= 12.0


def test_all_six_holder_screws_land_in_supported_frame_holes():
    from blinds_cad import frames as F
    from blinds_cad.cells21700 import holder_stack
    from blinds_cad.enclosure import frame
    from blinds_cad.params import P

    holders = F.BAY_IN_UNIT * holder_stack()
    structure = frame()
    for x, y, z in P.battery_mount_points:
        holder_hole = Pos(x, y + P.holder3_body_d + 1, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.holder3_hole_d / 2, P.holder3_body_d + 2)
        )
        insert_hole = Pos(x, y + 0.1, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.m3_insert_d / 2, P.battery_insert_depth + 0.2)
        )
        boss_gauge = Pos(x, y, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.battery_boss_d / 2, P.battery_mount_depth)
        )

        assert (holders & holder_hole).volume < 1e-6, (x, z)
        assert (structure & insert_hole).volume < 1e-6, (x, z)
        assert (structure & boss_gauge).volume >= 40.0, (x, z)
