"""Full blinds unit v2 — wall frame, working parts, and removable cover.

The fit-proof view: motor + spur pinion + layshaft + sprocket(+ring) +
chain + battery stack (cells in two directly mounted bought holders) + the
flat rev C main PCB envelope with its USB-C and front tactiles on the
wall-mounted exoskeleton. The sleeve and cap halves are translucent.
`just cad view blinds-unit`.
"""

from . import frames as F
from .cells21700 import cell_stack, holder_stack
from .cover import cap_front, cap_rear, sleeve
from .drivecassette import (
    bearing_at,
    bearing_caps,
    bevel_spacer,
    drive_cassette,
    inner_spacer,
    layshaft_rod,
    motor_spacer,
    outer_spacer,
)
from .enclosure import axle_keeper, frame
from .gears import bevel_gear, pinion, spur_gear
from .jgb37 import jgb37
from .params import P
from .pcbboard import board as pcb_board
from .pcbboard import button, components, usbc
from .sprocket import chain_ghost, sprocket


def pcb_ghost():
    """Board + component envelope as one solid, for the fit tests."""
    return pcb_board() + components()


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    s.add(frame(), "frame", color="lightsteelblue", alpha=0.8)
    s.add(axle_keeper(), "axle-keeper", color="steelblue")
    s.add(sleeve(), "sleeve", color="whitesmoke", alpha=0.18)
    s.add(cap_rear(), "cap-rear", color="gainsboro", alpha=0.5)
    s.add(cap_front(), "cap-front", color="whitesmoke", alpha=0.5)
    s.add(jgb37(), "motor", color="silver", loc=F.MOTOR_IN_UNIT)
    s.add(drive_cassette(), "drive-cassette", color="lightsteelblue", alpha=0.8)
    s.add(bearing_caps(), "bearing-caps", color="steelblue", alpha=0.8)
    s.add(pinion(), "pinion", color="tomato", loc=F.PINION_IN_UNIT)
    s.add(motor_spacer(), "motor-spacer", color="darkorange")
    s.add(bevel_gear(), "layshaft-bevel", color="gold", loc=F.LAYSHAFT_IN_UNIT)
    s.add(bevel_spacer(), "bevel-spacer", color="goldenrod")
    s.add(
        bearing_at(P.lay_bearing_centers_x[0]),
        "left-bearing",
        color="silver",
    )
    s.add(inner_spacer(), "inner-spacer", color="goldenrod")
    s.add(spur_gear(), "layshaft-spur", color="goldenrod", loc=F.SPUR_IN_UNIT)
    s.add(outer_spacer(), "outer-spacer", color="goldenrod")
    s.add(
        bearing_at(P.lay_bearing_centers_x[1]),
        "right-bearing",
        color="silver",
    )
    s.add(layshaft_rod(), "layshaft-rod", color="dimgray")
    s.add(sprocket(), "sprocket", color="orange", loc=F.SPROCKET_IN_UNIT)
    s.add(chain_ghost(200), "chain", color="gray", alpha=0.5, loc=F.CHAIN_IN_UNIT)
    s.add(cell_stack(), "cells", color="teal", loc=F.BAY_IN_UNIT)
    s.add(holder_stack(), "holders", color="dimgray", alpha=0.9, loc=F.BAY_IN_UNIT)
    s.add(pcb_board(), "pcb", color="darkgreen", loc=F.PCB_IN_UNIT)
    s.add(components(), "pcb-parts", color="dimgray", alpha=0.4, loc=F.PCB_IN_UNIT)
    s.add(usbc(), "usbc", color="gold", loc=F.USBC_IN_UNIT)
    s.add(button(), "btn-up", color="black", loc=F.btn_in_unit(P.btn_x2))
    s.add(button(), "btn-down", color="black", loc=F.btn_in_unit(P.btn_x1))
    return s
