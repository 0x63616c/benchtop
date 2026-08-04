"""Complete Retro Mac assembly: shell, independent cradle, caps, and iPad."""

from .cradle import cradle_left, cradle_right, slot_cap_left, slot_cap_right
from .ipad import camera_bump, ipad_body, ipad_display
from .shell import SKIN_BUILDERS


def scene():
    from splitflap_cad.viewer import Scene

    result = Scene()
    skin_names = (
        "skin-front-left-lower", "skin-front-right-lower",
        "skin-front-left-upper", "skin-front-right-upper",
        "skin-rear-left-lower", "skin-rear-right-lower",
        "skin-rear-left-upper", "skin-rear-right-upper",
    )
    for name, builder in zip(skin_names, SKIN_BUILDERS, strict=True):
        result.add(builder(), name, color="gainsboro", alpha=0.58)
    return (
        result
        .add(cradle_left(), "cradle-left", color="goldenrod")
        .add(cradle_right(), "cradle-right", color="darkgoldenrod")
        .add(slot_cap_left(), "slot-cap-left", color="gainsboro")
        .add(slot_cap_right(), "slot-cap-right", color="lightgray")
        .add(ipad_body(), "ipad-body", color="silver", alpha=0.82)
        .add(ipad_display(), "ipad-display", color="black")
        .add(camera_bump(), "ipad-camera", color="dimgray")
    )
