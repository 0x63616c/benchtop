"""Assembly and print contract for the removable blinds drive cassette."""

from math import sqrt

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
    assert bearing_bounds.min.X == pytest.approx(0)
    assert rod_bounds.min.X == pytest.approx(0)


def test_sprocket_uses_the_same_625zz_bearings_as_the_layshaft():
    from blinds_cad.drivecassette import drive_parts, sprocket_bearing_625zz
    from blinds_cad.params import P

    parts = drive_parts()
    bearing_bounds = sprocket_bearing_625zz().bounding_box()
    shaft_bounds = parts["sprocket-shaft"].bounding_box()

    assert P.spr_shaft_d == 5.0
    assert P.spr_bearing_d == P.lay_bearing_d == 16.0
    assert P.spr_bearing_w == P.lay_bearing_w == 5.0
    assert tuple(bearing_bounds.size) == pytest.approx((16.0, 5.0, 16.0))
    assert shaft_bounds.size.Y == pytest.approx(40.0)
    assert len(parts["chain-wheel"].solids()) == 1
    assert len(parts["sprocket-bevel"].solids()) == 1
    assert (parts["chain-wheel"] & parts["sprocket-bevel"]).volume < 1e-6
    assert (parts["chain-wheel"] & parts["layshaft-bevel"]).volume < 1e-6

    assert (
        parts["sprocket-bevel"].bounding_box().max.Y + P.spr_spacer_axial_clear
        == pytest.approx(parts["sprocket-spacer"].bounding_box().min.Y)
    )
    assert (
        parts["sprocket-spacer"].bounding_box().max.Y + P.spr_spacer_axial_clear
        == pytest.approx(parts["chain-wheel"].bounding_box().min.Y)
    )
    assert P.spr_spacer_axial_clear <= 0.1


def test_both_sprocket_625zz_bearings_fit_entirely_inside_the_pod():
    from blinds_cad.drivecassette import drive_parts

    parts = drive_parts()
    cassette = parts["drive-cassette"].bounding_box()
    lid = parts["cassette-lid"].bounding_box()
    shaft = parts["sprocket-shaft"].bounding_box()
    rear = parts["rear-sprocket-bearing"].bounding_box()
    front = parts["front-sprocket-bearing"].bounding_box()

    assert cassette.min.Y <= rear.min.Y < rear.max.Y <= cassette.max.Y
    assert lid.min.Y <= front.min.Y < front.max.Y <= lid.max.Y
    assert shaft.min.Y <= rear.min.Y
    assert shaft.max.Y == pytest.approx(front.max.Y)

    for bearing in ("rear-sprocket-bearing", "front-sprocket-bearing"):
        for moving in ("sprocket-bevel", "sprocket-spacer", "chain-wheel"):
            assert (parts[bearing] & parts[moving]).volume < 1e-6


def test_sprocket_bearing_bore_passes_through_floor_and_lid():
    from blinds_cad.drivecassette import _axis_y_cylinder, drive_parts
    from blinds_cad.params import P

    parts = drive_parts()
    bore = _axis_y_cylinder(
        (P.spr_bearing_d + P.spr_bearing_clear) / 2,
        P.drive_floor_y0 - 0.1,
        P.cassette_lid_y0
        + P.cassette_lid_web_t
        - P.drive_floor_y0
        + 0.2,
        P.drive_x,
        P.spr_z,
    )
    assert (parts["drive-cassette"] & bore).volume < 1e-6
    assert (parts["cassette-lid"] & bore).volume < 1e-6


def test_sprocket_bevel_backing_disc_does_not_fill_the_active_teeth():
    """The flat print face is a thin backing disc, not a tall cylindrical
    base that leaves a seam through the active bevel tooth form."""
    from blinds_cad.gears import bevel_ring
    from blinds_cad.params import P
    from blinds_cad.sprocket import sprocket_bevel

    gear = sprocket_bevel()
    raw = Rot(0, 0, P.bevel_ring_phase) * bevel_ring()
    trimmed_heel_z = raw.bounding_box().max.Z - P.spr_ring_heel_trim
    disc_z0 = trimmed_heel_z - P.spr_ring_back_overlap

    assert len(gear.solids()) == 1
    assert P.spr_ring_back_t <= 1.2
    assert P.spr_ring_back_overlap == P.spr_ring_back_t
    assert gear.bounding_box().max.Z == pytest.approx(trimmed_heel_z)
    assert P.spr_bevel_pin_z + P.spr_pin_guide_d / 2 < disc_z0


