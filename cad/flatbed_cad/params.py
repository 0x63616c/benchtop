"""Flatbed dimensions in millimetres.

The first model is deliberately a calibration print. Its dimensions become
the measured joint vocabulary for the later motor mount and panel box.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # Nominal sheet-like panel construction.
    panel_t: float = 5.0

    # Cross-lap coupons. Clearance is the total slot oversize, not per side.
    lap_len: float = 50.0
    lap_w: float = 14.0
    lap_clearances: tuple[float, ...] = (0.10, 0.20, 0.30)
    lap_marker_d: float = 1.5
    lap_pair_gap: float = 2.0
    lap_row_gap: float = 3.0

    # M3 fastener coupon. These are starting values spanning the repo's
    # existing 4.2 mm M3 heat-set bore idiom. The intended insert is a short
    # M3 insert installed from the broad printed face, never into a 5 mm edge.
    fastener_w: float = 70.0
    fastener_h: float = 28.0
    fastener_boss_h: float = 2.0
    fastener_boss_d: float = 10.0
    insert_bore_ds: tuple[float, ...] = (4.0, 4.2, 4.4)
    insert_bore_depth: float = 4.5
    clearance_hole_ds: tuple[float, ...] = (3.2, 3.4, 3.6)
    fastener_pitch: float = 22.0
    fastener_row_y: float = 7.0
    fastener_marker_d: float = 1.2

    # One compact, palm-scale print layout.
    layout_gap: float = 3.0

    @property
    def lap_slot_depth(self) -> float:
        return self.lap_w / 2

    @property
    def fastener_t(self) -> float:
        return self.panel_t + self.fastener_boss_h


P = Params()
