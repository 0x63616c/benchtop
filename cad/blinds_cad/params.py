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

    # --- 21700 cell (Samsung 50E) + contact envelope (BOM #19 pins holder) ---
    cell_d: float = 21.7
    cell_len: float = 70.6
    cell_contact: float = 4.0      # spring/tab room per end
    cell_pitch: float = 23.5       # stack pitch (cell + bay wall)
    cell_n: int = 6                # 2S3P

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
    enc_d: float = 42.0            # accepted off-wall depth
    enc_h: float = 190.0
    enc_wall: float = 2.0          # Ø37 in 42 leaves 0.5/side — thin walls are the point
    enc_fillet: float = 4.0        # vertical outer edges
    bulkhead_t: float = 3.0        # motor-mount rib (6×M3 into it)
    bulkhead_x: float = 74.0       # gearbox face plane (motor tail lands at x≈12)
    bulkhead_top: float = 44.0     # rib top — clears cell bay above, covers top M3s (z≈40.4)
    axis_y: float = 21.0           # sprocket/motor shaft axis, mid-depth
    axis_z: float = 20.0           # sprocket axis height (gearbox axis +7 above)
    guide_or: float = 17.0         # wrap-guide block outer radius
    chain_slot: float = 7.0        # top-face slot square (ball 5 + joiner room)

    # --- battery bay ---
    bay_z0: float = 57.0           # first cell axis height (bottom 46.15 clears
                                   # gearbox top 45.5 and bulkhead top 44)
    bay_y: float = 19.5            # cell axis depth — back of cells clears the
                                   # cleat hook bar (y<=8) by 0.65
    bay_x: float = 43.0            # stack centre — right end 4.2 clear of chain corridor

    # --- PCB envelope (vertical, left of motor tail; BOM #19 pins reality) ---
    pcb_t: float = 1.6
    pcb_w: float = 34.0            # spans depth-ish
    pcb_h: float = 36.0            # fits under the battery bay
    pcb_x: float = 6.0             # board plane centre; comps toward motor (+x)
    pcb_z0: float = 6.0
    btn_d: float = 8.0             # two side buttons, left wall
    btn_z1: float = 30.0           # near PCB top — board-mount plungers
    btn_z2: float = 44.0
    usb_w: float = 9.2             # USB-C slot, bottom face
    usb_t: float = 3.4
    usb_x: float = 8.0

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
    def cell_span(self) -> float:
        return self.cell_len + 2 * self.cell_contact

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
