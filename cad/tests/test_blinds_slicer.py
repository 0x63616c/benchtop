"""Bambu Studio regressions for documented blinds print orientations."""

import json
from pathlib import Path
import shutil
import subprocess

from build123d import Pos, Rot, export_stl
import pytest


PROFILE_ROOT = Path(
    "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL"
)


def _resolved_preset(kind: str, name: str) -> dict:
    source = PROFILE_ROOT / kind / f"{name}.json"
    data = json.loads(source.read_text())
    resolved = {}
    if parent := data.get("inherits"):
        resolved.update(_resolved_preset(kind, parent))
    for include in data.get("include", []):
        resolved.update(_resolved_preset(kind, include))
    resolved.update(
        {key: value for key, value in data.items() if key not in ("inherits", "include")}
    )
    return resolved


def _printable(name: str):
    if name == "frame":
        from blinds_cad.enclosure import frame

        return Rot(90, 0, 0) * frame()
    if name == "drive-cassette":
        from blinds_cad.drivecassette import drive_cassette

        return Rot(90, 0, 0) * drive_cassette()
    if name == "bearing-caps":
        from blinds_cad.drivecassette import bearing_caps_print

        return bearing_caps_print()
    if name == "drive-spacers":
        from blinds_cad.drivecassette import spacers_print

        return spacers_print()
    if name == "sprocket":
        from blinds_cad.sprocket import sprocket_print

        return sprocket_print()
    from blinds_cad import gears

    return getattr(gears, f"{name}_print")()


@pytest.mark.slow
@pytest.mark.parametrize(
    "model",
    (
        "frame",
        "drive-cassette",
        "bearing-caps",
        "drive-spacers",
        "sprocket",
        "pinion",
        "spur_gear",
        "bevel_gear",
    ),
)
def test_structural_and_drive_parts_slice_without_support_or_warnings(tmp_path, model):
    studio = shutil.which("bambu-studio")
    if studio is None or not PROFILE_ROOT.exists():
        pytest.skip("Bambu Studio P2S profiles are not installed")

    oriented = _printable(model)
    bounds = oriented.bounding_box()
    oriented = Pos(
        10 - bounds.min.X,
        10 - bounds.min.Y,
        -bounds.min.Z,
    ) * oriented
    stl = tmp_path / f"blinds-{model}.stl"
    export_stl(oriented, str(stl))

    presets = {
        "machine.json": _resolved_preset("machine", "Bambu Lab P2S 0.4 nozzle"),
        "process.json": _resolved_preset("process", "0.20mm Standard @BBL P2S"),
        "filament.json": _resolved_preset("filament", "Generic PETG @BBL P2S"),
    }
    presets["process.json"].update(
        curr_bed_type="Textured PEI Plate",
        enable_support="0",
    )
    for filename, preset in presets.items():
        (tmp_path / filename).write_text(json.dumps(preset))

    completed = subprocess.run(
        [
            studio,
            "--debug", "2",
            "--load-settings",
            f"{tmp_path / 'machine.json'};{tmp_path / 'process.json'}",
            "--load-filaments", str(tmp_path / "filament.json"),
            "--load-filament-ids", "1",
            "--slice", "0",
            "--outputdir", str(tmp_path),
            str(stl),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr

    result = json.loads((tmp_path / "result.json").read_text())
    assert result["return_code"] == 0, result["error_string"]
    warnings = [
        plate.get("warning_message", "")
        for plate in result.get("sliced_plates", [])
        if plate.get("warning_message")
    ]
    assert warnings == []

    gcode = (tmp_path / "plate_1.gcode").read_text(errors="replace")
    assert "; FEATURE: Support" not in gcode
    assert ";TYPE:Support" not in gcode
