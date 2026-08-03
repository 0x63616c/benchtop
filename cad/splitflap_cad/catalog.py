"""THE model registry — single source of truth for every viewable model
and printable part. Everything reads from here: `just cad list`, the
viewer push CLI (__main__.py), ctl's save→model auto-focus
(src_to_model in `list --json`), and STL export.

Pure data: a Model is (project, help, module stem, scene attr); a Printable is
(project, module stem, part attr). Modules import lazily on build, so listing
the catalog never builds geometry. Convention: every part module
exports `scene()` (extra views get their own attr, e.g. plate_scene)
and plain part builders for printables.

Adding a part = its module + one Model entry (+ a Printable entry if it
prints).
"""

from dataclasses import dataclass
from importlib import import_module


def _attr(src: str, name: str):
    # Bare stem = module in this package; dotted = absolute import of a
    # sibling project package (e.g. "blinds_cad.jgb37"). One catalog
    # serves every cad project so the ctl tooling stays single-entry.
    if "." in src:
        return getattr(import_module(src), name)
    return getattr(import_module(f".{src}", __package__), name)


@dataclass(frozen=True)
class Model:
    project: str  # PROJECTS key; groups the model in ctl
    help: str  # one line; powers `just cad list` and the docs
    src: str  # module stem that builds it — maps saved file -> model
    scene: str = "scene"  # module attr returning a viewer.Scene

    def build(self):
        return _attr(self.src, self.scene)()


@dataclass(frozen=True)
class Printable:
    project: str  # PROJECTS key; groups exports in ctl
    src: str  # module stem
    part: str  # module attr returning the printable solid

    def build(self):
        return _attr(self.src, self.part)()


@dataclass(frozen=True)
class Render:
    """A 2D drawing: a module attr that writes a PNG to the path given."""

    project: str  # PROJECTS key; groups drawings in ctl
    src: str  # module stem
    fn: str  # module attr taking one Path

    def draw(self, out):
        return _attr(self.src, self.fn)(out)


PROJECTS = {
    "split-flap": "modular split-flap display",
    "blinds": "motorized roller-blind drive",
    "ipad-wall": "iPad swivel-bar wall mount",
    "grommets": "wall-hole cable grommets",
    "poop-bucket": "Bambu P2S waste-chute bucket",
    "mirror-light": "arched-mirror LED halo",
    "lid-clip": "storage-box lid clip",
    "box-corner": "storage-box corner brace",
    "gear-box": "compact right-angle gearbox",
}


