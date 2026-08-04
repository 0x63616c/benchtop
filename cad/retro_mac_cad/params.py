"""Retro Mac dimensions in millimetres.

The exterior follows the Macintosh Plus proportions at a 12.9 / 9 scale.
The device envelope is the bare 2020 iPad Pro 12.9-inch (4th generation).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # Published Macintosh Plus envelope and display diagonal.
    mac_h: float = 13.6 * 25.4
    mac_w: float = 9.6 * 25.4
    mac_d: float = 10.9 * 25.4
    mac_display_diag: float = 9.0

    # Published iPad Pro 12.9-inch (4th generation) envelope.
    ipad_w: float = 280.6  # landscape width
    ipad_h: float = 214.9  # landscape height
    ipad_t: float = 5.9
    ipad_corner_r: float = 9.0
    display_px_w: int = 2732
    display_px_h: int = 2048
    display_ppi: float = 264.0
    display_corner_r: float = 10.0

    # Conservative rear-camera envelope. It clears the 4th-generation square
    # camera island; verify against the physical iPad before the final print.
    camera_w: float = 35.0
    camera_h: float = 35.0
    camera_extra_t: float = 2.8
    camera_edge_inset: float = 9.0

    # P2S and printed fit allowances.
    printer_x: float = 256.0
    printer_y: float = 256.0
    printer_z: float = 256.0
    skin_t: float = 3.0
    shell_fit: float = 0.35
    ipad_side_clear: float = 0.55
    ipad_depth_clear: float = 0.55

    # Exterior character and the original front/rear service-seam strategy.
    case_corner_r: float = 24.0
    rear_top_slope: float = 34.0
    front_section_d: float = 150.0
    seam_lip: float = 8.0
    seam_lip_t: float = 2.0

    # Screen placement: display centre high on the front, like a compact Mac.
    screen_top_margin: float = 58.0
    floppy_w: float = 78.0
    floppy_h: float = 5.0
    floppy_x: float = 78.0
    floppy_z: float = 103.0
    speaker_hole_d: float = 3.2
    speaker_x: float = 89.0
    speaker_z: float = 139.0

    # The iPad screen is just behind the front skin. The rail is deliberately
    # shorter than the insertion path so each L-shaped half fits the P2S.
    ipad_front_y: float = -3.8
    rail_w: float = 11.0
    rail_lip: float = 2.0
    rail_lip_t: float = 1.6
    bottom_ledge_h: float = 6.0
    rail_above_ipad: float = 8.0
    mount_arm_w: float = 14.0
    cap_t: float = 3.0
    cap_plug_h: float = 2.5
    cap_center_gap: float = 0.5

    @property
    def scale(self) -> float:
        return 12.9 / self.mac_display_diag

    @property
    def case_w(self) -> float:
        return self.mac_w * self.scale

    @property
    def case_h(self) -> float:
        return self.mac_h * self.scale

    @property
    def case_d(self) -> float:
        return self.mac_d * self.scale

    @property
    def display_w(self) -> float:
        return self.display_px_w / self.display_ppi * 25.4

    @property
    def display_h(self) -> float:
        return self.display_px_h / self.display_ppi * 25.4

    @property
    def screen_z(self) -> float:
        return self.case_h - self.screen_top_margin - self.display_h / 2

    @property
    def ipad_bottom_z(self) -> float:
        return self.screen_z - self.ipad_h / 2

    @property
    def ipad_top_z(self) -> float:
        return self.screen_z + self.ipad_h / 2

    @property
    def ipad_back_y(self) -> float:
        return self.ipad_front_y - self.ipad_t

    @property
    def camera_back_y(self) -> float:
        return self.ipad_back_y - self.camera_extra_t

    @property
    def pocket_half_w(self) -> float:
        return self.ipad_w / 2 + self.ipad_side_clear

    @property
    def slot_y0(self) -> float:
        return self.camera_back_y - self.ipad_depth_clear

    @property
    def slot_y1(self) -> float:
        return self.ipad_front_y + self.ipad_depth_clear

    @property
    def rail_bottom_z(self) -> float:
        return self.ipad_bottom_z - self.ipad_side_clear - self.bottom_ledge_h

    @property
    def rail_top_z(self) -> float:
        return self.ipad_top_z + self.rail_above_ipad


P = Params()
