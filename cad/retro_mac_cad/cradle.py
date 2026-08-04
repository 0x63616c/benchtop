"""Two-piece top-loading iPad cradle and removable slot caps.

The cradle carries the device independently of the cosmetic shell. Each half
is an L-shaped side rail plus half of the bottom ledge; no printed dimension
exceeds the P2S envelope. Thin felt or TPU tape belongs on the contact faces.
"""

from build123d import Box, Pos
from splitflap_cad.geo import box_between

from .params import P


def _cradle_half(side: int):
    pocket_x = side * P.pocket_half_w
    outer_x = side * (P.pocket_half_w + P.rail_w)
    x0, x1 = sorted((pocket_x, outer_x))
    y0 = P.slot_y0 - P.rail_lip_t
    y1 = P.slot_y1 + P.rail_lip_t

    # Side wall and front/rear lips form a non-pinching sliding channel.
    body = box_between(x0, y0, P.rail_bottom_z, x1, y1, P.rail_top_z)
    lip_inner = side * (P.ipad_w / 2 - P.rail_lip)
    lx0, lx1 = sorted((outer_x, lip_inner))
    body += box_between(
        lx0,
        P.ipad_front_y + P.ipad_depth_clear,
        P.ipad_bottom_z - P.ipad_side_clear,
        lx1,
        P.slot_y1 + P.rail_lip_t,
        P.rail_top_z,
    )
    body += box_between(
        lx0,
        y0,
        P.ipad_bottom_z - P.ipad_side_clear,
        lx1,
        P.slot_y0,
        P.rail_top_z,
    )

    # Half-width bottom ledge supports the iPad without creating a >256 mm bar.
    ledge_inner = -P.cap_center_gap / 2 if side < 0 else P.cap_center_gap / 2
    bx0, bx1 = sorted((outer_x, ledge_inner))
    body += box_between(
        bx0,
        y0,
        P.rail_bottom_z,
        bx1,
        y1,
        P.ipad_bottom_z - P.ipad_side_clear,
    )

    # Two short mounting arms reach the inner side skins, leaving the display
    # opening and insertion path completely unobstructed.
    arm_outer = side * (P.case_w / 2 - P.skin_t - P.shell_fit)
    ax0, ax1 = sorted((outer_x, arm_outer))
    for z in (P.ipad_bottom_z + 25.0, P.ipad_top_z - 25.0):
        body += box_between(
            ax0,
            y0,
            z - P.mount_arm_w / 2,
            ax1,
            y0 + P.mount_arm_w,
            z + P.mount_arm_w / 2,
        )
    return body


def cradle_left():
    return _cradle_half(-1)


def cradle_right():
    return _cradle_half(1)


def _slot_cap(side: int):
    half_w = P.pocket_half_w - P.cap_center_gap / 2
    x = side * (P.cap_center_gap / 2 + half_w / 2)
    width = half_w
    cap = Pos(x, (P.slot_y0 + P.slot_y1) / 2, P.case_h - P.cap_t / 2) * Box(
        width,
        P.slot_y1 - P.slot_y0,
        P.cap_t,
    )
    plug = Pos(x, (P.slot_y0 + P.slot_y1) / 2, P.case_h - P.cap_t - P.cap_plug_h / 2) * Box(
        width - 0.8,
        P.slot_y1 - P.slot_y0 - 0.8,
        P.cap_plug_h,
    )
    return cap + plug


def slot_cap_left():
    return _slot_cap(-1)


def slot_cap_right():
    return _slot_cap(1)


def scene():
    from splitflap_cad.viewer import Scene

    return (
        Scene()
        .add(cradle_left(), "cradle-left", color="goldenrod")
        .add(cradle_right(), "cradle-right", color="darkgoldenrod")
        .add(slot_cap_left(), "slot-cap-left", color="gainsboro")
        .add(slot_cap_right(), "slot-cap-right", color="lightgray")
    )
