"""Wall-mounted structural exoskeleton for the blinds unit.

Built in the UNIT frame.  This one print owns the wall anchors, motor
bulkhead, layshaft saddles, motor-tail cradle, enclosed sprocket guide,
PCB tray, direct battery-holder spine, and cosmetic-sleeve retainers.  It
prints wall-face down: X/Z are the 98 x 242 bed footprint and Y is only
the 44 mm print height.

The thin cosmetic sleeve and two-piece top live in cover.py. No
load-bearing feature is fused into either cosmetic part.

View it: `just cad view blinds-frame`.
"""

import math

from build123d import (
    Circle,
    Cylinder,
    Polygon,
    Pos,
    RegularPolygon,
    Rot,
    Torus,
    extrude,
)
from splitflap_cad.geo import box_between

from .params import P


def frame():
    """Complete load-bearing wall frame, ready for the slide-on cover."""
    body = _backbone()
    body += _pcb_tray()
    body += _bulkhead()
    body += _right_saddle()
    body += _tail_cradle()
    body += _wrap_guide()
    body += _floor_bosses()
    body += _battery_mount_spine()
    body += _sleeve_guides()
    body += _sleeve_retainers()

    body -= _keeper_pockets()
    body -= _keeper_tap_cuts()
    body -= _axle_hardware_cuts()

    # Four direct-to-wall #8 anchor holes through the rear rails.
    for x, z in P.frame_wall_holes:
        body -= Pos(x, P.frame_t / 2, z) * (
            Rot(90, 0, 0) * Cylinder(P.wall_screw_d / 2, P.frame_t + 2)
        )
    return body


def axle_keeper():
    """Flat-printing front bridge that supports and retains the fixed axle."""
    x0 = P.drive_x - P.keeper_outer_half_w
    x1 = P.drive_x + P.keeper_outer_half_w
    y1 = P.frame_front_y
    body = box_between(x0, P.keeper_y0, P.keeper_z0, x1, y1, P.keeper_z1)

    # Rearward side ribs stiffen the thin bridge without entering the
    # sprocket/chain envelope. Matching frame pockets locate the part.
    rib_y0 = P.keeper_y0 - P.keeper_rim
    body += box_between(
        x0, rib_y0, P.keeper_z0,
        x0 + P.keeper_side_rib, P.keeper_y0, P.keeper_z1,
    )
    body += box_between(
        x1 - P.keeper_side_rib, rib_y0, P.keeper_z0,
        x1, P.keeper_y0, P.keeper_z1,
    )

    for x in P.keeper_screw_x:
        for z in P.keeper_screw_z:
            body -= Pos(x, (P.keeper_y0 + y1) / 2, z) * (
                Rot(90, 0, 0)
                * Cylinder(P.keeper_screw_d / 2, y1 - P.keeper_y0 + 2)
            )

    body -= Pos(P.drive_x, (P.keeper_y0 + y1) / 2, P.spr_z) * (
        Rot(90, 0, 0) * Cylinder(P.axle_d / 2 + 0.1, y1 - P.keeper_y0 + 2)
    )
    head_depth = y1 - P.axle_head_seat_y
    body -= Pos(P.drive_x, P.axle_head_seat_y + head_depth / 2, P.spr_z) * (
        Rot(90, 0, 0) * Cylinder(P.axle_head_d / 2, head_depth + 0.2)
    )
    return body


def _keeper_pockets():
    """Flush plate recess plus two anti-rattle side-rib sockets."""
    x0 = P.drive_x - P.keeper_outer_half_w
    x1 = P.drive_x + P.keeper_outer_half_w
    y1 = P.frame_front_y + 0.1
    pocket = box_between(x0, P.keeper_y0, P.keeper_z0, x1, y1, P.keeper_z1)
    rib_y0 = P.keeper_y0 - P.keeper_rim
    pocket += box_between(
        x0, rib_y0, P.keeper_z0,
        x0 + P.keeper_side_rib, P.keeper_y0, P.keeper_z1,
    )
    pocket += box_between(
        x1 - P.keeper_side_rib, rib_y0, P.keeper_z0,
        x1, P.keeper_y0, P.keeper_z1,
    )
    return pocket


