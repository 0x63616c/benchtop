"""Public assembly contract for the printable blinds enclosure system.

The wall frame and removable axle keeper are structural. The sleeve and
two cap halves are cosmetic, removable parts. These tests observe only the
exported solids and their assembled locations, so the construction can
change without weakening the contract.
"""

import pytest
from build123d import Cylinder, Pos, Rot


@pytest.fixture(scope="module")
def enclosure_parts():
    from blinds_cad.enclosure import axle_keeper, frame
    from blinds_cad.cover import cap_front, cap_rear, sleeve

    return {
        "frame": frame(),
        "axle-keeper": axle_keeper(),
        "sleeve": sleeve(),
        "cap-rear": cap_rear(),
        "cap-front": cap_front(),
    }


def test_every_enclosure_part_is_one_printable_solid(enclosure_parts):
    for name, part in enclosure_parts.items():
        assert len(part.solids()) == 1, name


def test_cosmetic_parts_clear_the_structural_frame(enclosure_parts):
    frame = enclosure_parts["frame"]
    for name in ("sleeve", "cap-rear", "cap-front"):
        overlap = (frame & enclosure_parts[name]).volume
        assert overlap < 1e-6, f"frame x {name}: {overlap:.3f} mm3"


def test_axle_keeper_seats_without_overlapping_frame(enclosure_parts):
    overlap = (
        enclosure_parts["frame"] & enclosure_parts["axle-keeper"]
    ).volume
    assert overlap < 1e-6


def test_cap_halves_close_the_top_without_overlapping(enclosure_parts):
    from blinds_cad.params import P

    rear = enclosure_parts["cap-rear"]
    front = enclosure_parts["cap-front"]
    assert (rear & front).volume < 1e-6

    combined = rear + front
    bb = combined.bounding_box()
    assert bb.min.X == pytest.approx(0.0)
    assert bb.max.X == pytest.approx(P.enc_w)
    assert bb.min.Y == pytest.approx(0.0)
    assert bb.max.Y == pytest.approx(P.enc_d)
    assert bb.max.Z == pytest.approx(P.enc_h)


def test_chain_passes_through_cap_seam_without_threading(enclosure_parts):
    """Both cap halves can approach the installed chain from opposite
    sides of its Y plane; neither encloses a strand in a closed hole."""
    from blinds_cad.params import P

    rear = enclosure_parts["cap-rear"]
    front = enclosure_parts["cap-front"]
    for x in P.strand_x:
        gauge = Pos(x, P.spr_wy, P.enc_h - 3) * Cylinder(
            P.chain_slot / 2, 6
        )
        assert (rear & gauge).volume < 1e-6
        assert (front & gauge).volume < 1e-6

    assert rear.bounding_box().max.Y <= P.spr_wy + P.cap_lap
    assert front.bounding_box().min.Y == pytest.approx(P.spr_wy)


def test_direct_wall_anchor_holes_are_open(enclosure_parts):
    from blinds_cad.params import P

    frame = enclosure_parts["frame"]
    for x, z in P.frame_wall_holes:
        gauge = Pos(x, P.frame_t / 2, z) * (
            Rot(90, 0, 0) * Cylinder(P.wall_screw_d / 2, P.frame_t + 2)
        )
        assert (frame & gauge).volume < 1e-6, (x, z)


def test_sprocket_axle_is_captive_without_trapping_the_sleeve(enclosure_parts):
    """The M5 axle screws into a wall-side captive nut. Its front head
    remains accessible through the sleeve, so removing the sleeve never
    releases the sprocket."""
    from blinds_cad.params import P

    frame = enclosure_parts["frame"]
    keeper = enclosure_parts["axle-keeper"]
    sleeve = enclosure_parts["sleeve"]

    head_depth = P.frame_front_y - P.axle_head_seat_y
    head = Pos(
        P.drive_x,
        P.axle_head_seat_y + head_depth / 2,
        P.spr_z,
    ) * (Rot(90, 0, 0) * Cylinder(P.axle_head_d / 2, head_depth + 0.2))
    assert (frame & head).volume < 1e-6
    assert (keeper & head).volume < 1e-6

    nut = Pos(
        P.drive_x,
        P.axle_nut_y0 + P.axle_nut_h / 2,
        P.spr_z,
    ) * (Rot(90, 0, 0) * Cylinder(P.axle_nut_af / 2, P.axle_nut_h))
    assert (frame & nut).volume < 1e-6
    bolt_tip_y = P.axle_head_seat_y - P.axle_bolt_len
    assert bolt_tip_y >= 0.0
    assert bolt_tip_y == pytest.approx(P.axle_nut_y0)
    assert P.axle_head_seat_y >= P.axle_nut_y0 + P.axle_nut_h

    passage = Pos(P.drive_x, P.enc_d - P.sleeve_t / 2, P.spr_z) * (
        Rot(90, 0, 0) * Cylinder(P.axle_head_clear_d / 2, P.sleeve_t + 2)
    )
    assert (sleeve & passage).volume < 1e-6


def test_parts_fit_the_p2s_in_their_documented_orientations(enclosure_parts):
    """P2S build volume is 256 mm cubed.  The frame prints wall-face
    down, keeper and sleeve front-face down, and cap halves top-face down."""
    frame = enclosure_parts["frame"].bounding_box()
    keeper = enclosure_parts["axle-keeper"].bounding_box()
    sleeve = enclosure_parts["sleeve"].bounding_box()
    rear = enclosure_parts["cap-rear"].bounding_box()
    front = enclosure_parts["cap-front"].bounding_box()

    assert frame.size.X <= 256 and frame.size.Z <= 256 and frame.size.Y <= 50
    assert keeper.size.X <= 256 and keeper.size.Z <= 256 and keeper.size.Y <= 10
    assert sleeve.size.X <= 256 and sleeve.size.Z <= 256 and sleeve.size.Y <= 50
    for cap in (rear, front):
        assert cap.size.X <= 256 and cap.size.Y <= 256 and cap.size.Z <= 10


def test_axle_keeper_screw_holes_have_closed_edge_ligaments():
    from blinds_cad.params import P

    radius = P.keeper_screw_d / 2
    x0 = P.drive_x - P.keeper_outer_half_w
    x1 = P.drive_x + P.keeper_outer_half_w
    for x in P.keeper_screw_x:
        assert min(x - radius - x0, x1 - x - radius) >= P.keeper_hole_ligament
    for z in P.keeper_screw_z:
        assert min(
            z - radius - P.keeper_z0,
            P.keeper_z1 - z - radius,
        ) >= P.keeper_hole_ligament


def test_frame_guides_sleeve_with_running_clearance(enclosure_parts):
    from blinds_cad.params import P

    frame = enclosure_parts["frame"].bounding_box()
    assert frame.min.X - P.sleeve_t == pytest.approx(P.sleeve_fit)
    assert P.enc_w - P.sleeve_t - frame.max.X == pytest.approx(P.sleeve_fit)
    assert P.enc_d - P.sleeve_t - frame.max.Y == pytest.approx(P.sleeve_fit)
