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
| KH-6X6X7H-ZJ | Side-press tactile switch (up/down buttons) | [C2837543](https://www.lcsc.com/product-detail/C2837543.html) | 2 | $0.03 | 6,320 (min 20) |
| Passives, inductors, sense R, ESD, LEDs | est. until schematic | — | ~30 | ~$3.00 | — |

**PCB parts per unit ≈ $13.93** → ×12 sets ≈ **$167**

## Battery (per unit)

| Part | Qty/unit | Unit $ | Source |
|---|---|---|---|
| Samsung 50E 21700 (2S3P) | 6 | $0 (owned ×48, balanced) | — |
| 21700 PCB-mount holder, 1-slot ([B0BSC61X69](https://www.amazon.com/dp/B0BSC61X69), 10-pack $12.99) | 6 | $1.30 | Amazon, in stock |

Holders ×8 units = 48 slots → **5 packs = $64.95**

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

Live parametric quote 2026-07-26: **90×70mm, 2-layer, qty 10 = $4.00** ($2.00 with special
offer), + shipping (DHL DDP $27.92 quoted; slower registered mail typically ~$10 — pick at
order). Assembly: exact PCBA quote needs gerber+BOM+CPL, so it lands with the layout ticket;
JLC economic assembly runs ~$8 setup + ~$0.0017/joint + parts — with our parts hand-solderable
except QFN chargers, budget **~$40–60** for assembly of the 4 QFN/power parts ×10, or reflow at
home (P2S bed... no — hotplate/iron; QFN-29 is the hard one).

## Totals

| Bucket | New spend |
|---|---|
| LCSC PCB parts (12 sets) | ~$167 |
| 21700 holders (5×10-pack) | $64.95 |
| Motors ×8 @ $11.98 (2 already ordered + 60rpm unit) | ~$114 |
| Chain spares + joiners | $21.47 |
| Rev A breadboard | $60.93 |
| JLCPCB fab ×10 + ship | ~$15–32 |
| PCBA (QFN parts) | ~$40–60 |
| **Grand total (8 units + spares)** | **~$485–520** |

Per-unit marginal electronics cost ≈ **$34** (PCB parts + holders + motor; cells owned).
