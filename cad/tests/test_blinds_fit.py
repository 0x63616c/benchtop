"""Blinds unit fit guard: every bought part fits the wall frame and
removable cover without interference (fit-model rule — the assembly
must PROVE the bought parts fit before anything prints).

Marked slow: full boolean intersections. The fast fingerprint tier
already covers each part's own geometry.
"""

import itertools

import pytest

pytestmark = pytest.mark.slow

# pairs that touch by design: allowed interpenetration in mm^3. The gear
# meshes are phased + backlashed, so anything beyond a straight-tooth
# approximation graze means the mesh geometry regressed.
MESHES = {
    frozenset({"chain", "sprocket"}): 200.0,   # ghost rides in the pockets
    frozenset({"sprocket", "layshaft-bevel"}): 0.5,
    frozenset({"layshaft-spur", "pinion"}): 0.5,
}


@pytest.fixture(scope="module")
def posed():
    from blinds_cad import frames as F
    from blinds_cad.blindsunit import button, pcb_ghost, usbc
    from blinds_cad.cells21700 import cell_stack, holder_stack
    from blinds_cad.cover import cap_front, cap_rear, sleeve
    from blinds_cad.drivecassette import (
        bearing_at,
        bearing_caps,
        bevel_spacer,
        drive_cassette,
        inner_spacer,
        layshaft_rod,
        motor_spacer,
        outer_spacer,
    )
    from blinds_cad.enclosure import axle_keeper, frame
    from blinds_cad.gears import bevel_gear, pinion, spur_gear
    from blinds_cad.jgb37 import jgb37
    from blinds_cad.params import P
    from blinds_cad.sprocket import chain_ghost, sprocket

    return {
        "frame": frame(),
        "axle-keeper": axle_keeper(),
        "sleeve": sleeve(),
        "cap-rear": cap_rear(),
        "cap-front": cap_front(),
        "drive-cassette": drive_cassette(),
        "bearing-caps": bearing_caps(),
        "motor": F.MOTOR_IN_UNIT * jgb37(),
        "pinion": F.PINION_IN_UNIT * pinion(),
        "motor-spacer": motor_spacer(),
        "layshaft-bevel": F.LAYSHAFT_IN_UNIT * bevel_gear(),
        "bevel-spacer": bevel_spacer(),
        "left-bearing": bearing_at(P.lay_bearing_centers_x[0]),
        "inner-spacer": inner_spacer(),
        "layshaft-spur": F.SPUR_IN_UNIT * spur_gear(),
        "outer-spacer": outer_spacer(),
        "right-bearing": bearing_at(P.lay_bearing_centers_x[1]),
        "layshaft-rod": layshaft_rod(),
        "sprocket": F.SPROCKET_IN_UNIT * sprocket(),
        "chain": F.CHAIN_IN_UNIT * chain_ghost(200),
        "cells": F.BAY_IN_UNIT * cell_stack(),
        "holders": F.BAY_IN_UNIT * holder_stack(),
        "pcb": F.PCB_IN_UNIT * pcb_ghost(),
        "usbc": F.USBC_IN_UNIT * usbc(),
        "btn-up": F.btn_in_unit(P.btn_x2) * button(),
        "btn-down": F.btn_in_unit(P.btn_x1) * button(),
    }


def test_no_interference(posed):
    clashes = []
    for a, b in itertools.combinations(posed, 2):
        limit = MESHES.get(frozenset({a, b}), 1e-6)
        v = (posed[a] & posed[b]).volume
        if v > limit:
            clashes.append(f"{a} x {b}: {v:.2f} mm3 (limit {limit})")
    assert not clashes, clashes


def test_envelope(posed):
    """Owner constraints: <=100 wide, 44 deep; internals inside cover."""
    from blinds_cad.params import P

    bb = posed["sleeve"].bounding_box()
    assert bb.max.X - bb.min.X <= 100.0
    assert abs((bb.max.Y - bb.min.Y) - P.enc_d) < 1e-6
    assert posed["frame"].bounding_box().max.Y < P.enc_d
    assert posed["cap-rear"].bounding_box().max.Z == pytest.approx(P.enc_h)
    assert posed["cap-front"].bounding_box().max.Z == pytest.approx(P.enc_h)
    for name in (
        "drive-cassette", "bearing-caps", "motor", "pinion",
        "layshaft-bevel", "layshaft-spur", "layshaft-rod", "sprocket",
        "cells", "holders", "pcb",
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
