# Trade Study: Flatbed Output Bearing Layout

**Date:** 2026-08-06
**Status:** DECIDED
**Decision:** Rotate the output axis through the left/right walls and support it with one 625ZZ bearing in each wall.

## 1. Context

The current +Z output uses two adjacent 625ZZ bearings in the roof. Physical
testing found perceptible output-rod wobble because the bearings have little
span. The replacement must retain the 90-degree 24T:18T bevel drive, keep the
motor enclosed, avoid the motor/input shaft, remain support-free to print, and
place the bearings on opposite sides of the output gear.

## 2. Options

### Option A: Keep both bearings in the roof

Retain the current +Z output and stacked roof carrier. This requires the least
new geometry but preserves the short bearing span that caused the wobble.

### Option B: Put one bearing above and one below the +Z gear

Keep the upward output and add a lower internal bearing. A 16 mm lower bearing
occupies the input-bevel envelope; placing it below that envelope requires a
taller box and a shaft through the motor/input level.

### Option C: Through-shaft across the left/right walls

Rotate the bevel cartridge 90 degrees about the motor axis. The output remains
perpendicular to the motor, while each 2 mm side sheet gains one local bearing
carrier and the shaft spans the full enclosure width.

### Option D: Through-shaft across the front/rear walls

Point the output along the motor axis. This makes the shafts parallel, so the
bevel pair must be replaced by a parallel-shaft gear train and the rear motor
and cable opening must share a bearing.

## 3. Comparison Table

| Criteria | A: Stacked roof | B: Above/below | C: Left/right | D: Front/rear |
|---|---|---|---|---|
| **Bearing span** | Poor: about one bearing gap | Good, but height-limited | Best: nearly the full 55 mm width | Good: nearly the full enclosure depth |
| **90-degree drive** | Preserved | Preserved | Preserved | Lost; needs another gear topology |
| **Collision risk** | Already clear | Lower bearing intersects the input-bevel envelope | Local wall carriers can be checked independently | Conflicts with motor, bulkhead, and rear cable route |
| **Enclosure impact** | None | Requires extra height and internal carrier structure | Only local side-wall bosses | Major drivetrain and panel redesign |
| **Printability** | Proven, but mechanically weak | More tall internal parts | Flat side sheets with local upward bosses | More parts and a new gear train |

## 4. Recommendation

**Rationale:** Option C gives the widest useful bearing span while preserving
the existing right-angle ratio and compact depth. The side sheets already use
local bosses, so bearing carriers follow the same flat-print construction.

**What we're giving up:** The output exits a side rather than the top or the
panels currently named front/rear. Both side sheets and shaft spacers must be
reprinted.

**When to revisit:** Reconsider only if the installation requires a top output
or cannot tolerate a side-exiting shaft. A true front/rear output should be
treated as a separate parallel-shaft gearbox design.
