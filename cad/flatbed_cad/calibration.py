"""Five-way M3 captive-nut corner calibration for flat-printed panels.

The base coupons test 2 mm panel-slot clearance and M3 through-hole diameter.
The upright coupons test the width and depth of a side-loading rectangular
M3 hex-nut trap. Every base accepts every upright, so the ten printed pieces
provide 25 combinations rather than coupling two independent tolerances.

One through five witness holes identify each ascending variant. Everything in
``calibration_kit`` is oriented flat on Z=0 and exports as one multi-body STL.
"""

from build123d import Box, Compound, Cylinder, Pos

from splitflap_cad.viewer import Scene

from .frames import UPRIGHT_ON_BASE
from .params import P


def _markers(body, count: int, y: float):
    """Cut a centered one-to-five-hole identity mark through a coupon."""
    x0 = -(count - 1) * P.marker_pitch / 2
    for i in range(count):
        body -= Pos(x0 + i * P.marker_pitch, y, P.panel_t / 2) * Cylinder(
            P.marker_d / 2,
            P.panel_t + 0.2,
        )
    return body


def base_coupon(variant: int):
    """Flat base with two wall-tab slots and the vertical M3 bolt hole."""
    clearance = P.panel_clearances[variant]
    body = Pos(0, 0, P.panel_t / 2) * Box(P.base_w, P.base_d, P.panel_t)

    for x in (-P.tab_pitch / 2, P.tab_pitch / 2):
        body -= Pos(x, 0, P.panel_t / 2) * Box(
            P.tab_w + P.tab_end_clearance,
            P.panel_t + clearance,
            P.panel_t + 0.2,
        )
    body -= Pos(0, 0, P.panel_t / 2) * Cylinder(
        P.clearance_hole_ds[variant] / 2,
        P.panel_t + 0.2,
    )
    return _markers(body, variant + 1, -P.base_d / 2 + 3.0)


def upright_coupon(variant: int):
    """Flat wall sample with two tabs and an open-bottom M3 nut trap."""
    body = Pos(0, P.upright_h / 2, P.panel_t / 2) * Box(
        P.upright_w,
        P.upright_h,
        P.panel_t,
    )
    for x in (-P.tab_pitch / 2, P.tab_pitch / 2):
        body += Pos(x, -P.tab_len / 2, P.panel_t / 2) * Box(
            P.tab_w,
            P.tab_len,
            P.panel_t,
        )

    pocket_d = P.nut_pocket_ds[variant]
    pocket_bottom = P.nut_center_y - pocket_d / 2
    body -= Pos(0, P.nut_center_y, P.panel_t / 2) * Box(
        P.nut_pocket_ws[variant],
        pocket_d,
        P.panel_t + 0.2,
    )
    # The bolt rises through this open stem into the nut. Together the stem
    # and rectangular pocket form the classic laser-cut T profile.
    body -= Pos(0, pocket_bottom / 2 - 0.1, P.panel_t / 2) * Box(
        P.bolt_stem_w,
        pocket_bottom + 0.2,
        P.panel_t + 0.2,
    )
    return _markers(body, variant + 1, P.upright_h - 3.0)


def calibration_kit():
    """Five interchangeable bases and uprights in a palm-scale layout."""
    parts = []
    x0 = -2 * P.coupon_pitch
    upright_y = P.base_d / 2 + P.row_gap + P.tab_len
    for variant in range(5):
        x = x0 + variant * P.coupon_pitch
        parts.append(Pos(x, 0, 0) * base_coupon(variant))
        parts.append(Pos(x, upright_y, 0) * upright_coupon(variant))
    return Compound(children=parts)


def assembled_scene() -> Scene:
    """The middle base/upright combination assembled at 90 degrees."""
    variant = 2
    return (
        Scene()
        .add(base_coupon(variant), "base-0.20-slot-3.4-hole", "slategray")
        .add(
            upright_coupon(variant),
            "upright-5.8x2.7-nut-trap",
            "coral",
            loc=UPRIGHT_ON_BASE,
        )
    )


def scene() -> Scene:
    return Scene().add(calibration_kit(), "flatbed-nut-joint-calibration", "coral")
