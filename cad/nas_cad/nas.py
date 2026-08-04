"""Parametric upright multi-bay storage block with animated push-doors."""

from build123d import Pos

from .bay import add_opening_animation, bay_group, vertical_bay_frame, vertical_bay_location
from .params import P


def storage_frame(columns: int = P.bay_columns, rows: int = P.bay_rows):
    """Union of upright repeated bays; dimensions follow columns and rows."""
    if columns < 1 or rows < 1:
        raise ValueError("NAS storage frame needs at least one row and column")
    result = None
    pitch_x = P.bay_h + P.bay_array_gap
    pitch_z = P.bay_w + P.bay_array_gap
    for row in range(rows):
        for column in range(columns):
            part = Pos(column * pitch_x, 0, row * pitch_z) * vertical_bay_frame()
            result = part if result is None else result + part
    return result


def scene(columns: int = P.bay_columns, rows: int = P.bay_rows):
    """Six narrow vertical bays; doors animate in a left-to-right wave."""
    from splitflap_cad.viewer import Scene

    storage = Scene()
    pitch_x = P.bay_h + P.bay_array_gap
    pitch_z = P.bay_w + P.bay_array_gap
    for row in range(rows):
        for column in range(columns):
            index = row * columns + column + 1
            bay_name = f"bay-{index}"
            loc = Pos(column * pitch_x, 0, row * pitch_z) * vertical_bay_location()
            storage.add_group(bay_group(), bay_name, loc=loc)

    result = Scene().add_group(storage, "nas-storage")
    for index in range(1, columns * rows + 1):
        add_opening_animation(
            result,
            f"nas-storage/bay-{index}",
            start=(index - 1) * 0.16,
        )
    return result.animation_speed(1.0)
