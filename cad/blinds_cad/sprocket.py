"""Bead-chain sprocket — 12-pocket wheel per ticket #16, v2: printed
as ONE piece with its m2 z10 bevel ring gear.

Printable. Local frame: axis +Z, z=0 at the WHEEL's mid-plane. Going
+Z (toward the wall once posed): wheel (±4), Ø10 drum bridge, bevel
ring with its heel plane at z=25 and cone apex at z=15, back disc to
z=27.5. Plain Ø5.2 bore throughout — it spins on a fixed M5 cross-axle
(front wall -> cleat bar), driven by the layshaft's identical bevel.

Pocket geometry unchanged from #16: pitch circle Ø≈22.9 (12 × 6mm
pitch / π); hemispherical Ø5.4 ball pockets centred ON the pitch
circle; continuous 3.5mm cord groove at pocket depth.

Print standing on the wheel face (z=-4 down), no supports (P2S, PLA):
the drum and 45° ring cone self-support.

View it: `just cad view blinds-sprocket` (chain ghost included).
"""

import math

from build123d import Box, Cylinder, Pos, Rot, Sphere, Torus

from .params import P
from .gears import bevel


def sprocket():
    r_pitch = P.spr_pcd / 2

    wheel = Cylinder(P.spr_od / 2, P.spr_w)
    # continuous cord groove, floor AT the pitch radius — beads' cord
    # and any crimp joiner ride here (see spr_groove_w note in params)
    wheel -= _ring(r_pitch, P.spr_od / 2 + 1, P.spr_groove_w)
    # 12 ball pockets on the pitch circle
    for i in range(P.spr_n):
        a = math.radians(i * 360 / P.spr_n)
        wheel -= Pos(r_pitch * math.cos(a), r_pitch * math.sin(a)) * Sphere(
            P.spr_pocket_d / 2
        )

    # back-rim relief: the layshaft bevel's heel teeth sweep to within
    # 0.6 of the wheel's back face at its outer radius — recess the rim
    # beyond the drum over the last 1mm (pockets live at mid-plane, safe)
    wheel -= Pos(0, 0, 3.55) * _ring(P.spr_drum_d / 2 + 0.2, P.spr_od / 2 + 1, 1.1)

    # ring heel plane in local z: wheel mid-plane is unit y=spr_wy and
    # local +Z runs wall-ward, so the heel (unit y=ring_heel_y) lands at
    rz = P.spr_wy - P.ring_heel_y  # 25.6

    # drum bridge: wheel back face -> ring gear
    drum_z0, drum_z1 = P.spr_w / 2, rz - P.bevel_face / math.sqrt(2)
    drum = Pos(0, 0, (drum_z0 + drum_z1) / 2) * Cylinder(
        P.spr_drum_d / 2, drum_z1 - drum_z0
    )

    # bevel ring: heel plane z=rz, apex toward the wheel at rz-10 —
    # gears.bevel() builds apex +Z, so flip it over before placing
    ring = Pos(0, 0, rz) * (Rot(180, 0, 0) * bevel(P.gear_m, P.bevel_z, P.bevel_face))
    ring += Pos(0, 0, rz + 1.25) * Cylinder(7.5, 2.5)  # back disc

    body = wheel + drum + ring
    # plain bore on the M5 axle
    body -= Pos(0, 0, 11) * Cylinder(P.spr_bore_d / 2, 44)
    return body


def _ring(r_in: float, r_out: float, w: float):
    """Annular slot: outer cylinder minus inner, w tall, centred on z=0."""
    return Cylinder(r_out, w) - Cylinder(r_in, w + 1)


def chain_ghost(run_len: float = 120.0):
    """The chain path, UNIT-aligned at the wheel center: wheel axis +Y,
    two vertical (+Z) bead runs at x=±pitch radius, 180° wrap under the
    wheel as a half torus. Display-only."""
    r = P.spr_pcd / 2
    rod = Cylinder(P.chain_ball_d / 2, run_len)
    runs = Pos(-r, 0, run_len / 2) * rod + Pos(r, 0, run_len / 2) * rod
    wrap = Rot(90, 0, 0) * Torus(r, P.chain_ball_d / 2)  # ring in the X-Z plane
    wrap -= Pos(0, 0, r + P.chain_ball_d) * Box(
        4 * r, 4 * P.chain_ball_d, 2 * r + 2 * P.chain_ball_d
    )  # keep the lower half
    return runs + wrap


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    # pose the wheel into the chain frame (axis +Y) so they co-display
    s.add(sprocket(), "sprocket", color="orange", loc=Rot(90, 0, 0))
    s.add(chain_ghost(), "chain", color="gray", alpha=0.5)
    return s
