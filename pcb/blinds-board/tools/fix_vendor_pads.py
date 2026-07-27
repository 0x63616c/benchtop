"""Fix the two vendored footprints whose netless through-holes fail DRC.

    ~/.local/share/uv/tools/atopile/bin/python tools/fix_vendor_pads.py

EasyEDA emits both of these as plated, unnamed, unnetted holes, which is wrong
in two different ways:

  * TPS61088 — eight 0.2mm thermal vias under the PowerPAD. Unnamed means no
    net, so the router sees no obstacle and lays tracks over them, and 0.2mm
    drill with a 0.4mm pad is under JLC's standard 0.3/0.55. Renamed to pad 21
    (PGND, the pad they sit in) and opened out to 0.55/0.3.
  * USB-C — two 0.75mm mounting posts, plated with zero annular ring. They are
    mechanical: converted to non-plated.

Idempotent: re-running finds nothing left to change.
"""

import re
from pathlib import Path

PARTS = Path(__file__).parent.parent / "parts"


def fix_tps():
    (path,) = (PARTS / "TPS61088RHLR").glob("*.kicad_mod")
    text = path.read_text()
    if '(pad "" thru_hole' not in text:
        return 0
    text, n = re.subn(
        r'\(pad "" thru_hole circle\n(\s+)\(at ([-\d.]+) ([-\d.]+)\)\n\s+\(size 0\.4 0\.4\)\n\s+\(drill 0\.2\)',
        lambda m: (f'(pad "21" thru_hole circle\n{m.group(1)}(at {m.group(2)} {m.group(3)})\n'
                   f'{m.group(1)}(size 0.55 0.55)\n{m.group(1)}(drill 0.3)'),
        text,
    )
    path.write_text(text)
    return n


def fix_usb():
    (path,) = (PARTS / "USB_C_16P").glob("*.kicad_mod")
    text = path.read_text()
    text, n = re.subn(r'\(pad "" thru_hole circle', '(pad "" np_thru_hole circle', text)
    path.write_text(text)
    return n


def strip_copper_graphics():
    """Delete fp_lines/polys drawn on F.Cu or B.Cu in the vendored footprints.

    Several EasyEDA connector footprints draw their outline on a COPPER layer
    instead of silk. KiCad treats that as netless copper and every track or via
    that passes near one is a clearance error against a shape that was only
    ever meant to be a drawing.
    Also drops zero-length lines with no layer at all: trim_lib_silk leaves one
    behind for every silk segment it clips away to nothing, and a layerless line
    inherits the footprint's layer — which is F.Cu. Thirteen of them sit on the
    origin of every XH connector, and KiCad reports a clearance error against
    each one.
    """
    n = 0
    for path in sorted(PARTS.glob("*/*.kicad_mod")):
        text = path.read_text()
        out, i, hit = [], 0, 0
        while True:
            j = min([x for x in (text.find("(fp_line", i), text.find("(fp_poly", i),
                                 text.find("(fp_rect", i), text.find("(fp_circle", i))
                     if x >= 0] or [-1])
            if j < 0:
                out.append(text[i:])
                break
            depth, k = 0, j
            while k < len(text):
                if text[k] == "(":
                    depth += 1
                elif text[k] == ")":
                    depth -= 1
                    if depth == 0:
                        k += 1
                        break
                k += 1
            block = text[j:k]
            degenerate = "(layer" not in block or "(start 0 0)" in block and "(end 0 0)" in block
            if '(layer "F.Cu")' in block or '(layer "B.Cu")' in block or degenerate:
                out.append(text[i:j].rstrip("\t"))   # drop the graphic
                hit += 1
            else:
                out.append(text[i:k])
            i = k
        if hit:
            path.write_text("".join(out))
            print(f"  {path.parent.name}: dropped {hit} copper-layer graphic(s)")
            n += hit
    return n


if __name__ == "__main__":
    print(f"TPS61088: {fix_tps()} thermal vias renamed to PGND and opened to 0.55/0.3")
    print(f"USB-C: {fix_usb()} mounting posts made non-plated")
    print(f"copper graphics: {strip_copper_graphics()} dropped")
