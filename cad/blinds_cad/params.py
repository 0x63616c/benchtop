"""Single source of truth for every blinds dimension. Millimetres.

Same rule as splitflap: raw measurements are named constants, anything
positional derives from them. Cosmetic edge breaks <=1mm may inline.

Motor dims come from the ASLONG JGB37-520B factory datasheet
(docs/research/motor-sourcing.md, ticket #15) — caliper-verify on
arrival before printing the shell. Sprocket dims are ticket #16's
paper decision. Cell-contact and PCB dims are ENVELOPES until the BOM
ticket (#19) pins real parts.
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
                                      # sprocket bore rides x80–94, needs flat there
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
    cell_n: int = 6                # 2S3P
    holder_l: float = 83.1         # along the cell
    holder_w: float = 23.9         # stack direction
    holder_h: float = 21.8         # off the carrier face
    cell_pitch: float = 24.5       # holder_w + 0.6 gap
    carrier_t: float = 1.6
    carrier_y0: float = 8.5        # carrier back face — clears the cleat hook bar (y<=8)
    carrier_standoff_d: float = 7.0  # M3 heat-set bosses off the back wall

    # --- bead chain (measured: 5mm ball, 6mm pitch) + sprocket (#16) ---
    chain_ball_d: float = 5.0
    chain_pitch: float = 6.0
    chain_cord_d: float = 1.0
    spr_n: int = 12                # pockets
    spr_pocket_d: float = 5.4      # ball + 0.4 print clearance
    spr_groove_w: float = 3.5      # cord groove — continuous joiner relief
                                   # (#16's per-gap 3.5×8 reliefs overlap: 12×8
                                   # > 72mm circumference, so continuous IS the spec)
    spr_rim_over: float = 0.7      # wheel OR beyond the pitch circle (pocket cup)
    spr_w: float = 8.0             # wheel width
    spr_hub_d: float = 14.0
    spr_hub_len: float = 6.0       # hub boss on the motor side
    spr_bore_d: float = 6.2        # D-shaft bore
    spr_bore_flat: float = 5.55
    spr_ball_clear: float = 1.0    # housing channel clearance over balls (#16)

    # --- enclosure ---
    enc_w: float = 98.0            # <=100 rule
    enc_d: float = 44.0            # accepted off-wall depth (+2 over #21: the
                                   # rev B board is 38 wide and needs rail room)
    enc_h: float = 221.0           # 6× holders at 24.5 pitch, sitting above a
                                   # 66mm-tall PCB (#22) instead of a 38mm guess
    enc_wall: float = 2.0          # Ø37 in 42 leaves 0.5/side — thin walls are the point
    enc_fillet: float = 4.0        # vertical outer edges
    bulkhead_t: float = 3.0        # motor-mount rib (6×M3 into it)
    bulkhead_x: float = 74.0       # gearbox face plane (motor tail lands at x≈12)
    bulkhead_top: float = 44.0     # rib top — clears cell bay above, covers top M3s (z≈40.4)
    axis_y: float = 21.0           # sprocket/motor shaft axis, mid-depth
    axis_z: float = 20.0           # sprocket axis height (gearbox axis +7 above)
    guide_or: float = 17.0         # wrap-guide block outer radius
    chain_slot: float = 7.0        # top-face slot square (ball 5 + joiner room)

    # --- battery bay (holder stack on the carrier) ---
    bay_z0: float = 82.0           # first cell axis — holder bottom 70.05 clears
                                   # the real PCB (top edge 68), which is what
                                   # moved: #21's 58 cleared the gearbox, and the
                                   # board is now the taller obstacle
    bay_x: float = 44.0            # stack centre — holder right end 85.6, 0.9
                                   # clear of the chain corridor at 86.5

    # --- PCB (vertical, left of motor tail) ---
    # REAL rev B geometry, from pcb/blinds-board/tools/place_and_render.py.
    # #21's 34×38 was a placeholder guess and was wrong by a factor of two in
    # area: the board carries 87 footprints.
    pcb_t: float = 1.6
    pcb_w: float = 38.0            # spans y 3..41
    pcb_h: float = 66.0            # z 2..68, under the battery bay
    pcb_x: float = 6.6             # board plane centre. The slab between wall
                                   # (x=2) and motor tail (x=11.8) is 9.8 wide:
                                   # 3.8 wall-side for the button bodies, 4.4
                                   # motor-side for the USB-C and inductors
    pcb_z0: float = 2.0            # bottom edge ON the floor's inner face so the
                                   # USB-C mouth is flush with the slot
    pcb_comp_h: float = 3.4        # motor-side component envelope — USB-C is
                                   # the tallest fitted part at 3.26
    pcb_comp_inset: float = 1.5    # envelope inset from the board outline

    # buttons: KH-6X6X7H class 6×6 tactile, board-mounted on the wall-side
    # face, plunger through the wall. NOTE for #22: BOM line C2837543 is the
    # RIGHT-ANGLE variant — swap to the straight (top-push) sibling.
    btn_body: float = 6.0
    btn_body_t: float = 3.6
    btn_plunger_d: float = 3.5
    btn_plunger_len: float = 3.4   # body face -> tip (6×6×7 overall)
    btn_d: float = 5.0             # wall hole Ø
    btn_y: float = 35.0            # both switches, from the layout (board x=32)
    btn_z1: float = 53.7           # DOWN (board y=14.3)
    btn_z2: float = 60.4           # UP   (board y=7.6)

    # USB-C: TYPE-C-31-M-12 right-angle SMD on the motor-side face, mouth
    # down through the bottom slot
    usb_body_w: float = 8.94       # across the board (y)
    usb_body_l: float = 7.35       # along the board (z)
    usb_body_h: float = 3.26       # off the board face (x)
    usb_w: float = 9.2             # bottom-slot cut, ACROSS the board (y)
    usb_t: float = 3.4             # bottom-slot cut, through-board (x)
    usb_y: float = 17.0            # receptacle centre depth (board x=14)
    usb_z: float = 5.5             # receptacle body centre height

    # card-edge rails: printed towers off floor+left wall gripping the
    # board's y-edges; closed tops react USB insertion push-up
    rail_groove: float = 2.0       # groove width (board 1.6 + 0.2/side)
    rail_top: float = 69.0         # just over the board's top edge (68)

    # --- wall plate + cleat ---
    plate_w: float = 90.0
    plate_h: float = 160.0
    plate_t: float = 4.0
    plate_screw_d: float = 4.5     # countersunk for #8
    plate_screw_head: float = 9.0
    plate_screw_inset: float = 10.0
    cleat_h: float = 12.0          # 45° french-cleat rail height
    cleat_t: float = 6.0

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

    @property
    def pcb_y0(self) -> float:
        """Board's low-y edge: centred in the cavity, rails either side."""
        return (self.enc_d - self.pcb_w) / 2

    @property
    def pcb_z1(self) -> float:
        return self.pcb_z0 + self.pcb_h

    @property
    def usb_x(self) -> float:
        """Bottom-slot centre = receptacle axis on the board's motor side."""
        return self.pcb_x + self.pcb_t / 2 + self.usb_body_h / 2

    @property
    def spr_x(self) -> float:
        """Sprocket wheel centre plane: hub seats against the boss face."""
        return self.bulkhead_x + self.jgb_boss_h + self.spr_hub_len + self.spr_w / 2

    @property
    def strand_y(self) -> tuple:
        """The two vertical chain-run depths (front/back of the wrap)."""
        r = self.spr_pcd / 2
        return (self.axis_y - r, self.axis_y + r)


P = Params()
