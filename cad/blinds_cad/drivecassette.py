"""Removable motor/gear cassette and bought layshaft hardware.

The production layshaft is a 5 mm steel rod running in two 625ZZ
bearings.  Cassette plastics and the split bearing caps are added in
the next vertical slice; these reference solids establish the hardware
contract and common unit-coordinate axes first.
"""

import math

from build123d import Align, Box, Cylinder, Pos, Rot
from splitflap_cad.geo import box_between

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


def bearing_625zz():
    """Display-only 625ZZ envelope, local axis +X from x=0..5."""
    outer = _axis_x_cylinder(P.lay_bearing_d / 2, 0, P.lay_bearing_w, 0, 0)
    bore = _axis_x_cylinder(P.lay_rod_d / 2, -0.5, P.lay_bearing_w + 1, 0, 0)
    return outer - bore


def layshaft_rod():
    """Bought 5 mm steel rod in assembled unit coordinates."""
    return _axis_x_cylinder(
        P.lay_rod_d / 2,
        P.lay_rod_x0,
        P.lay_rod_x1 - P.lay_rod_x0,
        P.drive_y,
        P.lay_z,
    )


def _motor_bulkhead():
    """Cassette-owned motor face and left bearing support."""
    from .enclosure import _support_free_cross_bore

    body = box_between(
        P.bulkhead_x,
        P.drive_cassette_back_y,
        P.drive_bulkhead_z0,
        P.bulkhead_x + P.bulkhead_t,
        P.frame_front_y,
        P.frame_z1,
    )
    body -= _support_free_cross_bore(
        P.jgb_boss_d / 2 + 0.75,
        P.bulkhead_t + 2,
        P.bulkhead_x + P.bulkhead_t / 2,
        P.drive_y,
        P.motor_z,
    )
    for index in range(P.jgb_screw_n):
        angle = math.radians(index * 360 / P.jgb_screw_n)
        radius = P.jgb_screw_bcd / 2
        body -= _support_free_cross_bore(
            P.m3_tap_d / 2,
            P.bulkhead_t + 2,
            P.bulkhead_x + P.bulkhead_t / 2,
            P.drive_y + radius * math.cos(angle),
            P.motor_z - P.jgb_ecc + radius * math.sin(angle),
        )
    # The front bearing cap replaces this slice of the old full bulkhead.
    body -= box_between(
        P.lay_bearing_centers_x[0] - P.lay_bearing_boss_w / 2 - 0.2,
        P.drive_y,
        P.lay_z - P.lay_bearing_boss_d / 2 - 4.5,
        P.lay_bearing_centers_x[0] + P.lay_bearing_boss_w / 2 + 0.2,
        P.lay_cap_y1 + 0.2,
        P.lay_z + P.lay_bearing_boss_d / 2 + 4.5,
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
        (P.lay_rod_d + P.lay_rod_clear) / 2,
        x - P.lay_bearing_boss_w / 2 - 0.5,
        P.lay_bearing_boss_w + 1,
        P.drive_y,
        P.lay_z,
    )


def _cap_ears(x: float, y0: float, y1: float, insert: bool):
    ears = None
    ear_x = x + 1.5 if x == P.lay_bearing_centers_x[0] else x
    for z in (P.lay_z - P.lay_cap_ear_offset, P.lay_z + P.lay_cap_ear_offset):
        ear = box_between(
            ear_x - P.lay_cap_ear_d / 2,
            y0,
            z - P.lay_cap_ear_d / 2,
            ear_x + P.lay_cap_ear_d / 2,
            y1,
            z + P.lay_cap_ear_d / 2,
        )
        diameter = P.m3_insert_d if insert else P.lay_cap_clear_d
        depth = P.lay_cap_insert_depth + 0.2 if insert else y1 - y0 + 0.2
        ear -= Pos(ear_x, y1 + 0.1, z) * (
            Rot(90, 0, 0) * Cylinder(diameter / 2, depth)
        )
        ears = ear if ears is None else ears + ear
    return ears


def _bearing_cap(x: float):
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
    cap += _cap_ears(x, P.drive_y, P.lay_cap_y1, insert=False)
    cap -= _bearing_pocket(x)
    cap -= _bearing_shaft_cut(x)
    return cap


def bearing_caps():
    """Two removable front bearing halves in assembled coordinates."""
    return _bearing_cap(P.lay_bearing_centers_x[0]) + _bearing_cap(
        P.lay_bearing_centers_x[1]
    )


def drive_cassette():
    """One-piece motor mount and rear bearing cradle, separate from frame."""
    body = box_between(
        P.cradle_x0,
        P.drive_tab_y0,
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
        P.frame_z1,
    )
    for x in P.lay_bearing_centers_x:
        body += _rear_bearing_boss(x)
        body += _cap_ears(x, P.drive_y - P.lay_cap_insert_depth, P.drive_y, insert=True)
        body -= _bearing_pocket(x)
        body -= _bearing_shaft_cut(x)

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
