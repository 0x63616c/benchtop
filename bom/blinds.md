# Blinds — electronics BOM (per unit, ×8 build)

Resolves [#19](https://github.com/0x63616c/benchtop/issues/19). All lines browser-verified in stock
2026-07-26 (cmux browser). Battery cells, M3 screws/inserts, drywall anchors, #8 screws, homing
magnets: **owned**, $0 lines. Motor purchase tracked in [#20](https://github.com/0x63616c/benchtop/issues/20).

## PCB parts (LCSC, populate ×10 boards)

Unit price at the ladder tier covering a 12-set buy (10 boards + 2 spares of each part).

| Part | Role | LCSC # | Qty/unit | Unit $ | Stock (2026-07-26) |
|---|---|---|---|---|---|
| ESP32-C3-MINI-1-N4 | MCU/WiFi module (ESPHome light-sleep OK — `wifi: power_save_mode: LIGHT`, esp-idf; #14 measured 7.5mA @ DTIM3) | [C2838502](https://www.lcsc.com/product-detail/C2838502.html) | 1 | $3.47 | 26,318 |
| DRV8871DDAR | Brushed motor driver, 3.6A peak, current-limit R | [C75864](https://www.lcsc.com/product-detail/C75864.html) | 1 | $1.80 | 5,052 |
| BQ25798RQMR | 2S buck-boost charger, USB-PD 12V in (per #18) | [C2876593](https://www.lcsc.com/product-detail/C2876593.html) | 1 | $2.43 | 630 |
| HUSB238A-BB001-QN16R | PD sink, resistor-strapped 12V/3A | [C24833806](https://www.lcsc.com/product-detail/C24833806.html) | 1 | $0.53 | 4,753 |
| BQ29209DRBR | 2S balance + OV protect | [C139352](https://www.lcsc.com/product-detail/C139352.html) | 1 | $0.87 | 1,010 |
| TPS61088RHLR | 12V motor-rail boost, EN-gated | [C87357](https://www.lcsc.com/product-detail/C87357.html) | 1 | $0.87 | 2,000 |
| TLV62569DBVR | 3.3V buck, 2A (AP63203WU-7 out of stock at LCSC) | [C141836](https://www.lcsc.com/product-detail/C141836.html) | 1 | $0.09 | 77,835 |
| DRV5032FBDBZR | Hall switch, chain index mark (µW, 1.65–5.5V) | [C2655033](https://www.lcsc.com/product-detail/C2655033.html) | 1 | $0.64 | 1,460 |
| TYPE-C-31-M-12 | USB-C 16-pin receptacle (PD data pins) | [C165948](https://www.lcsc.com/product-detail/C165948.html) | 1 | $0.17 | 270,670 |
| KH-6X6X7H-ZJ | Tactile switch, up/down. **Right-angle again** (v2 center-drop, spec 2026-07-26): the board lies flat, plungers go +Y out of the front wall — the -ZJ this line originally listed is correct after all; the straight -TJ swap was a rev B artifact | [C2837543](https://www.lcsc.com/product-detail/C2837543.html) | 2 | $0.02 | 25,000+ |
| Passives, inductors, connectors, LED | **finalised by the [#22](https://github.com/0x63616c/benchtop/issues/22) layout** — 26 line items, all JLC-stocked, most of them Basic. Detail below | — | 76 | $4.92 | — |

**PCB parts per unit ≈ $15.82** → ×12 sets ≈ **$190**

87 placed parts per board, 38 line items. The passive estimate was low by
$1.92 a board: three switching converters and a 2S protector need more
decoupling, feedback dividers and strap resistors than "~30 passives" allowed.

### Passives, in full (per board)

| Value / part | LCSC # | Qty | Unit $ | Where |
|---|---|---|---|---|
| 10uF 25V 0805 X5R | C89831 | 11 | $0.139 | VBUS, PMID, REGN, SYS, BAT, converter inputs, MCU bulk |
| 100nF 0603 X7R | C14663 | 12 | $0.024 | HF decoupling everywhere |
| 22uF 25V 0805 X5R | C784585 | 5 | $0.501 | 12V motor rail (3), DRV8871 VM, 3V3 out |
| 47nF 0603 | C1622 | 3 | $0.014 | charger bootstraps (2), boost soft-start |
| 1uF 0603 | C106858 | 3 | $0.044 | PD sink VDD, boost VCC, MCU |
| 330nF 0603 | C282682 | 1 | $0.015 | BQ29209 3s OV delay |
| 10nF 0603 | C57112 | 1 | $0.012 | boost loop compensation |
| 1nF 0603 | C100040 | 1 | $0.015 | BQ25798 SDRV (no ship FET fitted) |
| 22pF 0603 C0G | C1653 | 1 | $0.008 | 3V3 feedback feed-forward |
| 2.2uH 7.5A 5.4x5.2 | C177247 | 2 | $0.138 | charger buck-boost + 12V boost |
| 2.2uH 4x4 | C36409 | 1 | $0.064 | 3V3 buck |
| 200k 1% 0603 | C25811 | 5 | $0.003 | boost FSW/ILIM/FB, /CE divider |
| 10k 1% 0603 | C25804 | 6 | $0.008 | TS divider, /INT, EN, IO2 strap |
| 100k 1% 0603 | C25803 | 4 | $0.008 | QON, EN pulls, 3V3 FB |
| 22k 1% 0603 | C31850 | 2 | $0.007 | boost + buck FB bottom legs |
| 1M 1% 0603 | C22935 | 2 | $0.003 | HUSB238A mode straps |
| 100R 1% 0603 | C22775 | 2 | $0.011 | BQ29209 RVD + midpoint sense |
| 4.7k 1% 0603 | C23162 | 2 | $0.012 | I2C pull-ups |
| 30k 1% 0603 | C22984 | 1 | $0.012 | DRV8871 ILIM = 2.1A |
| 21k 1% 0603 | C22956 | 1 | $0.003 | PD sink: request 3A |
| 8.2k 1% 0603 | C25981 | 1 | $0.008 | BQ25798 PROG: 2 cells, 750kHz |
| 6.04k 1% 0603 | C25977 | 1 | $0.003 | PD sink: request 12V |
| 1k 1% 0603 | C21190 | 1 | $0.009 | status LED |
| 261R 1% 0603 | C22925 | 1 | $0.002 | BQ29209 bottom-cell balance |
| 160R 1% 0603 | C22814 | 1 | $0.003 | BQ29209 top-cell balance |
| 0603 green LED | C12624 | 1 | $0.012 | charge status |
| XH-3AW right-angle | C18428 | 3 | $0.010 | battery, hall (board), hall (tab) |
| XH-2AW right-angle | C33132 | 1 | $0.010 | motor |

No ESD diodes: the only exposed pins are USB-C's, and both the PD sink and the
ESP32-C3's USB PHY have their own on-die clamps. Worth revisiting if rev B
ever sees a static-prone install.

## Battery (per unit)

| Part | Qty/unit | Unit $ | Source |
|---|---|---|---|
| Samsung 50E 21700 (2S3P) | 6 | $0 (owned ×48, balanced) | — |
| Bistook 21700 holder, 3-slot (owned; 83 × 66.59 × 21.8 mm max) | 2 | $0 | Owned |

Two holders per unit provide the six removable cell positions. They screw
directly to the frame and are wired as two 1S3P banks; no carrier PCB is needed.

## Motor (tracked in #20)

| Part | Qty | Unit $ | Status |
|---|---|---|---|
| JGB37-520 12V 111rpm encoder ([B0GTN399G7](https://www.amazon.com/dp/B0GTN399G7)) | 8 | $11.98 | ×2 ordered 2026-07-26; ×1 60rpm ($18.49) ordered for fast path; bulk ×7 gated on unit #1 |

## Chain & mechanical

Existing chains measure ~5mm ball / 6mm pitch — standard plastic blind chain is nominal
**4.5×6mm**; connectors below are that standard size. **Verify joiner snap-fit on the real chain
on arrival** before cutting all loops.

| Part | Qty | $ | Source |
|---|---|---|---|
| 10m spare chain + 10 joiners, 4.5×6mm white ([B088KQ8F4N](https://www.amazon.com/dp/B088KQ8F4N)) | 1 | $13.98 | Amazon, in stock |
| Joiners 30-pack, 4.5mm ([B074QKLTN3](https://www.amazon.com/dp/B074QKLTN3)) | 1 | $7.49 | Amazon, in stock |
| Homing magnet bead: 6×3mm magnet + printed clip | 8 | $0 (owned ×80) | — |
| M3 heat-set inserts, M3 screws, #8 screws, drywall anchors | — | $0 (owned) | — |

## Rev A breadboard (one-time, no fab wait)

| Part | Qty | $ | Source |
|---|---|---|---|
| ESP32-C3 Super Mini 3-pack ([B0H32V6L94](https://www.amazon.com/dp/B0H32V6L94)) | 1 | $12.99 | Amazon — **only 6 left**, order soon |
| DRV8871 driver module 4-pack ([B0GVS7FP6Y](https://www.amazon.com/dp/B0GVS7FP6Y)) | 1 | $11.99 | Amazon, in stock |
| Adafruit HUSB238 PD breakout [#5807](https://www.adafruit.com/product/5807) | 1 | $5.95 | Adafruit, 78 in stock |
| Mikroe Charger 25 Click (BQ25792) [MIKROE-5839](https://www.digikey.com/en/products/detail/mikroelektronika/MIKROE-5839/21671595) | 1 | $30.00 | DigiKey, 18 in stock (Mikroe direct: unavailable) |

**Rev A subtotal = $60.93**

## PCB fab + assembly (JLCPCB, ×10)

The rev B layout ([#22](https://github.com/0x63616c/benchtop/issues/22)) landed at 38×66;
the v2 center-drop unit (spec 2026-07-26) reshapes it to **88×32mm flat main board + an
18×12mm snap-off hall tab below, 88×47mm as one panel, 6 layers**. Six, not two:
24 nets have to escape a 4mm 29-pin QFN and two routing layers cannot do it — see the ticket.

That changes the fab line from the 2-layer estimate above. JLCPCB 6-layer, 38×81mm, qty 10 is
roughly **$45–60** (6-layer starts around $40 for small boards at 10pcs), plus shipping (DHL DDP
$27.92, live-quoted 2026-07-26).

That $27.92 and the calculator's behaviour are real — the quote page was driven live — but the
**6-layer 38×81 qty-10 price above is still an estimate**: cmux's WKWebView bridge could not set
layers/dimensions/qty on JLC's SPA (no eval in the main frame, no mouse input), and it has no
file-upload primitive at all, which the PCBA flow requires. The one number the calculator did
return was $47.80 for its own defaults (2-layer, 100×100mm, qty 5, incl. $16.80 lead-free HASL).
Getting the real PCBA quote needs a human-driven upload of the fab package.

Assembly: 87 parts/board across 38 line items, 4 of them fine-pitch (BQ25798 QFN-29 at 0.4mm,
TPS61088 VQFN-20, HUSB238A QFN-16, BQ29209 SON-8). JLC economic assembly runs ~$8 setup +
~$0.0017/joint + parts; at ~300 joints a board that is **~$60–90 for ten**, and the QFN-29 is
the one part not worth attempting with an iron. A full PCBA quote needs the gerber+BOM+CPL
upload, which is a follow-up.

## Totals

| Bucket | New spend |
|---|---|
| LCSC PCB parts (12 sets) | ~$190 |
| 21700 holders | $0 (owned) |
| Motors ×8 @ $11.98 (2 already ordered + 60rpm unit) | ~$114 |
| Chain spares + joiners | $21.47 |
| Rev A breadboard | $60.93 |
| JLCPCB fab ×10 + ship (6-layer) | ~$55–90 |
| PCBA (87 parts × 10) | ~$60–90 |
| **Grand total (8 units + spares)** | **~$570–650** |

Per-unit marginal electronics cost ≈ **$36** (PCB parts + holders + motor; cells owned).

## Mechanical, v2 center-drop drive (per unit)

The v2 drive train (spec 2026-07-26) uses separately printed m2 z14 and z17
spur gears plus a separate z10 layshaft bevel. The layshaft gears are pinned
to a bought Ø5 mm steel rod running in two 625ZZ bearings. The matching z10
sprocket bevel and chain wheel are separate prints, pinned to a second Ø5 mm
shaft running in two 625ZZ bearings. Bought hardware:

| Part | Qty | Note |
|---|---|---|
| M3×8 (into gearbox face) | 6 | motor → bulkhead rib, BCD31 |
| M3×8 + heat-set (board, battery holders) | 3 + 6 | rev C board bosses, direct holder spine |
| M3×8 (sleeve retention) | 2 | underside screws into the wall frame; sleeve remains non-structural |
| M3×8 + heat-set (cassette lid) | 3 + 3 | triangular clamp pattern; one structural lid retains the layshaft pair and front sprocket 625ZZ |
| 625ZZ bearing (5×16×5 mm) | 4 | two layshaft bearings plus rear/front sprocket-shaft bearings |
| Ø5×38.5 mm steel rod | 1 | removable layshaft; cut/deburr from 5 mm stock |
| Ø5×40 mm steel rod | 1 | rotating sprocket shaft; chain wheel and bevel pin to it |
| Ø2×12 mm steel cross pin | 1 | locks the layshaft spur to its rod |
| Ø2×14 mm steel cross pin | 3 | locks the layshaft bevel, sprocket bevel, and chain wheel to their rods |
| M3 grub screw | 1 | locks the motor pinion through its printable/tappable pilot |
| M3×8 + heat-set (cassette dock) | 2 + 2 | keyed shelf carries load; two screws only clamp the pod to the frame |
| Steel 1:1 bevel pair, m2-ish, Ø5/Ø6 bores | 0 (fallback) | only if the printed bevels wear — bores are standard |

Printed structural parts: `blinds-frame`, `blinds-drive-cassette`,
`blinds-cassette-lid`, `blinds-drive-spacers`,
`blinds-sleeve`, `blinds-cap-rear`, and `blinds-cap-front`. Printed drive
parts are `blinds-pinion`, `blinds-layshaft-spur`, `blinds-layshaft-bevel`,
`blinds-sprocket`, `blinds-sprocket-bevel`, and `blinds-sprocket-spacer`.
Print the frame and cassette wall-face down, the single lid room-face down,
the gears face/heel-down, and the spacers upright. Bambu Studio slow-test guards
slice all structural and drive parts on the P2S PETG profile with generated
support disabled.
