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

    # --- 21700 cell (Samsung 50E) in Bistook 1-slot PCB holder
    # (BOM #19, Amazon B0BSC61X69 — listing-verified 3.27×0.94×0.86in;
    # caliper on arrival). Holders solder to a battery CARRIER PCB that
    # does the 2S3P busing + balance tap; XT30PW power + JST-XH balance
    # to the main board (#22 adds the connector lines).
    cell_d: float = 21.7
    cell_len: float = 70.6
    cell_n: int = 6                # 2S3P, one full-width stack again in v2
    holder_l: float = 83.1         # along the cell
    holder_w: float = 23.9         # stack direction
    holder_h: float = 21.8         # off the carrier face
    cell_pitch: float = 24.5       # holder_w + 0.6 gap
    carrier_t: float = 1.6
    carrier_y0: float = 8.5        # carrier back face — clears the cleat bar (y<=7)
    carrier_standoff_d: float = 7.0  # M3 heat-set bosses off the back wall

    # --- bead chain (measured: 5mm ball, 6mm pitch) + sprocket (#16) ---
    chain_ball_d: float = 5.0
    chain_pitch: float = 6.0
    chain_cord_d: float = 1.0
    spr_n: int = 12                # pockets
    spr_pocket_d: float = 5.4      # ball + 0.4 print clearance
    spr_groove_w: float = 3.5      # cord groove — continuous joiner relief
    spr_rim_over: float = 0.7      # wheel OR beyond the pitch circle (pocket cup)
    spr_w: float = 8.0             # wheel width
    spr_ball_clear: float = 1.0    # housing channel clearance over balls (#16)
    spr_bore_d: float = 5.2        # plain bore on the fixed M5 cross-axle
    spr_drum_d: float = 10.0       # hollow-ish drum bridging wheel -> ring gear
    axle_d: float = 5.0            # M5 bolt, front wall -> cleat bar

    # --- gear train (all module 2, printed; steel bevels drop in later) ---
    gear_m: float = 2.0
    spur_pinion_z: int = 14        # on the motor D-shaft
    spur_wheel_z: int = 17         # on the layshaft (14:17 = torque up 1.21x)
    spur_w: float = 7.0            # face width, both spurs
    bevel_z: int = 10              # 1:1 miter pair, layshaft -> sprocket ring
    bevel_face: float = 5.0
    lay_shaft_d: float = 8.0       # printed layshaft body
    lay_hub_d: float = 16.0        # bevel-end hub
    saddle_bore: float = 8.4       # U-saddle bores in rib + right block

    # --- enclosure ---
    enc_w: float = 98.0            # <=100 rule
    enc_d: float = 44.0            # accepted off-wall depth (v1 rev B value)
    enc_h: float = 242.0           # PCB floor + 6-cell stack + motor + sprocket
    enc_wall: float = 2.0          # Ø37 in 42 leaves 0.5/side — thin walls are the point
    enc_fillet: float = 4.0        # vertical outer edges
    drive_x: float = 49.0          # chain/sprocket center = enc_w/2
    drive_y: float = 21.0          # motor + layshaft axis depth (mid-cavity)
    motor_z: float = 189.0         # motor SHAFT axis height; eccentric DOWN
                                   # (gearbox axis 182, can 163.5..200.5)
    bulkhead_x: float = 67.0       # gearbox face plane (motor tail lands at x≈4.8)
    bulkhead_t: float = 3.0        # vertical motor-mount rib (6×M3 into it)
    bulkhead_z0: float = 164.0     # rib bottom — clears the carrier top (163.5)
    pinion_x: float = 81.5         # spur mesh plane center (teeth x 78..85)
    saddle_x0: float = 86.0        # right layshaft U-saddle block x span
    saddle_x1: float = 92.0
    collar_x0: float = 8.0         # motor tail collar x span
    collar_x1: float = 14.0
    spr_wy: float = 36.6           # sprocket WHEEL center depth (chain plane y);
                                   # 36.0 grazed the layshaft bevel's heel teeth
                                   # with the wheel's back rim
    guide_or: float = 17.0         # wrap-guide clearance radius envelope
    chain_slot: float = 7.0        # top-face slot square (ball 5 + joiner room)

    # --- battery bay (one 6-holder stack on the carrier) ---
    bay_z0: float = 26.5           # first cell axis — carrier bottom 13.55
                                   # clears the flat PCB's parts (top 13.4)

    # --- main PCB rev C (flat on the floor, components up) ---
    pcb_t: float = 1.6
    pcb_l: float = 88.0            # along the wall (x), spans 5..93
    pcb_wd: float = 32.0           # off the wall (y), spans 8..40
    pcb_z0: float = 6.0            # laminate bottom, on 4x M3 bosses
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

    # --- wall plate + cleat ---
    plate_w: float = 90.0
    plate_h: float = 220.0         # taller unit -> taller plate; rail near top
    plate_t: float = 4.0
    plate_screw_d: float = 4.5     # countersunk for #8
    plate_screw_head: float = 9.0
    plate_screw_inset: float = 10.0
    plate_z0: float = 15.0         # plate bottom in unit z
    cleat_h: float = 12.0          # 45° french-cleat rail height
    cleat_t: float = 6.0
    cleat_rail_top: float = 232.0  # rail top in unit z — ABOVE the motor and
                                   # spur gears; bar y<=7 clears the sprocket
                                   # ring gear (back face y 8.5)
    cleat_x0: float = 11.0         # bar/rail x span — stops short of the
    cleat_x1: float = 76.0         # layshaft spur wheel (x 78..85, od r19)

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
    def cell_axis_y(self) -> float:
        """Cell axis depth: carrier face + holder cradle height."""
        return self.carrier_y0 + self.carrier_t + self.holder_h - self.cell_d / 2

    # gear-train derived geometry
    @property
    def spur_pinion_r(self) -> float:
        return self.gear_m * self.spur_pinion_z / 2  # 14

    @property
    def spur_wheel_r(self) -> float:
        return self.gear_m * self.spur_wheel_z / 2  # 17

    @property
    def bevel_r(self) -> float:
        return self.gear_m * self.bevel_z / 2  # 10

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
