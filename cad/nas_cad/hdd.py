"""Dimensioned SFF-8301 3.5-inch hard-drive reference model.

Coordinates: +X left-to-right, +Y front-to-connector-end, +Z bottom-to-top.
The front face starts at Y=0 and the connector end is at Y=hdd_d.
"""

from build123d import Align, Box, Cylinder, Pos, Rot

from .params import P


def _box_at(x: float, y: float, z: float, w: float, d: float, h: float):
    return Pos(x + w / 2, y + d / 2, z + h / 2) * Box(w, d, h)


def hdd_body():
    """Maximum-height SFF-8301 envelope with standard mounting holes."""
    body = _box_at(0, 0, 0, P.hdd_w, P.hdd_d, P.hdd_base_h)
    shoulder = _box_at(
        P.hdd_cover_inset,
        P.hdd_cover_inset,
        P.hdd_base_h,
        P.hdd_w - 2 * P.hdd_cover_inset,
        P.hdd_d - 2 * P.hdd_cover_inset,
        P.hdd_h - P.hdd_base_h,
    )
    body += shoulder

    # Required rear and alternate front bottom pairs from SFF-8301.
    for x in (P.hdd_bottom_hole_x, P.hdd_w - P.hdd_bottom_hole_x):
        for y in (P.hdd_bottom_hole_rear_y, P.hdd_bottom_hole_front_y):
            body -= Pos(x, y, -0.1) * Cylinder(
                P.hdd_thread_d / 2,
                P.hdd_hole_depth + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    # Two specified holes on each side; axes run inward along X.
    for y in (P.hdd_side_hole_rear_y, P.hdd_side_hole_front_y):
        body -= Pos(-0.1, y, P.hdd_side_hole_z) * Rot(0, 90, 0) * Cylinder(
            P.hdd_thread_d / 2,
            P.hdd_hole_depth + 0.1,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        body -= Pos(P.hdd_w + 0.1, y, P.hdd_side_hole_z) * Rot(0, -90, 0) * Cylinder(
            P.hdd_thread_d / 2,
            P.hdd_hole_depth + 0.1,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    return body


def hdd_cover():
    """Stamped top-cover cue, separate for scene colouring."""
    return _box_at(
        P.hdd_cover_inset + 1.0,
        P.hdd_cover_inset + 1.0,
        P.hdd_h - P.hdd_cover_h,
        P.hdd_w - 2 * (P.hdd_cover_inset + 1.0),
        P.hdd_d - 2 * (P.hdd_cover_inset + 1.0),
        P.hdd_cover_h,
    )


def hdd_label():
    """Top label disc makes drive orientation obvious in an assembly."""
    return Pos(P.hdd_w / 2, P.hdd_d * 0.48, P.hdd_h + 0.05) * Cylinder(
        P.hdd_label_d / 2,
        0.12,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def hdd_hub():
    return Pos(P.hdd_w / 2, P.hdd_d * 0.48, P.hdd_h + 0.17) * Cylinder(
        P.hdd_hub_d / 2,
        0.35,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def sata_drive_connector():
    """Provisional combined 22-pin SATA connector envelope at drive rear."""
    x = P.hdd_w - P.sata_right_margin - P.sata_w
    return _box_at(x, P.hdd_d - P.sata_d, P.sata_z, P.sata_w, P.sata_d, P.sata_h)


def hdd_envelope():
    """Single fit-check solid including the connector envelope."""
    return hdd_body() + hdd_cover() + sata_drive_connector()


def add_hdd_to_scene(scene, loc=None, prefix="hdd"):
    scene.add(hdd_body(), f"{prefix}-body", color="dimgray", loc=loc)
    scene.add(hdd_cover(), f"{prefix}-cover", color="silver", loc=loc)
    scene.add(hdd_label(), f"{prefix}-label", color="whitesmoke", loc=loc)
    scene.add(hdd_hub(), f"{prefix}-hub", color="lightgray", loc=loc)
    scene.add(sata_drive_connector(), f"{prefix}-sata", color="black", loc=loc)
    return scene


def scene():
    from splitflap_cad.viewer import Scene

    return add_hdd_to_scene(Scene())