def test_complete_pod_hugs_the_real_hardware_envelope():
    from blinds_cad.drivecassette import drive_parts

    parts = drive_parts()
    mins = tuple(
        min(getattr(part.bounding_box().min, axis) for part in parts.values())
        for axis in "XYZ"
    )
    maxs = tuple(
        max(getattr(part.bounding_box().max, axis) for part in parts.values())
        for axis in "XYZ"
    )
    size = tuple(maximum - minimum for minimum, maximum in zip(mins, maxs))

    assert size[0] <= 90.0
    assert size[1] <= 42.5
    assert size[2] <= 87.0


def test_chain_channels_have_at_least_1_5mm_clearance_per_side():
    from blinds_cad.params import P

    minimum_opening = P.chain_ball_d + 3.0
    assert P.spr_ball_clear >= 1.5
    assert P.chain_slot >= minimum_opening


def test_layshaft_tunnel_is_open_to_room_side_without_a_triangular_roof():
    from splitflap_cad.geo import box_between

    from blinds_cad.drivecassette import _layshaft_tunnel
    from blinds_cad.params import P

    radius = P.bevel_r + P.cassette_layshaft_radial_clear
    open_front = box_between(
        P.drive_x - P.cassette_layshaft_tunnel_l / 2,
        P.drive_y,
        P.spr_z - radius,
        P.drive_x + P.cassette_layshaft_tunnel_l / 2,
        P.frame_front_y + 1,
        P.spr_z + radius,
    )

    assert (open_front - _layshaft_tunnel()).volume < 1e-6


def test_lid_screws_cover_the_grid_and_outer_corners():
    from blinds_cad.drivecassette import (
        _axis_y_cylinder,
        drive_cassette,
    )
    from blinds_cad.params import P

    cassette = drive_cassette()
    grid = {
        (x, z)
        for x in (29.0, 69.0, 90.0)
        for z in (205.0, 236.5)
    }
    corners = {
        (12.0, 158.0),
        (90.0, 158.0),
        (12.0, 236.5),
        (90.0, 236.5),
    }
    assert set(P.cassette_lid_screw_points) == grid | corners
    column_length = P.cassette_lid_seat_y - P.drive_cassette_back_y
    for x, z in P.cassette_lid_screw_points:
        outer = _axis_y_cylinder(
            P.cassette_lid_boss_d / 2,
            P.drive_cassette_back_y,
            column_length,
            x,
            z,
        )
        insert = _axis_y_cylinder(
            P.cassette_lid_insert_d / 2,
            P.cassette_lid_seat_y - P.cassette_lid_insert_depth,
            P.cassette_lid_insert_depth + 0.1,
            x,
            z,
        )
        printable_column = outer - insert

        assert (cassette & printable_column).volume >= 0.98 * printable_column.volume


def test_lid_columns_clear_chain_and_rotating_hardware():
    from blinds_cad.drivecassette import _axis_y_cylinder, drive_parts
    from blinds_cad.params import P

    parts = drive_parts()
    rotating = (
        "chain-wheel", "sprocket-bevel", "layshaft-bevel",
        "layshaft-spur", "pinion",
    )
    for x, z in P.cassette_lid_screw_points:
        column = _axis_y_cylinder(
            P.cassette_lid_boss_d / 2,
            P.drive_cassette_back_y,
            P.cassette_lid_seat_y - P.drive_cassette_back_y,
            x,
            z,
        )
        for name in rotating:
            assert (column & parts[name]).volume < 1e-6, (x, z, name)


def test_lid_columns_clear_both_vertical_chain_runs():
    from blinds_cad.params import P

    boss_r = P.cassette_lid_boss_d / 2
    chain_r = P.chain_ball_d / 2 + P.spr_ball_clear
    chain_z0 = P.spr_z - 1
    for x, z in P.cassette_lid_screw_points:
        below_chain_run = z + boss_r <= chain_z0
        for strand_x in P.strand_x:
            beside_chain_run = (
                x + boss_r <= strand_x - chain_r
                or x - boss_r >= strand_x + chain_r
            )
            assert below_chain_run or beside_chain_run, (x, z, strand_x)


