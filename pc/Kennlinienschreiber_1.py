"""
Transistor-Kennlinien-Schreiber
================================
Nimmt das Ausgangskennlinienfeld (Ic über Uce) eines Bipolartransistors auf.
Kommuniziert per Modbus RTU über USB mit dem Arduino-Kennlinien-Schreiber.

Hardware-Voraussetzungen:
  - Arduino mit Kennlinien-Schreiber-Firmware
  - DAC Kanal 0 (UC) steuert Kollektorspannung über Rc
  - DAC Kanal 1 (UB) steuert Basisstrom über Rb
  - ADC Mittelwerte: Reg 8=Urc1, 9=Urc2, 10=Urb1, 11=Urb2

Abhängigkeiten:
  pip install pymodbus matplotlib numpy
"""

import time
import argparse
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.widgets import Button
from pymodbus.client import ModbusSerialClient

# ─────────────────────────────────────────────
#  Konstanten (laut Firmware config.h)
# ─────────────────────────────────────────────
MODBUS_ADR   = 1
BAUD         = 115200

REG_DA0      = 0   # DAC-Register: UC=0, UB=1
REG_ADMIW    = 8   # ADC-Mittelwerte: Urc1=8, Urc2=9, Urb1=10, Urb2=11

DAC_MAX_V    = 2.5        # DAC Vollausschlag [V]
ADC_MAX_V    = 4.096      # ADC Referenzspannung [V]
DAC_BITS     = 65535      # 16-Bit DAC
ADC_BITS     = 65535      # 16-Bit ADC

# ─────────────────────────────────────────────
#  Hilfsfunktionen
# ─────────────────────────────────────────────

def volt_to_dac(v: float) -> int:
    """Spannung [V] → 16-Bit DAC-Wert (0..65535)"""
    raw = int(round(v / DAC_MAX_V * DAC_BITS))
    return max(0, min(DAC_BITS, raw))

def adc_to_volt(raw: int) -> float:
    """16-Bit ADC-Wert → Spannung [V]"""
    return raw / ADC_BITS * ADC_MAX_V


# ─────────────────────────────────────────────
#  Modbus-Kommunikation
# ─────────────────────────────────────────────

def write_dac(client, kanal: int, volt: float):
    """Setzt DAC-Kanal (0=UC, 1=UB) auf gewünschte Spannung."""
    client.write_register(REG_DA0 + kanal, volt_to_dac(volt), slave=MODBUS_ADR)

def read_adcs(client) -> dict:
    """Liest die 4 ADC-Mittelwert-Register und gibt Spannungen zurück."""
    result = client.read_holding_registers(REG_ADMIW, count=4, slave=MODBUS_ADR)
    if result.isError():
        raise IOError("Modbus-Lesefehler!")
    regs = result.registers
    return {
        "Urc1": adc_to_volt(regs[0]),
        "Urc2": adc_to_volt(regs[1]),
        "Urb1": adc_to_volt(regs[2]),
        "Urb2": adc_to_volt(regs[3]),
    }


# ─────────────────────────────────────────────
#  Messung
# ─────────────────────────────────────────────

