"""Blinds unit fit guard: every posed part stays inside the shell's
cavity envelope and nothing interferes (fit-model rule — the assembly
must PROVE the bought parts fit before anything prints).

Marked slow: full boolean intersections. The fast fingerprint tier
already covers each part's own geometry.
"""

import itertools

import pytest

pytestmark = pytest.mark.slow

# pairs that touch by design
MESHES = [
    {"chain", "sprocket"},      # the ghost chain rides in the wheel's pockets
    {"sprocket", "layshaft"},   # bevel mesh
    {"layshaft", "pinion"},     # spur mesh
]


@pytest.fixture(scope="module")
def posed():
    from blinds_cad import frames as F
    from blinds_cad.blindsunit import button, pcb_ghost, usbc
    from blinds_cad.cells21700 import carrier, cell_stack, holder_stack
    from blinds_cad.enclosure import shell
    from blinds_cad.gears import layshaft, pinion
    from blinds_cad.jgb37 import jgb37
    from blinds_cad.params import P
    from blinds_cad.sprocket import chain_ghost, sprocket
    from blinds_cad.wallplate import wallplate

    return {
        "shell": shell(),
        "plate": F.PLATE_IN_UNIT * wallplate(),
        "motor": F.MOTOR_IN_UNIT * jgb37(),
        "pinion": F.PINION_IN_UNIT * pinion(),
        "layshaft": F.LAYSHAFT_IN_UNIT * layshaft(),
        "sprocket": F.SPROCKET_IN_UNIT * sprocket(),
        "chain": F.CHAIN_IN_UNIT * chain_ghost(200),
        "cells": F.BAY_IN_UNIT * cell_stack(),
        "holders": F.BAY_IN_UNIT * holder_stack(),
        "carrier": F.BAY_IN_UNIT * carrier(),
        "pcb": F.PCB_IN_UNIT * pcb_ghost(),
        "usbc": F.USBC_IN_UNIT * usbc(),
        "btn-up": F.btn_in_unit(P.btn_x2) * button(),
        "btn-down": F.btn_in_unit(P.btn_x1) * button(),
    }


def test_no_interference(posed):
    clashes = []
    for a, b in itertools.combinations(posed, 2):
        if {a, b} in MESHES:
            continue
        v = (posed[a] & posed[b]).volume
        if v > 1e-6:
            clashes.append(f"{a} x {b}: {v:.2f} mm3")
    assert not clashes, clashes


def test_envelope(posed):
    """Owner constraints: <=100 wide, 44 deep; internals inside the shell."""
    from blinds_cad.params import P

    bb = posed["shell"].bounding_box()
    assert bb.max.X - bb.min.X <= 100.0
    assert abs((bb.max.Y - bb.min.Y) - P.enc_d) < 1e-6
    for name in (
        "motor", "pinion", "layshaft", "sprocket",
        "cells", "holders", "carrier", "pcb",
    ):
        b = posed[name].bounding_box()
        assert b.min.X > 0 and b.max.X < P.enc_w, name
        assert b.min.Y > 0 and b.max.Y < P.enc_d, name
        assert b.min.Z > 0 and b.max.Z < P.enc_h, name
    # button plungers + USB mouth deliberately reach the front wall —
    # bodies stay inside, plungers may poke through (+Y)
    for name in ("btn-up", "btn-down", "usbc"):
        b = posed[name].bounding_box()
        assert b.min.Y > 0 and b.max.Y < P.enc_d + 2.0, name


def test_wrap_is_full_semicircle(posed):
    """Chain ghost's wrap spans the sprocket's full lower half — the
    >=180° wrap the guide channel must sustain."""
    from blinds_cad.params import P

    bb = posed["chain"].bounding_box()
    r = P.spr_pcd / 2 + P.chain_ball_d / 2
    assert bb.min.Z <= P.spr_z - r + 0.1
    assert bb.min.X <= P.drive_x - r + 0.1 and bb.max.X >= P.drive_x + r - 0.1


def test_gear_mesh_geometry():
    """The two mesh center distances the layout is built on."""
    from blinds_cad.params import P

    assert P.lay_z - P.motor_z == P.spur_pinion_r + P.spur_wheel_r
    assert P.bevel_heel_x - P.drive_x == P.bevel_r
    assert P.drive_y - P.ring_heel_y == P.bevel_r
