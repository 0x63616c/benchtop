# Blinds unit v2 — center-drop chain (design)

Owner requirement change (2026-07-26): the bead chain must pass through
the **center of the unit's width**, strands separated **left/right**
(chain plane parallel to the wall), not off to the right edge with
strands front/back as in v1 (#21). Bead chain tolerates the 90° twist
over the drop to the blind's chain wheel.

## Consequences

- Sprocket axis must point **out of the wall** (unit +Y). The JGB37
  motor is 82mm along its shaft — cannot be coaxial in 44mm of depth.
  A 90° drive is required.
- Chain corridor sits at x = 49 ± 11.5 in the top ~35mm of the unit
  only (chain enters the two top slots and wraps **under** the
  sprocket) — interior below stays free.

## Decisions

**Geometry check killed the vertical-motor layout that was approved
verbally:** with the shaft vertical at (49, 21), the shaft tip crosses
the sprocket's Y-axis axle plane, and no rotating hub can bridge the
sprocket's back and front past a static shaft that intersects its own
axis. The corrected layout keeps every approved property (chain
centered, strands left/right, 98 × 44, printed gears with steel
fallback) with the motor horizontal:

- **Layout (tower), 98 × 44 × 242:**
  - PCB flat on the floor (z 6..7.6), components up, on 3× M3 bosses
    plus one plain support pillar under the USB edge.
  - All 6 battery holders horizontal, full width, one stack
    (z ≈ 14..160) — the v1-style rectangular carrier survives.
  - Motor horizontal along X near the top: gearbox face x=67, shaft
    +X, shaft axis (y 21, z 189), eccentric DOWN (gearbox axis z 182,
    can z 163.5..200.5).
  - Sprocket axis along Y at (x 49, z 220); chain slots in the top
    face at x = 49 ± 11.5, y ≈ 36.
- **Drive: two printed stages.** Spur pair m2 14:17 (motor pinion on
  the D-shaft at x≈81.5 → layshaft at (21, 220), center distance 31).
  Layshaft is one print: spur gear + Ø8 shaft + m2 z10 bevel at its
  left end (heel plane x=59). That bevel meshes a z10 bevel ring
  printed as ONE piece with the 12-pocket sprocket (ring heel plane
  y=11, drum bridge, wheel at y≈36). Sprocket spins on a fixed M5
  cross-axle (front-access head → captive wall-side frame nut). Net:
  111rpm × 14/17 ≈ 91rpm →
  ~109mm/s chain (target 100); sprocket torque ≈ 0.6 × 17/14 × ~0.72
  gear efficiency ≈ 0.52Nm vs 0.39 needed. Steel bevel fallback still
  possible (bores stay standard).
- **Motor mount:** vertical rib bulkhead at x 67..70 (6×M3 BCD31 into
  the gearbox face, layshaft U-saddle in the same rib) + a support-free
  half cradle near x≈11. Layshaft right end rides a second U-saddle at x 86..92;
  saddles open toward the back for insertion, retained by clips.
- **Carrier PCB:** unchanged concept from v1 — rectangular, 6 holders,
  2S3P busing, balance tap, XT30PW + JST-XH.
- **Main PCB rev C:** reshape to ~90×35 lying flat. Buttons = the
  right-angle tactile the BOM already lists (C2837543), front edge,
  plungers through the front wall at z≈8. USB-C right-angle exits the
  front face beside them. Schematic unchanged; re-place + A* re-route.
- **Enclosure (revised 2026-08-03):** a wall-mounted structural
  exoskeleton owns the motor bulkhead, layshaft saddles, fixed sprocket
  axle, battery-carrier bosses, PCB tray, and four #8 wall anchors. A
  separate 0.8 mm open-back, open-top sleeve slides over it and is held
  by two underside M3 screws. Rear and front top-cap halves meet at the
  chain plane, closing around both installed strands without threading.
  A flat-printed, four-screw front keeper supports the axle without
  bridging over the sprocket cavity. Button, USB, and axle-head openings remain in the sleeve front face.
  The French cleat and monolithic structural shell are removed.

## Rejected

- Widen to ~130 for direct drive — breaks the ≤100 width rule.
- Worm drive — kills the ~30s travel target.
- Chain-redirect idlers — friction + 90° twist forced in ~50mm.
- Vertical motor + bevel — shaft tip intersects the sprocket axle
  plane; every bridge topology (drum over the shaft, crown+spur,
  wheel-beside-ring) collides with the pinion, gearbox, or rear frame.
- Single-bevel off the motor shaft directly — the motor is 82mm along
  its axis, so its shaft tip can never reach x≈49 inside 98mm.

## Risks / verify on arrival

- Printed bevel wear under 0.4Nm — steel fallback designed in.
- Shaft flat length (pinion rides the shaft tip) — caliper on arrival.
- Button feel at ~80mm off the floor on the front face.

## Execution order

params/frames rewrite → part modules (pinion, sprocket+ring, frame,
sleeve, split cap) → fit-proof `blinds-unit` scene + zero-interference
checks → regen goldens → PCB rev C re-place/re-route + DRC → tickets
#21/#22 + BOM note.
