"""Reusable five-size test plate for short M3 heat-set inserts.

The 5 mm plate carries five 3.4 mm-deep blind bores from 4.0 through 4.4 mm.
Each bore is engraved with its modeled diameter. This is separate from the
2 mm captive-nut corner kit because it calibrates a different construction
style and can be reused for future printed parts.
"""

from build123d import Box, Cylinder, Pos

from splitflap_cad.viewer import Scene

from .geo import engrave_text
from .params import P


def insert_test_plate():
    """Flat M3x3 heat-set-insert bore ladder with a solid blind floor."""
    body = Pos(0, 0, P.insert_plate_t / 2) * Box(
        P.insert_plate_w,
        P.insert_plate_h,
        P.insert_plate_t,
    )
    x0 = -2 * P.insert_pitch
    for variant, bore_d in enumerate(P.insert_bore_ds):
        x = x0 + variant * P.insert_pitch
        body -= Pos(
            x,
            P.insert_hole_y,
            P.insert_plate_t - P.insert_bore_depth / 2 + 0.1,
        ) * Cylinder(bore_d / 2, P.insert_bore_depth + 0.2)
        body = engrave_text(
            body,
            f"D{bore_d:.1f}",
            x=x,
            y=P.insert_label_y,
            top=P.insert_plate_t,
            size=P.label_size,
        )
    return engrave_text(
        body,
        "M3x3 INSERT",
        x=0,
        y=P.insert_title_y,
        top=P.insert_plate_t,
        size=P.label_size,
    )


def scene() -> Scene:
    return Scene().add(insert_test_plate(), "m3x3-insert-test", "coral")