def test_drive_cassette_is_removable_and_two_mounts_plus_key_are_supported():
    from blinds_cad.drivecassette import cassette_lid, drive_cassette
    from blinds_cad.enclosure import frame
    from blinds_cad.params import P

    structure = frame()
    cassette = drive_cassette()
    lid = cassette_lid()

    assert len(structure.solids()) == 1
    assert len(cassette.solids()) == 1
    assert len(lid.solids()) == 1
    assert (structure & cassette).volume < 1e-6
    assert (cassette & lid).volume < 1e-6
    assert len(P.drive_mount_points) == 2

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


def test_frame_shelf_and_upper_key_are_real_load_bearing_datums():
    from splitflap_cad.geo import box_between

    from blinds_cad.drivecassette import drive_cassette
    from blinds_cad.enclosure import frame
    from blinds_cad.params import P

    structure = frame()
    cassette = drive_cassette()
    shelf = box_between(
        P.cradle_x0,
        0,
        P.drive_shelf_z0,
        P.saddle_x1,
        P.drive_mount_face_y,
        P.drive_shelf_z1,
    )
    key = box_between(
        P.drive_key_x - P.drive_key_w / 2,
        0,
        P.drive_key_z - P.drive_key_h / 2,
        P.drive_key_x + P.drive_key_w / 2,
        P.drive_key_y1,
        P.drive_key_z + P.drive_key_h / 2,
    )

    seated_shelf = shelf - cassette
    assert seated_shelf.volume >= 0.20 * shelf.volume
    assert (cassette & shelf).volume >= 0.70 * shelf.volume
    assert (structure & seated_shelf).volume >= 0.99 * seated_shelf.volume
    assert ((structure + cassette) & shelf).volume >= 0.99 * shelf.volume
    assert (structure & key).volume >= 0.99 * key.volume
    assert P.drive_lower_z0 == pytest.approx(P.drive_shelf_z1)
    assert (cassette & shelf).volume == pytest.approx(
        shelf.volume - seated_shelf.volume,
        abs=1e-6,
    )
    assert (cassette & key).volume < 1e-6


def test_bearing_shells_join_full_height_rectangular_spines():
    from splitflap_cad.geo import box_between

    from blinds_cad.drivecassette import (
        _bearing_lid_shell,
        _bearing_pocket,
        _bearing_shaft_cut,
        cassette_lid,
    )
    from blinds_cad.params import P

    lid = cassette_lid()
    for x in P.lay_bearing_centers_x:
        bridge = box_between(
            x - P.cassette_lid_spine_w / 2,
            P.lay_cap_y1 - P.cassette_lid_shell_embed,
            P.lay_z - P.lay_bearing_boss_d / 2,
            x + P.cassette_lid_spine_w / 2,
            P.cassette_lid_y0 + 0.1,
            P.lay_z + P.lay_bearing_boss_d / 2,
        )
        shell = _bearing_lid_shell(x)
        cuts = _bearing_pocket(x) + _bearing_shaft_cut(x)
        assert P.cassette_lid_shell_embed >= 3.0
        assert (shell & bridge).volume >= 30.0
        assert (lid & cuts).volume < 1e-6


def test_lid_web_is_a_solid_rectangle():
    from splitflap_cad.geo import box_between

    from blinds_cad.drivecassette import (
        _axis_y_cylinder,
        _cassette_lid_web,
        _posed_gears,
    )
    from blinds_cad.params import P

    web = _cassette_lid_web()
    floor_depth = (
        P.drive_cassette_back_y
        + P.drive_cassette_back_web_t
        - P.drive_floor_y0
    )
    assert P.cassette_lid_web_t + P.cassette_lid_rear_t == pytest.approx(
        floor_depth
    )
    rectangle = box_between(
        P.cassette_lid_x0,
        P.cassette_lid_y0,
        P.cassette_lid_z0,
        P.cassette_lid_x1,
        P.cassette_lid_y0 + P.cassette_lid_web_t,
        P.cassette_lid_z1,
    )
    bearing_opening = _axis_y_cylinder(
        (P.spr_bearing_d + P.spr_bearing_clear) / 2,
        P.cassette_lid_seat_y - 0.1,
        P.cassette_lid_web_t + P.cassette_lid_rear_t + 0.2,
        P.drive_x,
        P.spr_z,
    )
    spur = _posed_gears()["layshaft-spur"].bounding_box()
    clear = P.cassette_spur_window_clear
    spur_window = box_between(
        spur.min.X - clear,
        P.cassette_lid_seat_y - 0.1,
        spur.min.Z - clear,
        spur.max.X + clear,
        P.cassette_lid_y0 + P.cassette_lid_web_t + 0.1,
        spur.max.Z + clear,
    )
    printable_rectangle = rectangle - bearing_opening - spur_window
    assert (web & printable_rectangle).volume >= 0.99 * printable_rectangle.volume


