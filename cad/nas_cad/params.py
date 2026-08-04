"""NAS dimensions in millimetres.

The HDD envelope and mounting positions come from SNIA SFF-8301 Rev 1.9.
The SATA connector is deliberately an envelope until a physical backplane
part is selected and measured.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # SFF-8301 Rev 1.9, Table 3-1. Use the largest standard 1-inch drive.
    hdd_w: float = 101.60
    hdd_d: float = 147.00
    hdd_h: float = 26.10
    hdd_bottom_hole_x: float = 3.18
    hdd_bottom_hole_rear_y: float = 41.28
    hdd_bottom_hole_front_y: float = 117.48  # A7 + A13 alternate pair
    hdd_side_hole_rear_y: float = 28.50
    hdd_side_hole_front_y: float = 130.10  # A8 + A9
    hdd_side_hole_z: float = 6.35
    hdd_thread_d: float = 3.5  # visual major diameter of 6-32 UNC
    hdd_hole_depth: float = 3.56

    # Visual construction of a representative modern 3.5-inch HDD.
    hdd_base_h: float = 19.2
    hdd_cover_inset: float = 2.4
    hdd_cover_h: float = 1.2
    hdd_label_d: float = 73.0
    hdd_hub_d: float = 20.0

    # Provisional combined SATA data + power connector envelope.
    sata_w: float = 43.0
    sata_d: float = 7.0
    sata_h: float = 7.2
    sata_right_margin: float = 6.0
    sata_z: float = 2.0
    backplane_pcb_t: float = 1.6
    backplane_w: float = 74.0
    backplane_h: float = 24.0

    # Removable caddy. The drive is retained with four side screws.
    drive_side_clear: float = 0.75
    drive_bottom_clear: float = 1.0
    caddy_floor_t: float = 2.4
    caddy_rail_t: float = 3.0
    caddy_rail_h: float = 12.0
    caddy_front_t: float = 4.0
    caddy_rear_margin: float = 3.0
    caddy_front_overhang: float = 8.0
    caddy_vent_w: float = 14.0
    caddy_vent_d: float = 76.0
    caddy_vent_gap: float = 8.0

    # Front cam lever. Pivot axis is vertical; closed lever spans the bezel.
    latch_t: float = 4.0
    latch_h: float = 9.0
    latch_pivot_d: float = 4.0
    latch_pivot_margin: float = 8.0
    latch_end_margin: float = 8.0
    latch_cam_r: float = 7.0
    latch_open_deg: float = 62.0
    caddy_open_travel: float = 45.0

    # Repeatable bay frame. Open front and rear keep airflow unobstructed.
    bay_wall: float = 3.0
    bay_clear_x: float = 0.65
    bay_clear_z: float = 0.75
    bay_depth: float = 174.0
    bay_front_post_d: float = 12.0
    bay_rear_post_d: float = 14.0
    bay_joiner_d: float = 5.2
    bay_joiner_edge: float = 7.0

    # Default storage block; callers can pass any positive rows/columns.
    bay_columns: int = 2
    bay_rows: int = 3
    bay_array_gap: float = 0.8

    # Bambu Lab P2S advertised build volume.
    printer_x: float = 256.0
    printer_y: float = 256.0
    printer_z: float = 256.0

    @property
    def caddy_inner_w(self) -> float:
        return self.hdd_w + 2 * self.drive_side_clear

    @property
    def caddy_w(self) -> float:
        return self.caddy_inner_w + 2 * self.caddy_rail_t

    @property
    def caddy_d(self) -> float:
        return self.caddy_front_overhang + self.hdd_d + self.caddy_rear_margin

    @property
    def caddy_h(self) -> float:
        return self.caddy_floor_t + self.drive_bottom_clear + self.hdd_h

    @property
    def bay_w(self) -> float:
        return self.caddy_w + 2 * (self.bay_clear_x + self.bay_wall)

    @property
    def bay_h(self) -> float:
        return self.caddy_h + 2 * (self.bay_clear_z + self.bay_wall)


P = Params()
