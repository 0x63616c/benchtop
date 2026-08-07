"""Six flat-print skins and internal motor bulkhead for the JGB37 speedbox.

The two side sheets remain 2 mm thick. Each M3 nut trap sits in a local boss
with a 10 x 8 mm footprint that rises to 8 mm from the print face; the nut
slides in from the inside and stops against the original 2 mm wall. Edge tabs
locate the top, bottom, front, and rear skins, and fourteen bolts clamp the
assembly.

Every builder returns its part in flat print orientation on Z=0. Assembly
poses live in ``frames.py``. The left and right skins differ only because the
right one's vertical features are mirrored before its inward-facing assembly
pose. Each side's bearing carrier prints upward and lands inside the box.
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


def _cut_m3_hole(body, x: float, y: float, thickness: float):
    """Cut one plain M3 clearance hole with no head recess."""
    body -= Pos(x, y, -0.1) * _cylinder(
        P.fg_joint_hole_d / 2,
        thickness + 0.2,
    )
    return body


def _cut_split_windows(
    body,
    *,
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    thickness: float,
    rib_w: float,
    split_along_x: bool,
):
    """Cut two rectangular windows separated by one straight structural rib."""
    if split_along_x:
        window_w = (width - rib_w) / 2
        offset = rib_w / 2 + window_w / 2
        centers = ((center_x - offset, center_y), (center_x + offset, center_y))
        size = (window_w, height)
    else:
        window_h = (height - rib_w) / 2
        offset = rib_w / 2 + window_h / 2
        centers = ((center_x, center_y - offset), (center_x, center_y + offset))
        size = (width, window_h)
    for x, y in centers:
        body -= Pos(x, y, thickness / 2) * Box(
            size[0],
            size[1],
            thickness + 0.2,
        )
    return body


def _cut_single_window(body, *, width: float, height: float, thickness: float):
    return body - Pos(0, 0, thickness / 2) * Box(
        width,
        height,
        thickness + 0.2,
    )


def _cut_horizontal_joint(body, u: float, edge_sign: int):
    """Tabs and a raised T-nut boss on a local +/-Y sheet edge."""
    edge = edge_sign * P.fg_inner_h / 2
    boss_v = edge - edge_sign * P.fg_joint_boss_span / 2
    body += Pos(u, boss_v, P.fg_joint_boss_t / 2) * Box(
        P.fg_joint_boss_w,
        P.fg_joint_boss_span,
        P.fg_joint_boss_t,
    )
    for tab_offset in (-P.fg_joint_tab_pitch / 2, P.fg_joint_tab_pitch / 2):
        body += Pos(
            u + tab_offset,
            edge + edge_sign * P.fg_panel_t / 2,
            P.fg_side_t / 2,
        ) * Box(P.fg_joint_tab_w, P.fg_panel_t, P.fg_side_t)

    pocket_v = edge - edge_sign * P.fg_joint_nut_inset
    blind_z = P.fg_joint_boss_t - P.fg_joint_nut_access_depth / 2 + 0.05
    body -= Pos(u, pocket_v, blind_z) * Box(
        P.fg_joint_nut_w,
        P.fg_joint_nut_d,
        P.fg_joint_nut_access_depth + 0.1,
    )
    near_edge = pocket_v + edge_sign * P.fg_joint_nut_d / 2
    body -= Pos(u, (edge + near_edge) / 2, blind_z) * Box(
        P.fg_joint_stem_w,
        abs(edge - near_edge) + 0.2,
        P.fg_joint_nut_access_depth + 0.1,
    )
    return body


def _cut_vertical_joint(body, v: float, edge_sign: int):
    """Tabs and a raised T-nut boss on a local +/-X sheet edge."""
    edge = edge_sign * P.fg_inner_d / 2
    boss_u = edge - edge_sign * P.fg_joint_boss_span / 2
    body += Pos(boss_u, v, P.fg_joint_boss_t / 2) * Box(
        P.fg_joint_boss_span,
        P.fg_joint_boss_w,
        P.fg_joint_boss_t,
    )
    for tab_offset in (-P.fg_joint_tab_pitch / 2, P.fg_joint_tab_pitch / 2):
        body += Pos(
            edge + edge_sign * P.fg_panel_t / 2,
            v + tab_offset,
            P.fg_side_t / 2,
        ) * Box(P.fg_panel_t, P.fg_joint_tab_w, P.fg_side_t)

    pocket_u = edge - edge_sign * P.fg_joint_nut_inset
    blind_z = P.fg_joint_boss_t - P.fg_joint_nut_access_depth / 2 + 0.05
    body -= Pos(pocket_u, v, blind_z) * Box(
        P.fg_joint_nut_d,
        P.fg_joint_nut_w,
        P.fg_joint_nut_access_depth + 0.1,
    )
    near_edge = pocket_u + edge_sign * P.fg_joint_nut_d / 2
    body -= Pos((edge + near_edge) / 2, v, blind_z) * Box(
        abs(edge - near_edge) + 0.2,
        P.fg_joint_stem_w,
        P.fg_joint_nut_access_depth + 0.1,
    )
    return body


def _add_front_center_nut_boss(body, edge_sign: int):
    """Add a horizontal skin's nut boss for a centered front bolt."""
    edge = edge_sign * P.fg_box_d / 2
    boss_y = edge - edge_sign * (
        P.fg_panel_t + P.fg_joint_boss_span / 2
    )
    body += Pos(0, boss_y, P.fg_front_center_boss_t / 2) * Box(
        P.fg_joint_boss_w,
        P.fg_joint_boss_span,
        P.fg_front_center_boss_t,
    )

    # Match the side receivers: the front skin consumes the first 2 mm, then
    # the nut pocket begins 3 mm farther in. Every M3x6 now engages equally.
    pocket_y = edge - edge_sign * (
        P.fg_panel_t + P.fg_joint_nut_inset
    )
    cavity_floor = P.fg_front_center_axis_z - P.fg_joint_nut_w / 2
    access_depth = P.fg_front_center_boss_t - cavity_floor
    cavity_z = cavity_floor + access_depth / 2 + 0.05
    body -= Pos(0, pocket_y, cavity_z) * Box(
        P.fg_joint_nut_w,
        P.fg_joint_nut_d,
        access_depth + 0.1,
    )
    near_edge = pocket_y + edge_sign * P.fg_joint_nut_d / 2
    body -= Pos(0, (edge + near_edge) / 2, cavity_z) * Box(
        P.fg_joint_stem_w,
        abs(edge - near_edge) + 0.2,
        access_depth + 0.1,
    )
    return body