def test_cassette_has_a_full_depth_rectangular_floor():
    from splitflap_cad.geo import box_between

    from blinds_cad.drivecassette import (
        _layshaft_spur_window,
        _posed_gears,
        _posed_motor,
        _sprocket_shaft_cuts,
        drive_cassette,
    )
    from blinds_cad.params import P

    cassette = drive_cassette()
    rectangle = box_between(
        P.cassette_lid_x0,
        P.drive_floor_y0,
        P.drive_shelf_z0,
        P.cassette_lid_x1,
        P.drive_cassette_back_y + P.drive_cassette_back_web_t,
        P.cassette_lid_z1,
    )
    clear = P.drive_floor_pocket_clear
    openings = _sprocket_shaft_cuts()
    openings += _layshaft_spur_window(
        P.drive_floor_y0 - 0.1,
        P.frame_front_y + 0.1,
    )
    motor = _posed_motor().bounding_box()
    pinion = _posed_gears()["pinion"].bounding_box()
    floor_y1 = P.drive_cassette_back_y + P.drive_cassette_back_web_t
    openings += box_between(
        motor.min.X - clear,
        P.drive_floor_y0 - 0.1,
        motor.min.Z - clear,
        P.bulkhead_x + clear,
        floor_y1 + 0.1,
        motor.max.Z + clear,
    )
    openings += box_between(
        pinion.min.X - clear,
        P.drive_floor_y0 - 0.1,
        pinion.min.Z - clear,
        pinion.max.X + clear,
        floor_y1 + 0.1,
        pinion.max.Z + clear,
    )
    for x, _y, z in P.drive_mount_points:
        openings += box_between(
            x - P.drive_mount_boss_d / 2 - P.drive_cassette_fit,
            0,
            z - P.drive_mount_boss_d / 2 - P.drive_cassette_fit,
            x + P.drive_mount_boss_d / 2 + P.drive_cassette_fit,
            P.drive_tab_y0,
            z + P.drive_mount_boss_d / 2 + P.drive_cassette_fit,
        )
    openings += box_between(
        P.drive_key_x - P.drive_key_w / 2 - P.drive_cassette_fit,
        0,
        P.drive_key_z - P.drive_key_h / 2 - P.drive_cassette_fit,
        P.drive_key_x + P.drive_key_w / 2 + P.drive_cassette_fit,
        P.drive_key_y1 + P.drive_cassette_fit,
        P.drive_key_z + P.drive_key_h / 2 + P.drive_cassette_fit,
    )
    printable_floor = rectangle - openings
    assert (cassette & printable_floor).volume >= 0.99 * printable_floor.volume


def test_spur_gear_has_a_clear_window_through_the_lid():
    from splitflap_cad.geo import box_between

    from blinds_cad.drivecassette import cassette_lid, drive_parts
    from blinds_cad.params import P

    spur = drive_parts()["layshaft-spur"]
    bounds = spur.bounding_box()
    clear = P.cassette_spur_window_clear
    window = box_between(
        bounds.min.X - clear,
        P.cassette_lid_seat_y - 0.1,
        bounds.min.Z - clear,
        bounds.max.X + clear,
        P.cassette_lid_y0 + P.cassette_lid_web_t + 0.1,
        bounds.max.Z + clear,
    )

    assert P.spur_pinion_z == 14 and P.spur_wheel_z == 17
    assert P.lay_z - P.motor_z == pytest.approx(
        P.spur_pinion_r + P.spur_wheel_r
    )
    assert clear >= P.drive_running_gap
    assert (cassette_lid() & window).volume < 1e-6
    assert (cassette_lid() & spur).volume < 1e-6


