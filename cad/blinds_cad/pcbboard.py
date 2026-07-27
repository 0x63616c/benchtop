"""Main PCB reference — the rev C envelope for the v2 center-drop unit.

The board lies FLAT on the enclosure floor (components up, 4× M3
corner holes onto printed bosses): 88×32×1.6, an envelope until the
rev C re-layout in pcb/blinds-board catches up. The two tactile
switches become the RIGHT-ANGLE KH-6X6X7H variant (the part BOM line
C2837543 always was), bodies at the board's front edge with plungers
+Y through the front wall; the USB-C receptacle sits between them,
mouth +Y through the wall.

Solids stay separated so each fit question stays separate:
  * `board()`      — the laminate, 1.6mm, with corner holes
  * `components()` — one lumped keep-out above the laminate. 5.8mm
                     tall: XH-2.5 housings (5.75) are the ceiling and
                     just clear the holder stack above (14.05)
  * `usbc()`, `button()` — the wall-penetrating parts

The snap-off hall tab is not modelled: it leaves the panel before the
board goes in the enclosure (it mounts up at the wrap guide, 3 wires).

Local frame: board center at the origin, laminate in the XY plane,
+Z up (same axes as the unit, translated).

`just cad view blinds-pcb`.
"""

from build123d import Box, Cylinder, Pos, Rot

from .params import P


def board():
    """The laminate, corner holes included."""
    b = Box(P.pcb_l, P.pcb_wd, P.pcb_t)
    ins = P.pcb_hole_inset
    for x in (-P.pcb_l / 2 + ins, P.pcb_l / 2 - ins):
        for y in (-P.pcb_wd / 2 + ins, P.pcb_wd / 2 - ins):
            b -= Pos(x, y, 0) * Cylinder(1.6, P.pcb_t + 2)
    return b


def components():
    """Component envelope above the laminate — XH housings set 5.8.
    The front strip belongs to the buttons/USB-C (modelled apart)."""
    depth = P.pcb_wd - P.pcb_comp_inset - P.pcb_comp_front_inset
    return Pos(0, (P.pcb_comp_inset - P.pcb_comp_front_inset) / 2 + 0, P.pcb_t / 2 + P.pcb_comp_h / 2) * Box(
        P.pcb_l - 2 * P.pcb_comp_inset, depth, P.pcb_comp_h,
    )


def usbc():
    """TYPE-C-31-M-12 body (right-angle SMD, mouth +Y in v2)."""
    return Box(P.usb_body_w, P.usb_body_l, P.usb_body_h)


def button():
    """KH-6X6X7H right-angle tactile: 6×6 face vertical, plunger +Y."""
    body = Box(P.btn_body, P.btn_body_t, P.btn_body)
    plunger = Pos(0, P.btn_body_t / 2 + P.btn_plunger_len / 2, 0) * (
        Rot(90, 0, 0) * Cylinder(P.btn_plunger_d / 2, P.btn_plunger_len)
    )
    return body + plunger


def scene():
    from splitflap_cad.viewer import Scene

    from . import frames as F

    s = Scene()
    s.add(board(), "board", color="darkgreen", alpha=0.85)
    s.add(components(), "components", color="dimgray", alpha=0.35)
    s.add(usbc(), "usb-c", color="gold", loc=F.USBC_IN_BOARD)
    s.add(button(), "btn-up", color="black", loc=F.btn_in_board(P.btn_x2))
    s.add(button(), "btn-down", color="black", loc=F.btn_in_board(P.btn_x1))
    return s
