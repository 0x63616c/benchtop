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


if __name__ == "__main__":
    print(f"TPS61088: {fix_tps()} thermal vias renamed to PGND and opened to 0.55/0.3")
    print(f"USB-C: {fix_usb()} mounting posts made non-plated")
