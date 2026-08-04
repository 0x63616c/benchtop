"""Single source of truth for every blinds dimension. Millimetres.

v2 "center-drop" layout (spec 2026-07-26): the bead chain passes
through the CENTER of the unit's width, strands separated left/right
(chain plane parallel to the wall). That forces the sprocket axis out
of the wall (+Y), and the 82mm motor can't be coaxial in 44 of depth,
so the drive is two printed stages: spur pair m2 14:17 off the motor
shaft onto a layshaft, then a 1:1 m2 z10 bevel pair onto the sprocket.

Same rule as splitflap: raw measurements are named constants, anything
positional derives from them. Cosmetic edge breaks <=1mm may inline.

Motor dims come from the ASLONG JGB37-520B factory datasheet
(docs/research/motor-sourcing.md, ticket #15) — caliper-verify on
arrival before printing the shell. Sprocket pocket geometry is ticket
#16's paper decision, unchanged by v2.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # --- JGB37-520B gearmotor (encoder version, 1:90 / 111rpm) ---
    # Local frame: origin = SHAFT axis at the gearbox front face,
    # shaft +Z, body -Z; gearbox axis sits +7 in local +Y (eccentric).
    jgb_gear_d: float = 37.0       # gearbox OD
    jgb_gear_len: float = 24.0     # 1:90 gearbox length (ordered 111rpm)
    jgb_gear_len_alt: float = 26.5  # 60rpm proto variant — clearance uses this
    jgb_ecc: float = 7.0           # shaft axis offset from gearbox axis
    jgb_boss_d: float = 12.0       # front bearing boss around the shaft
    jgb_boss_h: float = 6.0
    jgb_shaft_d: float = 6.0       # D-shaft
    jgb_shaft_flat: float = 5.4    # across the flat
    jgb_shaft_len: float = 15.5    # from the boss face
    jgb_shaft_flat_len: float = 15.5  # full-length flat assumed — CALIPER on arrival;
                                      # the spur pinion rides x78-85, needs flat there
    jgb_can_d: float = 33.0        # 520 motor can
    jgb_can_len: float = 22.7
    jgb_term_len: float = 3.5      # terminal end cap
    jgb_enc_len: float = 12.0      # encoder cap on the rear
    jgb_screw_bcd: float = 31.0    # 6×M3 on the gearbox face
    jgb_screw_n: int = 6
    jgb_screw_d: float = 3.0
    jgb_screw_depth: float = 5.0

    # --- 21700 cell (Samsung 50E) in two owned Bistook 3-slot holders ---
    cell_d: float = 21.7
    cell_len: float = 70.6
    cell_n: int = 6                # 2S3P

    # --- owned Bistook 3-slot holders (two per unit) ---
    # Supplier drawing + owner measurements, 2026-08-03.  The plastic
    # back has one centred 4.2 mm hole per cell slot.  Metal contacts can
    # stand 4 mm proud but fold flat into the room-side wiring cavity.
    holder3_l: float = 83.00
    holder3_h: float = 66.59
    holder3_body_d: float = 14.51
    holder3_contact_d: float = 21.80
    holder3_slot_pitch: float = 21.39
    holder3_slot_edge: float = 11.90
    holder3_hole_d: float = 4.20
    holder3_gap: float = 3.00
    battery_z0: float = 17.00       # lower holder bottom; PCB parts end at 13.4
    battery_mount_y: float = 8.50   # holder plastic back / printed rail face
    battery_mount_depth: float = 8.50
    battery_mount_spine_w: float = 10.0
    battery_mount_spine_z0: float = 8.0
    battery_mount_spine_z1: float = 153.18
    battery_boss_d: float = 8.0
    battery_insert_depth: float = 4.5

    # --- bead chain (measured: 5mm ball, 6mm pitch) + sprocket (#16) ---
    chain_ball_d: float = 5.0
    chain_pitch: float = 6.0
    chain_cord_d: float = 1.0
    spr_n: int = 12                # pockets
    spr_pocket_d: float = 5.4      # ball + 0.4 print clearance
    spr_groove_w: float = 3.5      # cord groove — continuous joiner relief
    spr_rim_over: float = 0.7      # wheel OR beyond the pitch circle (pocket cup)
    spr_w: float = 6.4             # wheel width; 5 mm beads + 0.7 mm side rims
    spr_ball_clear: float = 1.5    # housing channel clearance per ball side (#16)
    spr_ring_back_d: float = 12.0  # hidden inside tooth roots; no outer skirt seam
    spr_ring_back_t: float = 1.2
    spr_ring_back_overlap: float = 0.4
    spr_bevel_hub_d: float = 8.0   # torque hub; stays inside crossing bevel
    spr_bevel_hub_z0: float = -1.5
    spr_bevel_pin_z: float = 0.0   # transverse guide exits only through hub sides
    spr_shaft_d: float = 5.0       # bought smooth steel shaft, not a printed axle
    spr_shaft_clear: float = 0.2
    spr_shaft_y0: float = 3.0
    spr_shaft_len: float = 40.0
    spr_bearing_d: float = 10.0    # two MR105ZZ bearings, 5x10x4 mm
    spr_bearing_w: float = 4.0
    spr_bearing_clear: float = 0.2
    spr_bearing_centers_y: tuple = (5.6, 40.5)
    spr_pin_guide_d: float = 2.2
    spr_wheel_pin_len: float = 14.0
    spr_bevel_pin_len: float = 14.0
    spr_spacer_d: float = 8.0
    spr_spacer_print_pitch: float = 12.0

    # --- gear train (all module 2, printed; steel bevels drop in later) ---
    gear_m: float = 2.0
    spur_pinion_z: int = 14        # on the motor D-shaft
    spur_wheel_z: int = 17         # on the layshaft (14:17 = torque up 1.21x)
    spur_w: float = 7.0            # face width, both spurs
    bevel_z: int = 10              # 1:1 miter pair, layshaft -> sprocket ring
    bevel_face: float = 5.0
    gear_backlash: float = 0.05  # coefficient of module per py_gearworks gear
    gear_hub_d: float = 12.0
    gear_hub_len: float = 3.0
    pinion_grub_pilot_d: float = 2.6
    lay_pin_guide_d: float = 2.2
    lay_spur_pin_len: float = 12.0
    lay_bevel_pin_len: float = 14.0
    gear_print_radial_growth: float = 0.7  # 55deg bed-facing envelope

    # Production layshaft: bought 5 mm rod in two 625ZZ bearings.  The
    # old Ø8 printed shaft becomes separate pinned gears + spacers.
    lay_rod_d: float = 5.0
    lay_rod_clear: float = 0.2
    lay_rod_x0: float = 54.0
    lay_rod_x1: float = 92.5
    lay_bearing_d: float = 16.0
    lay_bearing_w: float = 5.0
    lay_bearing_clear: float = 0.2
    lay_bearing_centers_x: tuple = (69.0, 89.0)

    # --- enclosure ---
    enc_w: float = 98.0            # <=100 rule
    enc_d: float = 44.0            # accepted off-wall depth (v1 rev B value)
    enc_h: float = 242.0           # PCB floor + 6-cell stack + motor + sprocket
    enc_wall: float = 2.0          # Ø37 in 42 leaves 0.5/side — thin walls are the point
    drive_x: float = 49.0          # chain/sprocket center = enc_w/2
    drive_y: float = 21.0          # motor + layshaft axis depth (mid-cavity)
    motor_z: float = 189.0         # motor SHAFT axis height; eccentric DOWN
                                   # (gearbox axis 182, can 163.5..200.5)
    bulkhead_x: float = 67.0       # gearbox face plane (motor tail lands at x≈4.8)
    bulkhead_t: float = 3.0        # vertical motor-mount rib (6×M3 into it)
    bulkhead_z0: float = 164.0     # rib bottom — clears battery holders (153.18)
    pinion_x: float = 81.5         # spur mesh plane center (teeth x 78..85)
    saddle_x0: float = 86.0        # right layshaft U-saddle block x span
    saddle_x1: float = 92.0
    cradle_x0: float = 8.0         # support-free motor tail cradle x span
    cradle_x1: float = 14.0
    cradle_shell: float = 2.0      # material beyond the motor pocket
    spr_wy: float = 34.8           # chain-wheel center depth; its rear face clears
                                   # the separate layshaft bevel by 0.8 mm
    guide_or: float = 17.0         # wrap-guide clearance radius envelope
    chain_slot: float = 8.0        # ball 5 + 1.5 mm running clearance per side

                                   # clears the flat PCB's parts (top 13.4)

    # --- main PCB rev C (flat on the floor, components up) ---
    pcb_t: float = 1.6
    pcb_l: float = 88.0            # along the wall (x), spans 5..93
    pcb_wd: float = 32.0           # off the wall (y), spans 8..40
    pcb_z0: float = 6.0            # on 3x M3 bosses + plain USB-edge pillar
    pcb_boss_h: float = 4.0
    pcb_comp_h: float = 5.8        # component envelope above the laminate —
                                   # XH-2.5 housings (5.75) are the ceiling;
                                   # they stay under the holder stack (14.05)
    pcb_comp_inset: float = 1.5    # envelope inset from the board outline
    pcb_comp_front_inset: float = 6.0  # front strip is the buttons'/USB's own
    # M3 holes + bosses, UNIT coords (= board holes in tools/place_and_render:
    # unit x = board x + 5, unit y = 40 - board y). The 4th corner is the
    # MCU/antenna — no screw; a plain pillar under the USB edge instead.
    pcb_holes: tuple = ((90.0, 36.0), (9.0, 13.0), (90.0, 13.0))
    pcb_pillar: tuple = (49.0, 38.0)

    # buttons: KH-6X6X7H right-angle 6x6 tactile (BOM line C2837543 —
    # v1 flagged it as the wrong variant; flat-board v2 makes it RIGHT),
    # bodies at the board's front edge, plungers +Y through the front wall
    btn_body: float = 6.2          # 6x6 face, vertical in v2
    btn_body_t: float = 3.6        # body depth along the plunger
    btn_plunger_d: float = 3.5
    btn_plunger_len: float = 3.4   # body face -> tip
    btn_d: float = 5.0             # front-wall hole Ø
    btn_x1: float = 38.0           # DOWN
    btn_x2: float = 60.0           # UP

    # USB-C: TYPE-C-31-M-12 right-angle SMD, mouth +Y through the
    # front wall beside the buttons
    usb_body_w: float = 8.94       # across the board (x in v2)
    usb_body_l: float = 7.35       # along the plunge direction (y)
    usb_body_h: float = 3.26       # off the board face (z in v2)
    usb_w: float = 9.2             # front-wall slot, across (x)
    usb_t: float = 3.8             # front-wall slot, tall (z)
    usb_x: float = 49.0            # receptacle center, between the buttons

    # --- wall-mounted exoskeleton + cosmetic cover ---
    # The frame prints wall-face down and owns every mechanical load.
    # The open-back sleeve prints front-face down and carries no load.
    frame_t: float = 3.0           # wall-side structural rail thickness
    frame_rail_w: float = 8.0      # perimeter/cross-rail width in X/Z
    frame_x0: float = 4.0
    frame_x1: float = 94.0
    frame_z0: float = 4.0
    frame_z1: float = 238.0
    frame_wall_holes: tuple = ((8.0, 45.0), (90.0, 45.0),
                               (18.0, 234.0), (80.0, 234.0))
    frame_cross_rails_z: tuple = (80.0, 150.0)
    frame_load_spines_x: tuple = (32.0, 62.0)
    frame_load_spine_depths: tuple = (3.0, 2.3)  # right clears gearbox rear
    frame_tray_z0: float = 2.0
    frame_tray_z1: float = 4.5
    saddle_y1: float = 29.0
    saddle_z0: float = 213.0

    cassette_half_w: float = 17.0
    cassette_wheel_axial_clear: float = 1.0
    cassette_wheel_radial_clear: float = 1.2
    cassette_ring_radial_clear: float = 2.0
    cassette_layshaft_radial_clear: float = 3.6
    cassette_layshaft_tunnel_l: float = 36.0
    drive_removal_step: float = 2.0

    keeper_y0: float = 38.3        # removable front MR105 bearing cap starts here
    keeper_z0: float = 203.0
    keeper_z1: float = 240.5
    keeper_outer_half_w: float = 20.0
    keeper_side_rib: float = 3.0
    # Explicit points avoid the chain channels: the upper pair moves inward
    # while the lower pair stays outside the sprocket's swept envelope.
    keeper_screw_points: tuple = (
        (37.0, 207.0),
        (61.0, 207.0),
        (46.0, 236.5),
        (52.0, 236.5),
    )
    keeper_screw_d: float = 3.4
    keeper_tap_boss_d: float = 6.0
    keeper_fit: float = 0.3        # recess clearance around removable keeper
    keeper_hole_ligament: float = 2.0
    keeper_tap_depth: float = 8.0
    keeper_rim: float = 4.0

    m3_tap_d: float = 2.6
    m3_insert_d: float = 4.6
    pcb_boss_d: float = 7.0
    pcb_pillar_d: float = 6.0

    sleeve_t: float = 0.8          # two 0.4mm lines; cosmetic only
    sleeve_h: float = 240.5        # open top; caps finish at enc_h
    sleeve_fit: float = 0.4        # frame-to-sleeve running clearance
    sleeve_guide_bands: tuple = ((18.0, 28.0), (140.0, 150.0))
    sleeve_guide_embed: float = 3.0  # root width inside each side rail
    sleeve_retainer_xy: tuple = ((18.0, 4.5), (80.0, 4.5))
    sleeve_retainer_d: float = 3.4 # M3 clearance in the sleeve bottom
    sleeve_retainer_boss_d: float = 7.0
    sleeve_retainer_boss_h: float = 7.0

    # Removable motor/gear cassette.  The frame presents four M3 insert
    # pads at y=6; the cassette begins 0.4 mm in front and can be removed
    # without reprinting the wall skeleton.
    drive_mount_face_y: float = 6.0
    drive_mount_points: tuple = (
        (18.0, 6.0, 158.0),
        (80.0, 6.0, 158.0),
        (69.0, 6.0, 202.0),
        (89.0, 6.0, 202.0),
    )
    drive_mount_boss_d: float = 8.0
    drive_mount_clear_d: float = 3.4
    drive_mount_insert_depth: float = 4.5
    drive_cassette_fit: float = 0.4
    drive_tab_y0: float = 6.4
    drive_tab_y1: float = 12.0
    drive_lower_z0: float = 154.0
    drive_lower_z1: float = 162.0
    drive_cassette_back_y: float = 3.4
    drive_bulkhead_z0: float = 160.0
    drive_housing_bridge_overlap: float = 2.0
    lay_bearing_boss_d: float = 20.0
    lay_bearing_boss_w: float = 6.0
    lay_bearing_pocket_w: float = 5.2
    lay_cap_y1: float = 31.0
    lay_cap_ear_offset: float = 12.5
    lay_cap_ear_d: float = 8.0
    lay_cap_clear_d: float = 3.4
    lay_cap_insert_depth: float = 4.5
    drive_running_gap: float = 0.2
    lay_spacer_d: float = 8.0
    motor_spacer_d: float = 10.0
    motor_spacer_bore_d: float = 6.2
    drive_spacer_print_pitch: float = 14.0

    cap_t: float = 1.2
    cap_skirt: float = 4.0
    cap_fit: float = 0.3
    cap_lap: float = 2.0           # assembly allowance at the chain-plane seam

    wall_screw_d: float = 4.5      # direct frame anchors for #8 screws

    # --- derived ---
    @property
    def spr_pcd(self) -> float:
        """Pitch circle: n pockets × chain pitch laid on the circumference."""
        return self.spr_n * self.chain_pitch / math.pi  # ≈22.92

    @property
    def spr_od(self) -> float:
        return self.spr_pcd + 2 * self.spr_rim_over

    @property
    def jgb_body_len(self) -> float:
        """Encoder rear -> gearbox face (≈62.2)."""
        return self.jgb_gear_len + self.jgb_can_len + self.jgb_term_len + self.jgb_enc_len

    @property
    def battery_mount_points(self) -> tuple:
        """Six M3 insert centres matching the bought holders' 4.2 mm holes."""
        return tuple(
            (
                self.drive_x,
                self.battery_mount_y,
                self.battery_z0
                + bank * (self.holder3_h + self.holder3_gap)
                + self.holder3_slot_edge
                + slot * self.holder3_slot_pitch,
            )
            for bank in range(2)
            for slot in range(3)
        )

    # gear-train derived geometry
    @property
    def spur_pinion_r(self) -> float:
        return self.gear_m * self.spur_pinion_z / 2  # 14

    @property
    def spur_pinion_phase(self) -> float:
        """Half-tooth clocking after the motor/lay axes oppose in-unit."""
        return 180 / self.spur_pinion_z

    @property
    def spur_wheel_r(self) -> float:
        return self.gear_m * self.spur_wheel_z / 2  # 17

    @property
    def bevel_r(self) -> float:
        return self.gear_m * self.bevel_z / 2  # 10

    @property
    def bevel_ring_phase(self) -> float:
        """Half-tooth clocking after the miter pair is reframed in-unit."""
        return 180 / self.bevel_z

    @property
    def lay_z(self) -> float:
        """Layshaft axis height = spur mesh center distance above the motor."""
        return self.motor_z + self.spur_pinion_r + self.spur_wheel_r  # 220

    @property
    def spr_z(self) -> float:
        """Sprocket axis height — the layshaft IS the sprocket-axis plane
        (bevel apex at (drive_x, drive_y, lay_z))."""
        return self.lay_z

    @property
    def bevel_heel_x(self) -> float:
        """Layshaft bevel heel plane: bevel_r right of the apex."""
        return self.drive_x + self.bevel_r  # 59

    @property
    def ring_heel_y(self) -> float:
        """Sprocket ring-gear heel plane: bevel_r wall-side of the apex."""
        return self.drive_y - self.bevel_r  # 11

    @property
    def frame_front_y(self) -> float:
        """Front face of the frame, behind the cosmetic sleeve."""
        return self.enc_d - self.sleeve_t - self.sleeve_fit  # 42.8

    @property
    def strand_x(self) -> tuple:
        """The two vertical chain-run x positions (left/right of center)."""
        r = self.spr_pcd / 2
        return (self.drive_x - r, self.drive_x + r)

    @property
    def pcb_x0(self) -> float:
        return (self.enc_w - self.pcb_l) / 2  # 5

    @property
    def pcb_y0(self) -> float:
        return 8.0  # front edge lands at 40, 2 shy of the wall for the rim

    @property
    def pcb_top(self) -> float:
        return self.pcb_z0 + self.pcb_t  # 7.6

    @property
    def btn_z(self) -> float:
        """Plunger axis height: 6x6 face center above the laminate."""
        return self.pcb_top + self.btn_body / 2 + 0.5  # 11.2-ish

    @property
    def usb_z(self) -> float:
        """Receptacle body center height."""
        return self.pcb_top + self.usb_body_h / 2


P = Params()
