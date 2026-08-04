"""Thin cosmetic enclosure for the wall-mounted blinds frame.

The sleeve is an open-back, open-top box: front, sides, and bottom only.
It slides from the room toward the wall after the working mechanism is
installed.  Two M3 screws through the underside retain it.

The top closes afterward with two flat-printing cap halves.  Their seam
runs through the bead-chain plane, so each half contributes one open
semicircle around each strand.  Neither part has to be threaded over the
continuous chain.

Print orientations (P2S, no generated support):
- sleeve: exterior front face on the bed;
- cap halves: exterior top face on the bed.
"""

from build123d import Cylinder, Pos, Rot
from splitflap_cad.geo import box_between

from .params import P


def sleeve():
    """The non-structural slide-on skin in assembled unit coordinates."""
    w, d, h, t = P.enc_w, P.enc_d, P.sleeve_h, P.sleeve_t

    body = box_between(0, 0, 0, t, d, h)
    body += box_between(w - t, 0, 0, w, d, h)
    body += box_between(0, d - t, 0, w, d, h)
    body += box_between(0, 0, 0, w, d, t)

    # Existing controls stay on the front face.
    for x in (P.btn_x1, P.btn_x2):
        body -= Pos(x, d - t / 2, P.btn_z) * (
            Rot(90, 0, 0) * Cylinder(P.btn_d / 2, t + 2)
        )
    body -= box_between(
        P.usb_x - P.usb_w / 2,
        d - t - 1,
        P.usb_z - P.usb_t / 2,
        P.usb_x + P.usb_w / 2,
        d + 1,
        P.usb_z + P.usb_t / 2,
    )

    # Two underside screws retain the sleeve against sliding back off.
    for x, y in P.sleeve_retainer_xy:
        body -= Pos(x, y, t / 2) * Cylinder(
            P.sleeve_retainer_d / 2, t + 2
        )
    return body


def _chain_clearance(part):
    """Cut an open semicircle from the mating edge of either cap half."""
    zc = P.enc_h - P.cap_t / 2
    for x in P.strand_x:
        part -= Pos(x, P.spr_wy, zc) * Cylinder(
            P.chain_slot / 2, P.cap_t + 2
        )
    return part


def _side_lips(y0: float, y1: float):
    """Two locating skirts inside the sleeve side walls."""
    t, c = P.sleeve_t, P.cap_fit
    z0, z1 = P.enc_h - P.cap_t - P.cap_skirt, P.enc_h - P.cap_t
    left = box_between(t + c, y0, z0, 2 * t + c, y1, z1)
    right = box_between(P.enc_w - 2 * t - c, y0, z0, P.enc_w - t - c, y1, z1)
    return left + right


def cap_rear():
    """Wall-side cap half; installs from behind the chain plane."""
    z0 = P.enc_h - P.cap_t
    body = box_between(0, 0, z0, P.enc_w, P.spr_wy, P.enc_h)
    body += _side_lips(P.sleeve_t, P.spr_wy - P.cap_lap)
    return _chain_clearance(body)


def cap_front():
    """Room-side cap half; installs after the rear half."""
    z0 = P.enc_h - P.cap_t
    body = box_between(0, P.spr_wy, z0, P.enc_w, P.enc_d, P.enc_h)
    body += _side_lips(P.spr_wy + P.cap_lap, P.enc_d - P.sleeve_t)
    return _chain_clearance(body)


def scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(sleeve(), "sleeve", color="whitesmoke", alpha=0.65)


def cap_scene():
    from splitflap_cad.viewer import Scene

    return (
        Scene()
        .add(cap_rear(), "cap-rear", color="lightsteelblue")
        .add(cap_front(), "cap-front", color="gainsboro")
    )
