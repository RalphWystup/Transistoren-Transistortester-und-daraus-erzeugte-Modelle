# -*- coding: utf-8 -*-
"""
kap08_led_quellen.py — QUELLENTREUE Reproduktion fuer Buchkapitel 8.2:
Modellfunktionen, Datenparser, Startwerte und Fit-Einstellungen sind
wortgetreu aus den Originalprogrammen uebernommen:
  - Aproximation_AP_LED_normale_Shockly.py    (reines Shockley-Modell)
  - Aproximation_AP_LED_5_erweiterte_Shockly.py (erweitert, mit R_S)
Messdaten: pi_stream_setup/LED_blau.txt (Kennlinienschreiber-Export).
Erzeugt die Buchabbildungen (immer MIT Messpunkten) und druckt alle
Fit- und Arbeitspunktwerte fuer den Buchtext.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

plt.rcParams.update({"font.size": 13, "axes.titlesize": 14})

Vt = 0.02585  # Volt bei 25 Grad C (wie in beiden Originalprogrammen)

# ---------------- Modellfunktionen (wortgetreu uebernommen) ----------------
def shockley(Vd, Is, n):
    """Reine Shockley-Gleichung I(V) — Original 'normale_Shockly'."""
    return Is * (np.exp(Vd / (n * Vt)) - 1)

def extended_shockley_voltage(Id, log10_Is, n, Rs):
    """Erweiterte Shockley-Gleichung V(I) — Original 'erweiterte_Shockly'."""
    Is = 10**log10_Is
    return n * Vt * np.log(Id / Is + 1) + Id * Rs

def solve_for_Id(Uges, R, log10_Is, n, Rs, Vt):
    """Newton-Raphson im Strom I_d — wortgetreu aus dem Original."""
    Is = 10**log10_Is
    Id = Uges / (R + Rs + 1.0)          # gedaempfter Kurzschlussstrom
    tolerance = 1e-7
    for _ in range(1000):
        if Id <= 0:
            Id = 1e-12
        f = n * Vt * np.log(Id / Is + 1) + Id * Rs + Id * R - Uges
        df = (n * Vt) / (Id + Is) + Rs + R
        Id_new = Id - f / df
        if abs(Id_new - Id) < tolerance:
            return Id_new if Id_new > 0 else None
        Id = Id_new
    return None

# ---------------- Messdaten einlesen (Parser wie im Original) --------------
DATEI = "/workspace/pi_stream_setup/LED_blau.txt"
spannung_alle, strom_alle = [], []
spannung_fit, strom_fit = [], []        # Fitfenster erweitert: I > 0,05 mA
spannung_fit0, strom_fit0 = [], []      # Fitfenster normal:    I > 0

with open(DATEI, "r", encoding="utf-8") as f:
    datenbereich = False
    for zeile in f:
        if zeile.startswith("Point"):
            datenbereich = True
            continue
        if not datenbereich:
            continue
        teile = zeile.strip().split()
        if len(teile) < 3:
            continue
        try:
            vf = float(teile[1].replace(",", "."))
            i_ma = float(teile[2].replace(",", "."))
            spannung_alle.append(vf)
            strom_alle.append(i_ma * 1e-3)
            if i_ma > 0:
                spannung_fit0.append(vf)
                strom_fit0.append(i_ma * 1e-3)
            if i_ma > 0.05:
                spannung_fit.append(vf)
                strom_fit.append(i_ma * 1e-3)
        except ValueError:
            pass

spannung_alle = np.array(spannung_alle); strom_alle = np.array(strom_alle)
spannung_fit = np.array(spannung_fit);   strom_fit = np.array(strom_fit)
spannung_fit0 = np.array(spannung_fit0); strom_fit0 = np.array(strom_fit0)
print("%d Messpunkte, davon %d im erweiterten Fitfenster (I > 0,05 mA)"
      % (len(strom_alle), len(strom_fit)))

# ---------------- Fit 1: reines Shockley-Modell (Original-Startwerte) ------
popt_n, _ = curve_fit(shockley, spannung_fit0, strom_fit0,
                      p0=[1e-15, 2.0], maxfev=20000)
Is_n, n_n = popt_n
print("Reines Shockley-Modell:    Is = %.3e A, n = %.4f" % (Is_n, n_n))

# ---------------- Fit 2: erweitertes Modell (Original-p0/bounds) -----------
p0 = [-20.0, 2.0, 15.0]
bounds = ([-35.0, 1.0, 0.0], [-10.0, 5.0, 200.0])
popt_e, pcov_e = curve_fit(extended_shockley_voltage, strom_fit,
                           spannung_fit, p0=p0, bounds=bounds, maxfev=10000)
log10_Is_e, n_e, Rs_e = popt_e
perr = np.sqrt(np.diag(pcov_e))
print("Erweitertes Modell:  Is = %.3e A (log10 %.2f±%.2f), n = %.3f±%.3f, "
      "Rs = %.2f±%.2f Ohm" % (10**log10_Is_e, log10_Is_e, perr[0],
                              n_e, perr[1], Rs_e, perr[2]))

# ---------------- Arbeitspunkt (Manuskript-Beispiel: 5 V, 100 Ohm) ---------
Uges, R = 5.0, 100.0
Id_ap = solve_for_Id(Uges, R, log10_Is_e, n_e, Rs_e, Vt)
Vd_ap = extended_shockley_voltage(Id_ap, log10_Is_e, n_e, Rs_e)
print("Arbeitspunkt (Uges=5 V, R=100 Ohm): Vd = %.4f V, Id = %.3f mA, "
      "Ur = %.3f V, Pr = %.1f mW"
      % (Vd_ap, 1e3 * Id_ap, Id_ap * R, 1e3 * Id_ap**2 * R))
# Newton-Protokoll fuer die Iterations-Tabelle im Buch
Is_e = 10**log10_Is_e
Id = Uges / (R + Rs_e + 1.0)
print("Newton-Iterationen (Start %.3f mA):" % (1e3 * Id))
for k in range(12):
    f = n_e * Vt * np.log(Id / Is_e + 1) + Id * Rs_e + Id * R - Uges
    df = (n_e * Vt) / (Id + Is_e) + Rs_e + R
    Id_neu = Id - f / df
    print("  k=%d  Id = %.6f mA" % (k + 1, 1e3 * Id_neu))
    if abs(Id_neu - Id) < 1e-7:
        break
    Id = Id_neu

# ---------------- Abbildung 1: Warum das reine Modell scheitert ------------
fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=160)
ax.plot(spannung_alle, 1e3 * strom_alle, "kx", ms=6, mew=1.5,
        label="Gemessene Punkte (LED_blau.txt)")
Vlin = np.linspace(spannung_alle.min(), spannung_alle.max(), 1000)
ax.plot(Vlin, 1e3 * shockley(Vlin, Is_n, n_n), "r-", lw=2,
        label="reines Shockley-Modell (Fit)")
Ilin = np.linspace(1e-9, strom_alle.max(), 1000)
ax.plot(extended_shockley_voltage(Ilin, log10_Is_e, n_e, Rs_e), 1e3 * Ilin,
        "b-", lw=2, label=r"erweitertes Modell mit $R_S$ (Fit)")
ax.set_xlabel("Diodenspannung [V]")
ax.set_ylabel("Strom [mA]")
ax.set_title("Reines und erweitertes Shockley-Modell an den Messpunkten")
ax.set_xlim(0, spannung_alle.max() * 1.05)
ax.set_ylim(-1, 1e3 * strom_alle.max() * 1.1)
ax.grid(True, alpha=0.4)
ax.legend(fontsize=11)
fig.tight_layout()
fig.savefig("bilder/kap08_led_vergleich_fits.png")
plt.close(fig)

# ---------------- Abbildung 2: Arbeitspunkt (wie Original-Diagramm 2) ------
fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=160)
max_strom_plot = max(Id_ap * 2, Uges / R, 0.015)
Id_plot = np.linspace(1e-9, max_strom_plot, 1000)
Vd_plot = extended_shockley_voltage(Id_plot, log10_Is_e, n_e, Rs_e)
V_gerade = np.linspace(0, Uges, 1000)
ax.plot(Vd_plot, 1e3 * Id_plot, "r-", lw=2, label="Diode (Modell mit Rs)")
ax.plot(V_gerade, 1e3 * (Uges - V_gerade) / R, "g-", lw=2,
        label="Lastgerade")
ax.plot(Vd_ap, 1e3 * Id_ap, "bo", ms=9, zorder=11, label="Arbeitspunkt")
ax.plot(spannung_alle, 1e3 * strom_alle, "kx", ms=6, mew=1.5, zorder=10,
        label="Gemessene Punkte")
ax.annotate("AP: (%.3f V,  %.3f mA)" % (Vd_ap, 1e3 * Id_ap),
            xy=(Vd_ap, 1e3 * Id_ap), xytext=(15, 15),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="blue"), color="blue")
ax.text(0.05, 0.95,
        "R      = %.1f $\\Omega$\nUges   = %.2f V\nRs_LED = %.2f $\\Omega$\n"
        "n      = %.3f" % (R, Uges, Rs_e, n_e),
        transform=ax.transAxes, va="top", fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.6))
ax.set_xlabel("Spannung [V]")
ax.set_ylabel("Strom [mA]")
ax.set_title("Arbeitspunkt auf der LED-Kennlinie")
ax.set_ylim(0, 1e3 * max_strom_plot * 1.05)
ax.set_xlim(0, Uges * 1.1)
ax.grid(True, alpha=0.4)
ax.legend(fontsize=11)
fig.tight_layout()
fig.savefig("bilder/kap08_led_arbeitspunkt.png")
plt.close(fig)

print("2 Abbildungen erzeugt.")