def _keeper_tap_cuts():
    cuts = None
    y = P.keeper_y0 - P.keeper_tap_depth / 2
    for x in P.keeper_screw_x:
        for z in P.keeper_screw_z:
            cut = Pos(x, y, z) * (
                Rot(90, 0, 0)
                * Cylinder(P.m3_tap_d / 2, P.keeper_tap_depth + 0.2)
            )
            cuts = cut if cuts is None else cuts + cut
    return cuts


def _backbone():
    """Flat wall-side rail grid; the print bed for every projecting feature.

    The two upper spines carry the drive cassette and motor bulkhead down
    into the middle cross rail.  Without them those large cantilevers were
    fused only to the top rail and looked (and behaved) nearly unsupported.
    """
    x0, x1 = P.frame_x0, P.frame_x1
    z0, z1 = P.frame_z0, P.frame_z1
    r, t = P.frame_rail_w, P.frame_t

    body = box_between(x0, 0, z0, x0 + r, t, z1)
    body += box_between(x1 - r, 0, z0, x1, t, z1)
    # Start the bottom rail at the tray floor so the cantilevered PCB tray
    # has its full thickness rooted into it, rather than a 0.5 mm sliver.
    for z in (P.frame_tray_z0, *P.frame_cross_rails_z, z1 - r):
        body += box_between(x0, 0, z, x1, t, z + r)
    for x, depth in zip(P.frame_load_spines_x, P.frame_load_spine_depths):
        body += box_between(
            x, 0, P.frame_cross_rails_z[-1],
            x + r, depth, z1,
        )
    return body


def _pcb_tray():
    """Thin structural floor under the PCB and sleeve-retainer bosses."""
    return box_between(
        P.frame_x0,
        0,
        P.frame_tray_z0,
        P.frame_x1,
        P.frame_front_y - P.sleeve_fit,
        P.frame_tray_z1,
    )


def _axle_hardware_cuts():
    """Through-bore and ring-tunnel-loaded captive M5 nut channel."""
    cuts = Pos(P.drive_x, P.enc_d / 2, P.spr_z) * (
        Rot(90, 0, 0) * Cylinder(P.axle_d / 2 + 0.1, P.enc_d + 2)
    )

    # RegularPolygon's major radius is corner radius. For a hexagon,
    # across-flats = sqrt(3) * corner radius.
    nut_slot_y1 = P.sprocket_back_y - 0.5
    nut_slot_l = nut_slot_y1 - P.axle_nut_y0
    nut = RegularPolygon(P.axle_nut_af / math.sqrt(3), 6, rotation=30)
    nut = extrude(nut, amount=nut_slot_l / 2, both=True)
    cuts += Pos(
        P.drive_x,
        (P.axle_nut_y0 + nut_slot_y1) / 2,
        P.spr_z,
    ) * (Rot(90, 0, 0) * nut)
    return cuts


def _bulkhead():
    """Vertical motor-mount rib at the gearbox face: 6×M3 into the face,
    boss through-hole, and the layshaft's left U-saddle."""
    y0 = 0
    y1 = P.frame_front_y
    rib = box_between(
        P.bulkhead_x,
        y0,
        P.bulkhead_z0,
        P.bulkhead_x + P.bulkhead_t,
        y1,
        P.frame_z1,
    )
    # boss through-hole on the SHAFT axis
    rib -= _support_free_cross_bore(
        P.jgb_boss_d / 2 + 0.75,
        P.bulkhead_t + 2,
        P.bulkhead_x + P.bulkhead_t / 2,
        P.drive_y,
        P.motor_z,
    )
    # 6×M3 tap holes on the GEARBOX axis (7 below the shaft — ecc down)
    for i in range(P.jgb_screw_n):
        a = math.radians(i * 360 / P.jgb_screw_n)
        r = P.jgb_screw_bcd / 2
        rib -= _support_free_cross_bore(
            P.m3_tap_d / 2,
            P.bulkhead_t + 2,
            P.bulkhead_x + P.bulkhead_t / 2,
            P.drive_y + r * math.cos(a),
            P.motor_z - P.jgb_ecc + r * math.sin(a),
        )
    rib -= _saddle_cut(P.bulkhead_x - 1, P.bulkhead_x + P.bulkhead_t + 1)
    return rib


