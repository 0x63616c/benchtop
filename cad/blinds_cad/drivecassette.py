"""Tight, self-contained motor/gear/sprocket cassette.

The chassis carries every fixed drive feature and slides onto a keyed frame
shelf.  One structural room-side lid closes both split 625ZZ seats, retains
the sprocket shaft, and ties the mechanism together with four M3 screws.
Only two lower screws attach the complete pod to the wall frame.
"""

import math
from functools import lru_cache

from build123d import (
    Align,
    Box,
    Cylinder,
    Pos,
    Rot,
    Torus,
)
from splitflap_cad.geo import box_between, support_free_cross_bore

from .params import P


def _cylinder(radius: float, height: float):
    """Axis +Z cylinder beginning at z=0."""
    return Cylinder(
        radius,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def _axis_x_cylinder(radius: float, x0: float, length: float, y: float, z: float):
    return Pos(x0, y, z) * Rot(0, 90, 0) * _cylinder(radius, length)


def _axis_y_cylinder(radius: float, y0: float, length: float, x: float, z: float):
    return Pos(x, y0, z) * Rot(-90, 0, 0) * _cylinder(radius, length)


def bearing_625zz():
    """Display-only 625ZZ envelope, local axis +X from x=0..5."""
    outer = _axis_x_cylinder(P.lay_bearing_d / 2, 0, P.lay_bearing_w, 0, 0)
    bore = _axis_x_cylinder(P.lay_rod_d / 2, -0.5, P.lay_bearing_w + 1, 0, 0)
    return outer - bore


def sprocket_bearing_mr105():
    """Display-only MR105ZZ envelope, local axis +Y from y=0..4."""
    outer = _axis_y_cylinder(P.spr_bearing_d / 2, 0, P.spr_bearing_w, 0, 0)
    bore = _axis_y_cylinder(
        P.spr_shaft_d / 2,
        -0.5,
        P.spr_bearing_w + 1,
        0,
        0,
    )
    return outer - bore


def sprocket_shaft():
    """Bought smooth 5 mm shaft, local +Y from y=0."""
    return _axis_y_cylinder(P.spr_shaft_d / 2, 0, P.spr_shaft_len, 0, 0)


def _lid_insert_columns():
    """Three back-rooted columns that make the single lid structural."""
    bosses = None
    length = P.cassette_lid_y0 - P.drive_cassette_back_y
    for x, z in P.cassette_lid_screw_points:
        boss = _axis_y_cylinder(
            P.cassette_lid_boss_d / 2,
            P.drive_cassette_back_y,
            length,
            x,
            z,
        )
        bosses = boss if bosses is None else bosses + boss
    return bosses


def _lid_insert_cuts():
    cuts = None
    for x, z in P.cassette_lid_screw_points:
        cut = _axis_y_cylinder(
            P.cassette_lid_insert_d / 2,
            P.cassette_lid_y0 - P.cassette_lid_insert_depth,
            P.cassette_lid_insert_depth + 0.1,
            x,
            z,
        )
        cuts = cut if cuts is None else cuts + cut
    return cuts


def _sprocket_shaft_cuts():
    """Smooth-shaft bore plus the rear MR105 bearing seat."""
    cuts = _axis_y_cylinder(
        (P.spr_shaft_d + P.spr_shaft_clear) / 2,
        P.spr_shaft_y0 - 0.5,
        P.spr_shaft_len + 1,
        P.drive_x,
        P.spr_z,
    )
    bearing_y0 = P.spr_bearing_centers_y[0] - P.spr_bearing_w / 2
    cuts += _axis_y_cylinder(
        (P.spr_bearing_d + P.spr_bearing_clear) / 2,
        bearing_y0,
        P.spr_bearing_w + 0.2,
        P.drive_x,
        P.spr_z,
    )
    return cuts


def _layshaft_tunnel():
    """Round gear envelope open toward the room/print-growth side."""
    radius = P.bevel_r + P.cassette_layshaft_radial_clear
    x0 = P.drive_x - P.cassette_layshaft_tunnel_l / 2
    tunnel = _axis_x_cylinder(
        radius,
        x0,
        P.cassette_layshaft_tunnel_l,
        P.drive_y,
        P.spr_z,
    )
    tunnel += box_between(
        x0,
        P.drive_y,
        P.spr_z - radius,
        x0 + P.cassette_layshaft_tunnel_l,
        P.frame_front_y + 1,
        P.spr_z + radius,
    )
    return tunnel


def sprocket_housing():
    """Cassette-owned chain-wrap, bevel, shaft, and bearing housing."""
    cx, cz, wy = P.drive_x, P.spr_z, P.spr_wy
    r_ball = P.chain_ball_d / 2 + P.spr_ball_clear
    wheel_y0 = P.spr_wy - P.spr_w / 2 - P.cassette_wheel_axial_clear
    wheel_y1 = P.frame_front_y + 0.1
    block = box_between(
        cx - P.cassette_half_w,
        P.drive_cassette_back_y,
        cz - P.guide_or,
        cx + P.cassette_half_w,
        P.frame_front_y,
        P.sleeve_h - P.sleeve_fit,
    )
    block -= Pos(cx, (wheel_y0 + wheel_y1) / 2, cz) * (
        Rot(90, 0, 0)
        * Cylinder(
            P.spr_od / 2 + P.cassette_wheel_radial_clear,
            wheel_y1 - wheel_y0,
        )
    )
    ring_y0 = (
        _posed_sprocket_parts()["sprocket-bevel"].bounding_box().min.Y - 0.5
    )
    ring_len = wheel_y0 - ring_y0
    block -= Pos(cx, (wheel_y0 + ring_y0) / 2, cz) * (
        Rot(90, 0, 0)
        * Cylinder(P.bevel_r + P.cassette_ring_radial_clear, ring_len)
    )
    block -= _layshaft_tunnel()
    block -= Pos(cx, wy, cz) * (Rot(90, 0, 0) * Torus(P.spr_pcd / 2, r_ball))
    for x in P.strand_x:
        block -= box_between(
            x - r_ball,
            wy - r_ball,
            cz - 1,
            x + r_ball,
            wy + r_ball,
            P.enc_h + 1,
        )
    return block


def layshaft_rod():
    """Bought 5 mm steel rod, local axis +X from x=0."""
    return _axis_x_cylinder(
        P.lay_rod_d / 2,
        0,
        P.lay_rod_x1 - P.lay_rod_x0,
        0,
        0,
    )


def _axis_x_tube(outer_d: float, bore_d: float, length: float):
    if length <= 0:
        raise ValueError(f"non-positive spacer length: {length}")
    tube = _axis_x_cylinder(outer_d / 2, 0, length, 0, 0)
    tube -= _axis_x_cylinder(bore_d / 2, -0.5, length + 1, 0, 0)
    return tube


def _axis_y_tube(outer_d: float, bore_d: float, length: float):
    if length <= 0:
        raise ValueError(f"non-positive spacer length: {length}")
    tube = _axis_y_cylinder(outer_d / 2, 0, length, 0, 0)
    tube -= _axis_y_cylinder(bore_d / 2, -0.5, length + 1, 0, 0)
    return tube


def _posed_gears():
    from . import frames as F
    from .gears import bevel_gear, pinion, spur_gear

    return {
        "pinion": F.PINION_IN_UNIT * pinion(),
        "layshaft-bevel": F.LAYSHAFT_IN_UNIT * bevel_gear(),
        "layshaft-spur": F.SPUR_IN_UNIT * spur_gear(),
    }


@lru_cache(maxsize=1)
def _posed_sprocket_parts():
    from . import frames as F
    from .sprocket import chain_wheel, sprocket_bevel

    return {
        "chain-wheel": F.SPROCKET_WHEEL_IN_UNIT * chain_wheel(),
        "sprocket-bevel": F.SPROCKET_BEVEL_IN_UNIT * sprocket_bevel(),
    }


@lru_cache(maxsize=1)
def _spacer_starts():
    """Unit-X starts for local spacer parts; lengths come from adjacent faces."""
    gears = _posed_gears()
    return {
        "motor": P.bulkhead_x + P.jgb_boss_h,
        "bevel": gears["layshaft-bevel"].bounding_box().max.X
        + P.drive_running_gap,
        "inner": P.lay_bearing_centers_x[0] + P.lay_bearing_w / 2,
        "outer": gears["layshaft-spur"].bounding_box().max.X
        + P.drive_running_gap,
    }


def motor_spacer():
    """Local motor-boss-to-pinion spacer, axis +X from x=0."""
    pinion_min = _posed_gears()["pinion"].bounding_box().min.X
    x0 = _spacer_starts()["motor"]
    x1 = pinion_min - P.drive_running_gap
    length = x1 - x0
    return _axis_x_tube(P.motor_spacer_d, P.motor_spacer_bore_d, length)


def bevel_spacer():
    x0 = _spacer_starts()["bevel"]
    bearing_min = P.lay_bearing_centers_x[0] - P.lay_bearing_w / 2
    return _axis_x_tube(
        P.lay_spacer_d,
        P.lay_rod_d + P.lay_rod_clear,
        bearing_min - x0,
    )


def inner_spacer():
    x0 = _spacer_starts()["inner"]
    gear_min = _posed_gears()["layshaft-spur"].bounding_box().min.X
    return _axis_x_tube(
        P.lay_spacer_d,
        P.lay_rod_d + P.lay_rod_clear,
        gear_min - P.drive_running_gap - x0,
    )


def outer_spacer():
    x0 = _spacer_starts()["outer"]
    bearing_min = P.lay_bearing_centers_x[1] - P.lay_bearing_w / 2
    return _axis_x_tube(
        P.lay_spacer_d,
        P.lay_rod_d + P.lay_rod_clear,
        bearing_min - x0,
    )


@lru_cache(maxsize=1)
def _sprocket_spacer_start():
    bevel = _posed_sprocket_parts()["sprocket-bevel"]
    return bevel.bounding_box().max.Y + P.spr_spacer_axial_clear


def sprocket_spacer():
    """Axially separates the bevel and chain wheel on the 5 mm shaft."""
    wheel = _posed_sprocket_parts()["chain-wheel"]
    length = (
        wheel.bounding_box().min.Y
        - P.spr_spacer_axial_clear
        - _sprocket_spacer_start()
    )
    return _axis_y_tube(
        P.spr_spacer_d,
        P.spr_shaft_d + P.spr_shaft_clear,
        length,
    )


def _motor_screw_centers():
    """Six gearbox-face screw centres in the unit Y/Z plane."""
    gearbox_z = P.motor_z - P.jgb_ecc
    centers = []
    for index in range(P.jgb_screw_n):
        angle = math.radians(index * 360 / P.jgb_screw_n)
        radius = P.jgb_screw_bcd / 2
        centers.append(
            (
                P.drive_y + radius * math.cos(angle),
                gearbox_z + radius * math.sin(angle),
            )
        )
    return tuple(centers)


def _motor_bulkhead():
    """Cassette-owned motor face and left bearing support."""
    body = box_between(
        P.bulkhead_x,
        P.drive_cassette_back_y,
        P.drive_bulkhead_z0,
        P.bulkhead_x + P.bulkhead_t,
        P.frame_front_y,
        P.frame_z1,
    )
    body -= support_free_cross_bore(
        P.jgb_boss_d / 2 + 0.75,
        P.bulkhead_t + 2,
        P.bulkhead_x + P.bulkhead_t / 2,
        P.drive_y,
        P.motor_z,
    )
    for y, z in _motor_screw_centers():
        body -= support_free_cross_bore(
            P.jgb_screw_clear_d / 2,
            P.bulkhead_t + 2,
            P.bulkhead_x + P.bulkhead_t / 2,
            y,
            z,
        )
    # The lid's left split-bearing shell replaces this room-side slice.
    body -= box_between(
        P.lay_bearing_centers_x[0] - P.lay_bearing_boss_w / 2 - 0.2,
        P.drive_y,
        P.lay_z - P.lay_bearing_boss_d / 2 - 0.2,
        P.lay_bearing_centers_x[0] + P.lay_bearing_boss_w / 2 + 0.2,
        P.frame_front_y + 0.2,
        P.lay_z + P.lay_bearing_boss_d / 2 + 0.2,
    )
    return body


def _tail_cradle():
    """Motor-tail support rooted into the cassette's lower rail."""
    gearbox_z = P.motor_z - P.jgb_ecc
    body = box_between(
        P.cradle_x0,
        P.drive_cassette_back_y,
        P.drive_bulkhead_z0,
        P.cradle_x1,
        P.drive_y,
        gearbox_z,
    )
    body -= _axis_x_cylinder(
        P.jgb_gear_d / 2 + 0.35,
        P.cradle_x0 - 1,
        P.cradle_x1 - P.cradle_x0 + 2,
        P.drive_y,
        gearbox_z,
    )
    return body


def _rear_bearing_boss(x: float):
    full = _axis_x_cylinder(
        P.lay_bearing_boss_d / 2,
        x - P.lay_bearing_boss_w / 2,
        P.lay_bearing_boss_w,
        P.drive_y,
        P.lay_z,
    )
    rear_clip = box_between(
        x - P.lay_bearing_boss_w / 2 - 0.1,
        P.drive_cassette_back_y,
        P.lay_z - P.lay_bearing_boss_d / 2 - 0.1,
        x + P.lay_bearing_boss_w / 2 + 0.1,
        P.drive_y,
        P.lay_z + P.lay_bearing_boss_d / 2 + 0.1,
    )
    return full & rear_clip


def _bearing_pocket(x: float):
    return _axis_x_cylinder(
        (P.lay_bearing_d + P.lay_bearing_clear) / 2,
        x - P.lay_bearing_pocket_w / 2,
        P.lay_bearing_pocket_w,
        P.drive_y,
        P.lay_z,
    )


def _bearing_shaft_cut(x: float):
    return _axis_x_cylinder(
        (P.lay_spacer_d + P.lay_rod_clear) / 2,
        x - P.lay_bearing_boss_w / 2 - 0.5,
        P.lay_bearing_boss_w + 1,
        P.drive_y,
        P.lay_z,
    )


def _bearing_lid_shell(x: float):
    """Room-side half of one 625ZZ split seat, without separate ears."""
    full = _axis_x_cylinder(
        P.lay_bearing_boss_d / 2,
        x - P.lay_bearing_boss_w / 2,
        P.lay_bearing_boss_w,
        P.drive_y,
        P.lay_z,
    )
    front_clip = box_between(
        x - P.lay_bearing_boss_w / 2 - 0.1,
        P.drive_y,
        P.lay_z - P.lay_bearing_boss_d / 2 - 0.1,
        x + P.lay_bearing_boss_w / 2 + 0.1,
        P.lay_cap_y1,
        P.lay_z + P.lay_bearing_boss_d / 2 + 0.1,
    )
    cap = full & front_clip
    cap -= _bearing_pocket(x)
    cap -= _bearing_shaft_cut(x)
    return cap


def _cassette_lid_web():
    """Minimal front truss joining the sprocket seat and layshaft shells."""
    x0, x1 = P.cassette_lid_x0, P.cassette_lid_x1
    y0 = P.cassette_lid_y0
    y1 = y0 + P.cassette_lid_web_t
    z0, z1 = P.cassette_lid_z0, P.cassette_lid_z1
    rail = P.cassette_lid_rail

    # Bottom rail is the common load path.  Three narrow uprights retain the
    # sprocket bearing and reach the two split layshaft seats.
    web = box_between(x0, y0, z0, x1, y1, z0 + rail)
    web += box_between(x0, y0, z0, x0 + rail, y1, z1)
    web += box_between(
        P.drive_x - P.cassette_lid_spine_w / 2,
        y0,
        z0,
        P.drive_x + P.cassette_lid_spine_w / 2,
        y1,
        P.spr_z,
    )
    for x in P.lay_bearing_centers_x:
        web += box_between(
            x - P.cassette_lid_spine_w / 2,
            y0,
            z0,
            x + P.cassette_lid_spine_w / 2,
            y1,
            z1,
        )

    # Full-depth boss around the front MR105 bearing.  It is tied into the
    # center upright but leaves the bearing and shaft completely clear.
    bearing_y0 = P.spr_bearing_centers_y[1] - P.spr_bearing_w / 2
    web += _axis_y_cylinder(
        P.spr_bearing_d / 2 + P.cassette_lid_sprocket_boss_wall,
        bearing_y0 - 0.2,
        P.frame_front_y - bearing_y0 + 0.2,
        P.drive_x,
        P.spr_z,
    )
    web -= _axis_y_cylinder(
        (P.spr_bearing_d + P.spr_bearing_clear) / 2,
        bearing_y0 - 0.3,
        P.spr_bearing_w + 0.6,
        P.drive_x,
        P.spr_z,
    )
    web -= _axis_y_cylinder(
        (P.spr_shaft_d + P.spr_shaft_clear) / 2,
        bearing_y0 + P.spr_bearing_w - 0.1,
        P.frame_front_y - bearing_y0 - P.spr_bearing_w + 0.3,
        P.drive_x,
        P.spr_z,
    )

    # The chain leaves vertically; do not bridge across either live strand.
    chain_r = P.chain_ball_d / 2 + P.spr_ball_clear
    for x in P.strand_x:
        web -= box_between(
            x - chain_r,
            bearing_y0 - 0.5,
            P.spr_z - 1,
            x + chain_r,
            P.frame_front_y + 0.5,
            z1 + 1,
        )
    return web


def cassette_lid():
    """One removable lid retaining every shaft and bearing in the pod."""
    lid = _cassette_lid_web()
    for x in P.lay_bearing_centers_x:
        lid += _bearing_lid_shell(x)
        lid += box_between(
            x - P.cassette_lid_spine_w / 2,
            P.lay_cap_y1 - 0.2,
            P.lay_z - P.lay_bearing_boss_d / 2,
            x + P.cassette_lid_spine_w / 2,
            P.cassette_lid_y0 + 0.1,
            P.lay_z + P.lay_bearing_boss_d / 2,
        )

    for x, z in P.cassette_lid_screw_points:
        lid += _axis_y_cylinder(
            P.cassette_lid_boss_d / 2,
            P.cassette_lid_y0,
            P.cassette_lid_web_t,
            x,
            z,
        )
        lid -= _axis_y_cylinder(
            P.cassette_lid_screw_d / 2,
            P.cassette_lid_y0 - 0.1,
            P.cassette_lid_web_t + 0.2,
            x,
            z,
        )

    return lid


def drive_cassette():
    """One-piece stepped chassis containing the complete drive train."""
    body = box_between(
        P.cradle_x0,
        P.drive_cassette_back_y,
        P.drive_lower_z0,
        P.saddle_x1,
        P.drive_tab_y1,
        P.drive_lower_z1,
    )
    body += _motor_bulkhead()
    body += _tail_cradle()
    body += box_between(
        P.saddle_x0,
        P.drive_cassette_back_y,
        P.drive_lower_z0,
        P.saddle_x1,
        P.drive_y,
        P.cassette_lid_z1 - P.cassette_lid_boss_d / 2,
    )
    body += sprocket_housing()
    body += box_between(
        P.drive_x + P.cassette_half_w - P.drive_housing_bridge_overlap,
        P.drive_cassette_back_y,
        P.cassette_lid_z0,
        P.bulkhead_x + P.bulkhead_t,
        P.drive_tab_y0,
        P.frame_z1,
    )

    # A small reinforced socket wraps the frame's upper anti-torque key.
    key_half_w = P.drive_key_w / 2
    key_half_h = P.drive_key_h / 2
    body += box_between(
        P.drive_key_x - key_half_w - P.drive_key_socket_wall,
        P.drive_cassette_back_y,
        P.drive_key_z - key_half_h - P.drive_key_socket_wall,
        P.drive_key_x + key_half_w + P.drive_key_socket_wall,
        P.drive_tab_y1,
        P.drive_key_z + key_half_h + P.drive_key_socket_wall,
    )

    for x in P.lay_bearing_centers_x:
        body += _rear_bearing_boss(x)
        body -= _bearing_pocket(x)
        body -= _bearing_shaft_cut(x)

    # The motor shaft continues through the right support to its tip.
    body -= _axis_x_cylinder(
        P.jgb_shaft_d / 2 + 0.3,
        P.saddle_x0 - 1,
        P.saddle_x1 - P.saddle_x0 + 2,
        P.drive_y,
        P.motor_z,
    )

    access_y, access_z = _motor_screw_centers()[P.jgb_tool_access_index]
    body -= _axis_x_cylinder(
        P.jgb_tool_access_d / 2,
        P.bulkhead_x + P.bulkhead_t,
        P.saddle_x1 - P.bulkhead_x - P.bulkhead_t + 0.2,
        access_y,
        access_z,
    )

    # The lid lives in a shallow room-side plane.  Only its two narrow
    # layshaft spines reach rearward; the rest stays ahead of all gears.
    fit = P.cassette_lid_fit
    body -= box_between(
        P.cassette_lid_x0 - fit,
        P.cassette_lid_y0 - fit,
        P.cassette_lid_z0 - fit,
        P.cassette_lid_x1 + fit,
        P.frame_front_y + fit,
        P.cassette_lid_z1 + fit,
    )
    for x in P.lay_bearing_centers_x:
        body -= box_between(
            x - P.cassette_lid_spine_w / 2 - fit,
            P.lay_cap_y1 - fit,
            P.lay_z - P.lay_bearing_boss_d / 2 - fit,
            x + P.cassette_lid_spine_w / 2 + fit,
            P.cassette_lid_y0 + fit,
            P.lay_z + P.lay_bearing_boss_d / 2 + fit,
        )
    bearing_y0 = P.spr_bearing_centers_y[1] - P.spr_bearing_w / 2
    body -= box_between(
        P.drive_x
        - P.spr_bearing_d / 2
        - P.cassette_lid_sprocket_boss_wall
        - fit,
        bearing_y0 - fit,
        P.spr_z
        - P.spr_bearing_d / 2
        - P.cassette_lid_sprocket_boss_wall
        - fit,
        P.drive_x
        + P.spr_bearing_d / 2
        + P.cassette_lid_sprocket_boss_wall
        + fit,
        P.frame_front_y + fit,
        P.spr_z
        + P.spr_bearing_d / 2
        + P.cassette_lid_sprocket_boss_wall
        + fit,
    )
    body -= _sprocket_shaft_cuts()

    # Add these after every moving-envelope and lid-fit cut: each selected
    # position is clear of the mechanism and remains rooted at the rear wall.
    body += _lid_insert_columns()
    body -= _lid_insert_cuts()

    # Upper frame key: 0.4 mm clearance on all insertion faces.
    body -= box_between(
        P.drive_key_x - key_half_w - P.drive_cassette_fit,
        0,
        P.drive_key_z - key_half_h - P.drive_cassette_fit,
        P.drive_key_x + key_half_w + P.drive_cassette_fit,
        P.drive_key_y1 + P.drive_cassette_fit,
        P.drive_key_z + key_half_h + P.drive_cassette_fit,
    )

    for x, _y, z in P.drive_mount_points:
        body -= box_between(
            x - P.drive_mount_boss_d / 2 - P.drive_cassette_fit,
            0,
            z - P.drive_mount_boss_d / 2 - P.drive_cassette_fit,
            x + P.drive_mount_boss_d / 2 + P.drive_cassette_fit,
            P.drive_tab_y0,
            z + P.drive_mount_boss_d / 2 + P.drive_cassette_fit,
        )
        body -= Pos(x, P.drive_tab_y1 + 0.5, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.drive_mount_clear_d / 2, P.drive_tab_y1 + 1)
        )
    return body


