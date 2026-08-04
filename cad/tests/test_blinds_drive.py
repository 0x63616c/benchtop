"""Assembly and print contract for the removable blinds drive cassette."""

from math import sqrt

import pytest
from build123d import Cylinder, Pos, Rot


def test_layshaft_uses_a_real_5mm_rod_and_two_625zz_bearings():
    from blinds_cad.drivecassette import bearing_625zz, layshaft_rod
    from blinds_cad.params import P

    bearing_bounds = bearing_625zz().bounding_box()
    rod_bounds = layshaft_rod().bounding_box()

    assert P.lay_rod_d == 5.0
    assert P.lay_bearing_d == 16.0
    assert P.lay_bearing_w == 5.0
    assert P.lay_bearing_centers_x == (69.0, 89.0)
    assert tuple(bearing_bounds.size) == pytest.approx((5.0, 16.0, 16.0))
    assert tuple(rod_bounds.size) == pytest.approx((38.5, 5.0, 5.0))


def test_drive_cassette_is_removable_and_all_four_mounts_are_supported():
    from blinds_cad.drivecassette import bearing_caps, drive_cassette
    from blinds_cad.enclosure import frame
    from blinds_cad.params import P

    structure = frame()
    cassette = drive_cassette()
    caps = bearing_caps()

    assert len(structure.solids()) == 1
    assert len(cassette.solids()) == 1
    assert len(caps.solids()) == 2
    assert (structure & cassette).volume < 1e-6

    for x, y, z in P.drive_mount_points:
        screw = Pos(x, P.drive_tab_y1 + 0.5, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.drive_mount_clear_d / 2, P.drive_tab_y1 + 1)
        )
        frame_pad = Pos(x, y, z) * (
            Rot(90, 0, 0)
            * Cylinder(P.drive_mount_boss_d / 2, P.drive_mount_face_y)
        )

        assert (structure & screw).volume < 1e-6, (x, z)
        assert (cassette & screw).volume < 1e-6, (x, z)
        assert (structure & frame_pad).volume >= 30.0, (x, z)


@pytest.mark.parametrize(
    "gear",
    [
        pytest.param("pinion_print", id="motor-spur-pinion"),
        pytest.param("spur_gear_print", id="layshaft-spur"),
        pytest.param("bevel_gear_print", id="layshaft-bevel"),
    ],
)
def test_each_gear_is_a_separate_heel_or_face_down_print(gear):
    from blinds_cad import gears

    part = getattr(gears, gear)()
    bounds = part.bounding_box()
    bed_faces = [
        face
        for face in part.faces()
        if face.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
        and face.bounding_box().max.Z == pytest.approx(0, abs=1e-6)
        and face.normal_at().Z < -0.99
    ]

    assert len(part.solids()) == 1
    assert bounds.min.Z == pytest.approx(0, abs=1e-6)
    assert bed_faces

    vertices, triangles = part.tessellate(0.1, 0.1)
    unsupported = []
    for a, b, c in triangles:
        p0, p1, p2 = vertices[a], vertices[b], vertices[c]
        ux, uy, uz = p1.X - p0.X, p1.Y - p0.Y, p1.Z - p0.Z
        vx, vy, vz = p2.X - p0.X, p2.Y - p0.Y, p2.Z - p0.Z
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        magnitude = sqrt(nx * nx + ny * ny + nz * nz)
        normal_z = nz / magnitude if magnitude else 0
        if normal_z < -0.71 and min(p0.Z, p1.Z, p2.Z) > 1e-4:
            unsupported.extend((p0, p1, p2))

    # Only the tiny cross-pin/grub-screw guide bridge may point down;
    # all tooth and rim surfaces stay inside the 55-degree envelope.
    assert max(
        (sqrt(vertex.X * vertex.X + vertex.Y * vertex.Y) for vertex in unsupported),
        default=0,
    ) <= 7.1


def test_spacers_and_bearing_caps_positively_locate_the_rod_stack():
    from blinds_cad.drivecassette import scene
    from blinds_cad.params import P

    args = scene().show_args()
    parts = dict(zip(args["names"], args["objects"]))
    required = {
        "cassette",
        "bearing-caps",
        "motor",
        "pinion",
        "motor-spacer",
        "layshaft-bevel",
        "bevel-spacer",
        "left-bearing",
        "inner-spacer",
        "layshaft-spur",
        "outer-spacer",
        "right-bearing",
        "layshaft-rod",
    }
    assert set(parts) == required

    assert (
        parts["motor-spacer"].bounding_box().max.X
        + P.drive_running_gap
        == pytest.approx(parts["pinion"].bounding_box().min.X)
    )
    assert (
        parts["layshaft-bevel"].bounding_box().max.X
        + P.drive_running_gap
        == pytest.approx(parts["bevel-spacer"].bounding_box().min.X)
    )
    assert parts["bevel-spacer"].bounding_box().max.X == pytest.approx(
        parts["left-bearing"].bounding_box().min.X
    )
    assert parts["left-bearing"].bounding_box().max.X == pytest.approx(
        parts["inner-spacer"].bounding_box().min.X
    )
    assert (
        parts["inner-spacer"].bounding_box().max.X
        + P.drive_running_gap
        == pytest.approx(parts["layshaft-spur"].bounding_box().min.X)
    )
    assert (
        parts["layshaft-spur"].bounding_box().max.X
        + P.drive_running_gap
        == pytest.approx(parts["outer-spacer"].bounding_box().min.X)
    )
    assert parts["outer-spacer"].bounding_box().max.X == pytest.approx(
        parts["right-bearing"].bounding_box().min.X
    )

    for name in required - {"layshaft-rod", "motor", "cassette", "bearing-caps"}:
        if name == "motor-spacer" or name == "pinion":
            continue
        assert (parts["layshaft-rod"] & parts[name]).volume < 1e-6, name
