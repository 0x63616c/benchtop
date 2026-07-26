"""Blinds unit fit guard: every posed part stays inside the shell's
cavity envelope and nothing interferes (fit-model rule — the assembly
must PROVE the bought parts fit before anything prints).

Marked slow: full boolean intersections. The fast fingerprint tier
already covers each part's own geometry.
"""

import itertools

import pytest

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def posed():
    from blinds_cad import frames as F
    from blinds_cad.blindsunit import button, pcb_ghost, usbc
    from blinds_cad.cells21700 import carrier, cell_stack, holder_stack
    from blinds_cad.enclosure import shell
    from blinds_cad.jgb37 import jgb37
    from blinds_cad.params import P
    from blinds_cad.sprocket import chain_ghost, sprocket
    from blinds_cad.wallplate import wallplate

    return {
        "shell": shell(),
        "plate": F.PLATE_IN_UNIT * wallplate(),
        "motor": F.MOTOR_IN_UNIT * jgb37(),
        "sprocket": F.SPROCKET_IN_UNIT * sprocket(),
        "chain": F.CHAIN_IN_UNIT * chain_ghost(200),
        "cells": F.BAY_IN_UNIT * cell_stack(),
        "holders": F.BAY_IN_UNIT * holder_stack(),
        "carrier": F.BAY_IN_UNIT * carrier(),
        "pcb": F.PCB_IN_UNIT * pcb_ghost(),
        "usbc": F.USBC_IN_UNIT * usbc(),
        "btn-up": F.btn_in_unit(P.btn_z2) * button(),
        "btn-down": F.btn_in_unit(P.btn_z1) * button(),
    }


def test_no_interference(posed):
    clashes = []
    for a, b in itertools.combinations(posed, 2):
        if {a, b} == {"chain", "sprocket"}:
            continue  # the ghost chain rides in the wheel's pockets by design
        v = (posed[a] & posed[b]).volume
        if v > 1e-6:
            clashes.append(f"{a} x {b}: {v:.2f} mm3")
    assert not clashes, clashes


def test_envelope(posed):
    """Owner constraints: <=100 wide, 42 deep; internals inside the shell."""
    from blinds_cad.params import P

    bb = posed["shell"].bounding_box()
    assert bb.max.X - bb.min.X <= 100.0
    assert abs((bb.max.Y - bb.min.Y) - P.enc_d) < 1e-6
    for name in ("motor", "sprocket", "cells", "holders", "carrier", "pcb", "usbc"):
        b = posed[name].bounding_box()
        assert b.min.X > 0 and b.max.X < P.enc_w, name
        assert b.min.Y > 0 and b.max.Y < P.enc_d, name
        assert b.min.Z > 0 and b.max.Z < P.enc_h, name
    # button plungers deliberately poke through the wall — body stays in
    for name in ("btn-up", "btn-down"):
        b = posed[name].bounding_box()
        assert b.max.X < P.enc_w and b.min.X > -1.0, name


def test_wrap_is_full_semicircle(posed):
    """Chain ghost's wrap spans the sprocket's full lower half — the
    >=180° wrap the guide channel must sustain."""
    from blinds_cad.params import P

    bb = posed["chain"].bounding_box()
    r = P.spr_pcd / 2 + P.chain_ball_d / 2
    assert bb.min.Z <= P.axis_z - r + 0.1
    assert bb.min.Y <= P.axis_y - r + 0.1 and bb.max.Y >= P.axis_y + r - 0.1
