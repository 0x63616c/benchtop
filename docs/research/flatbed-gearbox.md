# Flatbed JGB37 right-angle speedbox

## Locked prototype geometry

- Envelope: **55 x 95 x 43 mm**. All main sheets remain 2 mm thick; captive
  nuts live in local 8 mm bosses on the left/right sheets.
- Rear outside face to motor bulkhead: **65 mm**.
- Motor: JGB37-520 encoder envelope using the repo's assumed **24 mm L**
  gearbox variant. The motor/encoder body is 62.2 mm long; the rear panel and
  0.8 mm internal cable gap make up the 65 mm compartment.
- Output: **90 degrees upward (+Z)**, through the top panel.
- Ratio: **24T input : 18T output**. One motor revolution produces 1.333 output
  revolutions; ideal output torque is 75% of motor-shaft torque before loss.
- Two 625ZZ bearings (5 x 16 x 5 mm), separated by 0.2 mm, support the centered
  top-side 5 mm output rod in an 11 mm-deep roof carrier.
- Rear encoder/cable opening: **24 x 14 mm**.

The rectangular Z envelope is motor-limited. The Ø37 motor has 0.5 mm nominal
clearance to both the top and bottom inner faces. The input bevel has about
0.59 mm bottom clearance. Reducing the height further would create a collision
unless the six-panel rectangular construction changes.

## Flatpack joints and hardware

The enclosure reuses the physically selected three-dot Flatbed calibration:

- 0.20 mm slot clearance for 2 mm panels
- Ø3.4 mm M3 clearance holes
- 5.8 x 2.7 mm captive M3 nut pockets
- 3.5 mm-wide long bolt-entry channel in each T-slot

Each bolt axis is 5 mm inboard. A Ø6 mm M3 head therefore has a complete
circular landing face with 2 mm to the outer edge. The paired locating slots
use 16 mm pitch, leaving at least 2 mm between the head footprint and each
slot. The side-sheet nut bosses rise locally to 8 mm; their inside-loading
cavities end at the original 2 mm sheet, which acts as the nut stop and
continuous outer wall. The centered front fastener uses one 10 mm bottom boss
to place its bolt axis 7 mm above the floor and retain the same 2 mm head
ligament on the opposite long edge.

The top and bottom closure fasteners are behind the motor bulkhead, so neither
their bolts nor nuts enter the drive bay. Front/rear fasteners are lowered for
the compact 43 mm height. The motor bulkhead uses the JGB37 six-hole Ø31 mm
bolt circle and is locally 5 mm thick around the Ø37 motor face.

All four removable outer faces are fastened to both side sheets: top and bottom
use two M3 bolts per side; front and rear use one per side. The front also has
a centered third bolt on its opposite long edge, anchored by a top-loading nut
boss on the bottom skin. This is 13 closure bolts total. Large panel fields use
rectangular ladder-frame windows, not diagonal braces: the long faces have
straight center ribs, while the end faces keep broad perimeter frames. Bosses
and narrow fastener lands remain solid.

## Shaft and gear retention

The mathematical bevel axes intersect, but the bought shafts do not. The motor
shaft terminates inside the 24T D-bore input gear. The separate 5 mm output rod
starts 0.2 mm beyond the input gear, enters the outward-facing hub on the 18T
gear, passes through a 1.7 mm spacer and both top bearings, then exits the box.
There are no set-screw or transverse pin holes in either printed gear.

The output gear currently relies on a calibrated close bore fit. If the first
physical drive test shows axial creep, add an external 5 mm shaft collar rather
than putting a weak transverse hole through the 12T gear hub.

## Printable parts

The export names are `flatbed-gearbox-bottom`, `-top`, `-left`, `-right`,
`-front`, `-rear`, `-bulkhead`, `-input-gear`, `-output-gear`, and
`-output-spacer`. All are deliberately posed flat on the print bed.

## Still to measure

The JGB37 product family varies with internal ratio and supplier. Before a
final production enclosure, measure the actual motor's L dimension, encoder
PCB/connector protrusion, shaft length, and D-flat. The current motor reference
is an explicit collision envelope, not vendor CAD.
