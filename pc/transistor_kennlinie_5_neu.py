"""
Kennlinienschreiber – 1. Quadrant (NPN-Transistor)
====================================================
Host-PC Steuerung via Modbus RTU über USB/UART

Hardware:
  ESP32  →  DAC8565  (SPI)  →  OpAmp  →  Prüfling
  ESP32  ←  AD7682   (SPI)  ←  OpAmp  ←  Messwiderstände

Modbus-Register (ESP32):
  REG 0  : DA0 – UC  (Kollektor-Spannung, 0..65535 → 0..2,5V DAC → 0..72V)
  REG 1  : DA1 – UB  (Basis-Spannung,     0..65535 → 0..2,5V DAC → 0..72V)
  REG 4  : AD0 – Urc1  (Rohwert 0..65535 → 0..4,096V)
  REG 5  : AD1 – Urc2
  REG 6  : AD2 – Urb1
  REG 7  : AD3 – Urb2
  REG 8..11 : Mittelwerte der AD-Kanäle (ADMIW)

Schaltungsparameter:
  RB_GND =  1000 Ω   (Basis-GND-Widerstand)
  RC     =   100 Ω   (Kollektor-Messwiderstand, steckbar)
  RB     =  7500 Ω   (Basis-Widerstand, steckbar)
  VCC    =    24 V   (Versorgungsspannung)

Kaskadenregelung (beide als reiner I-Regler):
  Äußerer I-Regler: Basisstrom IB  → DA1 (UB)
  Innerer I-Regler: UCE = URC2     → DA0 (UC)

Ablauf:
  Für jeden Basisstrom-Sollwert IB_soll:
    UCE von 0 bis UCE_max in Schritten erhöhen:
      Inneren Regler einregeln (UCE)
      Äußeren Regler einregeln (IB)
      Messen: IC = (URC1 - URC2) / RC
      Datenpunkt speichern
  Kennlinien plotten und CSV speichern
"""

import time
import csv
import sys
import os
from datetime import datetime

import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ─────────────────────────────────────────────────────────────
#  KONFIGURATION  –  hier anpassen!
# ─────────────────────────────────────────────────────────────

SERIAL_PORT   = "COM4"          # ← serielle Schnittstelle anpassen (z.B. "/dev/ttyUSB0")
BAUD_RATE     = 115200
MODBUS_ADR    = 1

# Schaltungswiderstände
RB_GND  = 1000.0    # Ω
RC      =  100.0    # Ω
RB      = 7500.0    # Ω
VCC     =   24.0    # V (Versorgungsspannung)

# ADC / DAC Skalierung
ADC_VREF    = 4.095     # V  (interne Referenz AD7682)
ADC_MAX     = 65535     # 16-bit
DAC_VREF    = 2.5       # V  (DAC8565 Referenz)
DAC_MAX     = 65535     # 16-bit

# Verstärker-Skalierung (OpAmp-Ausgangsspannungen → Schaltungsspannungen)
# Anpassen je nach tatsächlicher OpAmp-Beschaltung!
VDAC_TO_VUC_FACTOR = 24.0 / 2.5     # DAC 0..2,5V → UC 0..24V (bei 24V Versorgung)
VDAC_TO_VUB_FACTOR = 24.0 / 2.5     # DAC 0..2,5V → UB 0..24V
VADC_TO_V_FACTOR   =  4.0 / 4.096   # ADC 0..4,096V → Messspannung 0..4V (anpassen!)

# Messbereich
UCE_START   =  0.0      # V
UCE_STOP    = 3.0      # V  (max UCE, je nach Transistor / VCC begrenzen)
UCE_STEP    =  0.05      # V  (Schrittweite; bei kleinen Änderungen auto-vergrößert)
UCE_STEP_DYNAMIC = True # True = Schrittweite dynamisch vergrößern wenn ΔIC klein

# Basisströme (in mA) – Kennlinienschar
IB_LIST_MA  = [0.2, 0.4]   # mA

# I-Regler Parameter
# Innerer Regler (UCE): ki_uce  [DAC-Digit / (V * Iteration)]
KI_UCE      =  500.0    # Verstärkung innerer I-Regler
# Äußerer Regler (IB): ki_ib   [DAC-Digit / (mA * Iteration)]
KI_IB       = 2000.0    # Verstärkung äußerer I-Regler

# Einschwingkriterien
SETTLE_TOL_UCE_V   = 0.05   # V   – Toleranz UCE für "eingeschwungen"
SETTLE_TOL_IB_MA   = 0.02   # mA  – Toleranz IB  für "eingeschwungen"
SETTLE_MIN_ITER    =    5   # Mindest-Iterationen nach Erreichen der Toleranz
SETTLE_MAX_ITER    =  200   # Maximale Iterationen pro Sollwert-Schritt
LOOP_DELAY_S       = 0.005  # s   – Wartezeit pro Iteration (5 ms)

