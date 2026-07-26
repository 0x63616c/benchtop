# blinds driver rev B — 2S USB-PD charger + 12 V motor rail

One board per automated blind ([wayfinder #12](https://github.com/0x63616c/benchtop/issues/12),
layout [#22](https://github.com/0x63616c/benchtop/issues/22)). It charges a 2S3P
21700 pack from USB-C Power Delivery, boosts the pack to a 12 V rail **only
while the blind is moving**, and runs an ESP32-C3 on 3.3 V the rest of the time.

**38 × 66 mm, 4-layer, 1.6 mm FR4**, plus a snap-off 18 × 12 mm hall-sensor tab
(panel is 38 × 81 mm). Components on the top side only; the two tactile
switches and the three XH connectors are through-hole.

## Power chain

```
USB-C ──► HUSB238A ──► BQ25798 ──┬──► BAT  2S3P 21700  (BQ29209 OV watchdog)
          PD sink,    buck-boost │
          12 V/3 A    charger    └──► SYS ─┬─► TPS61088 ──► 12 V ──► DRV8871 ──► motor
          by strap                         │   boost, EN-gated by the MCU
                                           └─► TLV62569 ──► 3V3 ──► ESP32-C3
```

SYS is alive from whichever source is present, so the MCU runs on the wall with
a flat pack, or on the pack with the wall unplugged. The 12 V rail is the only
thing that costs real quiescent current, and it is off unless a GPIO says
otherwise.

## Pinout

| ESP32-C3 | Signal | Goes to |
|---|---|---|
| IO4 / IO5 | IN1 / IN2 | DRV8871 — 00 coast, 10 fwd, 01 rev, 11 brake |
| IO6 | BOOST_EN | TPS61088 EN, with a 100 k pulldown |
| IO3 | HALL | DRV5032 push-pull output, via J4 |
| IO0 / IO1 | BTN_UP / BTN_DOWN | SW2 / SW1, to ground; use internal pull-ups |
| IO7 / IO8 | SCL / SDA | BQ25798, 4.7 k pull-ups to 3V3 |
| IO10 | /INT | BQ25798 interrupt, 10 k pull-up |
| IO18 / IO19 | USB D− / D+ | the USB-C receptacle — native USB, no bridge |
| IO2 | — | strapping pin, 10 k to 3V3, otherwise unused |

IO9 keeps its internal pull-up and there is **no BOOT button**: the C3's ROM
USB-Serial-JTAG enters download mode over the same USB-C that charges it.

> **The boost is off at reset and stays off until firmware says so.** That is
> the 100 k pulldown on IO6 doing its job — do not remove it to "fix" a board
> that does not move.

### Connectors

| Ref | Type | Pinout |
|---|---|---|
| J1 | USB-C 16-pin receptacle | PD input + native USB to the MCU |
| J2 | JST-XH 3-pin | Battery: `PACK+ / MID / PACK−`. The midpoint is what the BQ29209 balances on |
| J5 | JST-XH 2-pin | Motor: OUT1 / OUT2. Swap direction in firmware, not in the loom |
| J4 | JST-XH 3-pin | Hall: `3V3 / GND / DO` — cable to the tab |
| J3 | JST-XH 3-pin | On the **tab**: the other end of that cable |

> **In the enclosure the XH housings do not fit.** The slab between the wall
> and the motor tail is 4.4 mm and an XH shell is 5.75 mm tall. Solder the loom
> straight into the XH pads for a unit build; fit real housings only on the
> bench.

## The hall tab

The chain sprocket the hall sensor watches is ~80 mm from where the board
lives, so the DRV5032 cannot be on the board proper. It sits on a tab of the
same panel, joined by a 4 mm neck, with its own XH-3 facing J4. **Its three
nets are separate nets** (`p3v3_tab`, `gnd_tab`, `hall_do_tab`), so no copper
crosses the neck and snapping it off tears nothing.

## Configuration that is set by resistors, not firmware

| Part | Strap | Value | Why |
|---|---|---|---|
| HUSB238A | SNK_VSET | 6.04 k 1 % | request 12 V (datasheet window 5.7–6.3 k) |
| HUSB238A | SNK_ISET | 21 k 1 % | request 3 A (window 19.95–22.05 k) |
| BQ25798 | PROG | 8.2 k 1 % | 2 cells at 750 kHz — which is what makes 2.2 µH the right inductor |
| BQ25798 | ILIM_HIZ | tied to REGN | maximum input limit; the real one is an I²C register |
| BQ25798 | TS | 10 k / 10 k off REGN | no pack NTC in rev B: hold TS mid-window so charging is never suspended |
| TPS61088 | FSW → SW | 200 k | ≈770 kHz at 8 V in / 12 V out |
| TPS61088 | ILIM | 200 k | 5.95 A typical switch limit (1190000/R, PFM) |
| TPS61088 | FB | 200 k / 22 k | 12.15 V from a 1.204 V reference |
| TLV62569 | FB | 100 k / 22 k | 3.33 V from a 0.6 V reference |
| DRV8871 | ILIM | 30 k | 2.1 A trip — the datasheet's own worked example |

**Cell count is not a strap.** PROG only sets the power-up default; firmware
must configure 2S over I²C before enabling charge.

## Build loop

```
ato build                       # twice after adding a component — nets stamp a build late
PCB_BOARD=blinds-board just pcb place   # placement + routing + preview.svg
PCB_BOARD=blinds-board just pcb drc     # + real KiCad DRC
PCB_BOARD=blinds-board just pcb build   # + renders + gerbers/BOM/CPL
PCB_BOARD=blinds-board just pcb view    # live 3D board in this pane
```

Placement and routing are data tables in `tools/place_and_render.py`;
`tools/router.py` is the A* grid router that turns them into copper. Neither
one is a black box — read their docstrings before moving a part.
