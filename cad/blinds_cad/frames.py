"""Named frames: where each part's local frame sits in UNIT coordinates.

Unit frame: origin at the wall-side, left-bottom corner of the frame.
+X right (along the wall), +Y off the wall into the room, +Z up. The
frame mounts directly at y=0; the cosmetic sleeve shares this frame.

Naming: X_IN_UNIT maps X-local coords into unit coords.
"""

from build123d import Pos, Rot

from .params import P

# Motor frame (shaft axis at gearbox face, shaft +Z, eccentric +Y local)
# onto the horizontal shaft axis: local +Z -> unit +X (shaft points
# right), local +Y (eccentricity) -> unit -Z so the gearbox axis sits
# 7 BELOW the shaft axis (clears the wrap guide above).
_SHAFT_ROT = Rot(0, 90, 0) * Rot(0, 0, -90)
MOTOR_IN_UNIT = Pos(P.bulkhead_x, P.drive_y, P.motor_z) * _SHAFT_ROT

# Spur pinion (axis +Z, D-flat toward local +Y like the shaft) onto the
# shaft tip, teeth centered on the mesh plane. Tooth phasing lives in
# gears.pinion() so the D-bore stays aligned with the shaft flat.
PINION_IN_UNIT = Pos(P.pinion_x, P.drive_y, P.motor_z) * _SHAFT_ROT

# Layshaft (axis +Z, bevel heel plane at local z=0, apex +Z, body -Z)
# onto its axis: local +Z -> unit -X so the apex points at the sprocket
# and the shaft/spur run right toward the saddles.
LAYSHAFT_IN_UNIT = Pos(P.bevel_heel_x, P.drive_y, P.lay_z) * Rot(0, -90, 0)

# Sprocket (axis +Z, wheel mid-plane z=0, ring gear +Z) onto the M5
# axle: local +Z -> unit -Y so the ring sits wall-side at y=11.
SPROCKET_IN_UNIT = Pos(P.drive_x, P.spr_wy, P.spr_z) * Rot(90, 0, 0)

# Chain ghost is built unit-aligned (wheel axis +Y) — translate only.
CHAIN_IN_UNIT = Pos(P.drive_x, P.spr_wy, P.spr_z)

# Battery bay: bought holder plastic backs sit on the integral mounting
# spine's room-side face.  Cells run across +X in two three-slot banks.
BAY_IN_UNIT = Pos(P.drive_x, P.battery_mount_y, P.battery_z0)

# Main PCB: flat on the floor bosses, board center.
PCB_IN_UNIT = Pos(
    P.pcb_x0 + P.pcb_l / 2, P.pcb_y0 + P.pcb_wd / 2, P.pcb_z0 + P.pcb_t / 2
)

# USB-C receptacle: mouth flush with the front wall's inner face.
_USB_YC = P.enc_d - P.enc_wall - P.usb_body_l / 2
USBC_IN_UNIT = Pos(P.usb_x, _USB_YC, P.usb_z)

_BTN_YC = P.enc_d - P.enc_wall - P.btn_body_t / 2


def btn_in_unit(x: float):
    """Right-angle tactile body centre at the board's front edge."""
    return Pos(x, _BTN_YC, P.btn_z)


# Same two, in the BOARD's own frame (laminate centred at the origin)
# so pcbboard.py can pose them without knowing where the unit is.
_B = PCB_IN_UNIT.position
USBC_IN_BOARD = Pos(P.usb_x - _B.X, _USB_YC - _B.Y, P.usb_z - _B.Z)


def btn_in_board(x: float):
    return Pos(x - _B.X, _BTN_YC - _B.Y, P.btn_z - _B.Z)
