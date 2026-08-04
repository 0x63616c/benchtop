"""The catalog is the single registry — keep it honest without building
geometry (builders are lazy; nothing here should touch build123d)."""

from pathlib import Path

from splitflap_cad.catalog import MODELS, PRINTABLE, PROJECTS, RENDERS, SRC_TO_MODEL

CAD = Path(__file__).parent.parent
SRC = CAD / "splitflap_cad"


def _module_path(src: str) -> Path:
    """Bare stem lives in splitflap_cad; dotted src is package-absolute."""
    if "." in src:
        return CAD / (src.replace(".", "/") + ".py")
    return SRC / f"{src}.py"


def test_every_model_documented():
    for name, m in MODELS.items():
        assert m.help.strip(), f"{name} needs a help line"


def test_every_catalog_entry_belongs_to_a_project():
    entries = {**MODELS, **PRINTABLE, **RENDERS}
    for name, entry in entries.items():
        assert entry.project in PROJECTS, f"{name}: unknown project {entry.project!r}"

    used = {entry.project for entry in entries.values()}
    assert used == set(PROJECTS), "remove empty projects or add their first catalog entry"


def test_every_src_is_a_real_module():
    for name, m in MODELS.items():
        assert _module_path(m.src).exists(), f"{name}: no module {m.src}"


def test_src_map_covers_all_models():
    # models may share a src (unit/plate); the map keeps the first, and
    # every mapped name must be a real model. Keys are module STEMS —
    # which must therefore stay unique across project packages.
    assert set(SRC_TO_MODEL.values()) <= set(MODELS)
    assert set(SRC_TO_MODEL) == {m.src.rsplit(".", 1)[-1] for m in MODELS.values()}


def test_printable_builders_exist():
    assert set(PRINTABLE) == {
        "unit",
        "unit-nema",
        "bridge-nema",
        "flap",
        "drum-outer",
        "drum-inner-byj",
        "drum-inner-nema",
        "holder",
        "ipad-body",
        "ipad-lid",
        "grommet-usb",
        "grommet-bathroom",
        "poop-bucket",
        "mirror-spacer-straight",
        "mirror-spacer-arch",
        "mirror-spacer-corner",
        "lid-clip",
        "lid-clip-post",
        "box-corner",
        "gear-box-housing",
        "gear-box-lid",
        "gear-box-input-gear",
        "gear-box-output-gear",
        "gear-box-input-spacer",
        "gear-box-output-spacer",
        "gear-box-test-bushings",
        "gear-box-mesh-jig",
        "gear-box-motor-housing",
        "gear-box-motor-lid",
        "gear-box-motor-input-spacer",
        "gear-box-motor-output-spacer",
        "blinds-sprocket",
        "blinds-sprocket-bevel",
        "blinds-sprocket-spacer",
        "blinds-frame",
        "blinds-cassette-lid",
        "blinds-sleeve",
        "blinds-cap-rear",
        "blinds-cap-front",
        "blinds-pinion",
        "blinds-layshaft-spur",
        "blinds-layshaft-bevel",
        "blinds-drive-cassette",
        "blinds-drive-spacers",
    }


def test_render_registry_points_at_real_modules():
    for name, entry in RENDERS.items():
        assert (SRC / f"{entry.src}.py").exists(), f"{name}: no module {entry.src}.py"