def _right_saddle():
    """Layshaft right U-saddle grown directly from the wall grid."""
    block = box_between(
        P.saddle_x0,
        0,
        P.saddle_z0,
        P.saddle_x1,
        P.saddle_y1,
        P.frame_z1,
    )
    return block - _saddle_cut(P.saddle_x0 - 1, P.saddle_x1 + 1)


def _saddle_cut(x0, x1):
    """Layshaft bore + back-opening slot between the given x planes."""
    r = P.saddle_bore / 2
    cut = _support_free_cross_bore(
        r,
        x1 - x0,
        (x0 + x1) / 2,
        P.drive_y,
        P.lay_z,
    )
    cut += box_between(
        x0,
        P.frame_t - 0.2,
        P.lay_z - r,
        x1,
        P.drive_y,
        P.lay_z + r,
    )
    return cut


def _tail_cradle():
    """Back-grown half cradle steadying the motor near its encoder end.

    Stopping at the can centre makes the circular pocket support-free
    when the whole frame prints wall-face down.
    """
    gz = P.motor_z - P.jgb_ecc  # gearbox/can axis
    cradle = box_between(
        P.cradle_x0,
        0,
        P.bulkhead_z0 - 1.0,
        P.cradle_x1,
        P.drive_y,
        gz + P.jgb_gear_d / 2 + P.cradle_shell,
    )
    cradle -= Pos(
        (P.cradle_x0 + P.cradle_x1) / 2, P.drive_y, gz
    ) * (
        Rot(0, 90, 0)
        * Cylinder(P.jgb_gear_d / 2 + 0.35, P.cradle_x1 - P.cradle_x0 + 2)
    )
    return cradle


def _wrap_guide():
    """Back-grown drive cassette around the sprocket and bevel pair.

    The solid starts on the wall grid, then the sprocket, ring, layshaft,
    chain, and axle tunnels are removed.  That construction leaves every
    layer supported in the wall-face-down print orientation.
    """
    cx, cz, wy = P.drive_x, P.spr_z, P.spr_wy
    r_ball = P.chain_ball_d / 2 + P.spr_ball_clear
    wheel_y0 = P.spr_wy - P.spr_w / 2 - P.cassette_wheel_axial_clear
    wheel_y1 = P.frame_front_y + 0.1
    block = box_between(
        cx - P.cassette_half_w,
        0,
        cz - P.guide_or,
        cx + P.cassette_half_w,
        P.frame_front_y,
        P.sleeve_h - P.sleeve_fit,
    )
    # wheel clearance
    block -= Pos(cx, (wheel_y0 + wheel_y1) / 2, cz) * (
        Rot(90, 0, 0) * Cylinder(
            P.spr_od / 2 + P.cassette_wheel_radial_clear,
            wheel_y1 - wheel_y0,
        )
    )
    # ring gear and drum tunnel from the wall side to the wheel bore
    ring_y0 = P.sprocket_back_y - 0.5
    ring_len = wheel_y0 - ring_y0
    block -= Pos(cx, (wheel_y0 + ring_y0) / 2, cz) * (
        Rot(90, 0, 0) * Cylinder(
            P.bevel_r + P.cassette_ring_radial_clear,
            ring_len,
        )
    )
    # layshaft and bevel approach from the right along X
    block -= _support_free_layshaft_tunnel()
    # chain channel around the wrap
    block -= Pos(cx, wy, cz) * (Rot(90, 0, 0) * Torus(P.spr_pcd / 2, r_ball))
    # vertical run exits
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


