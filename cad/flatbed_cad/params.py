"""Flatbed dimensions in millimetres.

The first model is deliberately a calibration print. Its dimensions become
the measured joint vocabulary for the later motor mount and panel box.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # Nominal sheet-like panel construction.
    panel_t: float = 2.0

    # Five base coupons. Only the slot's panel-thickness direction varies;
    # its tab-length direction stays generously clear and is not under test.
    panel_clearances: tuple[float, ...] = (0.10, 0.15, 0.20, 0.25, 0.30)
    clearance_hole_ds: tuple[float, ...] = (3.2, 3.3, 3.4, 3.5, 3.6)
    base_w: float = 24.0
    base_d: float = 24.0
    tab_w: float = 5.0
    tab_len: float = 2.0  # passes through the base and finishes flush
    tab_pitch: float = 12.0
    tab_end_clearance: float = 0.4

    # Five upright coupons. Nominal DIN 934 M3 nuts are about 5.5 mm across
    # flats and 2.4 mm thick; this ladder deliberately brackets both values.
    nut_pocket_ws: tuple[float, ...] = (5.6, 5.7, 5.8, 5.9, 6.0)
    nut_pocket_ds: tuple[float, ...] = (2.5, 2.6, 2.7, 2.8, 2.9)
    upright_w: float = 22.0
    upright_h: float = 22.0
    nut_center_y: float = 4.5  # M3x8 reaches through the 2 mm base and nut
    bolt_stem_w: float = 3.8

    # One-to-five witness holes identify matching values after STL export.
    marker_d: float = 1.2
    marker_pitch: float = 2.2

    # Engraved two-line labels on the upward print face.
    label_font: str = "GeistMono-Medium.ttf"
    label_size: float = 2.5
    label_depth: float = 0.4
    base_label_ys: tuple[float, float] = (8.5, 5.0)
    upright_label_ys: tuple[float, float] = (14.0, 10.5)

    # Ten bodies in two compact print rows.
    coupon_gap: float = 3.0
    row_gap: float = 3.0

    @property
    def coupon_pitch(self) -> float:
        return self.base_w + self.coupon_gap


P = Params()
