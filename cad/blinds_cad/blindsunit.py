"""Full blinds unit — every part posed in unit frame, shell ghosted.

The fit-proof view: motor + sprocket + chain + cells + PCB envelope
inside the shell, wall plate behind. `just cad view blinds-unit`.
"""

from build123d import Box, Pos

from . import frames as F
from .cells21700 import cell_stack
from .enclosure import shell
from .jgb37 import jgb37
from .params import P
from .sprocket import chain_ghost, sprocket
from .wallplate import wallplate


def pcb_ghost():
    """BOM #19 pins the real board; this is the reserved volume."""
    return Box(P.pcb_t, P.pcb_w, P.pcb_h)


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    s.add(shell(), "shell", color="whitesmoke", alpha=0.3)
    s.add(wallplate(), "wallplate", color="lightsteelblue", alpha=0.8, loc=F.PLATE_IN_UNIT)
    s.add(jgb37(), "motor", color="silver", loc=F.MOTOR_IN_UNIT)
    s.add(sprocket(), "sprocket", color="orange", loc=F.SPROCKET_IN_UNIT)
    s.add(chain_ghost(200), "chain", color="gray", alpha=0.5, loc=F.CHAIN_IN_UNIT)
    s.add(cell_stack(), "cells", color="teal", loc=F.CELLS_IN_UNIT)
    s.add(pcb_ghost(), "pcb", color="green", alpha=0.6, loc=F.PCB_IN_UNIT)
    return s