def cassette_lid_print():
    """Single lid with the broad room-side web flat on the print bed."""
    oriented = Rot(-90, 0, 0) * cassette_lid()
    return Pos(0, 0, -oriented.bounding_box().min.Z) * oriented


def spacers_print():
    """Four axial spacers upright on one small build plate."""
    assembly_parts = (
        motor_spacer(),
        bevel_spacer(),
        inner_spacer(),
        outer_spacer(),
    )
    plate = None
    for index, part in enumerate(assembly_parts):
        upright = Rot(0, -90, 0) * part
        bounds = upright.bounding_box()
        upright = Pos(
            index * P.drive_spacer_print_pitch - bounds.min.X,
            -bounds.min.Y,
            -bounds.min.Z,
        ) * upright
        plate = upright if plate is None else plate + upright
    return plate


def sprocket_spacer_print():
    """Sprocket axial spacer standing on one annular end."""
    upright = Rot(90, 0, 0) * sprocket_spacer()
    bounds = upright.bounding_box()
    return Pos(-bounds.min.X, -bounds.min.Y, -bounds.min.Z) * upright


def drive_parts():
    """Named removable-drive parts, all posed in unit coordinates."""
    from . import frames as F
    from .jgb37 import jgb37
    from .sprocket import chain_wheel, sprocket_bevel

    gears = _posed_gears()
    starts = _spacer_starts()
    return {
        "drive-cassette": drive_cassette(),
        "cassette-lid": cassette_lid(),
        "chain-wheel": F.SPROCKET_WHEEL_IN_UNIT * chain_wheel(),
        "sprocket-bevel": F.SPROCKET_BEVEL_IN_UNIT * sprocket_bevel(),
        "sprocket-spacer": F.sprocket_axis_in_unit(_sprocket_spacer_start())
        * sprocket_spacer(),
        "rear-sprocket-bearing": F.REAR_SPROCKET_BEARING_IN_UNIT
        * sprocket_bearing_mr105(),
        "front-sprocket-bearing": F.FRONT_SPROCKET_BEARING_IN_UNIT
        * sprocket_bearing_mr105(),
        "sprocket-shaft": F.SPROCKET_SHAFT_IN_UNIT * sprocket_shaft(),
        "motor": F.MOTOR_IN_UNIT * jgb37(),
        "pinion": gears["pinion"],
        "motor-spacer": F.MOTOR_SPACER_IN_UNIT * motor_spacer(),
        "layshaft-bevel": gears["layshaft-bevel"],
        "bevel-spacer": F.layshaft_axis_in_unit(starts["bevel"])
        * bevel_spacer(),
        "left-bearing": F.LEFT_BEARING_IN_UNIT * bearing_625zz(),
        "inner-spacer": F.layshaft_axis_in_unit(starts["inner"])
        * inner_spacer(),
        "layshaft-spur": gears["layshaft-spur"],
        "outer-spacer": F.layshaft_axis_in_unit(starts["outer"])
        * outer_spacer(),
        "right-bearing": F.RIGHT_BEARING_IN_UNIT * bearing_625zz(),
        "layshaft-rod": F.LAYSHAFT_ROD_IN_UNIT * layshaft_rod(),
    }


