# -*- coding: utf-8 -*-
"""
kap07_plots.py — Abbildungen fuer Buchkapitel 7 (Parameterextraktion)
aus den ECHTEN Kurventracer-Messdaten des BC337-25 (Trendows-Export):
  kap07_gummel_mess.png   Gummel-Plot mit Auswertefenster und Fitgerade
  kap07_early_mess.png    Ausgangskennfeld mit Extrapolation auf -V_A
  kap07_beta_mess.png     beta(I_C) mit Plateau — Knie ausserhalb Messfenster
  kap07_zweipunkt.png     Zwei-Punkt-Auswertung (BC547, Rechenbeispiel 7.1)
Grosse Schrift, eine Aussage pro Bild — Buchformat.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 13, "axes.titlesize": 14})
VT = 0.02585
STIL = dict(figsize=(7.8, 4.8), dpi=160)


def lese_tracer(pfad):
    """Trendows-Export lesen: 6 Kopfzeilen, dann Spaltenpaare je Trace,
    deutsches Dezimalkomma. Rueckgabe: (tags, Liste von (x, y)-Arrays)."""
    with open(pfad, encoding="utf-8-sig") as f:
        zeilen = f.read().splitlines()
    tags = [t for t in zeilen[3].split("\t")[1:] if t.strip()]
    spuren = [[] for _ in tags]
    for zeile in zeilen[6:]:
        felder = zeile.split("\t")[1:]          # erste Spalte = Punktindex
        for k in range(len(tags)):
            try:
                x = float(felder[2*k].replace(",", "."))
                y = float(felder[2*k + 1].replace(",", "."))
                spuren[k].append((x, y))
            except (IndexError, ValueError):
                pass
    return tags, [np.array(s) for s in spuren]


# ------------------------------------------------ Gummel-Plot (Messung) ----
tags, spuren = lese_tracer("/workspace/Ic_Vbe.txt")
vbe, ic = spuren[2][:, 0], spuren[2][:, 1] * 1e-3   # Vce=6V, Ic in A
gut = ic > 5e-6                                     # Rauschboden 5 uA
fig, ax = plt.subplots(**STIL)
ax.semilogy(vbe[gut], ic[gut], "o", ms=4, color="tab:blue",
            label="Messung (%s)" % tags[2].replace(",", "."))
# Fitfenster: rein exponentieller Ast
fenster = (ic > 2e-5) & (ic < 2.5e-3)
p = np.polyfit(vbe[fenster], np.log(ic[fenster]), 1)
n_fit = 1.0 / (VT * p[0])
is_fit = np.exp(p[1]) / (1 + 6.0 / 146.0)
vfit = np.linspace(vbe[fenster].min() - 0.02, vbe[fenster].max() + 0.04, 50)
ax.semilogy(vfit, np.exp(np.polyval(p, vfit)), "-", lw=2.5, color="crimson",
            label="Fitgerade im Fenster")
ax.axvspan(vbe[fenster].min(), vbe[fenster].max(), color="tab:green",
           alpha=0.15)
ax.text(vbe[fenster].mean(), 3e-6, "Auswertefenster", color="tab:green",
        ha="center", fontsize=12)
ax.axhline(5e-6, color="gray", ls=":", lw=1.5)
ax.text(0.42, 6.5e-6, "Rauschboden ≈ 5 µA", color="gray", fontsize=11)
ax.annotate(r"Steigung → $n$ = %.3f" % n_fit + "\n"
            + r"Achsenabschnitt → $I_S$ = %.1e A" % is_fit,
            xy=(0.62, 3e-4), xytext=(0.42, 5e-3), fontsize=12,
            arrowprops=dict(arrowstyle="->", color="crimson"),
            color="crimson")
ax.set_xlabel(r"$V_{BE}$ in V")
ax.set_ylabel(r"$I_C$ in A")
ax.set_title("Schritt 1: Gummel-Plot der Messung (BC337-25)")
ax.set_xlim(0.40, 0.75)
ax.grid(alpha=0.3, which="both")
ax.legend(loc="lower right", fontsize=11)
fig.tight_layout()
fig.savefig("bilder/kap07_gummel_mess.png")
plt.close(fig)

# --------------------------------------- Ausgangskennfeld (Messung) --------
tags, spuren = lese_tracer("/workspace/Ic_Vce.txt")
fig, ax = plt.subplots(**STIL)
va_werte = []
for tag, s in zip(tags, spuren):
    vce, ic = s[:, 0], s[:, 1]
    ax.plot(vce, ic, lw=2, label=tag.replace("µ", "µ"))
    flach = vce > 4.0                                # aktiver Bereich
    a, b = np.polyfit(vce[flach], ic[flach], 1)      # ic = a*vce + b
    va = b / a
    va_werte.append(va)
    vx = np.linspace(-va, vce.max(), 80)
    ax.plot(vx, a * vx + b, ls="--", lw=0.9, color="gray")
va_mittel = np.mean(va_werte)
ax.axvline(-va_mittel, color="crimson", lw=1.5)
ax.annotate(r"$-V_A \approx -%.0f\,$V" % va_mittel,
            xy=(-va_mittel, 1), xytext=(-va_mittel + 15, 7),
            color="crimson", fontsize=13,
            arrowprops=dict(arrowstyle="->", color="crimson"))
ax.set_xlim(-160, 14)
ax.set_ylim(0, 13)
ax.set_xlabel(r"$V_{CE}$ in V")
ax.set_ylabel(r"$I_C$ in mA")
ax.set_title("Schritt 3: Early-Extrapolation der gemessenen "
             "Ausgangskennlinien")
ax.grid(alpha=0.3)
ax.legend(loc="upper left", fontsize=10)
fig.tight_layout()
fig.savefig("bilder/kap07_early_mess.png")
plt.close(fig)

# ------------------------------------------------- beta(I_C) (Messung) -----
tags, spuren = lese_tracer("/workspace/hFE_Ic.txt")
fig, ax = plt.subplots(**STIL)
plateau = []
for tag, s in zip(tags, spuren):
    ic, hfe = s[:, 0] * 1e-3, s[:, 1]                # Ic in A
    gut = (ic > 2e-5) & (hfe > 0)
    ax.semilogx(ic[gut], hfe[gut], lw=2, label=tag.replace(",", "."))
    plateau.append(hfe[gut][ic[gut] > 1e-3].max() if (ic[gut] > 1e-3).any()
                   else hfe[gut].max())
bf = float(np.mean(plateau))
ax.axhline(bf, color="gray", ls=":", lw=1.5)
ax.text(3e-5, bf + 6, r"Plateau → $\beta_F \approx %.0f$" % bf,
        color="gray", fontsize=12)
ax.axvline(11e-3, color="crimson", ls="--", lw=1.5)
ax.annotate("Messgrenze 11 mA —\nKnie ($I_{KF}\\approx0{,}9\\,$A)\n"
            "zwei Dekaden entfernt:\n$I_{KF}$ hier NICHT bestimmbar",
            xy=(11e-3, 120), xytext=(1.5e-4, 60), fontsize=11,
            color="crimson",
            arrowprops=dict(arrowstyle="->", color="crimson"))
ax.set_xlabel(r"$I_C$ in A")
ax.set_ylabel(r"$h_{FE} = I_C/I_B$")
ax.set_title(r"Schritt 2 und 4: $\beta$-Plateau — und die Grenze des "
             "Messfensters")
ax.set_ylim(0, 320)
ax.grid(alpha=0.3, which="both")
ax.legend(loc="lower right", fontsize=10)
fig.tight_layout()
fig.savefig("bilder/kap07_beta_mess.png")
plt.close(fig)

# ------------------------------------- Zwei-Punkt-Auswertung (BC547) -------
IS_547, N_547 = 5.0e-14, 1.008
fig, ax = plt.subplots(**STIL)
vbe = np.linspace(0.54, 0.70, 100)
ic = IS_547 * np.exp(vbe / (N_547 * VT))
ax.semilogy(vbe, ic, lw=2.5, color="tab:blue",
            label="Gummel-Gerade BC547")
p1, p2 = (0.600, 0.5e-3), (0.660, 5.0e-3)
for (x, y), name in ((p1, "Punkt 1"), (p2, "Punkt 2")):
    ax.plot(x, y, "o", ms=10, color="crimson", zorder=5)
    ax.plot([x, x], [1e-5, y], ls=":", color="crimson", lw=1)
    ax.plot([0.54, x], [y, y], ls=":", color="crimson", lw=1)
    ax.annotate("%s\n(%.3f V, %.1f mA)" % (name, x, 1e3 * y),
                xy=(x, y), xytext=(x + 0.006, y * 0.45), fontsize=11,
                color="crimson")
ax.annotate("", xy=(0.660, 1.6e-4), xytext=(0.600, 1.6e-4),
            arrowprops=dict(arrowstyle="<->", color="black"))
ax.text(0.630, 1.9e-4, r"$\Delta V_{BE}=60\,$mV", ha="center", fontsize=12)
ax.text(0.548, 2.2e-3,
        r"$n=\dfrac{\Delta V_{BE}}{V_T\,\ln(I_{C2}/I_{C1})}=1{,}008$"
        "\n\n"
        r"$I_S=\dfrac{I_{C1}}{e^{V_{BE1}/(nV_T)}}=5{,}0\cdot10^{-14}\,$A",
        fontsize=12,
        bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))
ax.set_xlabel(r"$V_{BE}$ in V")
ax.set_ylabel(r"$I_C$ in A")
ax.set_title("Zwei-Punkt-Auswertung von Hand (BC547, Rechenbeispiel 7.1)")
ax.grid(alpha=0.3, which="both")
ax.legend(loc="lower right", fontsize=11)
fig.tight_layout()
fig.savefig("bilder/kap07_zweipunkt.png")
plt.close(fig)

print("4 Abbildungen aus Messdaten erzeugt. n=%.3f, IS=%.2e, VA=%.0f, BF=%.0f"
      % (n_fit, is_fit, va_mittel, bf))
