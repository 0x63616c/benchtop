# Flatbed JGB37 right-angle speedbox

## Locked prototype geometry

- Envelope: **43 x 91 x 43 mm**, including six 2 mm flat-print skins.
- Rear outside face to motor bulkhead: **65 mm**.
- Motor: JGB37-520 encoder envelope using the repo's assumed **24 mm L**
  gearbox variant. The motor/encoder body is 62.2 mm long; the rear panel and
  0.8 mm internal cable gap make up the 65 mm compartment.
- Output: **90 degrees right**, through the right wall.
- Ratio: **24T input : 12T output**. One motor revolution produces two output
  revolutions; ideal output torque is half the motor-shaft torque before loss.
- One 625ZZ bearing (5 x 16 x 5 mm) supports the right-side 5 mm output rod.
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

The top and bottom closure fasteners are behind the motor bulkhead, so neither
their bolts nor nuts enter the drive bay. Front/rear fasteners are lowered for
the compact 43 mm height. The motor bulkhead uses the JGB37 six-hole Ø31 mm
bolt circle and is locally 5 mm thick around the Ø37 motor face.

## Shaft and gear retention

The mathematical bevel axes intersect, but the bought shafts do not. The motor
shaft terminates inside the 24T D-bore input gear. The separate 5 mm output rod
starts 0.2 mm beyond the input gear, enters the outward-facing hub on the 12T
gear, passes through a 0.7 mm spacer and the right bearing, then exits the box.
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
