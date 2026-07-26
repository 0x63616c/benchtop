"""21700 cell — reference model (Samsung 50E envelope + contact room).

Local frame: cell axis along +X, centred; z=0 on the axis. cell_stack()
returns the 6-high bay stack (axes along X, stacked in +Z at
cell_pitch) for the assembly.

View it: `just cad view blinds-cells`.
"""

from build123d import Cylinder, Pos, Rot

from .params import P


def cell():
    """One 21700: body + a stub nub for the positive end."""
    body = Rot(0, 90, 0) * Cylinder(P.cell_d / 2, P.cell_len)
    nub = Pos(P.cell_len / 2 + 0.4) * (Rot(0, 90, 0) * Cylinder(4.0, 0.8))
    return body + nub


def cell_stack():
    """The bay's 6 cells as one solid, stacked in +Z."""
    stack = None
    for i in range(P.cell_n):
        c = Pos(0, 0, i * P.cell_pitch) * cell()
        stack = c if stack is None else stack + c
    return stack


def scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(cell_stack(), "cells-2s3p", color="teal")
