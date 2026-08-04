"""Eight-piece scale-faithful compact Macintosh cosmetic shell.

The hollow shell is split left/right, lower/upper, and at the vintage-style
front/rear service seam. Every sector fits the Bambu Lab P2S. Internal seam
lips provide registration and an inside screw/glue land without changing the
outside silhouette.
"""

from functools import lru_cache

from build123d import Align, Box, Cylinder, Plane, Polygon, Pos, RectangleRounded, Rot, extrude, make_face
from splitflap_cad.geo import box_between

from .params import P


def _rounded_prism(w, h, radius, depth, y_front, z_center):
    profile = Pos(0, y_front, z_center) * (Plane.XZ * RectangleRounded(w, h, radius))
    return extrude(profile, amount=depth)


def _side_envelope(width, y_front, y_back_bottom, y_back_top, z0, z1):
    profile = make_face(
        Plane.YZ
        * Polygon(
            (y_front, z0),
            (y_back_bottom, z0),
            (y_back_top, z1),
            (y_front, z1),
        )
    )
    return extrude(profile, amount=width / 2, both=True)


@lru_cache(maxsize=1)
def full_shell():
    """Complete hollow skin before its eight printable-sector cuts."""
    outer = _rounded_prism(
        P.case_w, P.case_h, P.case_corner_r, P.case_d, 0, P.case_h / 2
    )
    outer &= _side_envelope(
        P.case_w + 2,
        0,
        -P.case_d,
        -P.case_d + P.rear_top_slope,
        0,
        P.case_h,
    )

    inner = _rounded_prism(
        P.case_w - 2 * P.skin_t,
        P.case_h - 2 * P.skin_t,
        P.case_corner_r - P.skin_t,
        P.case_d - 2 * P.skin_t,
        -P.skin_t,
        P.case_h / 2,
    )
    inner &= _side_envelope(
        P.case_w - 2 * P.skin_t,
        -P.skin_t,
        -P.case_d + P.skin_t,
        -P.case_d + P.rear_top_slope + P.skin_t,
        P.skin_t,
        P.case_h - P.skin_t,
    )
    shell = outer - inner

    # Exact active-display opening and top-loading device slot.
    shell -= _rounded_prism(
        P.display_w,
        P.display_h,
        P.display_corner_r,
        P.skin_t + 2,
        1,
        P.screen_z,
    )
    shell -= box_between(
        -P.pocket_half_w,
        P.slot_y0,
        P.case_h - P.skin_t - 1,
        P.pocket_half_w,
        P.slot_y1,
        P.case_h + 1,
    )

    # Macintosh face cues: floppy slot and a 3x3 speaker-hole array.
    shell -= box_between(
        P.floppy_x - P.floppy_w / 2,
        -P.skin_t - 1,
        P.floppy_z - P.floppy_h / 2,
        P.floppy_x + P.floppy_w / 2,
        1,
        P.floppy_z + P.floppy_h / 2,
    )
    for dx in (-7.0, 0.0, 7.0):
        for dz in (-7.0, 0.0, 7.0):
            shell -= Pos(P.speaker_x + dx, 1, P.speaker_z + dz) * Rot(90, 0, 0) * Cylinder(
                P.speaker_hole_d / 2,
                P.skin_t + 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    # Rear ventilation slots low on the sloped shell.
    for x in (-95.0, -57.0, -19.0, 19.0, 57.0, 95.0):
        shell -= box_between(
            x - 12.0,
            -P.case_d - 1,
            74.0,
            x + 12.0,
            -P.case_d + 10.0,
            80.0,
        )
    return shell


def _sector(side: int, level: int, section: int):
    eps = 0.05
    x0, x1 = (-P.case_w / 2 - eps, eps) if side < 0 else (-eps, P.case_w / 2 + eps)
    z0, z1 = (0 - eps, P.case_h / 2 + eps) if level < 0 else (P.case_h / 2 - eps, P.case_h + eps)
    if section > 0:  # front
        y0, y1 = -P.front_section_d - eps, eps
    else:  # rear
        y0, y1 = -P.case_d - eps, -P.front_section_d + eps
    part = full_shell() & box_between(x0, y0, z0, x1, y1, z1)

    # Registration lands are deliberately internal and cross only the mating
    # seam. Lower/left/rear sectors own the lap so every seam has one datum.
    inner_y = -P.skin_t - P.seam_lip_t
    if section > 0 and side < 0:
        part += box_between(
            -P.seam_lip,
            inner_y,
            z0 + P.case_corner_r,
            P.seam_lip,
            -P.skin_t,
            z1 - P.case_corner_r,
        )
    if section > 0 and level < 0:
        part += box_between(
            x0 + P.case_corner_r,
            inner_y,
            P.case_h / 2 - P.seam_lip,
            x1 - P.case_corner_r,
            -P.skin_t,
            P.case_h / 2 + P.seam_lip,
        )
    if section < 0:
        part += box_between(
            x0 + P.case_corner_r,
            -P.front_section_d - P.seam_lip,
            z0 + P.case_corner_r,
            x1 - P.case_corner_r,
            -P.front_section_d + P.seam_lip,
            z0 + P.case_corner_r + P.seam_lip_t,
        )
    return part


def skin_front_left_lower(): return _sector(-1, -1, 1)
def skin_front_right_lower(): return _sector(1, -1, 1)
def skin_front_left_upper(): return _sector(-1, 1, 1)
def skin_front_right_upper(): return _sector(1, 1, 1)
def skin_rear_left_lower(): return _sector(-1, -1, -1)
def skin_rear_right_lower(): return _sector(1, -1, -1)
def skin_rear_left_upper(): return _sector(-1, 1, -1)
def skin_rear_right_upper(): return _sector(1, 1, -1)


SKIN_BUILDERS = (
    skin_front_left_lower,
    skin_front_right_lower,
    skin_front_left_upper,
    skin_front_right_upper,
    skin_rear_left_lower,
    skin_rear_right_lower,
    skin_rear_left_upper,
    skin_rear_right_upper,
)


def scene():
    from splitflap_cad.viewer import Scene

    result = Scene()
    names = (
        "front-left-lower", "front-right-lower", "front-left-upper", "front-right-upper",
        "rear-left-lower", "rear-right-lower", "rear-left-upper", "rear-right-upper",
    )
    for name, builder in zip(names, SKIN_BUILDERS, strict=True):
        result.add(builder(), name, color="gainsboro", alpha=0.72)
    return result
