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
from .drivecassette import add_drive_to_scene
from .enclosure import frame
from .params import P
from .pcbboard import board as pcb_board
from .pcbboard import button, components, usbc
from .sprocket import chain_ghost


def pcb_ghost():
    """Board + component envelope as one solid, for the fit tests."""
    return pcb_board() + components()


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    s.add(frame(), "frame", color="lightsteelblue", alpha=0.8)
    s.add(sleeve(), "sleeve", color="whitesmoke", alpha=0.18)
    s.add(cap_rear(), "cap-rear", color="gainsboro", alpha=0.5)
    s.add(cap_front(), "cap-front", color="whitesmoke", alpha=0.5)
    add_drive_to_scene(s)
    s.add(chain_ghost(200), "chain", color="gray", alpha=0.5, loc=F.CHAIN_IN_UNIT)
    s.add(cell_stack(), "cells", color="teal", loc=F.BAY_IN_UNIT)
    s.add(holder_stack(), "holders", color="dimgray", alpha=0.9, loc=F.BAY_IN_UNIT)
    s.add(pcb_board(), "pcb", color="darkgreen", loc=F.PCB_IN_UNIT)
    s.add(components(), "pcb-parts", color="dimgray", alpha=0.4, loc=F.PCB_IN_UNIT)
    s.add(usbc(), "usbc", color="gold", loc=F.USBC_IN_UNIT)
    s.add(button(), "btn-up", color="black", loc=F.btn_in_unit(P.btn_x2))
    s.add(button(), "btn-down", color="black", loc=F.btn_in_unit(P.btn_x1))
    return s
