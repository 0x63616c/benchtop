"""Render production cassette-v2 documentation images.

Run from the repository root:
    PYTHONPATH=cad cad/.venv/bin/python cad/render_blinds_cassette_v2.py
"""

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from build123d import Pos
from matplotlib.colors import LightSource
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from blinds_cad.drivecassette import (
    _axis_y_cylinder,
    cassette_lid,
    drive_cassette,
    drive_parts,
)
from blinds_cad.enclosure import _drive_mounts
from blinds_cad.params import P


OUT = Path(__file__).parent.parent / "docs" / "research" / "img"
BACKGROUND = "#17191d"
FOREGROUND = "#f3f5f7"


@dataclass(frozen=True)
class Item:
    shape: object
    color: str
    alpha: float = 1.0


GEAR_NAMES = {
    "chain-wheel",
    "sprocket-bevel",
    "sprocket-spacer",
    "pinion",
    "motor-spacer",
    "layshaft-bevel",
    "bevel-spacer",
    "inner-spacer",
    "layshaft-spur",
    "outer-spacer",
}


def _assembled_items(*, lid_offset=0.0):
    items = []
    for name, shape in drive_parts().items():
        if name == "drive-cassette":
            items.append(Item(shape, "#8eb9d6", 0.72))
        elif name == "cassette-lid":
            items.append(Item(Pos(0, lid_offset, 0) * shape, "#3276a8", 0.9))
        elif name in GEAR_NAMES:
            items.append(Item(shape, "#f2a93b", 1.0))
        elif name == "motor":
            items.append(Item(shape, "#aeb5bd", 0.95))
        else:
            items.append(Item(shape, "#d7dce1", 1.0))
    return items


def _dock_items():
    offset = 12.0
    items = [Item(_drive_mounts(), "#7d8792", 0.95)]
    items.append(Item(Pos(0, offset, 0) * drive_cassette(), "#8eb9d6", 0.72))
    items.append(Item(Pos(0, offset, 0) * cassette_lid(), "#3276a8", 0.9))
    for x, _y, z in P.drive_mount_points:
        screw_y0 = P.drive_mount_face_y + offset
        items.append(
            Item(
                _axis_y_cylinder(1.7, screw_y0, 9.0, x, z),
                "#f2b84b",
            )
        )
        items.append(
            Item(_axis_y_cylinder(3.2, screw_y0 + 9.0, 2.0, x, z), "#f2b84b")
        )
    return items


def _render(items, filename, title, note, legend, *, elev=23, azim=52):
    fig = plt.figure(figsize=(12, 8), dpi=180, facecolor=BACKGROUND)
    ax = fig.add_subplot(111, projection="3d", facecolor=BACKGROUND)
    mins = np.array([np.inf, np.inf, np.inf])
    maxs = np.array([-np.inf, -np.inf, -np.inf])

    for item in items:
        vertices, triangles = item.shape.tessellate(0.55, 0.25)
        points = np.array([(v.X, v.Y, v.Z) for v in vertices])
        faces = points[np.asarray(triangles, dtype=int)]
        collection = Poly3DCollection(
            faces,
            facecolors=item.color,
            linewidth=0,
            alpha=item.alpha,
            zsort="average",
            shade=True,
            lightsource=LightSource(azdeg=315, altdeg=42),
        )
        collection.set_edgecolor("none")
        ax.add_collection3d(collection)
        mins = np.minimum(mins, points.min(axis=0))
        maxs = np.maximum(maxs, points.max(axis=0))

    center = (mins + maxs) / 2
    span = max(maxs - mins) * 0.60
    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(center[2] - span, center[2] + span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type("persp", focal_length=0.9)
    ax.set_axis_off()

    fig.text(0.045, 0.94, title, color=FOREGROUND, fontsize=18, weight="bold")
    fig.text(0.045, 0.905, note, color="#aeb6c2", fontsize=11)
    handles = [
        Patch(facecolor=color, edgecolor="none", alpha=alpha, label=label)
        for label, color, alpha in legend
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=len(handles),
        frameon=False,
        labelcolor=FOREGROUND,
        fontsize=9,
        bbox_to_anchor=(0.5, 0.02),
    )
    fig.subplots_adjust(left=0, right=1, bottom=0.08, top=0.89)
    output = OUT / filename
    fig.savefig(output, facecolor=BACKGROUND, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(output)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mechanism_legend = (
        ("stepped chassis", "#8eb9d6", 0.72),
        ("single lid", "#3276a8", 0.9),
        ("gears + sprocket", "#f2a93b", 1.0),
        ("bought hardware", "#d7dce1", 1.0),
    )
    _render(
        _assembled_items(),
        "blinds-drive-cassette-v2-assembled.png",
        "Production cassette v2 — 89.2 × 41.0 × 80.6 mm",
        "The mechanism is enclosed by one stepped chassis and one structural lid.",
        mechanism_legend,
    )
    _render(
        _assembled_items(lid_offset=28.0),
        "blinds-drive-cassette-v2-exploded.png",
        "One lid releases every service point",
        "Both 625ZZ split seats and the front MR105ZZ open in one roomward move.",
        mechanism_legend,
        azim=43,
    )
    _render(
        _dock_items(),
        "blinds-drive-cassette-v2-dock.png",
        "Keyed shelf; only two clamp screws",
        "The shelf carries weight and the upper key reacts torque before screws are fitted.",
        (
            ("frame dock", "#7d8792", 0.95),
            ("cassette", "#8eb9d6", 0.72),
            ("single lid", "#3276a8", 0.9),
            ("two screws", "#f2b84b", 1.0),
        ),
        azim=48,
    )


if __name__ == "__main__":
    main()
