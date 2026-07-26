"""Give every vendored footprint an F.CrtYd courtyard.

    ~/.local/share/uv/tools/atopile/bin/python tools/add_courtyards.py

EasyEDA footprints arrive with none, and KiCad ships `missing_courtyard` as an
IGNORED check — so a board where nothing has a courtyard passes DRC cleanly
while the courtyard-overlap check silently never runs. The pre-fab verifier
(pcb/tools/verify_fab.py) refuses that, which is the whole point.

The courtyard is the pad+silk bounding box with a hair of margin. Deliberately
tight: the placement in tools/place_and_render.py packs 0603s on a 3.0mm
pitch, and a courtyard fatter than the part would report overlaps on a board
that assembles perfectly well.

Idempotent — a footprint that already has an F.CrtYd is left alone.
"""

from pathlib import Path

from faebryk.libs.kicad.fileformats import kicad

PARTS = Path(__file__).parent.parent / "parts"
MARGIN = 0.05


def body_box(fp):
    xs, ys = [], []
    for pad in fp.pads:
        if pad.primitives is not None and len(pad.primitives.gr_polys):
            for poly in pad.primitives.gr_polys:
                for pt in poly.pts.xys:
                    xs.append(pad.at.x + pt.x)
                    ys.append(pad.at.y + pt.y)
            continue
        w, h = pad.size.w, (pad.size.h or pad.size.w)
        if round((pad.at.r or 0) % 180) == 90:
            w, h = h, w
        xs += [pad.at.x - w / 2, pad.at.x + w / 2]
        ys += [pad.at.y - h / 2, pad.at.y + h / 2]
    for ln in list(fp.fp_lines) + list(fp.fp_rects):
        if "SilkS" not in str(ln.layer):
            continue
        xs += [ln.start.x, ln.end.x]
        ys += [ln.start.y, ln.end.y]
    return min(xs) - MARGIN, min(ys) - MARGIN, max(xs) + MARGIN, max(ys) + MARGIN


def main():
    added = 0
    for path in sorted(PARTS.glob("*/*.kicad_mod")):
        fpf = kicad.loads(kicad.pcb.FootprintFile, path.read_text())
        fp = fpf.footprint
        if any("CrtYd" in str(ln.layer) for ln in list(fp.fp_lines) + list(fp.fp_rects)):
            continue
        x0, y0, x1, y1 = body_box(fp)
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                                   ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            fp.fp_lines.append(kicad.pcb.Line(
                start=kicad.pcb.Xy(x=round(ax, 3), y=round(ay, 3)),
                end=kicad.pcb.Xy(x=round(bx, 3), y=round(by, 3)),
                stroke=kicad.pcb.Stroke(width=0.05, type="default"),
                layer="F.CrtYd",
                uuid=kicad.gen_uuid(),
            ))
        kicad.dumps(fpf, path)
        added += 1
        print(f"  {path.parent.name}: courtyard {x1 - x0:.2f} x {y1 - y0:.2f}mm")
    print(f"added {added} courtyards")


if __name__ == "__main__":
    main()
