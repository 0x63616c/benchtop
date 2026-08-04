"""Dimensioned bare iPad Pro 12.9-inch (4th generation) reference.

Coordinates match the enclosure: landscape width on X, thickness toward -Y,
height on Z. The display faces +Y and the USB-C edge is on the right.
"""

from build123d import Align, Cylinder, Plane, Pos, RectangleRounded, Rot, extrude

from .params import P


def _rounded_prism(w, h, radius, depth, y_front, z_center):
    profile = Pos(0, y_front, z_center) * (Plane.XZ * RectangleRounded(w, h, radius))
    return extrude(profile, amount=depth)


def ipad_body():
    """Exact published outer body envelope, without the camera island."""
    return _rounded_prism(
        P.ipad_w,
        P.ipad_h,
        P.ipad_corner_r,
        P.ipad_t,
        P.ipad_front_y,
        P.screen_z,
    )


def ipad_display():
    """Nominal active display rectangle derived from resolution and 264 ppi."""
    return _rounded_prism(
        P.display_w,
        P.display_h,
        P.display_corner_r,
        0.16,
        P.ipad_front_y + 0.18,
        P.screen_z,
    )


def camera_bump():
    x = -P.ipad_w / 2 + P.camera_edge_inset + P.camera_w / 2
    z = P.ipad_top_z - P.camera_edge_inset - P.camera_h / 2
    return _rounded_prism(
        P.camera_w,
        P.camera_h,
        4.5,
        P.camera_extra_t,
        P.ipad_back_y,
        z,
    ).moved(Pos(x, 0, 0))


def ipad_envelope():
    """Fit-check solid including the conservative rear camera bump."""
    return ipad_body() + camera_bump()


def _camera_lens(x_offset, z_offset, diameter):
    x = -P.ipad_w / 2 + P.camera_edge_inset + P.camera_w / 2 + x_offset
    z = P.ipad_top_z - P.camera_edge_inset - P.camera_h / 2 + z_offset
    return Pos(x, P.camera_back_y - 0.05, z) * Rot(90, 0, 0) * Cylinder(
        diameter / 2,
        0.35,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def scene():
    from splitflap_cad.viewer import Scene

    return (
        Scene()
        .add(ipad_body(), "ipad-aluminium", color="silver", alpha=0.9)
        .add(ipad_display(), "ipad-display", color="black")
        .add(camera_bump(), "camera-island", color="dimgray")
        .add(_camera_lens(-8.0, 8.0, 10.0), "wide-camera", color="black")
        .add(_camera_lens(8.0, -8.0, 9.0), "ultrawide-camera", color="black")
        .add(_camera_lens(-8.0, -8.0, 5.0), "lidar", color="slategray")
    )
