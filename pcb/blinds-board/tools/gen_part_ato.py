"""Emit the per-part .ato drivers for the vendored footprints/symbols.

Kept as a generator rather than hand-written files because the footprint and
symbol filenames come straight off disk — typo'ing one of those is a silent
`ato build` failure that looks like a parser bug. Pin names come from the
vendored EasyEDA symbol, never from guessing pad order.

    ~/.local/share/uv/tools/atopile/bin/python tools/gen_part_ato.py
"""

from pathlib import Path

PARTS = Path(__file__).parent.parent / "parts"

# dir -> (component, manufacturer, mpn, lcsc, designator prefix, docstring, pins)
# pins: list of (declaration, comment) — declaration is a full ato pin line.
SPEC = {
    # --- ICs -------------------------------------------------------------
    "ESP32_C3_MINI_1": (
        "ESP32_C3_MINI_1_package", "Espressif Systems", "ESP32-C3-MINI-1-N4", "C2838502", "U",
        "ESP32-C3-MINI-1-N4 — RISC-V WiFi/BLE module, 4MB flash, PCB antenna.\n"
        "13.2x16.6mm castellated module; keep the antenna end hanging off the\n"
        "board edge with no copper under it on any layer.\n"
        "Strapping pins: IO2 and IO8 must be HIGH at reset, IO9 HIGH for normal\n"
        "boot (internal pull-up; pulling it low enters the ROM downloader).\n"
        "IO18/IO19 are the native USB D-/D+ — wiring those to the USB-C\n"
        "receptacle gives flashing and serial with no UART bridge.",
        [("signal GND ~ pin 1", ""), ("GND ~ pin 2", ""),
         ("signal P3V3 ~ pin 3", ""),
         ("signal IO2 ~ pin 5", "strapping: HIGH at reset"),
         ("signal IO3 ~ pin 6", ""),
         ("signal EN ~ pin 8", "active-high enable/reset, needs an RC"),
         ("GND ~ pin 11", ""),
         ("signal IO0 ~ pin 12", ""), ("signal IO1 ~ pin 13", ""),
         ("GND ~ pin 14", ""),
         ("signal IO10 ~ pin 16", ""),
         ("signal IO4 ~ pin 18", ""), ("signal IO5 ~ pin 19", ""),
         ("signal IO6 ~ pin 20", ""), ("signal IO7 ~ pin 21", ""),
         ("signal IO8 ~ pin 22", "strapping: HIGH at reset"),
         ("signal IO9 ~ pin 23", "strapping: LOW = ROM download"),
         ("signal IO18 ~ pin 26", "USB D-"), ("signal IO19 ~ pin 27", "USB D+"),
         ("signal RXD0 ~ pin 30", ""), ("signal TXD0 ~ pin 31", ""),
         ("GND ~ pin 36", ""), ("GND ~ pin 37", ""), ("GND ~ pin 38", ""),
         ("GND ~ pin 39", ""), ("GND ~ pin 40", ""), ("GND ~ pin 41", ""),
         ("GND ~ pin 42", ""), ("GND ~ pin 43", ""), ("GND ~ pin 44", ""),
         ("GND ~ pin 45", ""), ("GND ~ pin 46", ""), ("GND ~ pin 47", ""),
         ("GND ~ pin 48", ""), ("GND ~ pin 49", "GND land under the module"),
         ("GND ~ pin 50", ""), ("GND ~ pin 51", ""), ("GND ~ pin 52", ""),
         ("GND ~ pin 53", "")],
    ),
    "BQ25798RQMR": (
        "BQ25798RQMR_package", "Texas Instruments", "BQ25798RQMR", "C2876593", "U",
        "BQ25798 — 1-4 cell buck-boost battery charger with a USB-PD-class input,\n"
        "QFN-29 4x4mm. Charges the 2S3P 21700 pack from the PD 12V input and runs\n"
        "SYS from whichever of input/battery is available.\n"
        "Cell count, charge current and input current limit are I2C registers —\n"
        "the PROG and ILIM_HIZ resistors set power-up defaults only, so firmware\n"
        "must configure 2S before charging is enabled.\n"
        "SW1/SW2 straddle the single buck-boost inductor; BTST1/BTST2 are the two\n"
        "bootstrap caps, each referenced to its own switch node.\n"
        "RQM is a HotRod package: 29 real pads, no exposed thermal pad, so heat\n"
        "leaves through the GND and SYS/BAT pads and their vias.",
        [("signal STAT ~ pin 1", "open-drain charge status LED"),
         ("signal VBUS ~ pin 2", ""), ("VBUS ~ pin 3", ""),
         ("signal BTST1 ~ pin 4", ""), ("signal REGN ~ pin 5", "internal 5V LDO"),
         ("signal DP ~ pin 6", ""), ("signal DM ~ pin 7", ""),
         ("signal VAC2 ~ pin 8", ""), ("signal VAC1 ~ pin 9", ""),
         ("signal ACDRV2 ~ pin 10", "external OVP FET gate — unused"),
         ("signal ACDRV1 ~ pin 11", "external OVP FET gate — unused"),
         ("signal QON ~ pin 12", "active-low ship-mode exit / reset"),
         ("signal CE ~ pin 13", "active-low charge enable"),
         ("signal SCL ~ pin 14", ""), ("signal SDA ~ pin 15", ""),
         ("signal TS ~ pin 16", "pack thermistor sense"),
         ("signal ILIM_HIZ ~ pin 17", ""),
         ("signal BATP ~ pin 18", "battery voltage sense"),
         ("signal BTST2 ~ pin 19", ""),
         ("signal PROG ~ pin 20", ""),
         ("signal INT ~ pin 21", "open-drain interrupt"),
         ("signal BAT ~ pin 22", ""), ("BAT ~ pin 23", ""),
         ("signal SDRV ~ pin 24", "ship-FET gate — unused"),
         ("signal SYS ~ pin 25", ""),
         ("signal SW2 ~ pin 26", ""),
         ("signal GND ~ pin 27", ""),
         ("signal SW1 ~ pin 28", ""),
         ("signal PMID ~ pin 29", "")],
    ),
    "HUSB238A": (
        "HUSB238A_package", "Hynetek", "HUSB238A-BB001-QN16R", "C24833806", "U",
        "HUSB238A-BB001 — USB Type-C PD 3.0 sink controller, QFN-16 3x3mm.\n"
        "The BB001 order option is the strap-configured variant: the voltage and\n"
        "current it requests are set by resistors on SNK_VSET and SNK_ISET, so no\n"
        "I2C host is needed and negotiation completes before the MCU has booted.\n"
        "GATE drives an external load switch, so VBUS only reaches the charger\n"
        "once a contract is agreed.",
        [("signal DP ~ pin 1", ""), ("signal DM ~ pin 2", ""),
         ("signal CC1 ~ pin 3", ""), ("signal CC2 ~ pin 4", ""),
         ("signal VDD ~ pin 5", ""),
         ("signal DBG_N ~ pin 6", ""),
         ("signal OUT1 ~ pin 7", "EN_HVDCP in strap mode"),
         ("signal ADDR ~ pin 8", "ORIENT in strap mode"),
         ("signal SNK_VSET ~ pin 9", "strap: requested voltage"),
         ("signal SNK_ISET ~ pin 10", "strap: requested current"),
         ("signal INT_N ~ pin 11", ""),
         ("signal EN_N ~ pin 12", ""),
         ("signal OUT2 ~ pin 13", "FAULT in strap mode"),
         ("signal FLGIN ~ pin 14", ""),
         ("signal GATE ~ pin 15", "external load-switch gate"),
         ("signal VBUS ~ pin 16", ""),
         ("signal GND ~ pin 17", "thermal pad")],
    ),
    "BQ29209DRBR": (
        "BQ29209DRBR_package", "Texas Instruments", "BQ29209DRBR", "C139352", "U",
        "BQ29209 — 2-series secondary (redundant) overvoltage protector with an\n"
        "internal cell-balance path, SON-8 3x3mm. It watches each cell against a\n"
        "fixed OV threshold and above it drives OUT high; with CB_EN asserted it\n"
        "also bleeds the higher cell through the VC1_CB/VC2 balance pins.\n"
        "Last line of defence behind the charger's own termination.",
        [("signal VC2 ~ pin 1", "top cell +"), ("signal VC1 ~ pin 2", "cell midpoint"),
         ("signal VC1_CB ~ pin 3", "midpoint balance return"),
         ("signal CD ~ pin 4", "charge/discharge control input"),
         ("signal GND ~ pin 5", "pack -"),
         ("signal CB_EN ~ pin 6", "active-low cell-balance enable"),
         ("signal VDD ~ pin 7", ""), ("signal OUT ~ pin 8", "overvoltage output"),
         ("GND ~ pin 9", "thermal pad")],
    ),
    "TPS61088RHLR": (
        "TPS61088RHLR_package", "Texas Instruments", "TPS61088RHLR", "C87357", "U",
        "TPS61088 — 10A synchronous boost, VQFN-20 4.5x3.5mm. Lifts the 2S pack\n"
        "(6.0-8.4V) to the fixed 12V motor rail.\n"
        "EN is driven by the MCU, so the whole motor rail and its quiescent draw\n"
        "are off whenever the blind is idle — the biggest lever on battery life\n"
        "for a device that moves twice a day.\n"
        "MODE floating = PFM at light load (grounded = forced PWM). ILIM sets\n"
        "the switch current limit,\n"
        "FSW the switching frequency, SS the soft-start ramp, COMP the loop\n"
        "compensation.",
        [("signal VCC ~ pin 1", "internal LDO output — decouple only"),
         ("signal EN ~ pin 2", ""), ("signal FSW ~ pin 3", ""),
         ("signal SW ~ pin 4", ""), ("SW ~ pin 5", ""), ("SW ~ pin 6", ""),
         ("SW ~ pin 7", ""),
         ("signal BOOT ~ pin 8", ""), ("signal VIN ~ pin 9", ""),
         ("signal SS ~ pin 10", ""),
         ("signal MODE ~ pin 13", ""),
         ("signal VOUT ~ pin 14", ""), ("VOUT ~ pin 15", ""), ("VOUT ~ pin 16", ""),
         ("signal FB ~ pin 17", ""), ("signal COMP ~ pin 18", ""),
         ("signal ILIM ~ pin 19", ""),
         ("signal AGND ~ pin 20", ""), ("signal PGND ~ pin 21", "thermal pad")],
    ),
    "TLV62569DBVR": (
        "TLV62569DBVR_package", "Texas Instruments", "TLV62569DBVR", "C141836", "U",
        "TLV62569 — 2A synchronous buck, SOT-23-5, 1.5MHz. Makes the 3.3V logic\n"
        "rail straight off the charger's SYS node, so the MCU keeps running on\n"
        "battery with the motor rail switched off. FB regulates to 0.6V.",
        [("signal EN ~ pin 1", ""), ("signal GND ~ pin 2", ""),
         ("signal SW ~ pin 3", ""), ("signal VIN ~ pin 4", ""),
         ("signal FB ~ pin 5", "0.6V reference")],
    ),
    "DRV8871DDAR": (
        "DRV8871DDAR_package", "Texas Instruments", "DRV8871DDAR", "C75864", "U",
        "DRV8871 — 3.6A brushed-DC H-bridge, SO-8 with PowerPAD. Drives the\n"
        "JGB37-520 gearmotor from the 12V rail.\n"
        "IN1/IN2: 00 = coast, 10 = forward, 01 = reverse, 11 = brake (slow decay).\n"
        "ILIM sets the current-regulation trip point — the datasheet's own design\n"
        "example is 30k for 2.1A, and ITRIP scales as 1/R.",
        [("signal GND ~ pin 1", ""), ("signal IN2 ~ pin 2", ""),
         ("signal IN1 ~ pin 3", ""), ("signal ILIM ~ pin 4", ""),
         ("signal VM ~ pin 5", ""), ("signal OUT1 ~ pin 6", ""),
         ("signal PGND ~ pin 7", ""), ("signal OUT2 ~ pin 8", ""),
         ("GND ~ pin 9", "PowerPAD — the only real heat path")],
    ),
    "DRV5032FBDBZR": (
        "DRV5032FBDBZR_package", "Texas Instruments", "DRV5032FBDBZR", "C2655033", "U",
        "DRV5032FB — omnipolar digital hall switch, SOT-23-3, 1.65-5.5V, ~1.3uA.\n"
        "Push-pull output (the FB option), so it needs no pull-up and must not be\n"
        "wired-OR with a second sensor on the same net.",
        [("signal VCC ~ pin 1", ""), ("signal OUT ~ pin 2", ""),
         ("signal GND ~ pin 3", "")],
    ),
    # --- connectors, switches --------------------------------------------
    "USB_C_16P": (
        "USB_C_16P_package", "Korean Hroparts Elec", "TYPE-C-31-M-12", "C165948", "J",
        "USB Type-C 2.0 receptacle, 16-pin SMD with 4 through-hole shield legs.\n"
        "Both CC pins are broken out (the PD sink needs them for orientation) and\n"
        "the two D+/D- pairs reach the MCU as one pair, so the cable works either\n"
        "way round.",
        [("signal GND ~ pin A1B12", ""), ("GND ~ pin B1A12", ""),
         ("signal VBUS ~ pin A4B9", ""), ("VBUS ~ pin B4A9", ""),
         ("signal CC1 ~ pin A5", ""), ("signal CC2 ~ pin B5", ""),
         ("signal DP1 ~ pin A6", ""), ("signal DN1 ~ pin A7", ""),
         ("signal DP2 ~ pin B6", ""), ("signal DN2 ~ pin B7", ""),
         ("signal SBU1 ~ pin A8", ""), ("signal SBU2 ~ pin B8", ""),
         ("signal SHIELD ~ pin 1", ""), ("SHIELD ~ pin 2", ""),
         ("SHIELD ~ pin 3", ""), ("SHIELD ~ pin 4", "")],
    ),
    "SW_KH_6X6X7H_TJ": (
        "SW_KH_6X6X7H_TJ_package", "Shenzhen Kinghelm Elec", "KH-6X6X7H-TJ", "C2837517", "SW",
        "6x6x7mm through-hole tactile switch, STRAIGHT (top-push) variant.\n"
        "3.6mm body + 3.4mm plunger: the enclosure wall sits over the body and the\n"
        "plunger pokes through the wall hole — the right-angle -ZJ part in the BOM\n"
        "pushes along the board, which this enclosure cannot use.\n"
        "Pins 1/2 are one contact, 3/4 the other.",
        [("signal A ~ pin 1", ""), ("A ~ pin 2", ""),
         ("signal B ~ pin 3", ""), ("B ~ pin 4", "")],
    ),
    "XH_2AW": (
        "XH_2AW_package", "BOOMELE(Boom Precision Elec)", "XH-2AW", "C33132", "J",
        "XH 2.5mm 2-pin right-angle shrouded header (JST XH compatible).\n"
        "Rated 3A per contact — above the DRV8871's 2.1A trip point.",
        [("pin 1", ""), ("pin 2", "")],
    ),
    "XH_3AW": (
        "XH_3AW_package", "BOOMELE(Boom Precision Elec)", "XH-3AW", "C18428", "J",
        "XH 2.5mm 3-pin right-angle shrouded header (JST XH compatible).",
        [("pin 1", ""), ("pin 2", ""), ("pin 3", "")],
    ),
    # --- passives ---------------------------------------------------------
    "R0603_100R": ("R0603_100R_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF1000T5E", "C22775", "R",
                   "100R 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_160R": ("R0603_160R_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF1600T5E", "C22814", "R",
                   "160R 1% 0603 — the BQ29209 datasheet's top-cell balance resistor.",
                   [("pin 1", ""), ("pin 2", "")]),
    "R0603_261R": ("R0603_261R_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF2610T5E", "C22925", "R",
                   "261R 1% 0603 — the BQ29209 datasheet's bottom-cell balance\n"
                   "resistor (it specifies 260R; 261R is the E96 neighbour).",
                   [("pin 1", ""), ("pin 2", "")]),
    "R0603_1K": ("R0603_1K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF1001T5E", "C21190", "R",
                 "1k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_2K2": ("R0603_2K2_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF2201T5E", "C4190", "R",
                  "2.2k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_4K7": ("R0603_4K7_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF4701T5E", "C23162", "R",
                  "4.7k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_5K1": ("R0603_5K1_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF5101T5E", "C23186", "R",
                  "5.1k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_6K04": ("R0603_6K04_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF6041T5E", "C25977", "R",
                   "6.04k 1% 0603 — the HUSB238A strap value for a 12V request\n"
                   "(datasheet window 5.7-6.3k, so 1% tolerance is required here).",
                   [("pin 1", ""), ("pin 2", "")]),
    "R0603_8K2": ("R0603_8K2_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF8201T5E", "C25981", "R",
                  "8.2k 1% 0603 — the BQ25798 PROG strap for 2-cell / 750kHz.",
                  [("pin 1", ""), ("pin 2", "")]),
    "R0603_10K": ("R0603_10K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF1002T5E", "C25804", "R",
                  "10k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_20K": ("R0603_20K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF2002T5E", "C4184", "R",
                  "20k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_21K": ("R0603_21K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF2102T5E", "C22956", "R",
                  "21k 1% 0603 — the HUSB238A strap value for a 3A request\n"
                  "(datasheet window 19.95-22.05k).",
                  [("pin 1", ""), ("pin 2", "")]),
    "R0603_22K": ("R0603_22K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF2202T5E", "C31850", "R",
                  "22k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_30K": ("R0603_30K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF3002T5E", "C22984", "R",
                  "30k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_47K": ("R0603_47K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF4702T5E", "C25819", "R",
                  "47k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_100K": ("R0603_100K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF1003T5E", "C25803", "R",
                   "100k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "R0603_1M": ("R0603_1M_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF1004T5E", "C22935", "R",
                 "1M 1% 0603 — the HUSB238A datasheet asks for ~900k when strapping\n"
                 "its dual-function pins, purely to keep standby current down.",
                 [("pin 1", ""), ("pin 2", "")]),
    "R0603_200K": ("R0603_200K_package", "UNI-ROYAL(Uniroyal Elec)", "0603WAF2003T5E", "C25811", "R",
                   "200k 1% 0603 thick-film resistor.", [("pin 1", ""), ("pin 2", "")]),
    "C0603_22PF": ("C0603_22PF_package", "Samsung Electro-Mechanics", "CL10C220JB8NNNC", "C1653", "C",
                   "22pF 5% 50V C0G 0603.", [("pin 1", ""), ("pin 2", "")]),
    "C0603_100PF": ("C0603_100PF_package", "FH (Guangdong Fenghua)", "0603CG101J500NT", "C1635", "C",
                    "100pF 5% 50V C0G 0603.", [("pin 1", ""), ("pin 2", "")]),
    "C0603_1NF": ("C0603_1NF_package", "YAGEO", "CC0603KRX7R9BB102", "C100040", "C",
                  "1nF 10% 50V X7R 0603 — the BQ25798 wants exactly this on SDRV\n"
                  "when no external ship FET is fitted.",
                  [("pin 1", ""), ("pin 2", "")]),
    "C0603_10NF": ("C0603_10NF_package", "FH (Guangdong Fenghua)", "0603B103K500NT", "C57112", "C",
                   "10nF 10% 50V X7R 0603.", [("pin 1", ""), ("pin 2", "")]),
    "C0603_47NF": ("C0603_47NF_package", "Samsung Electro-Mechanics", "CL10B473KB8NNNC", "C1622", "C",
                   "47nF 10% 50V X7R 0603.", [("pin 1", ""), ("pin 2", "")]),
    "C0603_330NF": ("C0603_330NF_package", "CCTC", "TCC0603X7R334K500CT", "C282682", "C",
                    "330nF 10% 50V X7R 0603 — the BQ29209 overvoltage delay cap;\n"
                    "0.33uF is the datasheet's 3-second delay.",
                    [("pin 1", ""), ("pin 2", "")]),
    "C0603_100NF": ("C0603_100NF_package", "YAGEO", "CC0603KRX7R9BB104", "C14663", "C",
                    "100nF 10% 50V X7R 0603 — the standard HF decoupling part.",
                    [("pin 1", ""), ("pin 2", "")]),
    "C0603_1UF": ("C0603_1UF_package", "YAGEO", "CC0603KRX7R8BB105", "C106858", "C",
                  "1uF 10% 25V X7R 0603.", [("pin 1", ""), ("pin 2", "")]),
    "C0805_10UF_25V": ("C0805_10UF_25V_package", "YAGEO", "CC0805KKX5R8BB106", "C89831", "C",
                       "10uF 10% 25V X5R 0805 — roughly 5uF left at 8V of DC bias.",
                       [("pin 1", ""), ("pin 2", "")]),
    "C0805_22UF_25V": ("C0805_22UF_25V_package", "YAGEO", "CC0805MKX5R8BB226", "C784585", "C",
                       "22uF 20% 25V X5R 0805. Bulk on the 12V motor rail and on the\n"
                       "battery/SYS nodes; the 25V rating keeps a usable ~10uF after\n"
                       "DC-bias derating at 12V.",
                       [("pin 1", ""), ("pin 2", "")]),
    "IND_2R2_7A5": ("IND_2R2_7A5_package", "cjiang (Changjiang Microelectronics Tech)",
                    "FXL0530-2R2-M", "C177247", "L",
                    "2.2uH 20% shielded power inductor, 5.4x5.2x3.0mm, 7.5A saturation.\n"
                    "One part covers both big switchers — the charger's buck-boost\n"
                    "inductor and the boost inductor, each peaking near 4A.",
                    [("pin 1", ""), ("pin 2", "")]),
    "IND_2R2_4A9": ("IND_2R2_4A9_package", "Sunlord", "SWPA4030S2R2MT", "C36409", "L",
                    "2.2uH 20% shielded power inductor, 4x4x3mm — the 3.3V buck's\n"
                    "output inductor, the value the TLV62569 datasheet is tested at.",
                    [("pin 1", ""), ("pin 2", "")]),
    "LED_0603_GREEN": ("LED_0603_GREEN_package", "Hubei KENTO Elec", "KT-0603G", "C12624", "D",
                       "0603 green LED, ~3.1Vf. Charge-status indicator off the\n"
                       "charger's open-drain STAT pin.",
                       [("signal K ~ pin 1", "cathode"), ("signal A ~ pin 2", "anode")]),
}

TEMPLATE = '''#pragma experiment("TRAITS")
import has_designator_prefix
import has_part_picked
import is_atomic_part

component {component}:
    """
{doc}
    """
    trait is_atomic_part<manufacturer="{mfr}", partnumber="{mpn}", footprint="{fp}", symbol="{sym}">
    trait has_part_picked::by_supplier<supplier_id="lcsc", supplier_partno="{lcsc}", manufacturer="{mfr}", partno="{mpn}">
    trait has_designator_prefix<prefix="{prefix}">

    # pins
{pins}
'''


def main() -> None:
    for part_dir, (comp, mfr, mpn, lcsc, prefix, doc, pins) in SPEC.items():
        d = PARTS / part_dir
        (fp,) = d.glob("*.kicad_mod")
        (sym,) = d.glob("*.kicad_sym")
        body = "\n".join(
            f"    {decl}" + (f"  # {c}" if c else "") for decl, c in pins
        )
        text = TEMPLATE.format(
            component=comp, mfr=mfr, mpn=mpn, lcsc=lcsc, prefix=prefix,
            fp=fp.name, sym=sym.name,
            doc="\n".join("    " + ln for ln in doc.splitlines()),
            pins=body,
        )
        (d / f"{part_dir}.ato").write_text(text)
        print(f"wrote {part_dir}/{part_dir}.ato")


if __name__ == "__main__":
    main()
