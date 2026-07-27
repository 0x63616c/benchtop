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

- **Layout A (interleaved)**, keeps 98 × 44 footprint, height ≈ 232:
  - PCB flat on the floor, components up.
  - 4 battery holders horizontal, full width, above the PCB.
  - Motor vertical at center (shaft x=49, y=21, eccentric toward −X),
    shaft up, encoder down.
  - 2 battery holders rotated 90° (cells vertical) flanking the motor.
  - Bevel mesh + sprocket at the top, chain slots in the top face.
- **Drive: printed 1:1 module-2 bevel pair.** Pinion on the 6mm
  D-shaft; bevel ring printed as ONE piece with the 12-pocket sprocket
  (geometry from #16 unchanged). Sprocket+ring spins on a fixed M5
  cross-axle through the guide block. Bores sized so a ~$10 steel 1:1
  bevel pair drops in if the printed pair wears. 111rpm × 1:1 →
  ~133mm/s chain speed (target 100). Working torque ~0.4Nm of 0.6
  available.
- **Motor mount: horizontal deck** at z≈197 — shaft hole + 6×M3 BCD31
  screwed down into the gearbox face; lower cradle ring steadies the
  can. Replaces v1's vertical bulkhead.
- **Carrier PCB v2:** one tall carrier (~94×195) with a Ø40+ arch
  cutout around the motor; all 6 holders on the same face (4
  horizontal + 2 rotated 90°); same 2S3P busing, balance tap,
  XT30PW + JST-XH.
- **Main PCB rev C:** reshape to ~90×35 lying flat. Buttons = the
  right-angle tactile the BOM already lists (C2837543), front edge,
  plungers through the front wall at z≈8. USB-C right-angle exits the
  front face beside them. Schematic unchanged; re-place + A* re-route.
- **Enclosure/plate:** shell idioms unchanged; cleat hook moves up
  (~200); chain slots at x = 49 ± 11.5 in the top face; button + USB
  holes move to the front face. Hall snap-off tab mounts in the guide
  block near the chain, 3 wires down to the board.

## Rejected

- Widen to ~130 for direct drive — breaks the ≤100 width rule.
- Worm drive — kills the ~30s travel target.
- Chain-redirect idlers — friction + 90° twist forced in ~50mm.
- Horizontal motor + layshaft (spur+bevel) — 4 gears, no layout win.
- Tower layout (6 cells in one stack) — same drive, height ≈ 280.

## Risks / verify on arrival

- Printed bevel wear under 0.4Nm — steel fallback designed in.
- Shaft flat length (pinion rides the shaft tip) — caliper on arrival.
- Button feel at ~80mm off the floor on the front face.

## Execution order

params/frames rewrite → part modules (pinion, sprocket+ring, deck,
carrier v2, shell v2, plate) → fit-proof `blinds-unit` scene +
zero-interference checks → regen goldens → PCB rev C re-place/re-route
+ DRC → tickets #21/#22 + BOM note.
