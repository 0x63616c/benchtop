"""Split bead-chain sprocket for the removable blinds cassette.

The chain wheel and its m2 z10 bevel are independent flat-printing parts.
Both are cross-pinned to a bought 5 mm steel shaft running in two MR105ZZ
bearings.  There is no printed shaft and no tall wheel-to-gear bridge.

Pocket geometry unchanged from #16: pitch circle Ø≈22.9 (12 × 6mm
pitch / π); hemispherical Ø5.4 ball pockets centred ON the pitch
circle; continuous 3.5mm cord groove at pocket depth.

The wheel prints on either face.  The bevel prints with its trimmed wide
heel on the bed.  Neither part needs supports.

View it: `just cad view blinds-sprocket` (chain ghost included).
"""

import math

from build123d import Box, Cylinder, Pos, Rot, Sphere, Torus
from splitflap_cad.geo import support_free_cross_bore

from .params import P
from .gears import bevel_ring


def chain_wheel():
    """12-pocket chain wheel, local shaft axis +Z and centred at z=0."""
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

    wheel -= Cylinder((P.spr_shaft_d + P.spr_shaft_clear) / 2, P.spr_w + 2)
    wheel -= support_free_cross_bore(
        P.spr_pin_guide_d / 2,
        P.spr_od + 2,
        0,
        0,
        0,
    )
    return wheel


def sprocket_bevel():
    """Matched bevel ring with a broad rear disc for face-down printing."""
    ring = Rot(0, 0, P.bevel_ring_phase) * bevel_ring()
    ring += Pos(0, 0, P.spr_ring_back_t / 2) * Cylinder(
        P.spr_ring_back_d / 2,
        P.spr_ring_back_t,
    )
    ring -= Pos(0, 0, -1) * Cylinder(
        (P.spr_shaft_d + P.spr_shaft_clear) / 2,
        12,
    )
    ring -= support_free_cross_bore(
        P.spr_pin_guide_d / 2,
        P.spr_bevel_pin_len + 2,
        0,
        0,
        P.spr_ring_back_t / 2,
    )
    return ring


def sprocket():
    """Compatibility name for the chain-contacting printable part."""
    return chain_wheel()


def sprocket_print():
    """Chain wheel on one flat face."""
    part = chain_wheel()
    return Pos(0, 0, -part.bounding_box().min.Z) * part


def sprocket_bevel_print():
    """Separate bevel ring on its broad rear disc."""
    part = Rot(180, 0, 0) * sprocket_bevel()
    return Pos(0, 0, -part.bounding_box().min.Z) * part


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
    from . import frames as F
    from .drivecassette import sprocket_bearing_mr105, sprocket_shaft
    from splitflap_cad.viewer import Scene

    return (
        Scene()
        .add(F.SPROCKET_WHEEL_IN_UNIT * chain_wheel(), "chain-wheel", color="orange")
        .add(F.SPROCKET_BEVEL_IN_UNIT * sprocket_bevel(), "sprocket-bevel", color="gold")
        .add(F.SPROCKET_SHAFT_IN_UNIT * sprocket_shaft(), "5mm-shaft", color="dimgray")
        .add(F.REAR_SPROCKET_BEARING_IN_UNIT * sprocket_bearing_mr105(), "rear-bearing", color="silver")
        .add(F.FRONT_SPROCKET_BEARING_IN_UNIT * sprocket_bearing_mr105(), "front-bearing", color="silver")
        .add(F.CHAIN_IN_UNIT * chain_ghost(), "chain", color="gray", alpha=0.5)
    )


def bevel_scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(sprocket_bevel_print(), "sprocket-bevel", color="gold")
