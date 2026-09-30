# -*- coding: utf-8 -*-
"""
kap08_led_plots.py — Das 1D-Einstiegsbeispiel fuer Buchkapitel 8:
blaue LED (InGaN) mit BAHNWIDERSTAND R_S am Vorwiderstand.
Modell:  I = IS*exp(V_j/(n*VT)),  V_D = V_j + I*R_S   (implizit!)
Erzeugt:
  kap08_led_last.png        Kennlinie (mit/ohne R_S), Knick-Approximation,
                            Widerstandsgerade, beide Arbeitspunkte
  kap08_led_bisektion.png   Intervallschachtelung an f(V_D)
  kap08_newton_tangente.png Newton als Tangentenverfahren (grafisch)
und druckt die Iterationstabellen (Bisektion und Newton) fuer den Text.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 13, "axes.titlesize": 14})

# ---- blaue LED (InGaN) mit Bahnwiderstand, am Vorwiderstand ----
VCC = 5.0        # V   Versorgung
R   = 150.0      # Ohm Vorwiderstand
IS  = 3.3e-21    # A   Saettigungsstrom (blaue LED)
N   = 2.6        # -   Emissionskoeffizient (InGaN: deutlich > 1!)
RS  = 10.0       # Ohm Bahnwiderstand der LED (Modellerweiterung)
VT  = 0.02586    # V
# Faustannahme fuer die Handabschaetzung (Datenblatt-Flussspannung):
VD_FAUST = 3.0   # V   typische Flussspannung einer blauen LED

def f(vd):
    """Residuum in der KLEMMENSPANNUNG V_D:
    Strom aus der Widerstandsgeraden minus Strom der LED-Gleichung,
    ausgewertet an der inneren Spannung V_j = V_D - I*R_S."""
    i_gerade = (VCC - vd) / R
    v_j = vd - i_gerade * RS
    return i_gerade - IS * np.exp(v_j / (N * VT))

def fs(vd):
    """Ableitung f'(V_D) — mit der inneren Ableitung (1 + R_S/R)."""
    i_gerade = (VCC - vd) / R
    v_j = vd - i_gerade * RS
    return -1.0 / R - IS * np.exp(v_j / (N * VT)) / (N * VT) * (1 + RS / R)

# ---- Faust-Abschaetzung (eine Zeile, keine neue Kennlinie!) ----
i_apx = (VCC - VD_FAUST) / R
vd_apx = VD_FAUST
print("Faust-Abschaetzung: I = (VCC-3,0V)/R = %.2f mA" % (1e3 * i_apx))

# ---- Bisektion ----
print("== Bisektion, Startintervall [2,5 V ; 3,5 V] ==")
lo, hi = 2.5, 3.5
print("f(lo)=%+.3f mA, f(hi)=%+.3e A  -> Vorzeichenwechsel: Nullstelle sicher"
      % (1e3 * f(lo), f(hi)))
bis_verlauf = []
for k in range(1, 25):
    m = 0.5 * (lo + hi)
    bis_verlauf.append((k, lo, hi, m, f(m)))
    if k <= 8 or k in (12, 16, 20):
        print("%2d  [%.6f ; %.6f]  Mitte %.6f  f=%+.2e" % (k, lo, hi, m, f(m)))
    if f(lo) * f(m) < 0:
        hi = m
    else:
        lo = m

# ---- Newton ----
def newton_lauf(v0, schritte=14, name=""):
    print("== Newton, Startwert %.2f V %s==" % (v0, name))
    v = v0
    folge = [v]
    for k in range(schritte):
        fv = f(v)
        print("%2d  V_D=%.9f V   f=%+.3e A" % (k, v, fv))
        if abs(fv) < 1e-15:
            break
        v = v - fv / fs(v)
        folge.append(v)
    return folge

# Fehlversuch: Start im flachen Bereich -> Tangenten-Ueberschuss
fehl = newton_lauf(2.60, schritte=6, name="(FEHLVERSUCH) ")
# Hauptlauf: brauchbarer Startwert nahe der Knickspannung
newton_schritte = newton_lauf(2.95)
vd_stern = newton_schritte[-1]
i_stern = (VCC - vd_stern) / R
vj_stern = vd_stern - i_stern * RS
abw = 100 * (i_apx - i_stern) / i_stern
print("Loesung: V_D=%.4f V (V_j=%.4f V), I=%.3f mA" %
      (vd_stern, vj_stern, 1e3 * i_stern))
print("Approximation %.2f mA -> Abweichung %+.1f %%" % (1e3 * i_apx, abw))

# ---------------------------------- Kennlinien + Gerade + Approximation ----
fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=160)
# LED-Kennlinie MIT R_S: parametrisch ueber V_j (implizite Kennlinie!)
vj = np.linspace(2.0, 2.95, 400)
i_par = IS * np.exp(vj / (N * VT))
ax.plot(vj + i_par * RS, 1e3 * i_par, lw=2.5, color="tab:blue",
        label="LED-Modell mit Bahnwiderstand $R_S$")
ax.plot(vj, 1e3 * i_par, lw=1.6, ls="--", color="tab:cyan",
        label="ideale Diode (ohne $R_S$)")
# Widerstandsgerade
vv = np.linspace(2.0, 3.6, 50)
ax.plot(vv, 1e3 * (VCC - vv) / R, lw=2.5, color="tab:orange",
        label="Widerstandsgerade $(V_{CC}-V_D)/R$")
