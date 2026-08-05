"""Six flat-print skins and internal motor bulkhead for the JGB37 speedbox.

The two side skins are structural. Their edge tabs locate the top, bottom,
front, and rear skins; side-loading M3 nut traps clamp those skins with twelve
bolts. The selected physical calibration is encoded directly: 0.20 mm panel
clearance, Ø3.4 bolt holes, and 5.8 x 2.7 mm nut traps.

Every builder returns its part in flat print orientation on Z=0. Assembly
poses live in ``frames.py``. The left and right skins differ only because the
right one's vertical features are mirrored before its inward-facing assembly
pose. The top bearing boss prints upward and lands inside the box.
"""

from math import cos, radians, sin

from build123d import Align, Box, Cylinder, Pos

from splitflap_cad.viewer import Scene

from . import frames as F
from .params import P
from .speedbox import output_axis_y


def _box_at(x: float, y: float, z: float, w: float, d: float, h: float):
    return Pos(x + w / 2, y + d / 2, z + h / 2) * Box(w, d, h)


def _cylinder(radius: float, height: float):
    return Cylinder(
        radius,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def _cut_horizontal_joint(body, u: float, edge_sign: int):
    """Tabs and T-nut trap on a local +/-Y edge of a side skin."""
    edge = edge_sign * P.fg_inner_h / 2
    for tab_offset in (-P.fg_joint_tab_pitch / 2, P.fg_joint_tab_pitch / 2):
        body += Pos(
            u + tab_offset,
            edge + edge_sign * P.fg_panel_t / 2,
            P.fg_panel_t / 2,
        ) * Box(P.fg_joint_tab_w, P.fg_panel_t, P.fg_panel_t)

    pocket_v = edge - edge_sign * P.fg_joint_nut_inset
    body -= Pos(u, pocket_v, P.fg_panel_t / 2) * Box(
        P.fg_joint_nut_w,
        P.fg_joint_nut_d,
        P.fg_panel_t + 0.2,
    )
    near_edge = pocket_v + edge_sign * P.fg_joint_nut_d / 2
    body -= Pos(u, (edge + near_edge) / 2, P.fg_panel_t / 2) * Box(
        P.fg_joint_stem_w,
        abs(edge - near_edge) + 0.2,
        P.fg_panel_t + 0.2,
    )
    return body


def _cut_vertical_joint(body, v: float, edge_sign: int):
    """Tabs and T-nut trap on a local +/-X edge of a side skin."""
    edge = edge_sign * P.fg_inner_d / 2
    for tab_offset in (-P.fg_joint_tab_pitch / 2, P.fg_joint_tab_pitch / 2):
        body += Pos(
            edge + edge_sign * P.fg_panel_t / 2,
            v + tab_offset,
            P.fg_panel_t / 2,
        ) * Box(P.fg_panel_t, P.fg_joint_tab_w, P.fg_panel_t)

    pocket_u = edge - edge_sign * P.fg_joint_nut_inset
    body -= Pos(pocket_u, v, P.fg_panel_t / 2) * Box(
        P.fg_joint_nut_d,
        P.fg_joint_nut_w,
        P.fg_panel_t + 0.2,
    )
    near_edge = pocket_u + edge_sign * P.fg_joint_nut_d / 2
    body -= Pos((edge + near_edge) / 2, v, P.fg_panel_t / 2) * Box(
        abs(edge - near_edge) + 0.2,
        P.fg_joint_stem_w,
        P.fg_panel_t + 0.2,
    )
    return body


def _cut_bulkhead_slots(body, mirror_v: bool):
    u = (
        P.fg_motor_face_y
        - P.fg_box_d / 2
        + P.fg_bulkhead_t / 2
    )
    v_sign = -1 if mirror_v else 1
    for desired_v in P.fg_bulkhead_tab_positions:
        body -= Pos(u, v_sign * desired_v, P.fg_panel_t / 2) * Box(
            P.fg_bulkhead_t + P.fg_joint_clear,
            P.fg_bulkhead_tab_w + P.fg_joint_tab_end_clear,
            P.fg_panel_t + 0.2,
        )
    return body


def side_panel(right: bool = False):
    """Structural side skin with all nut traps."""
    body = Pos(0, 0, P.fg_panel_t / 2) * Box(
        P.fg_inner_d,
        P.fg_inner_h,
        P.fg_panel_t,
    )
    v_map = -1 if right else 1

    for u in P.fg_long_joint_positions:
        body = _cut_horizontal_joint(body, u, edge_sign=v_map * -1)
        body = _cut_horizontal_joint(body, u, edge_sign=v_map * 1)
    body = _cut_vertical_joint(body, v_map * 0.0, edge_sign=-1)
    body = _cut_vertical_joint(
        body,
        v_map * P.fg_front_joint_z,
        edge_sign=1,
    )
    body = _cut_bulkhead_slots(body, mirror_v=right)

    return body


def left_panel():
    return side_panel(right=False)


def right_panel():
    return side_panel(right=True)


def _cut_closure_station(body, x: float, y: float, tabs_along_y: bool):
    for offset in (-P.fg_joint_tab_pitch / 2, P.fg_joint_tab_pitch / 2):
        dx, dy = (0, offset) if tabs_along_y else (offset, 0)
        slot_w = (
            P.fg_panel_t + P.fg_joint_clear
            if tabs_along_y
            else P.fg_joint_tab_w + P.fg_joint_tab_end_clear
        )
        slot_d = (
            P.fg_joint_tab_w + P.fg_joint_tab_end_clear
            if tabs_along_y
            else P.fg_panel_t + P.fg_joint_clear
        )
        body -= Pos(x + dx, y + dy, P.fg_panel_t / 2) * Box(
            slot_w,
            slot_d,
            P.fg_panel_t + 0.2,
        )
    body -= Pos(x, y, P.fg_panel_t / 2) * _cylinder(
        P.fg_joint_hole_d / 2,
        P.fg_panel_t + 0.2,
    )
    return body


def horizontal_panel(top: bool = False):
    """Top/bottom skin with stations compensated for the top's flipped pose."""
    body = Pos(0, 0, P.fg_panel_t / 2) * Box(
        P.fg_box_w,
        P.fg_box_d,
        P.fg_panel_t,
    )
    for x in (-P.fg_box_w / 2 + P.fg_panel_t / 2,
              P.fg_box_w / 2 - P.fg_panel_t / 2):
        positions = (
            tuple(-u for u in P.fg_long_joint_positions)
            if top
            else P.fg_long_joint_positions
        )
        for u in positions:
            body = _cut_closure_station(body, x, u, tabs_along_y=True)
    if top:
        bearing_x = P.fg_motor_axis_x - P.fg_box_w / 2
        bearing_y = P.fg_box_d / 2 - output_axis_y()
        body += Pos(bearing_x, bearing_y, P.fg_panel_t) * _cylinder(
            P.fg_bearing_carrier_d / 2,
            P.fg_bearing_carrier_t - P.fg_panel_t,
        )
        body -= Pos(bearing_x, bearing_y, P.fg_bearing_shoulder) * _cylinder(
            (P.fg_bearing_d + P.fg_bearing_clear) / 2,
            P.fg_bearing_carrier_t - P.fg_bearing_shoulder + 0.2,
        )
        body -= Pos(bearing_x, bearing_y, -0.1) * _cylinder(
            P.fg_output_bore_d / 2,
            P.fg_bearing_carrier_t + 0.2,
        )
    return body


def bottom_panel():
    return horizontal_panel()


def top_panel():
    return horizontal_panel(top=True)


def end_panel(front: bool = False):
    """Front/rear skin between top and bottom; front clears the output area."""
    body = Pos(0, 0, P.fg_panel_t / 2) * Box(
        P.fg_box_w,
        P.fg_inner_h,
        P.fg_panel_t,
    )
    joint_v = P.fg_front_joint_z if front else 0.0
    for x in (-P.fg_box_w / 2 + P.fg_panel_t / 2,
              P.fg_box_w / 2 - P.fg_panel_t / 2):
        body = _cut_closure_station(body, x, joint_v, tabs_along_y=True)

    if not front:
        body -= Pos(
            0,
            P.fg_motor_center_z - P.fg_box_h / 2,
            P.fg_panel_t / 2,
        ) * Box(
            P.fg_wire_exit_w,
            P.fg_wire_exit_h,
            P.fg_panel_t + 0.2,
        )
    return body


def front_panel():
    return end_panel(front=True)


def rear_panel():
    return end_panel(front=False)


def motor_bulkhead():
    """Tabbed 2 mm bulkhead with a 5 mm reinforced motor mounting face."""
    body = Pos(0, 0, P.fg_bulkhead_t / 2) * Box(
        P.fg_inner_w,
        P.fg_inner_h,
        P.fg_bulkhead_t,
    )
    for edge_sign in (-1, 1):
        edge = edge_sign * P.fg_inner_w / 2
        for v in P.fg_bulkhead_tab_positions:
            body += Pos(
                edge + edge_sign * P.fg_panel_t / 2,
                v,
                P.fg_bulkhead_t / 2,
            ) * Box(P.fg_panel_t, P.fg_bulkhead_tab_w, P.fg_bulkhead_t)

    motor_centre_u = P.fg_box_w / 2 - P.fg_motor_axis_x
    motor_centre_v = P.fg_motor_center_z - P.fg_box_h / 2
    shaft_v = P.fg_shaft_z - P.fg_box_h / 2
    reinforce_d = P.fg_motor_gear_d
    body += Pos(motor_centre_u, motor_centre_v, P.fg_bulkhead_t) * _cylinder(
        reinforce_d / 2,
        P.fg_bulkhead_reinforce,
    )
    body -= Pos(motor_centre_u, shaft_v, -0.1) * _cylinder(
        P.fg_motor_boss_clear_d / 2,
        P.fg_bulkhead_t + P.fg_bulkhead_reinforce + 0.2,
    )
    for index in range(P.fg_motor_screw_n):
        angle = radians(index * 360 / P.fg_motor_screw_n)
        x = motor_centre_u + P.fg_motor_screw_bcd / 2 * cos(angle)
        v = motor_centre_v + P.fg_motor_screw_bcd / 2 * sin(angle)
        body -= Pos(x, v, -0.1) * _cylinder(
            P.fg_motor_mount_clear_d / 2,
            P.fg_bulkhead_t + P.fg_bulkhead_reinforce + 0.2,
        )
    return body


def scene() -> Scene:
    return (
        Scene()
        .add(bottom_panel(), "bottom", "lightblue", alpha=0.30, loc=F.FG_BOTTOM_IN_BOX)
        .add(top_panel(), "top", "lightskyblue", alpha=0.20, loc=F.FG_TOP_IN_BOX)
        .add(left_panel(), "left", "lightblue", alpha=0.25, loc=F.FG_LEFT_IN_BOX)
        .add(right_panel(), "right", "lightblue", alpha=0.25, loc=F.FG_RIGHT_IN_BOX)
        .add(rear_panel(), "rear", "lightskyblue", alpha=0.25, loc=F.FG_REAR_IN_BOX)
        .add(front_panel(), "front", "lightskyblue", alpha=0.20, loc=F.FG_FRONT_IN_BOX)
        .add(
            motor_bulkhead(),
            "motor-bulkhead",
            "steelblue",
            alpha=0.35,
            loc=F.FG_BULKHEAD_IN_BOX,
        )
    )
