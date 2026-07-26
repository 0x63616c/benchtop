"""Main PCB reference — the real rev B outline, not an envelope.

Geometry comes from `pcb/blinds-board/tools/place_and_render.py`: a 38×66mm
4-layer board, components on the motor-facing face, the two tactile switches
bodied on the wall-facing face with their plungers through the wall, and the
USB-C receptacle at the bottom edge with its mouth in the floor slot.

Three solids, so the fit question each one answers stays separate:
  * `board()`      — the laminate, 1.6mm
  * `components()` — one lumped keep-out for the motor-side parts. 3.4mm tall,
                     set by the USB-C receptacle (3.26mm); the 2.2uH shielded
                     inductors are next at 3.0mm and the ESP32 module 2.4mm.
  * `buttons()`    — the two 6×6 tactiles on the wall side.

The snap-off hall tab is not modelled: it leaves the panel before the board
goes in the enclosure.

NOTE for the build: the three XH-2.5 connector footprints (battery, motor,
hall) take a 5.75mm-tall housing, and the slab between the wall and the motor
tail is 4.4mm. In the enclosure the loom solders straight into the XH pads and
the housings are left off — they are still worth having on the board for bench
work, where nothing is 4mm away.

`just cad view blinds-pcb`.
"""

from build123d import Box, Cylinder, Pos, Rot

from .params import P


def board():
    """The laminate. Local frame: x = thickness, y = width, z = height."""
    return Box(P.pcb_t, P.pcb_w, P.pcb_h)


def components():
    """Motor-side component envelope — everything that stands off that face."""
    return Pos(P.pcb_t / 2 + P.pcb_comp_h / 2, 0, 0) * Box(
        P.pcb_comp_h, P.pcb_w - 2 * P.pcb_comp_inset, P.pcb_h - 2 * P.pcb_comp_inset
    )


def usbc():
    """TYPE-C-31-M-12 body (right-angle SMD, mouth -Z out of the board)."""
    return Box(P.usb_body_h, P.usb_body_w, P.usb_body_l)


def button():
    """KH-6X6X7H-TJ straight tactile: body on the board, plunger -X."""
    body = Box(P.btn_body_t, P.btn_body, P.btn_body)
    plunger = Pos(-P.btn_body_t / 2 - P.btn_plunger_len / 2, 0, 0) * (
        Rot(0, 90, 0) * Cylinder(P.btn_plunger_d / 2, P.btn_plunger_len)
    )
    return body + plunger


def scene():
    from splitflap_cad.viewer import Scene

    from . import frames as F

    s = Scene()
    s.add(board(), "board", color="darkgreen", alpha=0.85)
    s.add(components(), "components", color="dimgray", alpha=0.35)
    s.add(usbc(), "usb-c", color="gold", loc=F.USBC_IN_BOARD)
    s.add(button(), "btn-up", color="black", loc=F.btn_in_board(P.btn_z2))
    s.add(button(), "btn-down", color="black", loc=F.btn_in_board(P.btn_z1))
    return s
