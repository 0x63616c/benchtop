"""Flatbed local-to-assembly poses."""

from build123d import Pos, Rot

from .params import P


# Upright local Y becomes assembly +Z. Its seating edge lands on the base top
# while the two tabs occupy the base thickness and finish flush underneath.
UPRIGHT_ON_BASE = Pos(0, P.panel_t / 2, P.panel_t) * Rot(90, 0, 0)
