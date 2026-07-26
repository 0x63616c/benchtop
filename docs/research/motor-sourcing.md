# Motor sourcing — JGB37-520 encoder gearmotor (blinds, ticket #15)

Browser-verified on Amazon.com, 2026-07-26 (cmux browser, logged-in session).

## Pick

**JGB37-520 DC 12V gear motor with encoder, 111RPM variant**

- Listing: https://www.amazon.com/dp/B0GTN399G7 (seller: Whimsy Mall / brand "Shophubio")
- Price: **$11.98/ea** + $3.37 shipping; ×9 ≈ **$107.82 + ship**
- Stock: qty selector allows 30 — covers ×9
- Delivery: **Aug 11–25** (China dropship; owner rule: longer shipping OK)
- Backup, same OEM/boilerplate/price/stock: https://www.amazon.com/dp/B0G5Q64YJW

## Why this variant

- 111rpm no-load @12V = 1:90 gearbox on 520 motor (~10,000rpm base).
  Sprocket Ø22.9 → 72mm chain/rev → ~133mm/s no-load, ~100–110mm/s loaded
  → **~28–30s full travel** on 3m chain ✓ (target 30s).
- Torque: JGB37-520 1:90 class rated ~5.5–7 kg·cm (0.55–0.7Nm), stall ~25 kg·cm
  (the "25 Kg·cm" in sibling listings is stall). Requirement from bench findings:
  0.39Nm actual worst-blind, 0.6Nm spec with margin → **fits, thin margin at
  rated** — prototype must confirm thermal at duty (30s bursts, long rests — duty
  cycle is tiny, so fine).
- Encoder: standard JGB37 hall AB, **11 PPR at motor shaft** → 11×4×90 =
  **3960 counts/output-rev ≈ 55 counts/mm chain**. Plenty for mm-level position.

## Winding: 12V is the buyable reality

Amazon carries the encoder version effectively only in 12V for the ~100rpm band
(6V exists only at 18/70rpm, scarce, single-qty). **Battery ticket #18 must
assume a 12V motor rail** (2S3P native-ish or 1S+boost).

## Order plan (map rule: prototype-first)

1. Now: **×2** from B0GTN399G7 (prototype + spare-in-hand).
2. After unit #1 validates: **×7** same listing. Restock risk: unbranded
   dropship listing may vanish — if so, sibling ASINs (B0G5Q64YJW,
   B0GXFCDQYC "12V176", flexman family B0CRDR*) carry the same OEM motor;
   re-verify rpm variant before ordering.

## Rejected

- flexman family (Prime, next-day, $15–23): no ~100rpm variant (12/20/37/60/
  530/1000/1590 only), stock 2–5 per variant — can't cover ×9. 60rpm variant
  would give ~42s travel (miss target).
- 176rpm variants ($14.61): faster than needed, lower rated torque.
- AliExpress: not needed — Amazon covers qty and price.