def _add_side_bearing_carrier(body, right: bool):
    """Add one inward-facing 625ZZ pocket around the through-shaft."""
    u = output_axis_y() - P.fg_box_d / 2
    v_map = -1 if right else 1
    v = v_map * (P.fg_shaft_z - P.fg_box_h / 2)
    body += Pos(u, v, 0) * _cylinder(
        P.fg_bearing_carrier_d / 2,
        P.fg_bearing_carrier_t,
    )
    body -= Pos(u, v, P.fg_bearing_shoulder) * _cylinder(
        (P.fg_bearing_d + P.fg_bearing_clear) / 2,
        P.fg_bearing_carrier_t - P.fg_bearing_shoulder + 0.2,
    )
    body -= Pos(u, v, -0.1) * _cylinder(
        P.fg_output_bore_d / 2,
        P.fg_bearing_carrier_t + 0.2,
    )
    return body


def _cut_bulkhead_slots(body, mirror_v: bool):
    u = (
        P.fg_motor_face_y
        - P.fg_box_d / 2
        + P.fg_bulkhead_t / 2
    )
    v_sign = -1 if mirror_v else 1
    slot_depth = P.fg_panel_t + P.fg_joint_clear
    slot_z = P.fg_side_t - slot_depth / 2 + 0.05
    for desired_v in P.fg_bulkhead_tab_positions:
        body -= Pos(u, v_sign * desired_v, slot_z) * Box(
            P.fg_bulkhead_t + P.fg_joint_clear,
            P.fg_bulkhead_tab_w + P.fg_joint_tab_end_clear,
            slot_depth + 0.1,
        )
    return body


def _cut_horizontal_bulkhead_slots(body, top: bool):
    """Cut the two top/bottom slots for the bulkhead's added edge tabs."""
    assembly_y = P.fg_motor_face_y + P.fg_bulkhead_t / 2
    slot_y = (P.fg_box_d / 2 - assembly_y) if top else (
        assembly_y - P.fg_box_d / 2
    )
    slot_depth = P.fg_panel_t + P.fg_joint_clear
    positions = (
        P.fg_bulkhead_keyed_tab_positions
        if top
        else P.fg_bulkhead_tab_positions
    )
    for x in positions:
        body -= Pos(x, slot_y, P.fg_panel_t / 2) * Box(
            P.fg_bulkhead_tab_w + P.fg_joint_tab_end_clear,
            slot_depth,
            P.fg_panel_t + 0.2,
        )
    return body


