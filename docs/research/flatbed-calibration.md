# Flatbed captive-nut calibration print

The first Flatbed model is a palm-scale, laser-cut-style M3 T-slot joint kit.
It contains five interchangeable base coupons and five upright coupons. Any
base can be assembled with any upright, giving 25 possible combinations while
keeping panel fit and nut fit independent.

The one-to-five witness holes identify ascending variants:

| Markers | 2 mm panel clearance | M3 hole | Nut pocket width | Nut pocket depth |
|---:|---:|---:|---:|---:|
| 1 | 0.10 | 3.2 | 5.6 | 2.5 |
| 2 | 0.15 | 3.3 | 5.7 | 2.6 |
| 3 | 0.20 | 3.4 | 5.8 | 2.7 |
| 4 | 0.25 | 3.5 | 5.9 | 2.8 |
| 5 | 0.30 | 3.6 | 6.0 | 2.9 |

Dimensions are millimetres. The nut ladder starts from a nominal DIN 934 M3
hex nut around 5.5 mm across flats and 2.4 mm thick. Measure the actual nuts;
the rectangular trap holds two flats against rotation and intentionally lets
the nut protrude from the faces of the 2 mm panel.

Print `flatbed-calibration-kit.stl` flat using the material, nozzle, layer
height, wall count, and slicer compensation intended for the motor mount.
Supports are not required. Insert a nut through the broad face of an upright,
push its two tabs into a base, then run an M3 bolt through the base into the
nut. The trap height is set for an M3x8 button-head bolt through the 2 mm
base. Try different base/upright marker combinations until the tabs seat by
hand, the nut stays put, and the tightened corner remains square without
cracking or obvious play.

Use `just cad view flatbed-nut-joint` to inspect the assembled middle variant.