# ─────────────────────────────────────────────────────────────
#  MODBUS RTU (minimal, ohne externe Bibliothek)
# ─────────────────────────────────────────────────────────────

def _crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def _build_request(adr: int, fc: int, payload: bytes) -> bytes:
    frame = bytes([adr, fc]) + payload
    crc = _crc16(frame)
    return frame + bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def mb_read_regs(ser: serial.Serial, adr: int, reg: int, count: int) -> list[int] | None:
    """FC03 – mehrere Holding-Register lesen. Gibt Liste von uint16 zurück."""
    req = _build_request(adr, 0x03, bytes([reg >> 8, reg & 0xFF,
                                           count >> 8, count & 0xFF]))
    ser.reset_input_buffer()
    ser.write(req)
    expected = 5 + count * 2
    resp = ser.read(expected)
    if len(resp) < expected:
        return None
    if _crc16(resp[:-2]) != (resp[-2] | (resp[-1] << 8)):
        return None
    result = []
    for i in range(count):
        result.append((resp[3 + i*2] << 8) | resp[4 + i*2])
    return result


def mb_write_reg(ser: serial.Serial, adr: int, reg: int, value: int) -> bool:
    """FC06 – einzelnes Holding-Register schreiben."""
    value = max(0, min(65535, int(value)))
    req = _build_request(adr, 0x06, bytes([reg >> 8, reg & 0xFF,
                                           value >> 8, value & 0xFF]))
    ser.reset_input_buffer()
    ser.write(req)
    resp = ser.read(8)
    if len(resp) < 8:
        return False
    return _crc16(resp[:-2]) == (resp[-2] | (resp[-1] << 8))


def mb_write_multiple_regs(ser: serial.Serial, adr: int, reg: int,
                            values: list[int]) -> bool:
    """FC16 – mehrere Register schreiben."""
    count = len(values)
    byte_count = count * 2
    payload = bytes([reg >> 8, reg & 0xFF,
                     count >> 8, count & 0xFF,
                     byte_count])
    for v in values:
        v = max(0, min(65535, int(v)))
        payload += bytes([v >> 8, v & 0xFF])
    req = _build_request(adr, 0x10, payload)
    ser.reset_input_buffer()
    ser.write(req)
    resp = ser.read(8)
    if len(resp) < 8:
        return False
    return _crc16(resp[:-2]) == (resp[-2] | (resp[-1] << 8))

# ─────────────────────────────────────────────────────────────
#  EINHEITEN-UMRECHNUNG
# ─────────────────────────────────────────────────────────────

def adc_to_volt(raw: int) -> float:
    """ADC-Rohwert → Spannung am ADC-Eingang [V]"""
    return (raw / ADC_MAX) * ADC_VREF


def volt_to_dac(v: float) -> int:
    """Gewünschte DAC-Ausgangsspannung [V] → DAC-Rohwert"""
    v = max(0.0, min(DAC_VREF, v))
    return int((v / DAC_VREF) * DAC_MAX)


def uce_soll_to_dac(uce_v: float) -> int:
    """UCE-Sollwert [V] → DA0-Rohwert (über OpAmp-Skalierung)"""
    v_dac = uce_v / VDAC_TO_VUC_FACTOR
    return volt_to_dac(v_dac)


def ub_soll_to_dac(ub_v: float) -> int:
    """UB-Sollwert [V] → DA1-Rohwert"""
    v_dac = ub_v / VDAC_TO_VUB_FACTOR
    return volt_to_dac(v_dac)


def read_all_measurements(ser: serial.Serial) -> dict | None:
    """
    Liest alle relevanten Messregister und gibt physikalische Größen zurück.
    Verwendet ADMIW (Mittelwerte, REG 8..11).
    """
    regs = mb_read_regs(ser, MODBUS_ADR, 8, 4)  # REG_ADMIW: 8,9,10,11
    if regs is None:
        return None

    urc1_v = adc_to_volt(regs[0]) * (VCC / ADC_VREF)   # Skalierung an OpAmp anpassen
    urc2_v = adc_to_volt(regs[1]) * (VCC / ADC_VREF)
    urb1_v = adc_to_volt(regs[2]) * (VCC / ADC_VREF)
    urb2_v = adc_to_volt(regs[3]) * (VCC / ADC_VREF)

    # Ströme berechnen
    ic_ma  = (urc1_v - urc2_v) / RC * 1000.0            # mA
    ib_ma  = ((urb1_v - urb2_v) / RB - urb2_v / RB_GND) * 1000.0  # mA
    uce_v  = urc2_v                                       # UCE = Spannung an Rc2

    return {
        "urc1_v": urc1_v,
        "urc2_v": urc2_v,
        "urb1_v": urb1_v,
        "urb2_v": urb2_v,
        "ic_ma":  ic_ma,
        "ib_ma":  ib_ma,
        "uce_v":  uce_v,
    }

