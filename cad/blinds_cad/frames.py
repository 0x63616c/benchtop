"""Named frames: where each part's local frame sits in UNIT coordinates.

Unit frame: origin at the back-left-bottom corner of the enclosure.
+X right (along the wall), +Y off the wall into the room, +Z up. The
wall plate lives at y<0, behind the unit's back face.

Naming: X_IN_UNIT maps X-local coords into unit coords.
"""

from build123d import Pos, Rot

from .params import P

# Motor frame (shaft axis at gearbox face, shaft +Z, eccentric +Y local)
# onto the horizontal shaft axis: local +Z -> unit +X (shaft points
# right, at the sprocket), local +Y (eccentricity) -> unit +Z so the
# gearbox axis sits 7 ABOVE the sprocket axis.
MOTOR_IN_UNIT = Pos(P.bulkhead_x, P.axis_y, P.axis_z) * Rot(0, 90, 0) * Rot(0, 0, 90)

# Sprocket frame (wheel axis +Z, hub -Z toward motor) onto the shaft:
# local +Z -> unit +X, wheel mid-plane at spr_x. The trailing Rot about
# local Z points the bore's D-flat up (+Z unit), matching the shaft flat.
SPROCKET_IN_UNIT = Pos(P.spr_x, P.axis_y, P.axis_z) * Rot(0, 90, 0) * Rot(0, 0, 90)

# Chain ghost is built unit-aligned (axis +X at origin) — translate only.
CHAIN_IN_UNIT = Pos(P.spr_x, P.axis_y, P.axis_z)

# Battery bay (cells + holders + carrier share one frame): cell 0 axis
# through (bay_x, cell_axis_y, bay_z0), cells along +X, carrier at -y.
BAY_IN_UNIT = Pos(P.bay_x, P.cell_axis_y, P.bay_z0)

# PCB envelope: plain box built centred; place its centre.
PCB_IN_UNIT = Pos(P.pcb_x, P.enc_d / 2, P.pcb_z0 + P.pcb_h / 2)

# USB-C receptacle: centred box on the board's motor-side face, mouth down
# into the floor slot. Depth and height come from the real layout, not the
# board centreline — the receptacle sits well off-centre.
USBC_IN_UNIT = Pos(P.pcb_x + P.pcb_t / 2 + P.usb_body_h / 2, P.usb_y, P.usb_z)


def btn_in_unit(z: float):
    """Tactile body centre on the board's wall-side face at height z."""
    return Pos(P.pcb_x - P.pcb_t / 2 - P.btn_body_t / 2, P.btn_y, z)


# Same two, in the BOARD's own frame (x = thickness, y/z centred on the
# outline) so pcbboard.py can pose them without knowing where the unit is.
USBC_IN_BOARD = Pos(
    P.pcb_t / 2 + P.usb_body_h / 2,
    P.usb_y - P.enc_d / 2,
    P.usb_z - (P.pcb_z0 + P.pcb_h / 2),
)


def btn_in_board(z: float):
    return Pos(
        -P.pcb_t / 2 - P.btn_body_t / 2,
        P.btn_y - P.enc_d / 2,
        z - (P.pcb_z0 + P.pcb_h / 2),
    )

# Wall plate: its own frame is x centred, y=0 at the FRONT face (wall
# side is -y), z=0 at the plate bottom. Hangs behind the unit.
PLATE_IN_UNIT = Pos(P.enc_w / 2, 0, 15.0)
