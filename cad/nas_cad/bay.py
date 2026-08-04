"""Printable 3.5-inch HDD caddy, cam latch, and repeatable bay frame."""

from build123d import Align, Box, Cylinder, Pos, Rot

from .hdd import add_hdd_to_scene
from .params import P


def _box_at(x: float, y: float, z: float, w: float, d: float, h: float):
    return Pos(x + w / 2, y + d / 2, z + h / 2) * Box(w, d, h)


def caddy():
    """Vented tray with side rails and a front bezel; drive screws in."""
    body = _box_at(0, 0, 0, P.caddy_w, P.caddy_d, P.caddy_floor_t)
    rail_y = P.caddy_front_overhang
    body += _box_at(0, rail_y, 0, P.caddy_rail_t, P.hdd_d, P.caddy_rail_h)
    body += _box_at(
        P.caddy_w - P.caddy_rail_t,
        rail_y,
        0,
        P.caddy_rail_t,
        P.hdd_d,
        P.caddy_rail_h,
    )
    body += _box_at(0, 0, 0, P.caddy_w, P.caddy_front_t, P.caddy_h)

    # Three long floor vents preserve a stiff perimeter and connector end.
    vents_w = 3 * P.caddy_vent_w + 2 * P.caddy_vent_gap
    vent_x0 = (P.caddy_w - vents_w) / 2
    vent_y0 = P.caddy_front_overhang + (P.hdd_d - P.caddy_vent_d) / 2
    for i in range(3):
        body -= _box_at(
            vent_x0 + i * (P.caddy_vent_w + P.caddy_vent_gap),
            vent_y0,
            -0.1,
            P.caddy_vent_w,
            P.caddy_vent_d,
            P.caddy_floor_t + 0.2,
        )

    # Access holes line up with the two specified side holes on each side.
    drive_z = P.caddy_floor_t + P.drive_bottom_clear
    drive_x = P.caddy_rail_t + P.drive_side_clear
    for x, direction in ((0, 1), (P.caddy_w, -1)):
        for y in (P.hdd_side_hole_rear_y, P.hdd_side_hole_front_y):
            body -= Pos(x, P.caddy_front_overhang + y, drive_z + P.hdd_side_hole_z) * Rot(
                0, 90 * direction, 0
            ) * Cylinder(
                2.1,
                P.caddy_rail_t + P.drive_side_clear + 0.5,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    return body


def latch(angle_deg: float = 0.0):
    """Front lever in its local pivot frame; angle 0 is closed across bay."""
    length = P.caddy_w - P.latch_pivot_margin - P.latch_end_margin
    arm = _box_at(0, -P.latch_t / 2, 0, length, P.latch_t, P.latch_h)
    arm += Pos(0, 0, 0) * Cylinder(
        P.latch_cam_r,
        P.latch_h,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    arm -= Pos(0, 0, -0.1) * Cylinder(
        P.latch_pivot_d / 2,
        P.latch_h + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # Finger scoop at the free end.
    arm -= Pos(length - 6, 0, P.latch_h / 2) * Rot(90, 0, 0) * Cylinder(
        3.2,
        P.latch_t + 0.2,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    return Rot(0, 0, angle_deg) * arm


def bay_frame():
    """Open-air bay shell with corner joiner bores for stacking."""
    w, d, h, t = P.bay_w, P.bay_depth, P.bay_h, P.bay_wall
    body = _box_at(0, 0, 0, w, d, t)
    body += _box_at(0, 0, h - t, w, d, t)
    body += _box_at(0, 0, 0, t, P.bay_front_post_d, h)
    body += _box_at(w - t, 0, 0, t, P.bay_front_post_d, h)
    body += _box_at(0, d - P.bay_rear_post_d, 0, t, P.bay_rear_post_d, h)
    body += _box_at(w - t, d - P.bay_rear_post_d, 0, t, P.bay_rear_post_d, h)

    for x in (P.bay_joiner_edge, w - P.bay_joiner_edge):
        for y in (P.bay_joiner_edge, d - P.bay_joiner_edge):
            body -= Pos(x, y, -0.1) * Cylinder(
                P.bay_joiner_d / 2,
                h + 0.2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
    return body


def backplane():
    """Reference PCB and mating connector, not yet a selected part."""
    x = (P.bay_w - P.backplane_w) / 2
    y = P.bay_depth - P.bay_rear_post_d - P.backplane_pcb_t
    z = (P.bay_h - P.backplane_h) / 2
    pcb = _box_at(x, y, z, P.backplane_w, P.backplane_pcb_t, P.backplane_h)
    connector_x = P.bay_wall + P.bay_clear_x + P.caddy_rail_t + P.drive_side_clear
    connector_x += P.hdd_w - P.sata_right_margin - P.sata_w
    connector_z = P.bay_wall + P.bay_clear_z + P.caddy_floor_t + P.drive_bottom_clear
    connector_z += P.sata_z
    plug = _box_at(
        connector_x,
        y - P.sata_d,
        connector_z,
        P.sata_w,
        P.sata_d,
        P.sata_h,
    )
    return pcb, plug


def caddy_location(travel: float = 0.0):
    return Pos(
        P.bay_wall + P.bay_clear_x,
        P.bay_depth - P.bay_rear_post_d - P.backplane_pcb_t - P.caddy_d - travel,
        P.bay_wall + P.bay_clear_z,
    )


def drive_in_caddy_location(travel: float = 0.0):
    return caddy_location(travel) * Pos(
        P.caddy_rail_t + P.drive_side_clear,
        P.caddy_front_overhang,
        P.caddy_floor_t + P.drive_bottom_clear,
    )


def latch_location(travel: float = 0.0):
    c = caddy_location(travel)
    # Pivot just inboard of the left bezel edge, centred vertically.
    return c * Pos(
        P.latch_pivot_margin,
        -P.latch_t / 2 - 0.6,
        (P.caddy_h - P.latch_h) / 2,
    )


def _add_bay(scene, travel: float, angle: float):
    scene.add(bay_frame(), "bay-frame", color="lightsteelblue", alpha=0.82)
    scene.add(caddy(), "caddy", color="slategray", loc=caddy_location(travel))
    scene.add(
        latch(angle),
        "cam-latch",
        color="orange",
        loc=latch_location(travel),
    )
    pcb, plug = backplane()
    scene.add(pcb, "backplane-pcb", color="darkgreen")
    scene.add(plug, "backplane-sata", color="black")
    add_hdd_to_scene(scene, drive_in_caddy_location(travel))
    return scene


def scene():
    from splitflap_cad.viewer import Scene

    return _add_bay(Scene(), travel=0.0, angle=0.0)


def open_scene():
    from splitflap_cad.viewer import Scene

    return _add_bay(Scene(), travel=P.caddy_open_travel, angle=-P.latch_open_deg)


def caddy_scene():
    from splitflap_cad.viewer import Scene

    s = Scene().add(caddy(), "caddy", color="slategray")
    s.add(latch(0), "cam-latch", color="orange", loc=Pos(P.latch_pivot_margin, -2.6, 10))
    add_hdd_to_scene(
        s,
        Pos(
            P.caddy_rail_t + P.drive_side_clear,
            P.caddy_front_overhang,
            P.caddy_floor_t + P.drive_bottom_clear,
        ),
    )
    return s