def test_lid_m3_clearance_holes_and_body_insert_pockets_match_all_bosses():
    from blinds_cad.drivecassette import (
        _axis_y_cylinder,
        cassette_lid,
        drive_cassette,
    )
    from blinds_cad.params import P

    lid = cassette_lid()
    cassette = drive_cassette()
    assert P.cassette_lid_screw_d == 3.4
    assert P.cassette_lid_insert_d == 4.2
    assert P.cassette_lid_insert_depth == 9.6

    for x, z in P.cassette_lid_screw_points:
        clearance = _axis_y_cylinder(
            P.cassette_lid_screw_d / 2,
            P.cassette_lid_seat_y - 0.1,
            P.frame_front_y - P.cassette_lid_seat_y + 0.2,
            x,
            z,
        )
        insert = _axis_y_cylinder(
            P.cassette_lid_insert_d / 2,
            P.cassette_lid_seat_y - P.cassette_lid_insert_depth,
            P.cassette_lid_insert_depth + 0.1,
            x,
            z,
        )
        assert (lid & clearance).volume < 1e-6
        assert (cassette & insert).volume < 1e-6


def test_both_split_seats_use_the_same_625zz_pocket():
    from blinds_cad.drivecassette import _bearing_pocket, cassette_lid, drive_cassette
    from blinds_cad.params import P

    lid = cassette_lid()
    cassette = drive_cassette()
    axial_wall = (P.lay_bearing_boss_w - P.lay_bearing_pocket_w) / 2
    assert axial_wall == pytest.approx(0.8)
    for x in P.lay_bearing_centers_x:
        pocket = _bearing_pocket(x)
        bounds = pocket.bounding_box()
        assert tuple(bounds.size) == pytest.approx(
            (
                P.lay_bearing_w + P.lay_bearing_clear,
                P.lay_bearing_d + P.lay_bearing_clear,
                P.lay_bearing_d + P.lay_bearing_clear,
            )
        )
        assert (cassette & pocket).volume < 1e-6
        assert (lid & pocket).volume < 1e-6


def test_single_lid_has_an_open_roomward_installation_path():
    from build123d import Pos

    from blinds_cad.drivecassette import cassette_lid, drive_cassette

    lid = cassette_lid()
    cassette = drive_cassette()
    for roomward_step in range(0, 15, 2):
        assert ((Pos(0, roomward_step, 0) * lid) & cassette).volume < 1e-6


def test_motor_mount_has_loose_m3_bores_and_one_lower_tool_access():
    from blinds_cad.drivecassette import (
        _axis_x_cylinder,
        _motor_screw_centers,
        drive_cassette,
        drive_parts,
    )
    from blinds_cad.params import P

    cassette = drive_cassette()
    centers = _motor_screw_centers()
    assert P.jgb_screw_clear_d >= 3.5
    assert P.jgb_tool_access_d == 8.0
    assert len(centers) == P.jgb_screw_n

    for y, z in centers:
        screw = _axis_x_cylinder(
            P.jgb_screw_clear_d / 2,
            P.bulkhead_x - 0.1,
            P.bulkhead_t + 0.2,
            y,
            z,
        )
        assert (cassette & screw).volume < 1e-6

    access_y, access_z = centers[P.jgb_tool_access_index]
    tool = _axis_x_cylinder(
        P.jgb_tool_access_d / 2,
        P.bulkhead_x + P.bulkhead_t,
        P.saddle_x1 - P.bulkhead_x - P.bulkhead_t + 0.2,
        access_y,
        access_z,
    )
    assert (cassette & tool).volume < 1e-6
    parts = drive_parts()
    assert (parts["pinion"] & tool).volume < 1e-6
    assert (parts["layshaft-spur"] & tool).volume < 1e-6


@pytest.mark.slow
def test_complete_drive_with_lid_and_sprocket_withdraws_straight_out():
    """The complete closed cassette withdraws straight toward the room."""
    from build123d import Pos

    from blinds_cad.drivecassette import drive_parts
    from blinds_cad.enclosure import frame
    from blinds_cad.params import P

    moving = drive_parts()
    withdraw_steps = int(P.enc_d / P.drive_removal_step)
    path = [
        Pos(0, index * P.drive_removal_step, 0)
        for index in range(withdraw_steps + 1)
    ]

    structure = frame()
    for pose in path:
        for name, part in moving.items():
            assert ((pose * part) & structure).volume < 1e-6, (pose, name)