MODELS = {
    "assembly": Model(
        "split-flap",
        "full unit: plate + motor + hall PCB + drum",
        "assembly",
    ),
    "unit": Model(
        "split-flap",
        "printable side plate with interconnect fins",
        "unit",
    ),
    "plate": Model(
        "split-flap", "side plate only — no interconnect fins", "unit", "plate_scene"
    ),
    "unit-nema": Model(
        "split-flap",
        "NEMA variant: plate + bridge + motor + drum ghosts",
        "unitnema",
    ),
    "plate-nema": Model(
        "split-flap",
        "NEMA side plate only — no fins/bridge", "unitnema", "plate_scene"
    ),
    "bridge-nema": Model(
        "split-flap",
        "NEMA bridge alone, local frame", "unitnema", "bridge_scene"
    ),
    "drum-byj": Model(
        "split-flap", "drum outer + 28BYJ-bore inner, side by side", "drum"
    ),
    "drum-nema": Model(
        "split-flap",
        "drum outer + NEMA-bore inner, side by side", "drum", "nema_scene"
    ),
    "holder": Model(
        "split-flap",
        "PROTOTYPE flap-loading jig: ring + radial slots, drum ghost",
        "holder",
    ),
    "flap": Model("split-flap", "single flap card", "flap"),
    "flap-set": Model(
        "split-flap",
        "contact sheet: all 52 flap fronts + backs (backs flipped as displayed)",
        "glyphflap",
        "flap_set_demo",
    ),
    "flap-glyph": Model(
        "split-flap",
        "PROTOTYPE two-tone glyph flaps: assembled A + W/M + Q/? demos",
        "glyphflap",
        "glyph_flap_demo",
    ),
    "motor-byj": Model(
        "split-flap", "28BYJ-48 stepper (the real motor)", "stepper28byj"
    ),
    "motor-nema": Model(
        "split-flap", "NEMA 14 pancake reference (ordered part)", "motor"
    ),
    "fins": Model("split-flap", "parametric interconnect fins, alone", "fins"),
    "ipad-wall": Model(
        "ipad-wall",
        "SIDE QUEST iPad swivel-bar wall mount: wall + bracket + bar + iPad",
        "ipadwall",
    ),
    "grommet-usb": Model(
        "grommets",
        "SIDE QUEST 38mm wall-hole grommet, USB-C slot",
        "grommet",
    ),
    "grommet-bathroom": Model(
        "grommets",
        "SIDE QUEST 38mm wall-hole grommet, blank flange",
        "grommet",
        "bathroom_scene",
    ),
    "poop-bucket": Model(
        "poop-bucket",
        "SIDE QUEST Bambu P2S waste-chute bucket XL, vase mode",
        "poopbucket",
    ),
    "mirror-light": Model(
        "mirror-light",
        "SIDE QUEST arched-mirror LED halo: glass, spacers, closed strip loop",
        "mirrorlight",
    ),
    "mirror-spacer": Model(
        "mirror-light",
        "mirror halo: the three printable spacers, strip ghost in the groove",
        "mirrorlight",
        "spacer_scene",
    ),
    "lid-clip": Model(
        "lid-clip",
        "SIDE QUEST storage-box lid clip: bare coupon + stack post",
        "lidclip",
    ),
    "box-corner": Model(
        "box-corner",
        "SIDE QUEST storage-box corner brace: 30mm three-plate corner",
        "boxcorner",
    ),
    "gear-box": Model(
        "gear-box",
        "SIDE QUEST 45x36mm 3:2 right-angle gearbox: gears, rods, 625ZZs + box",
        "gearbox",
    ),
    "gear-box-test": Model(
        "gear-box",
        "SIDE QUEST gearbox test print: printed bushings replace all four bearings",
        "gearbox",
        "test_scene",
    ),
    # --- blinds project (blinds_cad package, wayfinder #12) ---
    "blinds-unit": Model(
        "blinds",
        "BLINDS full unit: wall frame + mechanism + slide-on sleeve + split cap",
        "blinds_cad.blindsunit",
    ),
    "blinds-frame": Model(
        "blinds",
        "BLINDS printable wall-mounted structural exoskeleton",
        "blinds_cad.enclosure",
    ),
    "blinds-axle-keeper": Model(
        "blinds",
        "BLINDS removable flat-printing sprocket axle keeper",
        "blinds_cad.enclosure",
        "axle_keeper_scene",
    ),
    "blinds-sleeve": Model(
        "blinds",
        "BLINDS thin open-back cosmetic sleeve",
        "blinds_cad.cover",
    ),
    "blinds-cap": Model(
        "blinds",
        "BLINDS two-piece top cap closing around the installed chain",
        "blinds_cad.cover",
        "cap_scene",
    ),
    "blinds-sprocket": Model(
        "blinds",
        "BLINDS 12-pocket bead-chain sprocket + chain ghost",
        "blinds_cad.sprocket",
    ),
    "blinds-motor": Model(
        "blinds",
        "BLINDS JGB37-520B gearmotor reference (ordered part)", "blinds_cad.jgb37"
    ),
    "blinds-pcb": Model(
        "blinds",
        "BLINDS rev C flat main PCB envelope (88x32, v2 layout)", "blinds_cad.pcbboard"
    ),
    "blinds-gears": Model(
        "blinds",
        "BLINDS printed drive: spur pinion + layshaft (spur+bevel)",
        "blinds_cad.gears",
    ),
    "blinds-cells": Model(
        "blinds",
        "BLINDS 6× 21700 stack reference (2S3P bay)", "blinds_cad.cells21700"
    ),
}

