"""Palm-scale calibration kit for flat-printed mechanical assemblies.

The six strips are three identical cross-lap pairs with 0.10, 0.20 and
0.30 mm total slot clearance. Each pair assembles into a 90-degree crossing;
that tests the same printed-wall fit used by tabs in a panel box.

The separate fastener coupon tests M3 clearance holes (3.2/3.4/3.6 mm) and
short heat-set insert bores (4.0/4.2/4.4 mm), ordered left-to-right. Small
marker holes identify columns and lap pairs: one, two, then three.

Everything is oriented flat on Z=0 and exported as one multi-body STL.
"""

from build123d import Box, Compound, Cylinder, Pos

from splitflap_cad.viewer import Scene

from .params import P


def _lap_strip(clearance: float, marker_count: int):
    """One half of a cross-lap pair, already in print orientation."""
    strip = Pos(0, 0, P.panel_t / 2) * Box(P.lap_len, P.lap_w, P.panel_t)
    slot_w = P.panel_t + clearance
    slot_y = -P.lap_w / 4
    strip -= Pos(0, slot_y, P.panel_t / 2) * Box(
        slot_w,
        P.lap_slot_depth + 0.2,
        P.panel_t + 0.2,
    )

    marker_x0 = -P.lap_len / 2 + 3.0
    for i in range(marker_count):
        strip -= Pos(
            marker_x0 + i * 2.5,
            P.lap_w / 2 - 2.5,
            P.panel_t / 2,
        ) * Cylinder(
            P.lap_marker_d / 2,
            P.panel_t + 0.2,
        )
    return strip


def fastener_coupon():
    """M3 through-hole and broad-face heat-set insert calibration."""
    body = Pos(0, 0, P.panel_t / 2) * Box(
        P.fastener_w,
        P.fastener_h,
        P.panel_t,
    )
    xs = (-P.fastener_pitch, 0.0, P.fastener_pitch)

    for column, (x, insert_d, clearance_d) in enumerate(
        zip(xs, P.insert_bore_ds, P.clearance_hole_ds, strict=True),
        start=1,
    ):
        # A local 7 mm pad lets a short insert sit in a broad face with a
        # meaningful floor. The future panel can use the same local boss.
        body += Pos(
            x,
            P.fastener_row_y,
            P.panel_t + P.fastener_boss_h / 2,
        ) * Cylinder(
            P.fastener_boss_d / 2,
            P.fastener_boss_h,
        )
        body -= Pos(
            x,
            P.fastener_row_y,
            P.fastener_t - P.insert_bore_depth / 2 + 0.1,
        ) * Cylinder(insert_d / 2, P.insert_bore_depth + 0.2)
        body -= Pos(x, -P.fastener_row_y, P.panel_t / 2) * Cylinder(
            clearance_d / 2,
            P.panel_t + 0.2,
        )

        # One/two/three witness holes identify the diameter column after the
        # STL has lost all semantic names.
        marker_x0 = x - (column - 1) * 2.0 / 2
        for i in range(column):
            body -= Pos(marker_x0 + i * 2.0, 0, P.panel_t / 2) * Cylinder(
                P.fastener_marker_d / 2,
                P.panel_t + 0.2,
            )
    return body


def calibration_kit():
    """All coupons laid out as one palm-scale, multi-body print."""
    parts = []
    row_pitch = 2 * P.lap_w + P.lap_pair_gap + P.lap_row_gap
    y0 = -row_pitch
    for row, clearance in enumerate(P.lap_clearances):
        pair_y = y0 + row * row_pitch
        for side in (-1, 1):
            y = pair_y + side * (P.lap_w + P.lap_pair_gap) / 2
            parts.append(Pos(0, y, 0) * _lap_strip(clearance, row + 1))

    laps_top = y0 + 2 * row_pitch + (P.lap_w + P.lap_pair_gap) / 2
    coupon_y = laps_top + P.lap_w / 2 + P.layout_gap + P.fastener_h / 2
    parts.append(Pos(0, coupon_y, 0) * fastener_coupon())
    return Compound(children=parts)


def scene() -> Scene:
    return Scene().add(calibration_kit(), "flatbed-calibration-kit", "coral")
