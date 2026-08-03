# Trade Study: Blinds Mount and Print Topology

**Date:** 2026-08-03
**Status:** OPEN

## 1. Context

The current blinds v2 enclosure is a single 98 x 44 x 242 mm shell with a
wall plate and an integral French-cleat receiver. It is nominally inside the
P2S's 256 mm build volume, but it is not a dependable support-free print:

- The shell is a 242 mm tower when printed upright.
- When printed front-face down, which is otherwise a good orientation, the
  receiver bar at the back has zero volumetric overlap with the shell before
  its boolean union. It is attached only along the top rim, so it starts as a
  floating cantilever in that orientation.
- The source calls the cleat 45 degrees but defines a 12 mm rise over 6 mm
  depth, a 2:1 slope (63.4 degrees to horizontal), not a 45-degree cleat.
- The present receiver consumes the only y=0..7 mm corridor behind the
  sprocket ring. The ring starts at y=8.5 mm, so a conventional 12 x 12 mm
  cleat cannot fit without moving the drive train.

The replacement must keep the 98 mm width and 44 mm chassis depth, provide a
positive load path into the wall plate, resist rattle and rotation at the
bottom of the unit, remain serviceable from the rear, and print without
generated support on the P2S. The mounting parts should use PETG or ASA rather
than PLA because they carry a sustained wall load beside a window.

## 2. Options

### Option A: Two removable 45-degree receiver blocks

Remove the integral hook from the chassis. Print the chassis with its front
face on the bed. Add two short receiver blocks at the upper rear, each attached
to a reinforced chassis hardpoint with two M3 screws and heat-set inserts. The
wall plate carries one continuous male rail. Each block has a 6 x 6 mm
45-degree socket and is printed with its long X axis vertical, making every
socket layer self-supporting. Two lower locating pads or pins bear against the
wall plate to stop rotation and rattle.

### Option B: Rear service cover with integral receiver

Make the open rear a removable, thin cover with the cleat receiver and axle
bearing tied into its full area. The cover screws into inserts around the
chassis rim; the chassis remains a front-down print. This gives the best
continuous load path and makes the rear cover a service panel. A female cleat
socket in a cover printed flat still creates unsupported material, so the
receiver would either need generated support or a second, separately printed
hook cassette.

### Option C: Keyhole wall plate

Replace the French cleat with two upper keyhole slots engaging #8 or M5 wall
screws, plus lower spacer pads and a small locking screw. The chassis and wall
plate both print flat. The load is carried directly by screw heads rather than
a wedge, and the lower pads control the projection moment.

### Option D: Metal cleat with printed adapters

Use a small commercial aluminium French-cleat or Z-clip for the load-bearing
joint. Print a flat wall adapter and a flat chassis adapter around it. This is
the most creep-resistant option and easiest to validate mechanically, but adds
a purchased part and loses the all-printed mounting goal.

### Option E: Wall-mounted exoskeleton with sliding sleeve

Move every load-bearing feature into a wall-mounted frame: the motor bulkhead,
layshaft saddles, sprocket axle, battery carrier supports, PCB shelf, and wall
anchors. The enclosure becomes a thin cosmetic sleeve with front, sides, top,
and bottom but no back. It slides over the assembled frame from the room toward
the wall and is retained by small lower tabs or two accessible M3 fasteners.

The two top chain openings are front-edge slots that terminate in round or
keyhole pockets at the final chain positions. The sleeve can therefore pass
over an already-installed chain without feeding the beads through a closed
hole. The sleeve is a one-wall shell with no infill; literal vase mode is only
possible if the slicer accepts the open-back path, so the safe default is
single-wall, zero-infill printing.

## 3. Comparison Table

| Criteria | A: Receiver blocks | B: Rear service cover | C: Keyhole wall plate | D: Metal cleat | E: Exoskeleton sleeve |
|---|---|---|---|---|---|
| Support-free printing | Strong: all four prints have a deliberate flat orientation; the two sockets print on end. | Mixed: chassis and cover are flat, but an integral female socket needs support unless split again. | Strong: only flat plates and vertical keyholes. | Strong: both adapters are flat prints. | Strong: frame pieces are flat prints; sleeve is single-wall and non-structural. |
| Load path | Strong with two blocks, four M3 fasteners, and a chassis hardpoint/load spreader. | Strongest once a separate hook cassette is added; the cover can spread load across the rim. | Adequate for the expected unit mass, but screw heads see the full shear and the lower spacer must resist the moment. | Strongest and least sensitive to polymer creep. | Strongest all-printed path because the sleeve carries no load. |
| Fit in existing drive clearance | Strong: a 6 x 6 mm wedge fits in y=0..7 ahead of the ring at y=8.5. | Mixed: the cover consumes rear volume and still needs a shallow, separate receiver. | Strong: no rail needs to occupy the ring clearance. | Strong: hardware profile can be selected to fit the 8.5 mm corridor. | Strong: chain clearance is solved in the sleeve's front-edge slots, not the wall joint. |
| Serviceability | Strong: back stays open and blocks can be removed independently. | Strong: cover becomes the intended rear service panel. | Moderate: removal requires lifting from the screw heads and managing a lock screw. | Moderate: depends on the clip chosen. | Strong: remove the sleeve without disturbing the chain, then service the exposed frame. |
| Code and part-count change | Moderate: remove one feature, add a small module, four hardpoints, and two pads. | Highest: adds a cover, rim joint, fastener pattern, and likely a cassette. | Lowest: replace rail and hook with keyholes and pads. | Moderate: requires physical hardware selection and adapter dimensions. | Highest: frame decomposition, sleeve, slide guides, and top chain slots all change. |
| Risk at a warm window | Moderate: use PETG or ASA, and inspect the printed receiver periodically. | Moderate: same polymer risk, but a larger load-spreading cover helps. | Moderate: slots can creep at the load edge unless generously reinforced. | Low: the primary load path is metal. | Moderate: use PETG or ASA for the frame; the thin sleeve can remain PLA if kept cosmetic. |

## 4. Recommendation

- **Rationale:** Option E is now the preferred architecture if the goal is a
  genuinely easy print and easy service. The exoskeleton owns the motor,
  gears, axle, batteries, and wall loads; the sleeve only hides them. Its
  front-edge top slots solve the chain-installation problem without asking the
  user to thread beads through a closed cover. Option A remains the smaller,
  lower-risk first implementation if the full frame decomposition is too much
  change at once.
- **What we're giving up:** Option E creates more frame pieces and needs a
  deliberate slide-guide and retention design. The thin sleeve is cosmetic,
  not a structural enclosure, and the exoskeleton remains visible whenever
  the sleeve is removed. PETG or ASA is still required for the load-bearing
  frame.
- **When to revisit:** Choose Option A if the frame decomposition makes the
  first prototype too large. Choose Option B if a rear service panel matters
  more than a cosmetic sleeve. Choose Option C if the least-complex print is
  more valuable than a cleat. Choose Option D if sustained sun or long-term
  no-creep loading makes printed anchors unacceptable.