def _support_free_cross_bore(radius, length, x, y, z):
    """Cross-axis circular clearance with a 45-degree print-direction roof."""
    profile = Circle(radius) + Polygon(
        (-radius, 0),
        (0, radius * math.sqrt(2)),
        (radius, 0),
    )
    tunnel = extrude(
        profile,
        amount=length / 2,
        both=True,
    )
    return Pos(x, y, z) * (Rot(0, 90, 0) * tunnel)


def _support_free_layshaft_tunnel():
    return _support_free_cross_bore(
        P.bevel_r + P.cassette_layshaft_radial_clear,
        P.cassette_layshaft_tunnel_l,
        P.drive_x,
        P.drive_y,
        P.spr_z,
    )


def _floor_bosses():
    """3× M3 bosses under the flat main PCB's holes + the plain support
    pillar under the USB-C edge (plug insertion force)."""
    bosses = None
    for x, y in P.pcb_holes:
        boss_z0 = P.pcb_z0 - P.pcb_boss_h
        b = Pos(x, y, (boss_z0 + P.pcb_z0) / 2) * Cylinder(
            P.pcb_boss_d / 2,
            P.pcb_boss_h,
        )
        b -= Pos(x, y, (boss_z0 + P.pcb_z0) / 2) * Cylinder(
            P.m3_tap_d / 2,
            P.pcb_boss_h + 2,
        )
        bosses = b if bosses is None else bosses + b
    px, py = P.pcb_pillar
    boss_z0 = P.pcb_z0 - P.pcb_boss_h
    bosses += Pos(px, py, (boss_z0 + P.pcb_z0) / 2) * Cylinder(
        P.pcb_pillar_d / 2,
        P.pcb_boss_h,
    )
    return bosses


def _battery_mount_spine():
    """Continuous direct mount for both bought three-cell holders.

    A full-height rectangular spine makes the wall-to-holder load path
    visible and unambiguous.  It overlaps the bottom and middle backbone
    rails, then presents six front-opening M3 heat-set pockets matching
    the holders' moulded 4.2 mm through holes.
    """
    x0 = P.drive_x - P.battery_mount_spine_w / 2
    x1 = P.drive_x + P.battery_mount_spine_w / 2
    spine = box_between(
        x0,
        0,
        P.battery_mount_spine_z0,
        x1,
        P.battery_mount_y,
        P.battery_mount_spine_z1,
    )
    for x, y, z in P.battery_mount_points:
        spine -= Pos(x, y + 0.1, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.m3_insert_d / 2, P.battery_insert_depth + 0.2)
        )
    return spine


def _sleeve_guides():
    """Four broad pads constrain the sleeve laterally during installation."""
    inner_x0 = P.sleeve_t + P.sleeve_fit
    inner_x1 = P.enc_w - P.sleeve_t - P.sleeve_fit
    guides = None
    for z0, z1 in P.sleeve_guide_bands:
        left = box_between(
            inner_x0, 0, z0,
            P.frame_x0 + P.sleeve_guide_embed, P.frame_front_y, z1,
        )
        right = box_between(
            P.frame_x1 - P.sleeve_guide_embed, 0, z0,
            inner_x1, P.frame_front_y, z1,
        )
        pair = left + right
        guides = pair if guides is None else guides + pair
    return guides


def _sleeve_retainers():
    """Two M3 tap bosses reached through the sleeve underside."""
    bosses = None
    for x, y in P.sleeve_retainer_xy:
        boss = Pos(x, y, P.sleeve_retainer_boss_z) * Cylinder(
            P.sleeve_retainer_boss_d / 2,
            P.sleeve_retainer_boss_h,
        )
        boss -= Pos(x, y, P.sleeve_retainer_boss_z) * Cylinder(
            P.m3_tap_d / 2,
            P.sleeve_retainer_boss_h + 2,
        )
        bosses = boss if bosses is None else bosses + boss
    return bosses


def scene():
    from splitflap_cad.viewer import Scene

    return (
        Scene()
        .add(frame(), "frame", color="lightsteelblue")
        .add(axle_keeper(), "axle-keeper", color="steelblue")
    )


def axle_keeper_scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(axle_keeper(), "axle-keeper", color="steelblue")
