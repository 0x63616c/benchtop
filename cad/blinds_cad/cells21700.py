"""Battery bay references: 21700 cells and two owned Bistook 3-slot holders.

Each holder is 83.00 × 66.59 × 14.51 mm plastic with a 21.80 mm
maximum contact envelope.  The three 4.2 mm mounting holes sit on the
cell-slot centres.  The holders mount directly to the printed frame;
their solder tabs are wired as two 1S3P banks in series.

Local frame: holder plastic back at y=0, lower-holder bottom at z=0.
Cells run along +X and the second holder is stacked in +Z.

View it: `just cad view blinds-cells`.
"""

from build123d import Box, Cylinder, Pos, Rot

from .params import P


def cell():
    """One 21700: body + a stub nub for the positive end."""
    body = Rot(0, 90, 0) * Cylinder(P.cell_d / 2, P.cell_len)
    nub = Pos(P.cell_len / 2 + 0.4) * (Rot(0, 90, 0) * Cylinder(4.0, 0.8))
    return body + nub


def _slot_centres():
    for bank in range(2):
        bank_z = bank * (P.holder3_h + P.holder3_gap)
        for slot in range(3):
            yield bank_z + P.holder3_slot_edge + slot * P.holder3_slot_pitch


def cell_stack():
    """Six cells in the two bought three-slot holders."""
    stack = None
    for z in _slot_centres():
        c = Pos(0, P.holder3_body_d, z) * cell()
        stack = c if stack is None else stack + c
    return stack


def _holder():
    """One shallow three-cell tray, open toward the room (+Y)."""
    body = Pos(0, P.holder3_body_d / 2, P.holder3_h / 2) * Box(
        P.holder3_l, P.holder3_body_d, P.holder3_h
    )
    for slot in range(3):
        z = P.holder3_slot_edge + slot * P.holder3_slot_pitch
        # Three cell troughs, with the cell axes on the tray's front plane.
        body -= Pos(0, P.holder3_body_d, z) * (
            Rot(0, 90, 0) * Cylinder(P.cell_d / 2 + 0.25, P.holder3_l + 2)
        )
        # Supplier/owner-confirmed 4.2 mm through mounting hole.
        body -= Pos(0, P.holder3_body_d / 2, z) * (
            Rot(90, 0, 0) * Cylinder(P.holder3_hole_d / 2, P.holder3_body_d + 2)
        )
    return body


def holder_stack():
    """The two plastic holders, separated by a printable wiring gap."""
    stack = None
    for bank in range(2):
        h = Pos(0, 0, bank * (P.holder3_h + P.holder3_gap)) * _holder()
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
