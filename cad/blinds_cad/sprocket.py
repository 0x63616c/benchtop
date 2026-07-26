"""Bead-chain sprocket — 12-pocket wheel per ticket #16's paper spec.

Printable. Local frame: wheel axis +Z, z=0 at the wheel's mid-plane;
hub boss extends -Z (motor side, seats toward the gearbox boss).

Geometry: pitch circle Ø≈22.9 (12 × 6mm pitch / π); hemispherical
Ø5.4 ball pockets centred ON the pitch circle; continuous 3.5mm cord
groove at pocket depth (the per-gap joiner reliefs of #16 overlap into
a full ring — see params). D-bore matches the motor's 6mm D-shaft.

Print flat, pockets up, no supports (P2S, PLA).

View it: `just cad view blinds-sprocket` (chain ghost included).
"""

import math

from build123d import Box, Cylinder, Pos, Rot, Sphere, Torus

from .params import P


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

    hub = Pos(0, 0, -P.spr_w / 2 - P.spr_hub_len / 2) * Cylinder(
        P.spr_hub_d / 2, P.spr_hub_len
    )
    body = wheel + hub

    # D-bore through everything
    bore = Cylinder(P.spr_bore_d / 2, P.spr_w + 2 * P.spr_hub_len)
    flat_y = P.spr_bore_flat - P.spr_bore_d / 2
    bore -= Pos(0, flat_y + P.spr_bore_d / 2) * Box(
        P.spr_bore_d * 2, P.spr_bore_d, P.spr_w + 2 * P.spr_hub_len
    )
    return body - bore


def _ring(r_in: float, r_out: float, w: float):
    """Annular slot: outer cylinder minus inner, w tall, centred on z=0."""
    return Cylinder(r_out, w) - Cylinder(r_in, w + 1)


def chain_ghost(run_len: float = 120.0):
    """The chain path in a UNIT-aligned local frame: wheel axis +X at
    the origin, two vertical (+Z) bead runs at y=±pitch radius, 180°
    wrap under the wheel as a half torus. Display-only."""
    r = P.spr_pcd / 2
    rod = Cylinder(P.chain_ball_d / 2, run_len)
    runs = Pos(0, -r, run_len / 2) * rod + Pos(0, r, run_len / 2) * rod
    # torus about +Z tipped onto +X (Rot maps pre +X -> post -Z), so the
    # kept lower half is the pre x>0 half: cut away pre x<0
    wrap = Torus(r, P.chain_ball_d / 2) - Pos(-(r + P.chain_ball_d), 0, 0) * Box(
        2 * r + 2 * P.chain_ball_d, 4 * r, 4 * P.chain_ball_d
    )
    return runs + Rot(0, 90, 0) * wrap


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    # pose the wheel into the chain frame (axis +X) so they co-display
    s.add(sprocket(), "sprocket", color="orange", loc=Rot(0, 90, 0))
    s.add(chain_ghost(), "chain", color="gray", alpha=0.5)
    return s
