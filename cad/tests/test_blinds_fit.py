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
    from blinds_cad.blindsunit import pcb_ghost
    from blinds_cad.cells21700 import cell_stack
    from blinds_cad.enclosure import shell
    from blinds_cad.jgb37 import jgb37
    from blinds_cad.sprocket import chain_ghost, sprocket
    from blinds_cad.wallplate import wallplate

    return {
        "shell": shell(),
        "plate": F.PLATE_IN_UNIT * wallplate(),
        "motor": F.MOTOR_IN_UNIT * jgb37(),
        "sprocket": F.SPROCKET_IN_UNIT * sprocket(),
        "chain": F.CHAIN_IN_UNIT * chain_ghost(200),
        "cells": F.CELLS_IN_UNIT * cell_stack(),
        "pcb": F.PCB_IN_UNIT * pcb_ghost(),
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
    for name in ("motor", "sprocket", "cells", "pcb"):
        b = posed[name].bounding_box()
        assert b.min.X > 0 and b.max.X < P.enc_w, name
        assert b.min.Y > 0 and b.max.Y < P.enc_d, name
        assert b.min.Z > 0 and b.max.Z < P.enc_h, name


def test_wrap_is_full_semicircle(posed):
    """Chain ghost's wrap spans the sprocket's full lower half — the
    >=180° wrap the guide channel must sustain."""
    from blinds_cad.params import P

    bb = posed["chain"].bounding_box()
    r = P.spr_pcd / 2 + P.chain_ball_d / 2
    assert bb.min.Z <= P.axis_z - r + 0.1
    assert bb.min.Y <= P.axis_y - r + 0.1 and bb.max.Y >= P.axis_y + r - 0.1
