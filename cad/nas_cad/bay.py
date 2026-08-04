"""Tool-less 3.5-inch HDD caddy, push-door, and repeatable bay frame.

The bay is modelled flat because that is the natural print and HDD frame.
The NAS assembly rotates each bay onto its side, producing the narrow vertical
doors used by compact desktop NAS products.
"""

from build123d import Align, Box, Cone, Cylinder, Pos, Rot

from .hdd import add_hdd_to_scene
from .params import P


def _box_at(x: float, y: float, z: float, w: float, d: float, h: float):
    return Pos(x + w / 2, y + d / 2, z + h / 2) * Box(w, d, h)


def _pin(x: float, y: float, z: float, direction: int):
    """Two-stage pin with a tapered lead-in for a standard side hole."""
    rotation = Rot(0, 90 * direction, 0)
    shaft = Pos(x, y, z) * rotation * Cylinder(
        P.retention_pin_d / 2,
        P.retention_pin_len,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    tip_x = x + direction * P.retention_pin_len
    tip = Pos(tip_x, y, z) * rotation * Cone(
        P.retention_pin_d / 2,
        P.retention_pin_tip_d / 2,
        P.retention_pin_tip_len,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return shaft + tip


def caddy():
    """Vented tray with fixed-left and flex-right tool-less locating pins."""
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
    # A shallow crossbar supports the push-door without obscuring airflow.
    body += _box_at(0, 0, 0, P.caddy_w, P.caddy_front_t, P.caddy_floor_t + 3.0)

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

    drive_z = P.caddy_floor_t + P.drive_bottom_clear
    pin_z = drive_z + P.hdd_side_hole_z
    pin_ys = tuple(
        P.caddy_front_overhang + y
        for y in (P.hdd_side_hole_rear_y, P.hdd_side_hole_front_y)
    )

    # The right rail is divided into two cantilever fingers. Pull their outer
    # tabs to release both pins; the left pins remain fixed as the hinge side.
    right_x = P.caddy_w - P.caddy_rail_t
    for pin_y in pin_ys:
        for slot_y in (
            pin_y - P.retention_finger_w / 2,
            pin_y + P.retention_finger_w / 2,
        ):
            body -= _box_at(
                right_x - 0.1,
                slot_y - P.retention_slot_w / 2,
                P.retention_finger_root_h,
                P.caddy_rail_t + 0.2,
                P.retention_slot_w,
                P.caddy_rail_h - P.retention_finger_root_h + 0.1,
            )
        body += _box_at(
            P.caddy_w,
            pin_y - P.retention_pull_tab_w / 2,
            P.caddy_rail_h - 4.0,
            P.retention_pull_tab_out,
            P.retention_pull_tab_w,
            4.0,
        )

    left_pin_x = P.caddy_rail_t
    right_pin_x = P.caddy_w - P.caddy_rail_t
    for pin_y in pin_ys:
        body += _pin(left_pin_x, pin_y, pin_z, 1)
        body += _pin(right_pin_x, pin_y, pin_z, -1)
    return body


def door():
    """Full-height printable push-door in its bottom-hinge local frame."""
    width = P.bay_w - 2 * P.door_gap
    height = P.bay_h - 2 * P.door_gap
    panel = _box_at(0, -P.door_t, 0, width, P.door_t, height)
    panel += Pos(0, -P.door_t / 2, 0) * Cylinder(
        P.door_hinge_d / 2,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    button_x = P.door_button_from_hinge
    panel += Pos(button_x, -P.door_t, height / 2) * Rot(90, 0, 0) * Cylinder(
        P.door_button_d / 2,
        P.door_button_depth,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return panel


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


def drive_in_caddy_location():
    return Pos(
        P.caddy_rail_t + P.drive_side_clear,
        P.caddy_front_overhang,
        P.caddy_floor_t + P.drive_bottom_clear,
    )


def door_in_caddy_location(angle_deg: float = 0.0):
    closed = caddy_location()
    return Pos(
        P.door_gap - closed.position.X,
        -closed.position.Y,
        P.door_gap - closed.position.Z,
    ) * Rot(0, 0, angle_deg)


def vertical_bay_location(x: float = 0.0):
    """Rotate a flat bay onto its side; local +X becomes vertical +Z."""
    return Pos(x + P.bay_h, 0, 0) * Rot(0, -90, 0)


def vertical_bay_frame():
    return vertical_bay_location() * bay_frame()


def _fixed_scene():
    from splitflap_cad.viewer import Scene

    pcb, plug = backplane()
    return (
        Scene()
        .add(bay_frame(), "frame", color="lightsteelblue", alpha=0.82)
        .add(pcb, "backplane-pcb", color="darkgreen")
        .add(plug, "backplane-sata", color="black")
    )


def _moving_scene(door_angle: float = 0.0):
    from splitflap_cad.viewer import Scene

    moving = Scene().add(caddy(), "tool-less-caddy", color="slategray")
    add_hdd_to_scene(moving, drive_in_caddy_location())
    door_scene = Scene().add(door(), "panel", color="gainsboro")
    moving.add_group(
        door_scene,
        "push-door",
        loc=door_in_caddy_location(door_angle),
    )
    return moving


def bay_group(travel: float = 0.0, door_angle: float = 0.0):
    """One tidy viewer group: fixed shell plus independently moving caddy."""
    from splitflap_cad.viewer import Scene

    return (
        Scene()
        .add_group(_fixed_scene(), "fixed")
        .add_group(
            _moving_scene(door_angle),
            "moving",
            loc=caddy_location(travel),
        )
    )


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene().add_group(bay_group(), "nas-bay", loc=vertical_bay_location())
    return add_opening_animation(s, "nas-bay", start=0.0)


def open_scene():
    from splitflap_cad.viewer import Scene

    return Scene().add_group(
        bay_group(P.caddy_open_travel, -P.door_open_deg),
        "nas-bay-open",
        loc=vertical_bay_location(),
    )


def caddy_scene():
    from splitflap_cad.viewer import Scene

    return Scene().add_group(_moving_scene(), "tool-less-caddy")


def add_opening_animation(scene, target: str, start: float):
    """Press, release, open, extract, pause, then close one bay."""
    door_target = f"{target}/moving/push-door"
    moving_target = f"{target}/moving"
    scene.track(
        door_target,
        "ty",
        (0.0, start, start + 0.18, start + 0.34, start + 4.0),
        (0.0, 0.0, P.door_press_travel, 0.0, 0.0),
    )
    scene.track(
        door_target,
        "rz",
        (0.0, start + 0.30, start + 0.72, start + 3.45, start + 3.85, start + 4.0),
        (0.0, 0.0, -P.door_open_deg, -P.door_open_deg, 0.0, 0.0),
    )
    scene.track(
        moving_target,
        "ty",
        (0.0, start + 0.68, start + 1.35, start + 2.8, start + 3.45, start + 4.0),
        (0.0, 0.0, -P.caddy_open_travel, -P.caddy_open_travel, 0.0, 0.0),
    )
    return scene
