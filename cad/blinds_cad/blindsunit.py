"""Full blinds unit — every part posed in unit frame, shell ghosted.

The fit-proof view: motor + sprocket + chain + battery bay (cells in
real holders on the carrier PCB) + main PCB with its USB-C receptacle
and side tactiles, inside the shell, wall plate behind.
`just cad view blinds-unit`.
"""

from build123d import Box, Cylinder, Pos, Rot

from . import frames as F
from .cells21700 import carrier, cell_stack, holder_stack
from .enclosure import shell
from .jgb37 import jgb37
from .params import P
from .sprocket import chain_ghost, sprocket
from .wallplate import wallplate


def pcb_ghost():
    """#22 pins the real layout; this is the reserved board volume."""
    return Box(P.pcb_t, P.pcb_w, P.pcb_h)


def usbc():
    """TYPE-C-31-M-12 body envelope (right-angle SMD, mouth -Z)."""
    return Box(P.usb_body_h, P.usb_body_w, P.usb_body_l)


def button():
    """KH 6×6 tactile (straight variant — see params note): body on the
    board, plunger -X through the wall hole."""
    body = Box(P.btn_body_t, P.btn_body, P.btn_body)
    plunger = Pos(-P.btn_body_t / 2 - P.btn_plunger_len / 2, 0, 0) * (
        Rot(0, 90, 0) * Cylinder(P.btn_plunger_d / 2, P.btn_plunger_len)
    )
    return body + plunger


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    s.add(shell(), "shell", color="whitesmoke", alpha=0.3)
    s.add(wallplate(), "wallplate", color="lightsteelblue", alpha=0.8, loc=F.PLATE_IN_UNIT)
    s.add(jgb37(), "motor", color="silver", loc=F.MOTOR_IN_UNIT)
    s.add(sprocket(), "sprocket", color="orange", loc=F.SPROCKET_IN_UNIT)
    s.add(chain_ghost(200), "chain", color="gray", alpha=0.5, loc=F.CHAIN_IN_UNIT)
    s.add(cell_stack(), "cells", color="teal", loc=F.BAY_IN_UNIT)
    s.add(holder_stack(), "holders", color="dimgray", alpha=0.9, loc=F.BAY_IN_UNIT)
    s.add(carrier(), "carrier", color="darkgreen", loc=F.BAY_IN_UNIT)
    s.add(pcb_ghost(), "pcb", color="green", alpha=0.6, loc=F.PCB_IN_UNIT)
    s.add(usbc(), "usbc", color="gold", loc=F.USBC_IN_UNIT)
    s.add(button(), "btn-up", color="black", loc=F.btn_in_unit(P.btn_z2))
    s.add(button(), "btn-down", color="black", loc=F.btn_in_unit(P.btn_z1))
    return s