_DRIVE_STYLE = {
    "drive-cassette": ("lightsteelblue", 0.8),
    "cassette-lid": ("steelblue", 0.8),
    "chain-wheel": ("orange", 1.0),
    "sprocket-bevel": ("gold", 1.0),
    "sprocket-spacer": ("darkorange", 1.0),
    "rear-sprocket-bearing": ("silver", 1.0),
    "front-sprocket-bearing": ("silver", 1.0),
    "sprocket-shaft": ("dimgray", 1.0),
    "motor": ("silver", 1.0),
    "pinion": ("tomato", 1.0),
    "motor-spacer": ("darkorange", 1.0),
    "layshaft-bevel": ("gold", 1.0),
    "bevel-spacer": ("goldenrod", 1.0),
    "left-bearing": ("silver", 1.0),
    "inner-spacer": ("goldenrod", 1.0),
    "layshaft-spur": ("goldenrod", 1.0),
    "outer-spacer": ("goldenrod", 1.0),
    "right-bearing": ("silver", 1.0),
    "layshaft-rod": ("dimgray", 1.0),
}


def add_drive_to_scene(result):
    """Add the canonical removable-drive presentation to a viewer scene."""
    for name, part in drive_parts().items():
        color, alpha = _DRIVE_STYLE[name]
        result.add(part, name, color=color, alpha=alpha)
    return result


def scene():
    """Complete removable drive assembly in unit coordinates."""
    from splitflap_cad.viewer import Scene

    return add_drive_to_scene(Scene())


def cassette_lid_scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(cassette_lid(), "cassette-lid", color="steelblue")


def sprocket_spacer_scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(
        sprocket_spacer_print(),
        "sprocket-spacer",
        color="darkorange",
    )
