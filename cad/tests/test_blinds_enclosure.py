"""Public assembly contract for the printable blinds enclosure system.

The wall frame and removable drive cassette are structural. The sleeve and
two cap halves are cosmetic, removable parts. These tests observe only the
exported solids and their assembled locations, so the construction can
change without weakening the contract.
"""

import pytest
from build123d import Cylinder, Pos, Rot


@pytest.fixture(scope="module")
def enclosure_parts():
    from blinds_cad.cover import cap_front, cap_rear, sleeve
    from blinds_cad.drivecassette import cassette_lid, drive_cassette
    from blinds_cad.enclosure import frame

    return {
        "frame": frame(),
        "drive-cassette": drive_cassette(),
        "cassette-lid": cassette_lid(),
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


def test_cassette_lid_seats_without_overlapping_drive_cassette(enclosure_parts):
    overlap = (
        enclosure_parts["drive-cassette"] & enclosure_parts["cassette-lid"]
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


def test_wall_anchors_do_not_cut_through_battery_mount():
    from blinds_cad import enclosure as e
    from blinds_cad.params import P

    battery_mount = e._battery_mount_spine()
    for x, z in P.frame_wall_holes:
        gauge = Pos(x, P.frame_t / 2, z) * (
            Rot(90, 0, 0) * Cylinder(P.wall_screw_d / 2, P.frame_t + 2)
        )
        assert (battery_mount & gauge).volume < 1e-6, (x, z)


def test_sprocket_shaft_and_bearings_are_captive_inside_the_sleeve(
    enclosure_parts,
):
    """The smooth 5 mm shaft is captured by chassis and lid bearings.
    It stops behind the cosmetic sleeve, so the sleeve needs no axle hole."""
    from blinds_cad import frames as F
    from blinds_cad.drivecassette import sprocket_bearing_625zz, sprocket_shaft
    from blinds_cad.params import P

    cassette = enclosure_parts["drive-cassette"]
    lid = enclosure_parts["cassette-lid"]
    sleeve = enclosure_parts["sleeve"]
    shaft = F.SPROCKET_SHAFT_IN_UNIT * sprocket_shaft()
    rear = F.REAR_SPROCKET_BEARING_IN_UNIT * sprocket_bearing_625zz()
    front = F.FRONT_SPROCKET_BEARING_IN_UNIT * sprocket_bearing_625zz()

    assert shaft.bounding_box().min.Y <= rear.bounding_box().min.Y
    assert shaft.bounding_box().max.Y == pytest.approx(front.bounding_box().max.Y)
    assert shaft.bounding_box().max.Y < P.enc_d - P.sleeve_t
    for part in (shaft, rear, front):
        assert (cassette & part).volume < 1e-6
        assert (lid & part).volume < 1e-6
        assert (sleeve & part).volume < 1e-6


def test_parts_fit_the_p2s_in_their_documented_orientations(enclosure_parts):
    """P2S build volume is 256 mm cubed.  The frame prints wall-face
    down, cassette lid and sleeve front-face down, and cap halves top-face down."""
    frame = enclosure_parts["frame"].bounding_box()
    lid = enclosure_parts["cassette-lid"].bounding_box()
    sleeve = enclosure_parts["sleeve"].bounding_box()
    rear = enclosure_parts["cap-rear"].bounding_box()
    front = enclosure_parts["cap-front"].bounding_box()

    assert frame.size.X <= 256 and frame.size.Z <= 256 and frame.size.Y <= 50
    assert lid.size.X <= 256 and lid.size.Z <= 256 and lid.size.Y <= 35
    assert sleeve.size.X <= 256 and sleeve.size.Z <= 256 and sleeve.size.Y <= 50
    for cap in (rear, front):
        assert cap.size.X <= 256 and cap.size.Y <= 256 and cap.size.Z <= 10


def test_cassette_lid_screw_holes_have_closed_edge_ligaments():
    from blinds_cad.params import P

    radius = P.cassette_lid_screw_d / 2
    for x, z in P.cassette_lid_screw_points:
        assert min(
            x - radius - P.cassette_lid_x0,
            P.cassette_lid_x1 - x - radius,
        ) >= P.cassette_lid_hole_ligament
        assert min(
            z - radius - P.cassette_lid_z0,
            P.cassette_lid_z1 - z - radius,
        ) >= P.cassette_lid_hole_ligament


def test_frame_guides_sleeve_with_running_clearance(enclosure_parts):
    from blinds_cad.params import P

    frame = enclosure_parts["frame"].bounding_box()
    assert frame.min.X - P.sleeve_t == pytest.approx(P.sleeve_fit)
    assert P.enc_w - P.sleeve_t - frame.max.X == pytest.approx(P.sleeve_fit)
    assert P.enc_d - P.sleeve_t - frame.max.Y == pytest.approx(P.sleeve_fit)


def test_sleeve_retainer_blocks_start_on_the_tray_not_below_it():
    from blinds_cad import enclosure as e
    from blinds_cad.params import P

    bounds = e._sleeve_retainers().bounding_box()
    assert bounds.min.Y == pytest.approx(0)
    assert bounds.min.Z == pytest.approx(P.frame_tray_z0)


def test_projecting_features_have_structural_root_overlap():
    """Projecting features need a volumetric joint, not coincident faces.

    The first exoskeleton iteration was technically one OCC solid while
    several bosses and guides only kissed a rail, and both upper drive
    structures hung almost entirely from the top rail.  These minimums
    guard the intended load paths into the wall-side backbone.
    """
    from blinds_cad import enclosure as e

    backbone = e._backbone()
    rooted = {
        "pcb-tray": (e._pcb_tray(), 600.0),
        "battery-mount-spine": (e._battery_mount_spine(), 390.0),
        "drive-mounts": (e._drive_mounts(), 100.0),
        "sleeve-guides": (e._sleeve_guides(), 300.0),
        "sleeve-retainers": (e._sleeve_retainers(), 190.0),
    }
    for name, (feature, minimum) in rooted.items():
        overlap = (feature & backbone).volume
        assert overlap >= minimum, f"{name}: only {overlap:.1f} mm3 rooted"
