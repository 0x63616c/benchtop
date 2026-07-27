"""Full blinds unit v2 — every part posed in unit frame, shell ghosted.

The fit-proof view: motor + spur pinion + layshaft + sprocket(+ring) +
chain + battery stack (cells in real holders on the carrier PCB) + the
flat rev C main PCB envelope with its USB-C and front tactiles, inside
the shell, wall plate behind. `just cad view blinds-unit`.
"""

from . import frames as F
from .cells21700 import carrier, cell_stack, holder_stack
from .enclosure import shell
from .gears import layshaft, pinion
from .jgb37 import jgb37
from .params import P
from .pcbboard import board as pcb_board
from .pcbboard import button, components, usbc
from .sprocket import chain_ghost, sprocket
from .wallplate import wallplate


def pcb_ghost():
    """Board + component envelope as one solid, for the fit tests."""
    return pcb_board() + components()


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    s.add(shell(), "shell", color="whitesmoke", alpha=0.3)
    s.add(wallplate(), "wallplate", color="lightsteelblue", alpha=0.8, loc=F.PLATE_IN_UNIT)
    s.add(jgb37(), "motor", color="silver", loc=F.MOTOR_IN_UNIT)
    s.add(pinion(), "pinion", color="tomato", loc=F.PINION_IN_UNIT)
    s.add(layshaft(), "layshaft", color="goldenrod", loc=F.LAYSHAFT_IN_UNIT)
    s.add(sprocket(), "sprocket", color="orange", loc=F.SPROCKET_IN_UNIT)
    s.add(chain_ghost(200), "chain", color="gray", alpha=0.5, loc=F.CHAIN_IN_UNIT)
    s.add(cell_stack(), "cells", color="teal", loc=F.BAY_IN_UNIT)
    s.add(holder_stack(), "holders", color="dimgray", alpha=0.9, loc=F.BAY_IN_UNIT)
    s.add(carrier(), "carrier", color="darkgreen", loc=F.BAY_IN_UNIT)
    s.add(pcb_board(), "pcb", color="darkgreen", loc=F.PCB_IN_UNIT)
    s.add(components(), "pcb-parts", color="dimgray", alpha=0.4, loc=F.PCB_IN_UNIT)
    s.add(usbc(), "usbc", color="gold", loc=F.USBC_IN_UNIT)
    s.add(button(), "btn-up", color="black", loc=F.btn_in_unit(P.btn_x2))
    s.add(button(), "btn-down", color="black", loc=F.btn_in_unit(P.btn_x1))
    return s
