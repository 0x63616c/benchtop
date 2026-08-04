# Trade Study: Retro Mac Print Topology

**Date:** 2026-08-04
**Status:** DECIDED
**Decision:** Use a load-bearing inner skeleton with removable cosmetic skins at the full 12.9:9 Macintosh scale.

## 1. Context

We are designing a compact-Macintosh-style enclosure for a bare 12.9-inch
iPad Pro (4th generation). The iPad slides in from the top in landscape
orientation, and the front opening reveals the display rather than the iPad's
black bezel.

The geometry is driven by three measured or published envelopes:

- iPad body: 280.6 x 214.9 x 5.9 mm. Apple specifies a 2732 x 2048 display at
  264 ppi, giving a nominal active rectangle of 262.8 x 197.0 mm before its
  rounded display corners.
- Macintosh Plus reference: 345.4 mm high x 243.8 mm wide x 276.9 mm deep,
  with a 9-inch display. Scaling the complete case by 12.9 / 9 preserves the
  original proportions and yields approximately 495 x 349 x 397 mm.
- Bambu Lab P2S build volume: 256 x 256 x 256 mm. The assembled enclosure can
  exceed this, but every printable component must fit this cube with practical
  plate margins.

The reference dimensions come from Apple's [iPad Pro 12.9-inch (4th
generation) specifications](https://support.apple.com/en-us/111977), Apple's
[Macintosh Plus specifications](https://support.apple.com/en-mide/112183), and
the Bambu Lab P2S product manual (256 mm cubed build volume).

All options below retain the scale-faithful 495 x 349 x 397 mm exterior and
the same exact iPad cradle. They differ only in how the oversized enclosure is
broken into printable parts. The visual comparison is in
[retro-mac-print-topologies.svg](assets/retro-mac-print-topologies.svg).

## 2. Options

### Option A: Tiled monocoque

Split the load-bearing shell into front, side, and rear tiles, with tongue and
groove joints on every edge. The front is four quadrants; the long sides and
rear are similarly tiled. The shell itself carries the iPad.

### Option B: Stacked structural rings

Build the body from several structural depth rings, each divided into pieces
that fit the plate. Thin front and rear fascia panels close the rings. The
topmost ring contains the iPad slot and the screen cradle spans the upper
rings.

### Option C: Inner skeleton with cosmetic skins

Use a separate rib-and-rail skeleton to carry the iPad and react its weight.
Thin cosmetic panels attach to that frame. Panel boundaries follow the
original front/rear service seam, the display bezel, lower fascia details, and
rear vent bands so the assembled seams read as intentional case lines.

## 3. Comparison Table

| Criteria | A: Tiled monocoque | B: Structural rings | C: Skeleton + skins |
|---|---|---|---|
| **Exterior fidelity** | Good; unavoidable tile seams cross broad surfaces. | Fair; repeated horizontal seams are unlike the original enclosure. | Best; skins can preserve the silhouette and place seams on authentic feature lines. |
| **iPad safety** | Fair; shell-joint tolerance directly affects the cradle. | Good; several rings share the load, but stack error can pinch the device. | Best; the cradle is one independently testable mechanism with soft-contact clearance. |
| **P2S printability** | Good; all tiles are small, but many need support or awkward orientations. | Best; repeated rings can be oriented consistently and are naturally stiff. | Good; ribs print flat and skins print face-down, but there are more distinct parts. |
| **Assembly alignment** | Hard; accumulated tile error can telegraph across every face. | Good; doweled rings self-register, though their seams must be filled or accepted. | Best; the skeleton establishes datum surfaces and skins only locate cosmetically. |
| **Serviceability** | Poor; opening the shell disturbs the load-bearing structure. | Fair; top rings can be removed, but the body stack loosens. | Best; remove the top cap and selected skins without releasing the cradle. |
| **Filament and print time** | Medium; thick shell joints repeat around every tile. | Highest; full-depth structural rings use the most material. | Lowest; material is concentrated in ribs, with thin non-structural skins. |
| **Failure mode** | A cracked joint can loosen the iPad support. | Ring separation is visible but can propagate around the case. | A cosmetic panel can fail without compromising the independently retained iPad. |

## 4. Recommendation

- **Rationale:** Choose Option C. A datum-controlled inner skeleton is the
  safest way to make an exact top-loading iPad fit while keeping the exterior
  scale-faithful. It also lets the platinum cosmetic shell be printed thin,
  face-down where possible, and replaced without reprinting the cradle.
- **What we're giving up:** It has the highest distinct part count and needs a
  deliberate hidden-fastener or snap strategy. Assembly takes longer than a
  ring stack.
- **When to revisit:** Choose Option B instead if the priority becomes the
  fastest mechanically robust prototype and visible horizontal seams are
  acceptable. Revisit the full 12.9:9 scale if the approximately 495 x 349 x
  397 mm assembled size is too large for the intended desk.