# ─────────────────────────────────────────────────────────────
#  I-REGLER
# ─────────────────────────────────────────────────────────────

class IRegler:
    """Reiner Integralregler (I-Regler): u[k] = u[k-1] + Ki * e[k]"""

    def __init__(self, ki: float, u_min: float = 0.0, u_max: float = 65535.0):
        self.ki    = ki
        self.u_min = u_min
        self.u_max = u_max
        self.u     = 0.0        # Stellgröße (DAC-Digit)

    def reset(self, u_init: float = 0.0):
        self.u = float(u_init)

    def step(self, error: float) -> int:
        """Einen Regelschritt ausführen. Gibt gerundeten DAC-Wert zurück."""
        self.u += self.ki * error
        self.u = max(self.u_min, min(self.u_max, self.u))
        return int(self.u)

# ─────────────────────────────────────────────────────────────
#  KENNLINIENAUFNAHME
# ─────────────────────────────────────────────────────────────

def run_measurement(ser: serial.Serial) -> dict:
    """
    Führt die vollständige Kennlinienaufnahme durch.
    Rückgabe: {"ib_ma": [...], "curves": {ib: [(uce, ic), ...]}}
    """
    results = {"ib_list_ma": IB_LIST_MA, "curves": {}}

    regler_uce = IRegler(ki=KI_UCE, u_min=0, u_max=65535)
    regler_ib  = IRegler(ki=KI_IB,  u_min=0, u_max=65535)

    total_curves = len(IB_LIST_MA)

    for ci, ib_soll_ma in enumerate(IB_LIST_MA):
        print(f"\n{'='*60}")
        print(f"  Kennlinie {ci+1}/{total_curves}: IB_soll = {ib_soll_ma:.2f} mA")
        print(f"{'='*60}")

        curve_points = []
        results["curves"][ib_soll_ma] = curve_points

        uce_soll = UCE_START
        regler_uce.reset(0.0)
        regler_ib.reset(0.0)

        # DA auf 0 setzen zu Beginn jeder Kennlinie
        mb_write_multiple_regs(ser, MODBUS_ADR, 0, [0, 0])
        time.sleep(0.1)

        prev_ic = None

        while uce_soll <= UCE_STOP + 1e-9:

            print(f"  UCE_soll = {uce_soll:.2f} V", end="  →  ", flush=True)

            # Einschwingen beider Regler
            settle_count = 0
            for iteration in range(SETTLE_MAX_ITER):
                m = read_all_measurements(ser)
                if m is None:
                    print("FEHLER: Keine Messdaten!")
                    continue

                # Innerer Regler: UCE = URC2
                e_uce = uce_soll - m["uce_v"]
                da0   = regler_uce.step(e_uce)

                # Äußerer Regler: IB
                e_ib  = ib_soll_ma - m["ib_ma"]
                da1   = regler_ib.step(e_ib)

                mb_write_multiple_regs(ser, MODBUS_ADR, 0, [da0, da1])
                time.sleep(LOOP_DELAY_S)

                # Eingeschwungen?
                if abs(e_uce) < SETTLE_TOL_UCE_V and abs(e_ib) < SETTLE_TOL_IB_MA:
                    settle_count += 1
                else:
                    settle_count = 0

                if settle_count >= SETTLE_MIN_ITER:
                    break

            # Endmessung nach Einschwingen
            m = read_all_measurements(ser)
            if m is None:
                print("Messfehler – Punkt übersprungen")
                uce_soll += UCE_STEP
                continue

            ic_ma  = m["ic_ma"]
            uce_ist = m["uce_v"]
            ib_ist  = m["ib_ma"]

            print(f"UCE_ist={uce_ist:.3f}V  IB_ist={ib_ist:.3f}mA  IC={ic_ma:.3f}mA "
                  f"(nach {iteration+1} Iter.)")

            curve_points.append((uce_ist, ic_ma))

            # Dynamische Schrittweite: bei kleiner IC-Änderung Schritt vergrößern
            step = UCE_STEP
            if UCE_STEP_DYNAMIC and prev_ic is not None:
                delta_ic = abs(ic_ma - prev_ic)
                if delta_ic < 0.1:    # wenig Änderung → größere Schritte
                    step = min(UCE_STEP * 3, 1.0)
            prev_ic = ic_ma

            uce_soll += step

        print(f"  → Kennlinie {ci+1} fertig: {len(curve_points)} Messpunkte")

    # DAC zurück auf 0
    mb_write_multiple_regs(ser, MODBUS_ADR, 0, [0, 0])
    print("\nMessung abgeschlossen. DAC auf 0 gesetzt.")
    return results


