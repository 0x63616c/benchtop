"""Printed gear train for the v2 center-drop drive. Printable ×2.

Two parts:
  * `pinion()`   — m2 z14 spur on the motor's 6mm D-shaft.
  * `layshaft()` — ONE print: m2 z17 spur + Ø8 shaft + m2 z10 bevel
                   at the far end. Rides in two U-saddles (bulkhead
                   rib + right block), retained by the mesh + clips.

Tooth geometry comes from py_gearworks: true involute spur teeth and
a matched octoid miter-bevel pair. The continuous Ø8 printed layshaft
has a 5.2mm axial bore for an optional 5mm steel reinforcing rod.

Local frames: gear axis +Z. The layshaft's bevel HEEL plane is z=0
with the cone apex at +Z (z=+bevel_r); shaft and spur extend -Z.

View: `just cad view blinds-gears`.
"""

from functools import lru_cache
from math import pi
import warnings

from build123d import Box, Cylinder, Pos, Rot
from py_gearworks import BevelGear, RIGHT, SpurGear

from .params import P


@lru_cache(maxsize=1)
def _spur_pair_parts():
    """Meshed py_gearworks spur pair, each returned on its own axis."""
    common = dict(
        module=P.gear_m,
        height=P.spur_w,
        backlash=P.gear_backlash,
    )
    pinion_definition = SpurGear(number_of_teeth=P.spur_pinion_z, **common)
    wheel_definition = SpurGear(number_of_teeth=P.spur_wheel_z, **common)
    wheel_definition.mesh_to(pinion_definition, target_dir=RIGHT)

    pinion_part = pinion_definition.build_part(n_vert=2)
    wheel_part = wheel_definition.build_part(n_vert=2)
    wheel_part = Pos(
        -(P.spur_pinion_r + P.spur_wheel_r), 0, 0
    ) * wheel_part
    return pinion_part, wheel_part


@lru_cache(maxsize=1)
def _bevel_pair_parts():
    """Matched py_gearworks 1:1 miter pair in layshaft/ring frames."""
    common = dict(
        number_of_teeth=P.bevel_z,
        module=P.gear_m,
        height=P.bevel_face,
        cone_angle=pi / 2,
        backlash=P.gear_backlash,
    )
    layshaft_definition = BevelGear(**common)
    ring_definition = BevelGear(**common)
    ring_definition.mesh_to(layshaft_definition, target_dir=RIGHT)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Gimbal lock detected.*")
        layshaft_part = layshaft_definition.build_part(n_vert=4)
        ring_part = ring_definition.build_part(n_vert=4)

    # The meshed ring has its heel centre at (bevel_r, 0, bevel_r),
    # axis toward -X. Reframe it onto a local +Z sprocket axis with its
    # heel plane at z=0 and apex at z=-bevel_r.
    ring_part = Pos(P.bevel_r, 0, -P.bevel_r) * Rot(0, -90, 0) * ring_part
    return layshaft_part, ring_part


def bevel_ring():
    """Matched sprocket-side bevel, heel plane at local z=0."""
    return _bevel_pair_parts()[1]


def _d_bore(length: float):
    """Ø6.2 D-bore matching the motor shaft (flat toward +Y local)."""
    bore = Cylinder(3.1, length)
    flat_y = 5.55 - 3.1
    bore -= Pos(0, flat_y + 3.1) * Box(6.2 * 2, 6.2, length + 2)
    return bore


def pinion():
    """Motor spur pinion, centered on z=0 (rides the shaft flat).

    Half-tooth phase rotation BEFORE the bore: posed on the shaft, the
    layshaft spur presents a gap at the mesh line, so the pinion must
    present a tooth there — while the D-flat stays aligned local +Y."""
    g = (
        Rot(0, 0, P.spur_pinion_phase)
        * Pos(0, 0, -P.spur_w / 2)
        * _spur_pair_parts()[0]
    )
    return g - _d_bore(P.spur_w + 2)


def layshaft():
    """Real bevel + continuous Ø8 shaft + real z17 spur, one print."""
    body = _bevel_pair_parts()[0]
    body += Pos(0, 0, -2.5) * Cylinder(P.lay_hub_d / 2, 5)  # bevel hub, z -5..0
    # (kept short: the hub must stay left of the bulkhead rib at x 67)
    shaft_len = 33.0  # unit x 59..92: through both saddles
    body += Pos(0, 0, -shaft_len / 2) * Cylinder(P.lay_shaft_d / 2, shaft_len)
    # spur wheel over the pinion: unit x = bevel_heel_x - local z, so the
    # teeth at unit x 78..85 live at local z -26..-19
    z_far = P.bevel_heel_x - (P.pinion_x + P.spur_w / 2)  # -26
    body += Pos(0, 0, z_far) * _spur_pair_parts()[1]
    body -= Pos(0, 0, (-shaft_len + P.bevel_face) / 2) * Cylinder(
        P.lay_rod_bore_d / 2, shaft_len + P.bevel_face + 1
    )
    return body


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    s.add(pinion(), "pinion", color="orange")
    s.add(layshaft(), "layshaft", color="goldenrod", loc=Pos(45, 0, 0))
    return s