@pytest.mark.parametrize(
    "gear",
    [
        pytest.param("pinion_print", id="motor-spur-pinion"),
        pytest.param("spur_gear_print", id="layshaft-spur"),
        pytest.param("bevel_gear_print", id="layshaft-bevel"),
    ],
)
def test_each_gear_is_a_separate_heel_or_face_down_print(gear):
    from blinds_cad import gears

    part = getattr(gears, gear)()
    bounds = part.bounding_box()
    bed_faces = [
        face
        for face in part.faces()
        if face.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
        and face.bounding_box().max.Z == pytest.approx(0, abs=1e-6)
        and face.normal_at().Z < -0.99
    ]

    assert len(part.solids()) == 1
    assert bounds.min.Z == pytest.approx(0, abs=1e-6)
    assert bed_faces

    vertices, triangles = part.tessellate(0.1, 0.1)
    unsupported = []
    for a, b, c in triangles:
        p0, p1, p2 = vertices[a], vertices[b], vertices[c]
        ux, uy, uz = p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z
        vx, vy, vz = p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        magnitude = sqrt(nx * nx + ny * ny + nz * nz)
        normal_z = nz / magnitude if magnitude else 0
        if normal_z < -0.71 and min(p0.Z, p1.Z, p2.Z) > 1e-4:
            unsupported.extend((p0, p1, p2))

    # Only the tiny cross-pin/grub-screw guide bridge may point down;
    # all tooth and rim surfaces stay inside the 55-degree envelope.
    assert max(
        (sqrt(vertex.X * vertex.X + vertex.Y * vertex.Y) for vertex in unsupported),
        default=0,
    ) <= 7.1


def test_spacers_and_single_lid_positively_locate_the_rod_stack():
    from blinds_cad.drivecassette import scene
    from blinds_cad.params import P

    args = scene().show_args()
    parts = dict(zip(args["names"], args["objects"]))
    required = {
        "drive-cassette",
        "cassette-lid",
        "chain-wheel",
        "sprocket-bevel",
        "sprocket-spacer",
        "rear-sprocket-bearing",
        "front-sprocket-bearing",
        "sprocket-shaft",
        "motor",
        "pinion",
        "motor-spacer",
        "layshaft-bevel",
        "bevel-spacer",
        "left-bearing",
        "inner-spacer",
        "layshaft-spur",
        "outer-spacer",
        "right-bearing",
        "layshaft-rod",
    }
    assert set(parts) == required

    assert (
        parts["motor-spacer"].bounding_box().max.X
        + P.drive_running_gap
        == pytest.approx(parts["pinion"].bounding_box().min.X)
    )
    assert (
        parts["layshaft-bevel"].bounding_box().max.X
        + P.drive_running_gap
        == pytest.approx(parts["bevel-spacer"].bounding_box().min.X)
    )
    assert parts["bevel-spacer"].bounding_box().max.X == pytest.approx(
        parts["left-bearing"].bounding_box().min.X
    )
    assert parts["left-bearing"].bounding_box().max.X == pytest.approx(
        parts["inner-spacer"].bounding_box().min.X
    )
    assert (
        parts["inner-spacer"].bounding_box().max.X
        + P.drive_running_gap
        == pytest.approx(parts["layshaft-spur"].bounding_box().min.X)
    )
    assert (
        parts["layshaft-spur"].bounding_box().max.X
        + P.drive_running_gap
        == pytest.approx(parts["outer-spacer"].bounding_box().min.X)
    )
    assert parts["outer-spacer"].bounding_box().max.X == pytest.approx(
        parts["right-bearing"].bounding_box().min.X
    )

    for name in required - {
        "layshaft-rod",
        "motor",
        "drive-cassette",
        "cassette-lid",
        "chain-wheel",
        "sprocket-bevel",
        "sprocket-spacer",
        "rear-sprocket-bearing",
        "front-sprocket-bearing",
        "sprocket-shaft",
    }:
        if name == "motor-spacer" or name == "pinion":
            continue
        assert (parts["layshaft-rod"] & parts[name]).volume < 1e-6, name