# saved file stem -> model name, for ctl's save auto-focus.
# First entry wins on shared src (unit.py saves focus the full unit,
# not the plate-only view). Keyed by the module STEM (last dotted
# segment) because ctl only knows the saved filename — stems must stay
# unique across every cad project package.
SRC_TO_MODEL: dict = {}
for _name, _m in MODELS.items():
    SRC_TO_MODEL.setdefault(_m.src.rsplit(".", 1)[-1], _name)


# --- printable solids (STL export) ---

PRINTABLE = {
    "unit": Printable("split-flap", "unit", "full_unit"),
    "unit-nema": Printable("split-flap", "unitnema", "full_unit_nema"),
    "bridge-nema": Printable("split-flap", "unitnema", "nema_bridge"),
    "holder": Printable("split-flap", "holder", "holder"),
    "flap": Printable("split-flap", "flap", "flap"),
    "drum-outer": Printable("split-flap", "drum", "drum_outer"),
    "drum-inner-byj": Printable("split-flap", "drum", "drum_inner_print"),
    "drum-inner-nema": Printable("split-flap", "drum", "drum_inner_nema_print"),
    "ipad-body": Printable("ipad-wall", "ipadwall", "bracket_body"),
    "ipad-lid": Printable("ipad-wall", "ipadwall", "bracket_lid"),
    "grommet-usb": Printable("grommets", "grommet", "grommet_usb"),
    "grommet-bathroom": Printable("grommets", "grommet", "grommet_bathroom"),
    "poop-bucket": Printable("poop-bucket", "poopbucket", "poop_bucket"),
    "mirror-spacer-straight": Printable(
        "mirror-light", "mirrorlight", "spacer_straight"
    ),
    "mirror-spacer-arch": Printable(
        "mirror-light", "mirrorlight", "spacer_arch"
    ),
    "mirror-spacer-corner": Printable(
        "mirror-light", "mirrorlight", "spacer_corner"
    ),
    "lid-clip": Printable("lid-clip", "lidclip", "lid_clip"),
    "lid-clip-post": Printable("lid-clip", "lidclip", "lid_clip_post"),
    "box-corner": Printable("box-corner", "boxcorner", "box_corner"),
    "gear-box-housing": Printable("gear-box", "gearbox", "housing"),
    "gear-box-lid": Printable("gear-box", "gearbox", "lid"),
    "gear-box-input-gear": Printable("gear-box", "gearbox", "input_gear"),
    "gear-box-output-gear": Printable("gear-box", "gearbox", "output_gear"),
    "gear-box-input-spacer": Printable("gear-box", "gearbox", "input_spacer"),
    "gear-box-output-spacer": Printable("gear-box", "gearbox", "output_spacer"),
    "gear-box-test-bushings": Printable("gear-box", "gearbox", "test_bushings"),
    "blinds-sprocket": Printable("blinds", "blinds_cad.sprocket", "sprocket"),
    "blinds-frame": Printable("blinds", "blinds_cad.enclosure", "frame"),
    "blinds-axle-keeper": Printable(
        "blinds", "blinds_cad.enclosure", "axle_keeper"
    ),
    "blinds-sleeve": Printable("blinds", "blinds_cad.cover", "sleeve"),
    "blinds-cap-rear": Printable("blinds", "blinds_cad.cover", "cap_rear"),
    "blinds-cap-front": Printable("blinds", "blinds_cad.cover", "cap_front"),
    "blinds-pinion": Printable("blinds", "blinds_cad.gears", "pinion"),
    "blinds-layshaft": Printable("blinds", "blinds_cad.gears", "layshaft"),
}


# --- rendered drawings (PNG) ---
# 2D deliverables: a render is a module attr taking an output Path.

RENDERS = {
    "mirror-light-layout": Render("mirror-light", "mirrorplot", "render_layout"),
    "mirror-light-section": Render("mirror-light", "mirrorplot", "render_section"),
}