# Arbeitspunkte
ax.plot(vd_stern, 1e3 * i_stern, "o", ms=12, color="crimson", zorder=6)
ax.plot(vd_apx, 1e3 * i_apx, "s", ms=10, color="tab:green", zorder=6)
ax.annotate("exakt (Newton-Raphson):\n$V_D=%.2f\\,$V, $I=%.1f\\,$mA"
            % (vd_stern, 1e3 * i_stern),
            xy=(vd_stern, 1e3 * i_stern), xytext=(3.12, 17.5), fontsize=12,
            color="crimson",
            arrowprops=dict(arrowstyle="->", color="crimson"))
ax.annotate("Faustannahme $V_D\\approx3{,}0\\,$V:\n$I=%.2f\\,$mA"
            % (1e3 * i_apx),
            xy=(vd_apx, 1e3 * i_apx), xytext=(2.05, 20.5), fontsize=12,
            color="tab:green",
            arrowprops=dict(arrowstyle="->", color="tab:green"))
ax.set_xlabel(r"$V_D$ in V")
ax.set_ylabel(r"$I$ in mA")
ax.set_title("Blaue LED am Vorwiderstand: Modell, Faustannahme, "
             "Arbeitspunkt")
ax.set_xlim(2.0, 3.6)
ax.set_ylim(0, 32)
ax.grid(alpha=0.3)
ax.legend(fontsize=10.5, loc="upper left")
fig.tight_layout()
fig.savefig("bilder/kap08_led_last.png")
plt.close(fig)

# ------------------------------------------- Bisektion grafisch ------------
fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=160)
vv = np.linspace(2.45, 3.3, 500)
ax.plot(vv, 1e3 * f(vv), lw=2.5, color="tab:blue", label=r"$f(V_D)$")
ax.axhline(0, color="black", lw=1)
farben = ["tab:orange", "tab:green", "tab:red", "tab:purple"]
hoehe = 12.5
for (k, lo_, hi_, m_, fm_), c in zip(bis_verlauf[:4], farben):
    ax.plot([lo_, hi_], [hoehe, hoehe], lw=3, color=c)
    ax.plot([lo_, lo_], [hoehe - 0.7, hoehe + 0.7], lw=3, color=c)
    ax.plot([hi_, hi_], [hoehe - 0.7, hoehe + 0.7], lw=3, color=c)
    ax.plot(m_, hoehe, "o", ms=6, color=c)
    ax.text(hi_ + 0.02, hoehe, "Schritt %d" % k, fontsize=10, color=c,
            va="center")
    hoehe -= 2.6
ax.plot(vd_stern, 0, "o", ms=11, color="crimson", zorder=5)
ax.annotate("Nullstelle", xy=(vd_stern, 0), xytext=(vd_stern - 0.3, -8),
            fontsize=12, color="crimson",
            arrowprops=dict(arrowstyle="->", color="crimson"))
ax.text(2.5, 4.5, "$f>0$", fontsize=12, color="gray")
ax.text(3.15, -5, "$f<0$", fontsize=12, color="gray")
ax.set_xlabel(r"$V_D$ in V")
ax.set_ylabel(r"$f(V_D)$ in mA")
ax.set_title("Intervallschachtelung: der Vorzeichenwechsel wird eingekreist")
ax.set_ylim(-14, 15)
ax.grid(alpha=0.3)
ax.legend(fontsize=11, loc="lower left")
fig.tight_layout()
fig.savefig("bilder/kap08_led_bisektion.png")
plt.close(fig)

# ------------------------------------------- Newton grafisch ---------------
fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=160)
vv = np.linspace(2.85, 3.22, 500)
ax.plot(vv, 1e3 * f(vv), lw=2.5, color="tab:blue", label=r"$f(V_D)$")
ax.axhline(0, color="black", lw=1)
for k in range(3):
    vk_ = newton_schritte[k]
    vk1 = newton_schritte[k + 1]
    ax.plot(vk_, 1e3 * f(vk_), "o", ms=9, color="crimson", zorder=5)
    ax.plot([vk_, vk1], [1e3 * f(vk_), 0], ls="--", lw=1.8, color="crimson")
    ax.plot([vk1, vk1], [0, 1e3 * f(vk1)], ls=":", lw=1.2, color="gray")
    ax.annotate("$V_%d$" % k, xy=(vk_, 1e3 * f(vk_)),
                xytext=(vk_ - 0.04, 1e3 * f(vk_) + 0.9), fontsize=13,
                color="crimson")
ax.plot(vd_stern, 0, "*", ms=18, color="tab:green", zorder=6)
ax.annotate("Lösung $V^{*}$", xy=(vd_stern, 0),
            xytext=(vd_stern + 0.06, -4), fontsize=12, color="tab:green",
            arrowprops=dict(arrowstyle="->", color="tab:green"))
ax.set_xlabel(r"$V_D$ in V")
ax.set_ylabel(r"$f(V_D)$ in mA")
ax.set_title("Newton-Raphson als Tangentenverfahren: jede Tangente zielt auf die "
             "Nullstelle")
ax.grid(alpha=0.3)
ax.legend(fontsize=11, loc="upper right")
fig.tight_layout()
fig.savefig("bilder/kap08_newton_tangente.png")
plt.close(fig)

print("3 Abbildungen erzeugt.")
