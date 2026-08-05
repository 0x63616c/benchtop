"""Shared Flatbed geometry idioms."""

from pathlib import Path

from build123d import Align, Plane, Pos, Text, TextAlign, extrude

from .params import P


_FONT = Path(__file__).resolve().parent.parent / "fonts" / P.label_font


def engrave_text(body, text: str, x: float, y: float, top: float, size: float):
    """Engrave centered text into an upward-facing horizontal surface."""
    glyphs = Text(
        text,
        font_size=size,
        font_path=str(_FONT),
        align=(Align.CENTER, Align.CENTER),
        text_align=(TextAlign.CENTER, TextAlign.CENTER),
    )
    cut = extrude(
        Plane.XY.offset(top - P.label_depth) * Pos(x, y) * glyphs,
        amount=P.label_depth + 0.1,
    )
    return body - cut
