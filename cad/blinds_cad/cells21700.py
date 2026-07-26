"""Battery bay references: 21700 cells, Bistook 1-slot PCB holders, and
the battery CARRIER PCB they solder to.

Holders are listing-verified 83.1 × 23.9 × 21.8 (caliper on arrival);
pins are solder-only, so the carrier board does the 2S3P busing +
balance tap and hands power to the main PCB (XT30PW + JST-XH, #22).

Local frame (whole bay): cell 0 axis through the origin, cells along
+X, stacked in +Z at cell_pitch; the carrier back face at local
y = -(carrier_t + holder_h - cell_d/2).

View it: `just cad view blinds-cells`.
"""

from build123d import Box, Cylinder, Pos, Rot

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


def _holder():
    """One holder: U-cradle envelope, open toward +Y (cell drops in)."""
    base_y = -(P.holder_h - P.cell_d / 2)  # cradle base relative to cell axis
    body = Pos(0, base_y + P.holder_h / 2, 0) * Box(P.holder_l, P.holder_h, P.holder_w)
    # cell trough with 0.25 clearance all round
    body -= Rot(0, 90, 0) * Cylinder(P.cell_d / 2 + 0.25, P.holder_l + 2)
    # open the top (+Y) so the trough is a U, not a bore
    body -= Pos(0, P.cell_d / 2, 0) * Box(P.holder_l + 2, P.cell_d, P.cell_d - 2)
    return body


def holder_stack():
    stack = None
    for i in range(P.cell_n):
        h = Pos(0, 0, i * P.cell_pitch) * _holder()
        stack = h if stack is None else stack + h
    return stack


def carrier():
    """Battery carrier PCB: spans the stack, holders solder to its +Y
    face, M3 corner holes onto the shell's standoff bosses."""
    w = P.holder_l + 0.4
    h = (P.cell_n - 1) * P.cell_pitch + P.holder_w + 2.0
    y_face = -(P.holder_h - P.cell_d / 2)  # holder base plane
    zc = (P.cell_n - 1) * P.cell_pitch / 2
    board = Pos(0, y_face - P.carrier_t / 2, zc) * Box(w, P.carrier_t, h)
    for sx in (-1, 1):
        for sz in (-1, 1):
            board -= Pos(sx * (w / 2 - 4), y_face - P.carrier_t / 2, zc + sz * (h / 2 - 4)) * (
                Rot(90, 0, 0) * Cylinder(1.6, P.carrier_t + 2)
            )
    return board


def scene():
    from splitflap_cad.viewer import Scene

    s = Scene()
    s.add(cell_stack(), "cells", color="teal")
    s.add(holder_stack(), "holders", color="dimgray", alpha=0.9)
    s.add(carrier(), "carrier", color="darkgreen")
    return s
