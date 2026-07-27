#!/usr/bin/env bash
# Place, check and export everything for the blinds driver board in one go.
#
#   tools/build_outputs.sh            # place + DRC + renders + fab
#   tools/build_outputs.sh --quick    # place + DRC only (skips the raytracer)
#
# DRC failures stop the run — no point rendering or shipping gerbers for a
# board that doesn't pass.
#
# NOTE: everything below comes from a DERIVED copy, build/filled.kicad_pcb, not
# from layouts/. `kicad-cli --save-board` rewrites the file in a dialect
# faebryk's parser rejects, so layouts/ stays atopile's and build/ is KiCad's.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/layouts/default/default.kicad_pcb"
PCB="$ROOT/build/filled.kicad_pcb"
KICAD="/Applications/KiCad.app/Contents/MacOS/kicad-cli"
ATO_PY="$HOME/.local/share/uv/tools/atopile/bin/python"
RENDER="$ROOT/render"
FAB="$ROOT/fab"
ZIP="$ROOT/fab-blinds-driver-revC.zip"
LAYERS="F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts"

[ -x "$KICAD" ] || { echo "kicad-cli not found at $KICAD"; exit 1; }
[ -x "$ATO_PY" ] || { echo "atopile python not found at $ATO_PY"; exit 1; }

echo "==> place + route + preview.svg"
"$ATO_PY" "$ROOT/tools/place_and_render.py"

echo "==> derive build/filled.kicad_pcb"
mkdir -p "$ROOT/build"
cp "$SRC" "$PCB"
cp "$ROOT/fp-lib-table" "$ROOT/build/fp-lib-table"
ln -sfn "$ROOT/parts" "$ROOT/build/parts"

# KiCad ships "missing_courtyard" as an IGNORED check, so a board with no
# courtyards anywhere passes DRC while the courtyard-overlap check silently
# never runs. Promote both to errors.
#
# net_settings is the one that actually bites: DRC checks the NETCLASS
# clearance, and KiCad's built-in Default is 0.2mm. Without this every trace on
# the board reports a violation at 0.195mm and the real errors are invisible.
#
# The clearance/width minimums are the board's own design point, not KiCad's
# defaults: 0.15mm signal traces at 0.13mm clearance, because a 0.4mm-pitch
# QFN cannot be escaped with anything wider. JLCPCB's process floor is
# 0.09mm/0.09mm, so this still has margin.
#
# solder_mask_bridge is ignored on purpose: at 0.4mm pitch the mask webs
# between neighbouring pads are thinner than the fab can hold, and every fab
# merges those openings anyway. Flagging it would bury the errors that matter.
cat > "$ROOT/build/filled.kicad_pro" <<'PRO'
{
  "net_settings": {
    "classes": [
      {
        "name": "Default",
        "clearance": 0.13,
        "track_width": 0.15,
        "via_diameter": 0.6,
        "via_drill": 0.3,
        "microvia_diameter": 0.3,
        "microvia_drill": 0.1
      }
    ]
  },
  "board": {
    "design_settings": {
      "rules": {
        "min_clearance": 0.12,
        "min_track_width": 0.13,
        "min_through_hole_diameter": 0.3,
        "min_via_annular_width": 0.12,
        "min_hole_clearance": 0.2,
        "min_hole_to_hole": 0.25,
        "min_copper_edge_clearance": 0.25,
        "min_silk_clearance": 0.0,
        "min_text_height": 0.7,
        "min_text_thickness": 0.12
      },
      "rule_severities": {
        "missing_courtyard": "error",
        "courtyards_overlap": "error",
        "malformed_courtyard": "error",
        "silk_over_copper": "warning",
        "silk_overlap": "warning",
        "solder_mask_bridge": "ignore",
        "starved_thermal": "warning"
      }
    }
  },
  "meta": {"filename": "filled.kicad_pro", "version": 3}
}
PRO

echo "==> DRC"
"$KICAD" pcb drc --severity-error --exit-code-violations --refill-zones \
    --save-board --units mm -o "$ROOT/build/drc.rpt" "$PCB" >/dev/null 2>&1 || {
    echo "DRC FAILED:"
    grep -E "^\*\* Found|^\[" "$ROOT/build/drc.rpt" | head -40
    exit 1
}
grep -E "^\*\* Found" "$ROOT/build/drc.rpt"

echo "==> geometry checks"
python3 "$ROOT/../tools/verify_fab.py" "$PCB"

if [ "${1:-}" = "--quick" ]; then
    echo "==> --quick: skipping renders and fab output"
    exit 0
fi

echo "==> 3D renders -> render/"
mkdir -p "$RENDER"
render() {  # name, then kicad-cli render args
    local name="$1"; shift
    "$KICAD" pcb render -o "$RENDER/$name.png" --quality high \
        --background opaque "$@" "$PCB" >/dev/null 2>&1
    echo "    $name.png"
}
render top    --side top    -w 1400 -h 2000
render bottom --side bottom -w 1400 -h 2000
render iso    --rotate '-30,0,35'  -w 1800 -h 1400 --floor --perspective
render iso2   --rotate '-30,0,-35' -w 1800 -h 1400 --floor --perspective
render front  --rotate '-75,0,0'   -w 1800 -h 1000 --floor

echo "==> gerbers + drill + BOM + placement -> fab/"
rm -rf "$FAB" "$ZIP"
mkdir -p "$FAB"
"$KICAD" pcb export gerbers -o "$FAB/" --layers "$LAYERS" "$PCB" >/dev/null
"$KICAD" pcb export drill -o "$FAB/" --format excellon --excellon-separate-th "$PCB" >/dev/null
"$KICAD" pcb export pos -o "$FAB/placement.csv" --format csv --units mm --side both "$PCB" >/dev/null
cp "$ROOT/build/builds/default/default.bom.csv" "$FAB/bom.csv"
(cd "$FAB" && zip -q "$ZIP" ./*)
echo "    $(basename "$ZIP") ($(unzip -l "$ZIP" | tail -1 | awk '{print $2}') files)"

echo "==> done"
