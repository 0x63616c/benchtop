# Flatbed JGB37 right-angle speedbox

The output-bearing topology decision is recorded in
[`2026-08-06-flatbed-output-bearing-layout.md`](../trades/2026-08-06-flatbed-output-bearing-layout.md).

## Locked prototype geometry

- Envelope: **55 x 108 x 43 mm**. All main sheets remain 2 mm thick; captive
  nuts live in local 8 mm bosses on the left/right sheets.
- Rear outside face to motor bulkhead: **65 mm**.
- Motor: JGB37-520 encoder envelope using the repo's assumed **24 mm L**
  gearbox variant. The motor/encoder body is 62.2 mm long; the rear panel and
  0.8 mm internal cable gap make up the 65 mm compartment.
- Output: **90 degrees sideways (+X)**, through the left/right side panels.
- Ratio: **24T input : 18T output**. One motor revolution produces 1.333 output
  revolutions; ideal output torque is 75% of motor-shaft torque before loss.
- Two 625ZZ bearings (5 x 16 x 5 mm), one in each side sheet with 48.4 mm
  between their centers, support the through-running 5 mm output rod.
- Rear encoder/cable opening: **24 x 14 mm**.

The rectangular Z envelope is motor-limited. The Ø37 motor has 0.5 mm nominal
clearance to both the top and bottom inner faces. The input bevel has about
0.59 mm bottom clearance. Reducing the height further would create a collision
unless the six-panel rectangular construction changes.

## Flatpack joints and hardware

The enclosure reuses the physically selected three-dot Flatbed calibration:

- 0.20 mm slot clearance for 2 mm panels
- Ø3.4 mm M3 clearance holes
- 6.2 x 3.0 mm captive M3 nut pockets
- 4.0 mm-wide long bolt-entry channel in each T-slot
- one standard fastener length throughout: **M3 x 6 mm**
- plain through-holes only; bolt heads sit on the outer panel faces

Each bolt axis is 5 mm inboard. A Ø5.8 mm M3 head therefore has a complete
circular landing face with at least 2 mm to the outer edge. The paired locating slots
use 16 mm pitch, leaving at least 2 mm between the head footprint and each
slot. The side-sheet nut bosses rise locally to 8 mm; their inside-loading
cavities end at the original 2 mm sheet, which acts as the nut stop and
continuous outer wall. Centered front fasteners use matching 10 mm bosses on
the top and bottom skins, placing their axes 7 mm from each long edge with the
same 2 mm head ligament.

The two centered front receivers place their nut cavities at the same 4.8 mm
center distance from the outer face as the side receivers. Every unrecessed
M3 x 6 closure bolt crosses about 2.7 mm of its 3 mm-deep nut pocket. The front
receiver towers are taller only because their nuts load vertically; that tower
height is perpendicular to bolt length.

The top and bottom closure fasteners are behind the motor bulkhead, so neither
their bolts nor nuts enter the drive bay. The two front side fasteners are now
centered vertically. The motor bulkhead uses the JGB37 six-hole Ø31 mm bolt
circle and is locally 3 mm thick around the Ø37 motor face, giving an M3 x 6
motor screw 3 mm of thread engagement without recessing its head.

All four removable outer faces are fastened to both side sheets: top and bottom
use two M3 bolts per side; front and rear use one per side. The front also has
one centered bolt on each long edge, so it is retained on all four edges. This
is 14 closure bolts total. Large panel fields use rectangular ladder-frame
windows, not diagonal braces: the long faces have straight center ribs, while
the end faces keep broad perimeter frames. Bosses and narrow fastener lands
remain solid.

The output-bearing pocket and the nearest front M3 nut cavity retain at least
2 mm of material between their cut boundaries. The extra millimetre of box
depth creates this ligament without offsetting the centered front fastener.

The motor bulkhead has eight locating tabs: two into each of the left, right,
top, and bottom sheets. The enlarged top and bottom windows stop at a straight 6 mm rail
through the bulkhead slots, with only 8 mm perimeter frames left at the ends.
The two top-edge bulkhead tabs are spread 5 mm farther apart than the other
three pairs. Only the top panel has the matching wider slot pair, keying the
bulkhead so it cannot be installed upside-down or rotated 180 degrees.

The top, bottom, front, and rear panels each carry four independent Ø3.4 mm
future-mounting holes. Their axes sit 10 mm inward from each panel edge on
connected Ø10 mm flat lands, so the pattern remains usable where it enters a
material-saving window. They do not participate in the enclosure joints and
are reserved for attaching the gearbox to later parts. The bearing-heavy
left/right sheets deliberately omit this auxiliary pattern.

## Shaft and gear retention

The mathematical bevel axes intersect, but the bought shafts do not. An 8 mm
printed input sleeve moves the 24T gear forward while the motor shaft remains
inside its corrected D-bore. The 5 mm output rod crosses the full 55 mm box
width, runs through one bearing in each side sheet, and projects 10 mm from the
right side. A short 8.41 mm sleeve carries thrust between the 18T gear and the
right bearing. The output gear now has a fully round 5.1 mm bore and the 5 mm
rod remains round along its whole length. There are no set-screw, D-flat, or
transverse pin features in the output gear.

The right sleeve establishes the gear's thrust position. A round bore is not a
positive torque coupling: this revision therefore relies on the printed fit or
a suitable retaining compound. If physical testing shows slip or axial creep,
use a split-clamp hub and/or an external 5 mm shaft collar rather than putting a
weak transverse hole through the 18T gear hub. The output hub is on the
narrowing apex side, and the wide heel is trimmed to a 55-degree bed-facing
envelope so the gear prints without supports.

## Printable parts

The export names are `flatbed-gearbox-bottom`, `-top`, `-left`, `-right`,
`-front`, `-rear`, `-bulkhead`, `-input-gear`, `-input-spacer`, `-output-gear`,
and `-output-spacer`. All are deliberately posed flat on the print bed.

## Still to measure

The JGB37 product family varies with internal ratio and supplier. Before a
final production enclosure, measure the actual motor's L dimension, encoder
PCB/connector protrusion and shaft length. The current motor reference
is an explicit collision envelope, not vendor CAD.