def messe_kennlinie(
    port: str,
    Rc: float,
    Rb: float,
    Ib_werte_uA: list,
    Uce_max: float = 2.0,
    Uce_schritte: int = 50,
    settle_ms: int = 20,
) -> list:
    """
    Nimmt das Ausgangskennlinienfeld auf.

    Für jeden Basisstrom Ib wird Uce von 0 bis Uce_max variiert
    und Ic gemessen.

    Rückgabe: Liste von Kurven-Dicts:
      {"Ib_uA": float, "Uce": [V], "Ic": [mA]}
    """
    client = ModbusSerialClient(
        port=port,
        baudrate=BAUD,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1,
    )
    if not client.connect():
        raise ConnectionError(f"Konnte nicht mit {port} verbinden!")

    print(f"\nVerbunden mit {port}")
    print(f"Rc = {Rc} Ω   Rb = {Rb} Ω")
    print(f"Uce: 0 … {Uce_max} V  ({Uce_schritte} Schritte)")
    print(f"Ib-Kurven: {Ib_werte_uA} µA\n")

    kurven = []
    Uce_werte = np.linspace(0, Uce_max, Uce_schritte)

    try:
        for Ib_uA in Ib_werte_uA:
            # Basisspannung berechnen: Ub = Ib * Rb
            Ub_soll = (Ib_uA * 1e-6) * Rb
            if Ub_soll > DAC_MAX_V:
                print(f"  ⚠ Ib={Ib_uA} µA: Ub={Ub_soll:.3f}V übersteigt DAC-Maximum ({DAC_MAX_V}V) – übersprungen")
                continue

            write_dac(client, 1, Ub_soll)  # UB setzen
            time.sleep(0.05)               # kurz einpendeln lassen

            Ic_werte = []
            Uce_gemessen = []
            print(f"  Messe Ib ≈ {Ib_uA} µA (Ub = {Ub_soll*1000:.1f} mV) ...", end="", flush=True)

            for Uc_soll in Uce_werte:
                write_dac(client, 0, Uc_soll)          # UC setzen
                time.sleep(settle_ms / 1000.0)          # Einschwingen abwarten

                adcs = read_adcs(client)

                # Ströme aus Spannungsabfall über Widerstände berechnen
                Ic = adcs["Urc1"] / Rc * 1000           # [mA]
                Ib_ist = adcs["Urb1"] / Rb * 1e6        # [µA], nur zur Info

                # Uce = Uc_soll - Urc  (Spannung am Transistor)
                Uce = Uc_soll - adcs["Urc1"]
                if Uce < 0:
                    Uce = 0.0

                Ic_werte.append(Ic)
                Uce_gemessen.append(Uce)

            kurven.append({
                "Ib_uA": Ib_uA,
                "Uce":   Uce_gemessen,
                "Ic":    Ic_werte,
            })
            print(f" ✓  (Ic_max ≈ {max(Ic_werte):.2f} mA)")

        # DACs auf 0 zurücksetzen
        write_dac(client, 0, 0.0)
        write_dac(client, 1, 0.0)

    finally:
        client.close()

    return kurven


# ─────────────────────────────────────────────
#  Plot
# ─────────────────────────────────────────────

