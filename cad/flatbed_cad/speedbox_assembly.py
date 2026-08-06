"""Complete enclosed Flatbed JGB37 right-angle speedbox assembly."""

from splitflap_cad.viewer import Scene

from . import frames as F
from .motor_reference import motor_reference
from .speedbox import (
    output_bearings,
    output_rod,
    pair_in_box,
    pair_parts,
    posed_input_spacer,
    posed_output_spacer,
)
from .speedbox_panels import (
    bottom_panel,
    front_panel,
    left_panel,
    motor_bulkhead,
    rear_panel,
    right_panel,
    top_panel,
)


def scene() -> Scene:
    """Six thin skins, local nut bosses, bulkhead, motor, and drivetrain."""
    input_part, output_part = pair_parts()
    gear_frame = pair_in_box()
    return (
        Scene()
        .add(bottom_panel(), "bottom", "lightblue", 0.30, F.FG_BOTTOM_IN_BOX)
        .add(top_panel(), "top", "lightskyblue", 0.20, F.FG_TOP_IN_BOX)
        .add(left_panel(), "left", "lightblue", 0.25, F.FG_LEFT_IN_BOX)
        .add(right_panel(), "right", "lightblue", 0.25, F.FG_RIGHT_IN_BOX)
        .add(rear_panel(), "rear", "lightskyblue", 0.25, F.FG_REAR_IN_BOX)
        .add(front_panel(), "front", "lightskyblue", 0.20, F.FG_FRONT_IN_BOX)
        .add(
            motor_bulkhead(),
            "motor-bulkhead",
            "steelblue",
            0.35,
            F.FG_BULKHEAD_IN_BOX,
        )
        .add(motor_reference(), "jgb37-520", "silver", loc=F.FG_MOTOR_IN_BOX)
        .add(input_part, "24T-input", "orange", loc=gear_frame)
        .add(posed_input_spacer(), "input-spacer", "darkorange")
        .add(output_part, "18T-output", "gold", loc=gear_frame)
        .add(posed_output_spacer(), "output-spacer", "goldenrod")
        .add(output_bearings(), "625ZZ-bearings", "silver")
        .add(output_rod(), "5mm-output-shaft", "dimgray")
    )
