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
    label_size: float = 5.0
    label_depth: float = 0.4
    base_label_ys: tuple[float, float] = (8.5, 4.0)
    upright_label_ys: tuple[float, float] = (14.0, 9.0)

    # Separate broad-face heat-set-insert test for the user's 3 mm-long M3
    # inserts. Blind bores leave a solid floor so installation matches a part.
    insert_plate_w: float = 76.0
    insert_plate_h: float = 24.0
    insert_plate_t: float = 5.0
    insert_bore_ds: tuple[float, ...] = (4.0, 4.1, 4.2, 4.3, 4.4)
    insert_bore_depth: float = 3.4
    insert_pitch: float = 14.0
    insert_hole_y: float = 1.0
    insert_label_y: float = -7.0
    insert_title_y: float = 9.0

    # Ten bodies in two compact print rows.
    coupon_gap: float = 3.0
    row_gap: float = 3.0

    @property
    def coupon_pitch(self) -> float:
        return self.base_w + self.coupon_gap

    @property
    def insert_floor_t(self) -> float:
        return self.insert_plate_t - self.insert_bore_depth

    # --- enclosed JGB37 right-angle speed gearbox ---
    # The motor dimensions match the existing 24 mm-L repo reference. The
    # encoder/terminal stack is one conservative cylindrical envelope until
    # the user's exact board and connector are measured.
    fg_motor_gear_d: float = 37.0
    fg_motor_gear_len: float = 24.0
    fg_motor_can_d: float = 33.0
    fg_motor_can_len: float = 26.2
    fg_motor_encoder_len: float = 12.0
    fg_motor_ecc: float = 7.0
    fg_motor_boss_d: float = 12.0
    fg_motor_boss_h: float = 6.0
    fg_motor_shaft_d: float = 6.0
    fg_motor_shaft_flat: float = 5.4
    fg_motor_shaft_len: float = 15.5
    fg_motor_screw_bcd: float = 31.0
    fg_motor_screw_n: int = 6
    fg_motor_screw_d: float = 3.0
    fg_motor_screw_depth: float = 5.0

    # Minimal six-sided envelope. X=width, Y=motor axis from rear to front,
    # Z=height/output axis. The 2 mm skin uses the selected three-dot
    # T-slot settings; the internal motor bulkhead is locally reinforced.
    fg_box_w: float = 43.0
    fg_box_d: float = 91.0
    fg_box_h: float = 43.0
    fg_panel_t: float = 2.0
    fg_rear_clear: float = 0.8
    fg_joint_clear: float = 0.20
    fg_joint_hole_d: float = 3.4
    fg_joint_nut_w: float = 5.8
    fg_joint_nut_d: float = 2.7
    fg_joint_nut_inset: float = 4.5
    fg_joint_stem_w: float = 3.5
    fg_joint_tab_w: float = 5.0
    fg_joint_tab_pitch: float = 12.0
    fg_joint_tab_end_clear: float = 0.4
    # Both top/bottom closure stations sit behind the motor bulkhead. Keeping
    # them out of the drive bay prevents their bolts and nuts touching it.
    fg_long_joint_positions: tuple[float, ...] = (-24.0, 0.0)
    fg_front_joint_z: float = 8.0

    # Internal motor mounting bulkhead: 2 mm sheet plus a 3 mm circular
    # reinforcement on the gear side. Four edge tabs locate it in the skins.
    fg_bulkhead_t: float = 2.0
    fg_bulkhead_reinforce: float = 3.0
    fg_bulkhead_tab_w: float = 5.0
    fg_bulkhead_tab_positions: tuple[float, ...] = (-12.0, 12.0)
    fg_motor_mount_clear_d: float = 3.4
    fg_motor_boss_clear_d: float = 12.4

    # Replaceable 24:12 bevel cartridge. This is a 2x speed increase:
    # output_rpm / motor_rpm = input_teeth / output_teeth = 2.
    fg_gear_module: float = 1.0
    fg_input_teeth: int = 24
    fg_output_teeth: int = 12
    fg_gear_face: float = 4.0
    fg_gear_backlash: float = 0.12
    fg_motor_gear_gap: float = 0.7
    fg_gear_hub_d: float = 10.0
    fg_gear_hub_len: float = 4.0
    fg_output_hub_len: float = 2.5
    fg_gear_print_radial_growth: float = 0.7
    fg_gear_running_gap: float = 0.2

    # The one-sided 5 mm output rod begins clear of the motor shaft, passes
    # through the output gear, and exits through one top-side 625ZZ bearing.
    fg_output_shaft_d: float = 5.0
    fg_output_bore_d: float = 5.2
    fg_output_exposed: float = 10.0
    fg_bearing_d: float = 16.0
    fg_bearing_w: float = 5.0
    fg_bearing_clear: float = 0.2
    fg_bearing_carrier_d: float = 18.5
    fg_bearing_carrier_t: float = 6.0
    fg_bearing_shoulder: float = 0.8

    # Rear cable exit; the box remains closed on all six sides around it.
    fg_wire_exit_w: float = 24.0
    fg_wire_exit_h: float = 14.0

    @property
    def fg_motor_body_len(self) -> float:
        return (
            self.fg_motor_gear_len
            + self.fg_motor_can_len
            + self.fg_motor_encoder_len
        )

    @property
    def fg_motor_face_y(self) -> float:
        return self.fg_panel_t + self.fg_rear_clear + self.fg_motor_body_len

    @property
    def fg_motor_axis_x(self) -> float:
        return self.fg_box_w / 2 - 0.5

    @property
    def fg_shaft_z(self) -> float:
        return 15.0

    @property
    def fg_motor_center_z(self) -> float:
        return self.fg_shaft_z + self.fg_motor_ecc

    @property
    def fg_output_speed_ratio(self) -> float:
        return self.fg_input_teeth / self.fg_output_teeth

    @property
    def fg_input_pitch_r(self) -> float:
        return self.fg_gear_module * self.fg_input_teeth / 2

    @property
    def fg_output_pitch_r(self) -> float:
        return self.fg_gear_module * self.fg_output_teeth / 2

    @property
    def fg_inner_w(self) -> float:
        return self.fg_box_w - 2 * self.fg_panel_t

    @property
    def fg_inner_d(self) -> float:
        return self.fg_box_d - 2 * self.fg_panel_t

    @property
    def fg_inner_h(self) -> float:
        return self.fg_box_h - 2 * self.fg_panel_t


P = Params()