# ─────────────────────────────────────────────────────────────
#  DATEN SPEICHERN
# ─────────────────────────────────────────────────────────────

def save_csv(results: dict, filename: str):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["IB_soll_mA", "UCE_ist_V", "IC_ist_mA"])
        for ib_ma, points in results["curves"].items():
            for uce, ic in points:
                writer.writerow([f"{ib_ma:.3f}", f"{uce:.4f}", f"{ic:.4f}"])
    print(f"CSV gespeichert: {filename}")


# ─────────────────────────────────────────────────────────────
#  PLOT
# ─────────────────────────────────────────────────────────────

def plot_kennlinien(results: dict, title_suffix: str = ""):
    fig, ax = plt.subplots(figsize=(10, 6))

    cmap = plt.cm.plasma
    n = len(results["ib_list_ma"])
    colors = [cmap(i / max(n - 1, 1)) for i in range(n)]

    for idx, ib_ma in enumerate(results["ib_list_ma"]):
        points = results["curves"].get(ib_ma, [])
        if not points:
            continue
        uce_arr = [p[0] for p in points]
        ic_arr  = [p[1] for p in points]
        ax.plot(uce_arr, ic_arr,
                color=colors[idx],
                linewidth=2.0,
                marker="o", markersize=3,
                label=f"IB = {ib_ma:.1f} mA")

    ax.set_xlabel("UCE [V]", fontsize=12)
    ax.set_ylabel("IC [mA]", fontsize=12)
    ax.set_title(f"Ausgangskennlinienfeld – 1. Quadrant (NPN){title_suffix}", fontsize=13)
    ax.legend(title="Basisstrom", loc="lower right", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    # Parameterbox
    info = (f"RC = {RC:.0f} Ω\n"
            f"RB = {RB/1000:.1f} kΩ\n"
            f"RB_GND = {RB_GND/1000:.1f} kΩ\n"
            f"VCC = {VCC:.0f} V")
    ax.text(0.02, 0.97, info, transform=ax.transAxes,
            fontsize=8, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8))

    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def list_ports():
    print("Verfügbare serielle Ports:")
    for p in serial.tools.list_ports.comports():
        print(f"  {p.device:15s}  {p.description}")


def main():
    print("=" * 60)
    print("  Kennlinienschreiber – 1. Quadrant")
    print(f"  Port: {SERIAL_PORT}  |  Baud: {BAUD_RATE}")
    print(f"  RC={RC}Ω  RB={RB}Ω  RB_GND={RB_GND}Ω  VCC={VCC}V")
    print(f"  IB-Stufen: {IB_LIST_MA} mA")
    print(f"  UCE: {UCE_START}..{UCE_STOP} V, Schritt {UCE_STEP} V")
    print(f"  Regler: I-Regler  Ki_UCE={KI_UCE}  Ki_IB={KI_IB}")
    print("=" * 60)

    # Ports auflisten falls Schnittstelle nicht gefunden
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=0.5
        )
    except serial.SerialException as e:
        print(f"\nFEHLER: Port '{SERIAL_PORT}' konnte nicht geöffnet werden: {e}\n")
        list_ports()
        sys.exit(1)

    print(f"Port {SERIAL_PORT} geöffnet.")
    time.sleep(0.5)

    # Verbindungstest: Register lesen
    test = mb_read_regs(ser, MODBUS_ADR, 0, 1)
    if test is None:
        print("WARNUNG: Kein Modbus-Response – trotzdem fortfahren? (j/n)")
        if input().strip().lower() != "j":
            ser.close()
            sys.exit(1)
    else:
        print(f"Modbus OK – DA0-Register = {test[0]}")

    try:
        results = run_measurement(ser)
    except KeyboardInterrupt:
        print("\n\nAbgebrochen durch Benutzer – DAC auf 0 gesetzt.")
        mb_write_multiple_regs(ser, MODBUS_ADR, 0, [0, 0])
        ser.close()
        sys.exit(0)

    ser.close()

    # Dateien speichern
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_name  = f"kennlinie_{ts}.csv"
    plot_name = f"kennlinie_{ts}.png"

    save_csv(results, csv_name)

    fig = plot_kennlinien(results, title_suffix=f"\n{ts}")
    fig.savefig(plot_name, dpi=150)
    print(f"Plot gespeichert: {plot_name}")
    plt.show()


if __name__ == "__main__":
    main()