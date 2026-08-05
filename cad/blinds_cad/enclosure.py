"""Wall-mounted structural exoskeleton for the blinds unit.

Built in the UNIT frame. This one print owns the wall anchors, removable-drive
mounting pads, PCB tray, direct battery-holder spine, and cosmetic-sleeve
retainers. It prints wall-face down: X/Z are the 98 x 242 bed footprint;
Y is only the 44 mm print height.

The thin cosmetic sleeve and two-piece top live in cover.py. No
load-bearing feature is fused into either cosmetic part.

View it: `just cad view blinds-frame`.
"""

from build123d import Cylinder, Pos, Rot
from splitflap_cad.geo import box_between

from .params import P


def frame():
    """Complete load-bearing wall frame, ready for the slide-on cover."""
    body = _backbone()
    body += _pcb_tray()
    body += _floor_bosses()
    body += _battery_mount_spine()
    body += _drive_mounts()
    body += _sleeve_guides()
    body += _sleeve_retainers()

    # The cassette floor now reaches 2 mm farther wallward than the old dock.
    # Cut its exact seated envelope so the frame retains material inside the
    # cassette's motor, gear, and mount windows instead of opening a crude box.
    from .drivecassette import drive_cassette

    body -= drive_cassette()

    # Four direct-to-wall #8 anchor holes through the rear rails.
    for x, z in P.frame_wall_holes:
        body -= Pos(x, P.frame_t / 2, z) * (
            Rot(90, 0, 0) * Cylinder(P.wall_screw_d / 2, P.frame_t + 2)
        )
    return body


def _backbone():
    """Flat wall-side rail grid; the print bed for every projecting feature.

    The two upper spines carry the removable drive cassette down
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


def _drive_mounts():
    """Keyed shelf plus two clamp screws for the complete drive pod.

    The shelf carries gravity, the upper key reacts drive torque, and the M3
    screws only hold the cassette against those datum surfaces.
    """
    mounts = box_between(
        P.cradle_x0,
        0,
        P.drive_shelf_z0,
        P.saddle_x1,
        P.drive_mount_face_y,
        P.drive_shelf_z1,
    )
    for x, y, z in P.drive_mount_points:
        pad = box_between(
            x - P.drive_mount_boss_d / 2,
            0,
            z - P.drive_mount_boss_d / 2,
            x + P.drive_mount_boss_d / 2,
            y,
            z + P.drive_mount_boss_d / 2,
        )
        pad -= Pos(x, y + 0.1, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.m3_insert_d / 2, P.drive_mount_insert_depth + 0.2)
        )
        mounts += pad

    key_half_w = P.drive_key_w / 2
    key_half_h = P.drive_key_h / 2
    mounts += box_between(
        P.drive_key_x - key_half_w,
        0,
        P.drive_key_z - key_half_h,
        P.drive_key_x + key_half_w,
        P.drive_key_y1,
        P.drive_key_z + key_half_h,
    )
    return mounts


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
    """Two rooted M3 blocks reached through the sleeve underside."""
    bosses = None
    for x, y in P.sleeve_retainer_xy:
        radius = P.sleeve_retainer_boss_d / 2
        z0 = P.frame_tray_z0
        z1 = z0 + P.sleeve_retainer_boss_h
        boss = box_between(
            x - radius,
            0,
            z0,
            x + radius,
            y + radius,
            z1,
        )
        boss -= Pos(x, y, (z0 + z1) / 2) * Cylinder(
            P.m3_tap_d / 2,
            P.sleeve_retainer_boss_h + 2,
        )
        bosses = boss if bosses is None else bosses + boss
    return bosses


def scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(frame(), "frame", color="lightsteelblue")