def side_panel(right: bool = False):
    """Windowed 2 mm side sheet with blind inside-facing nut bosses."""
    body = Pos(0, 0, P.fg_side_t / 2) * Box(
        P.fg_inner_d,
        P.fg_inner_h,
        P.fg_side_t,
    )
    body = _cut_split_windows(
        body,
        center_x=0,
        center_y=0,
        width=P.fg_inner_d - 2 * P.fg_side_frame_x,
        height=P.fg_inner_h - 2 * P.fg_side_frame_y,
        thickness=P.fg_side_t,
        rib_w=P.fg_side_rib_w,
        split_along_x=True,
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
    body = _add_side_bearing_carrier(body, right=right)

    return body


def left_panel():
    return side_panel(right=False)


def right_panel():
    return side_panel(right=True)


def _cut_closure_station(
    body,
    tab_x: float,
    hole_x: float,
    y: float,
    tabs_along_y: bool,
):
    for offset in (-P.fg_joint_tab_pitch / 2, P.fg_joint_tab_pitch / 2):
        dx, dy = (0, offset) if tabs_along_y else (offset, 0)
        slot_w = (
            P.fg_side_t + P.fg_joint_clear
            if tabs_along_y
            else P.fg_joint_tab_w + P.fg_joint_tab_end_clear
        )
        slot_d = (
            P.fg_joint_tab_w + P.fg_joint_tab_end_clear
            if tabs_along_y
            else P.fg_panel_t + P.fg_joint_clear
        )
        body -= Pos(tab_x + dx, y + dy, P.fg_panel_t / 2) * Box(
            slot_w,
            slot_d,
            P.fg_panel_t + 0.2,
        )
    return _cut_m3_hole(body, hole_x, y, P.fg_panel_t)


def horizontal_panel(top: bool = False):
    """Top/bottom skin with stations compensated for the top's flipped pose."""
    body = Pos(0, 0, P.fg_panel_t / 2) * Box(
        P.fg_box_w,
        P.fg_box_d,
        P.fg_panel_t,
    )
    window_y0 = -P.fg_box_d / 2 + P.fg_skin_end_frame_y
    window_y1 = P.fg_box_d / 2 - P.fg_skin_end_frame_y
    assembly_bulkhead_y = P.fg_motor_face_y + P.fg_bulkhead_t / 2
    bulkhead_y = (
        P.fg_box_d / 2 - assembly_bulkhead_y
        if top
        else assembly_bulkhead_y - P.fg_box_d / 2
    )
    rib_half = P.fg_skin_bulkhead_rib_w / 2
    for cut_y0, cut_y1 in (
        (window_y0, bulkhead_y - rib_half),
        (bulkhead_y + rib_half, window_y1),
    ):
        body -= Pos(
            0,
            (cut_y0 + cut_y1) / 2,
            P.fg_panel_t / 2,
        ) * Box(
            P.fg_skin_window_w,
            cut_y1 - cut_y0,
            P.fg_panel_t + 0.2,
        )
    side_stations = (
        (
            -P.fg_box_w / 2 + P.fg_side_t / 2,
            -P.fg_box_w / 2 + P.fg_joint_axis_inset,
        ),
        (
            P.fg_box_w / 2 - P.fg_side_t / 2,
            P.fg_box_w / 2 - P.fg_joint_axis_inset,
        ),
    )
    for tab_x, hole_x in side_stations:
        positions = (
            tuple(-u for u in P.fg_long_joint_positions)
            if top
            else P.fg_long_joint_positions
        )
        for u in positions:
            body = _cut_closure_station(
                body,
                tab_x,
                hole_x,
                u,
                tabs_along_y=True,
            )
    body = _cut_horizontal_bulkhead_slots(body, top=top)
    body = _add_front_center_nut_boss(body, edge_sign=-1 if top else 1)
    if not top:
        for x in (
            -P.fg_box_w / 2 + P.fg_mount_hole_edge_inset,
            P.fg_box_w / 2 - P.fg_mount_hole_edge_inset,
        ):
            for y in (
                -P.fg_box_d / 2 + P.fg_mount_hole_edge_inset,
                P.fg_box_d / 2 - P.fg_mount_hole_edge_inset,
            ):
                body = _cut_m3_hole(body, x, y, P.fg_panel_t)
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
    body = _cut_single_window(
        body,
        width=P.fg_skin_window_w,
        height=P.fg_inner_h - 2 * P.fg_end_frame_y,
        thickness=P.fg_panel_t,
    )
    joint_v = P.fg_front_joint_z if front else 0.0
    side_stations = (
        (
            -P.fg_box_w / 2 + P.fg_side_t / 2,
            -P.fg_box_w / 2 + P.fg_joint_axis_inset,
        ),
        (
            P.fg_box_w / 2 - P.fg_side_t / 2,
            P.fg_box_w / 2 - P.fg_joint_axis_inset,
        ),
    )
    for tab_x, hole_x in side_stations:
        body = _cut_closure_station(
            body,
            tab_x,
            hole_x,
            joint_v,
            tabs_along_y=True,
        )

    if front:
        for axis_z in (
            P.fg_front_center_axis_z,
            P.fg_box_h - P.fg_front_center_axis_z,
        ):
            center_v = axis_z - P.fg_box_h / 2
            body = _cut_m3_hole(
                body,
                0,
                center_v,
                P.fg_panel_t,
            )

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
        edge_v = edge_sign * P.fg_inner_h / 2
        positions = (
            P.fg_bulkhead_keyed_tab_positions
            if edge_sign == 1
            else P.fg_bulkhead_tab_positions
        )
        for u in positions:
            body += Pos(
                u,
                edge_v + edge_sign * P.fg_panel_t / 2,
                P.fg_bulkhead_t / 2,
            ) * Box(P.fg_bulkhead_tab_w, P.fg_panel_t, P.fg_bulkhead_t)

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
