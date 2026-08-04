"""Shared geometry idioms for the part builders.

Everything here is frame-agnostic build123d plumbing: no dimensions, no
part knowledge beyond the slot-0 marker style (which is deliberately
one style everywhere).
"""

import math

from build123d import Align, Box, Circle, Cone, Polygon, Pos, Rot, extrude

from .params import P


def box_between(x0, y0, z0, x1, y1, z1):
    """Axis-aligned box addressed by its minimum and maximum corners."""
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        x1 - x0, y1 - y0, z1 - z0
    )


def polar_locs(n: int, start: float = 0.0) -> list:
    """The n rotations of a full polar array about +Z: start, start+360/n, …"""
    return [Rot(0, 0, start + i * 360 / n) for i in range(n)]


def polar(shape, n: int, start: float = 0.0) -> list:
    """`shape` repeated n times around +Z. Subtract or add the copies:
    `for c in polar(cutter, n): body -= c`."""
    return [loc * shape for loc in polar_locs(n, start)]


def radial_plate(profile, thickness: float):
    """Stand a radial-section profile up as a plate.

    `profile` is sketched as radial(x) × axial(y); the result is that
    section in the XZ plane (x radial, y up became +Z), `thickness`
    thick, CENTRED across Y. Symmetric extrusion — the profile's winding
    direction cannot flip which side the material lands on, so no
    per-site recentring shifts.
    """
    return Rot(90, 0, 0) * extrude(profile, amount=thickness / 2, both=True)


def self_supporting_heel(part, radial_growth: float, base_radius: float | None = None):
    """Trim bed-facing bevel ends to a conical printable envelope.

    ``radial_growth`` is radial millimetres gained per millimetre of print
    height. When ``base_radius`` is omitted, the widest planar heel face
    establishes the bed radius. Supplying it lets an integral gear grow from
    an existing hub or drum instead.
    """
    heel_z = part.bounding_box().min.Z
    if base_radius is None:
        heel_faces = [
            face
            for face in part.faces()
            if abs(face.bounding_box().min.Z - heel_z) < 1e-6
            and abs(face.bounding_box().max.Z - heel_z) < 1e-6
        ]
        heel_bounds = max(heel_faces, key=lambda face: face.area).bounding_box()
        base_radius = max(abs(heel_bounds.min.X), abs(heel_bounds.max.X))

    height = part.bounding_box().max.Z - heel_z + 0.1
    envelope = Pos(0, 0, heel_z) * Cone(
        base_radius,
        base_radius + radial_growth * height,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return part & envelope


def support_free_cross_bore(radius: float, length: float, x: float, y: float, z: float):
    """Cross-axis circular clearance with a 45-degree print-direction roof."""
    profile = Circle(radius) + Polygon(
        (-radius, 0),
        (0, radius * math.sqrt(2)),
        (radius, 0),
    )
    tunnel = extrude(profile, amount=length / 2, both=True)
    return Pos(x, y, z) * (Rot(0, 90, 0) * tunnel)


def slot0_marker(apex_r: float, z_face: float, cut: str = "down", point: str = "out"):
    """The first-slot indicator: a debossed triangle on the +X (slot 0)
    line, one style for every part. Returns the solid to subtract.

    apex_r: radius of the triangle's point. point='out' aims the apex
    radially outward (base drum_mark_len further in), 'in' the reverse.
    cut='down' cuts drum_mark_depth into a top face at z_face, 'up' into
    a bottom face.
    """
    s = 1 if point == "out" else -1
    base_r = apex_r - s * P.drum_mark_len
    tri = Polygon(
        (apex_r, 0),
        (base_r, P.drum_mark_w / 2),
        (base_r, -P.drum_mark_w / 2),
        align=None,
    )
    z0 = z_face - P.drum_mark_depth if cut == "down" else z_face
    return Pos(0, 0, z0) * extrude(tri, amount=P.drum_mark_depth)
