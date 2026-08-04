"""Parametric multi-bay storage block assembled from the proven bay unit."""

from build123d import Pos

from .bay import (
    bay_frame,
    backplane,
    caddy,
    caddy_location,
    drive_in_caddy_location,
    latch,
    latch_location,
)
from .hdd import add_hdd_to_scene
from .params import P


def storage_frame(columns: int = P.bay_columns, rows: int = P.bay_rows):
    """Union of repeated bays; dimensions follow columns and rows."""
    if columns < 1 or rows < 1:
        raise ValueError("NAS storage frame needs at least one row and column")
    result = None
    for row in range(rows):
        for column in range(columns):
            loc = Pos(
                column * (P.bay_w + P.bay_array_gap),
                0,
                row * (P.bay_h + P.bay_array_gap),
            )
            part = loc * bay_frame()
            result = part if result is None else result + part
    return result


def scene(columns: int = P.bay_columns, rows: int = P.bay_rows):
    from splitflap_cad.viewer import Scene

    s = Scene()
    for row in range(rows):
        for column in range(columns):
            index = row * columns + column + 1
            cell = Pos(
                column * (P.bay_w + P.bay_array_gap),
                0,
                row * (P.bay_h + P.bay_array_gap),
            )
            s.add(bay_frame(), f"bay-{index}", color="lightsteelblue", alpha=0.82, loc=cell)
            s.add(caddy(), f"caddy-{index}", color="slategray", loc=cell * caddy_location())
            s.add(latch(), f"latch-{index}", color="orange", loc=cell * latch_location())
            pcb, plug = backplane()
            s.add(
                pcb,
                f"backplane-pcb-{index}",
                color="darkgreen",
                loc=cell,
            )
            s.add(
                plug,
                f"backplane-sata-{index}",
                color="black",
                loc=cell,
            )
            add_hdd_to_scene(s, cell * drive_in_caddy_location(), prefix=f"hdd-{index}")
    return s