def plot_kennlinienfeld(kurven: list, Rc: float, Rb: float, titel: str = ""):
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#1a1d27")

    # Farbverlauf für Kurven (blau → cyan)
    cmap = plt.cm.cool
    n = len(kurven)

    for i, kurve in enumerate(kurven):
        farbe = cmap(i / max(n - 1, 1))
        ax.plot(
            kurve["Uce"],
            kurve["Ic"],
            color=farbe,
            linewidth=2,
            label=f"Ib = {kurve['Ib_uA']:.0f} µA",
        )

    # Achsen
    ax.set_xlabel("U$_{CE}$ [V]", color="#c8ccd4", fontsize=13)
    ax.set_ylabel("I$_C$ [mA]", color="#c8ccd4", fontsize=13)
    ax.tick_params(colors="#c8ccd4")
    for spine in ax.spines.values():
        spine.set_edgecolor("#3a3d4d")

    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True, which="major", color="#2a2d3d", linewidth=0.8)
    ax.grid(True, which="minor", color="#1f2230", linewidth=0.4)

    # Legende
    legend = ax.legend(
        loc="lower right",
        framealpha=0.3,
        facecolor="#1a1d27",
        edgecolor="#3a3d4d",
        labelcolor="#c8ccd4",
        fontsize=10,
    )

    # Titel
    title_str = titel if titel else "Transistor-Ausgangskennlinienfeld"
    ax.set_title(
        title_str + f"\n(Rc = {Rc} Ω, Rb = {Rb/1000:.1f} kΩ)",
        color="#e0e4ef",
        fontsize=14,
        pad=12,
    )

    # Export-Button
    ax_btn = plt.axes([0.81, 0.01, 0.12, 0.045])
    btn = Button(ax_btn, "💾 CSV", color="#2a2d3d", hovercolor="#3a3d4d")
    btn.label.set_color("#c8ccd4")

    def exportiere_csv(event):
        import csv, datetime
        fname = f"kennlinie_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
        with open(fname, "w", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            # Header
            header = []
            for k in kurven:
                header += [f"Uce_Ib{k['Ib_uA']:.0f}uA [V]", f"Ic_Ib{k['Ib_uA']:.0f}uA [mA]"]
            writer.writerow(header)
            # Daten
            max_len = max(len(k["Uce"]) for k in kurven)
            for row_i in range(max_len):
                row = []
                for k in kurven:
                    if row_i < len(k["Uce"]):
                        row += [f"{k['Uce'][row_i]:.4f}", f"{k['Ic'][row_i]:.4f}"]
                    else:
                        row += ["", ""]
                writer.writerow(row)
        print(f"\nCSV gespeichert: {fname}")
        btn.label.set_text("✓ Gespeichert")
        fig.canvas.draw()

    btn.on_clicked(exportiere_csv)

    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────
#  Demo-Modus (ohne Hardware)
# ─────────────────────────────────────────────

def demo_kennlinie(Rc: float, Rb: float) -> list:
    """Simuliert ein typisches NPN-Ausgangskennlinienfeld (Early-Effekt inklusive)."""
    print("\n[DEMO-MODUS] Simuliere Kennlinie (kein Arduino angeschlossen)\n")
    Ib_werte = [10, 20, 40, 60, 80, 100]
    kurven = []
    Uce = np.linspace(0, 2.0, 100)

    for Ib_uA in Ib_werte:
        hFE = 150
        Ic_sat = Ib_uA * 1e-6 * hFE * 1000     # [mA]
        Early = 1 + Uce / 80                   # Early-Spannung ~80V
        Ic = Ic_sat * (1 - np.exp(-Uce / 0.1)) * Early
        kurven.append({
            "Ib_uA": Ib_uA,
            "Uce":   list(Uce),
            "Ic":    list(Ic),
        })
        print(f"  Ib = {Ib_uA:3d} µA  →  Ic_max ≈ {max(Ic):.2f} mA")

    return kurven


# ─────────────────────────────────────────────
#  Hauptprogramm
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Transistor-Kennlinien-Schreiber (Ausgangskennlinienfeld Ic/Uce)"
    )
    parser.add_argument("--port",    default="COM4",   help="Serieller Port (z.B. COM3 oder /dev/ttyACM0)")
    parser.add_argument("--Rc",      type=float, default=100.0,  help="Kollektorwiderstand [Ω]")
    parser.add_argument("--Rb",      type=float, default=10000.0, help="Basiswiderstand [Ω]")
    parser.add_argument("--Ib",      default="10,20,40,60,80,100", help="Basisstrom-Kurven [µA], kommagetrennt")
    parser.add_argument("--Uce_max", type=float, default=2.0,   help="Maximale Uce [V] (max. 2.5V)")
    parser.add_argument("--schritte",type=int,   default=50,    help="Anzahl Messpunkte pro Kurve")
    parser.add_argument("--settle",  type=int,   default=20,    help="Einschwingzeit pro Schritt [ms]")
    parser.add_argument("--demo",    action="store_true",        help="Demo-Modus ohne Hardware")
    parser.add_argument("--titel",   default="",                 help="Diagramm-Titel")
    args = parser.parse_args()

    Ib_liste = [float(x.strip()) for x in args.Ib.split(",")]

    print("=" * 55)
    print("   Transistor-Kennlinien-Schreiber")
    print("=" * 55)
    print(f"  Port:        {args.port}")
    print(f"  Rc:          {args.Rc} Ω")
    print(f"  Rb:          {args.Rb/1000:.1f} kΩ")
    print(f"  Ib-Kurven:   {Ib_liste} µA")
    print(f"  Uce:         0 … {args.Uce_max} V  ({args.schritte} Punkte)")
    print(f"  Einschwingen:{args.settle} ms/Schritt")
    print("=" * 55)

    try:
        if args.demo:
            kurven = demo_kennlinie(args.Rc, args.Rb)
        else:
            kurven = messe_kennlinie(
                port=args.port,
                Rc=args.Rc,
                Rb=args.Rb,
                Ib_werte_uA=Ib_liste,
                Uce_max=args.Uce_max,
                Uce_schritte=args.schritte,
                settle_ms=args.settle,
            )
    except ConnectionError as e:
        print(f"\n❌ Verbindungsfehler: {e}")
        print("   → Tipp: --demo für Simulation ohne Hardware")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nMessung abgebrochen.")
        sys.exit(0)

    if not kurven:
        print("❌ Keine Kurven aufgenommen.")
        sys.exit(1)

    print(f"\n✓ {len(kurven)} Kurve(n) aufgenommen. Zeige Diagramm ...\n")
    plot_kennlinienfeld(kurven, args.Rc, args.Rb, args.titel)


if __name__ == "__main__":
    main()