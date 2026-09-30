# -*- coding: utf-8 -*-
"""
kap08_rechnung.py — Rechnung und Abbildungen fuer Buchkapitel 8:
Arbeitspunkt der Fixed-Bias-Schaltung mit dem GEMESSENEN BC547-Satz
(Kapitel 7) per Newton-Raphson; R_B-Suche per Bisektion.
Erzeugt:
  kap08_schaltung.png     Schaltbild der Fixed-Bias-Schaltung
  kap08_lastgerade.png    Ausgangskennlinie, Lastgerade, Arbeitspunkt
  kap08_konvergenz.png    Newton- (quadratisch) und Bisektions-Konvergenz
und druckt die Arbeitspunkt-Tabelle fuer den Buchtext.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 13, "axes.titlesize": 14})

# ---- gemessene BC547-Parameter (Kapitel 7, Abschnitt 7.8) ----
IS, NF, BF = 5.0e-14, 1.01, 290.0
VAF, VAR, IKF, RBI = 95.0, 190.0, 0.08, 15.0
VT = 0.02586

# ---- Schaltung: Fixed Bias ----
VCC = 25.0
VBB = VCC
RC = 100.0

def beta_eff(ic):
    return BF / np.sqrt(1.0 + max(ic, 0.0) / IKF)

def F(x, RB):
    """Residuenvektor [f1, f2] des nichtlinearen Systems."""
    vbe, vce = x
    ib = (VBB - vbe) / RB                    # Basiskreis-Masche
    ic = (VCC - vce) / RC                    # Lastgerade
    veff = vbe - ib * RBI                    # innerer Basiswiderstand
    ex = np.exp(veff / (NF * VT))
    b = beta_eff(ic)
    f1 = ib - (IS / b) * ex * (1.0 + vce / VAR)
    f2 = ic - IS * ex * (1.0 + vce / VAF)
    return np.array([f1, f2])

def J(x, RB):
    """Analytische Jacobi-Matrix (Herleitung im Buchtext)."""
    vbe, vce = x
    ib = (VBB - vbe) / RB
    ic = (VCC - vce) / RC
    veff = vbe - ib * RBI
    ex = np.exp(veff / (NF * VT))
    b = beta_eff(ic)
    dveff = 1.0 + RBI / RB                   # dV_eff/dV_BE
    j11 = -1.0 / RB - (IS / b) * ex * dveff / (NF * VT) * (1 + vce / VAR)
    j12 = -(IS / b) * ex / VAR
    j21 = -IS * ex * dveff / (NF * VT) * (1 + vce / VAF)
    j22 = -1.0 / RC - IS * ex / VAF
    return np.array([[j11, j12], [j21, j22]])

def newton(RB, x0=(0.65, VCC / 2), tol=1e-10, protokoll=None):
    x = np.array(x0, float)
    for k in range(100):
        r = F(x, RB)
        if protokoll is not None:
            protokoll.append(np.linalg.norm(r))
        if np.linalg.norm(r) < tol:
            return x, k
        dx = np.linalg.solve(J(x, RB), -r)
        x = x + dx
    return x, 99

# ---- Bisektion: R_B fuer V_CE = V_CC/2 ----
ziel = VCC / 2
lo, hi = 10e3, 500e3
verlauf_bisekt = []
for i in range(60):
    RB = 0.5 * (lo + hi)
    (vbe, vce), _ = newton(RB)
    verlauf_bisekt.append(abs(vce - ziel))
    if abs(vce - ziel) <= 0.001 * ziel:      # enge Toleranz fuer die Tabelle
        break
    if vce < ziel:
        lo = RB                              # R_B vergroessern
    else:
        hi = RB
(vbe, vce), _ = newton(RB)
ib = (VBB - vbe) / RB
ic = (VCC - vce) / RC
b_eff = beta_eff(ic)
veff = vbe - ib * RBI

print("== Arbeitspunkt (gemessene BC547-Parameter) ==")
print("R_B      = %.1f kOhm" % (RB / 1e3))
print("V_BE     = %.1f mV   V_BE,eff = %.1f mV" % (vbe * 1e3, veff * 1e3))
print("V_CE     = %.3f V" % vce)
print("I_B      = %.1f uA" % (ib * 1e6))
print("I_C      = %.2f mA" % (ic * 1e3))
print("beta_eff = %.1f  (beta_F = %.0f)" % (b_eff, BF))
print("I_C/I_KF = %.2f" % (ic / IKF))

# Newton-Protokoll am Endergebnis-RB fuer die Konvergenzgrafik
prot = []
newton(RB, protokoll=prot)

# ideale Abschaetzung (Kap. 7 / VL): ohne Early, RBM, Webster
ic_ideal = VCC / (2 * RC)
vbe_ideal = NF * VT * np.log(ic_ideal / IS)
rb_ideal = (VBB - vbe_ideal) / (ic_ideal / BF)
print("ideale Abschaetzung: V_BE=%.3f V, R_B=%.1f kOhm"
      % (vbe_ideal, rb_ideal / 1e3))

# ------------------------------------------------------- Schaltbild --------
fig, ax = plt.subplots(figsize=(6.4, 5.2), dpi=160)
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
lw = 2

def draht(x0, y0, x1, y1):
    ax.plot([x0, x1], [y0, y1], color="black", lw=lw)

def widerstand(x, y0, y1, name, wert):
    ym, h, w = (y0 + y1) / 2, 0.9, 0.35
    draht(x, y0, x, ym - h / 2)
    draht(x, ym + h / 2, x, y1)
    ax.add_patch(plt.Rectangle((x - w / 2, ym - h / 2), w, h,
                               fill=False, lw=lw))
    ax.text(x + 0.5, ym, "%s\n%s" % (name, wert), fontsize=13, va="center")

# Versorgungsschiene
draht(2, 9, 8, 9)
ax.text(1.0, 9, r"$V_{CC}=25\,$V", fontsize=13, va="center", ha="center")
ax.plot(2, 9, "o", color="black", ms=4)
# R_B: von der Schiene zur Basis
widerstand(3, 9, 5.2, r"$R_B$", "%.1f k$\\Omega$" % (RB / 1e3))
draht(3, 5.2, 4.6, 5.2)
# R_C: von der Schiene zum Kollektor
widerstand(7, 9, 6.6, r"$R_C$", r"100 $\Omega$")
draht(7, 6.6, 7, 6.2)
# Transistor (vereinfachtes Symbol)
draht(4.6, 5.9, 4.6, 4.5)                  # Basisbalken
draht(4.6, 5.5, 7, 6.2)                    # Kollektorast
draht(4.6, 4.9, 7, 4.2)                    # Emitterast
ax.annotate("", xy=(7, 4.2), xytext=(6.0, 4.62),
            arrowprops=dict(arrowstyle="-|>", color="black", lw=lw))
ax.text(7.35, 5.2, "BC547\n(gemessener\nParametersatz)", fontsize=12)
# Emitter an Masse
draht(7, 4.2, 7, 3.2)
draht(6.6, 3.2, 7.4, 3.2)
draht(6.75, 3.0, 7.25, 3.0)
draht(6.9, 2.8, 7.1, 2.8)
# Spannungs-/Strompfeile
ax.annotate(r"$I_B$", xy=(4.2, 5.45), fontsize=13, color="crimson")
ax.annotate(r"$I_C$", xy=(7.15, 6.6), fontsize=13, color="crimson")
ax.annotate(r"$V_{CE}$", xy=(7.5, 4.4), fontsize=13, color="tab:blue")
ax.annotate(r"$V_{BE}$", xy=(4.9, 4.35), fontsize=13, color="tab:blue")
ax.set_title("Fixed-Bias-Schaltung: $R_B$ stellt den Arbeitspunkt ein")
fig.tight_layout()
fig.savefig("bilder/kap08_schaltung.png")
plt.close(fig)

# ------------------------------------------------- Lastgerade + AP ---------
fig, ax = plt.subplots(figsize=(7.8, 4.8), dpi=160)
vce_ax = np.linspace(0.05, VCC, 400)
# Transistorkennlinie fuer das gefundene V_BE (mit allen Effekten)
ic_kenn = []
for v in vce_ax:
    icg = (VCC - v) / RC
    b = beta_eff(icg)
    ibg = (VBB - vbe) / RB
    veffg = vbe - ibg * RBI
    ic_kenn.append(IS * np.exp(veffg / (NF * VT)) * (1 + v / VAF))
ax.plot(vce_ax, 1e3 * np.array(ic_kenn), lw=2.5, color="tab:blue",
        label=r"Transistorkennlinie bei gefundenem $V_{BE}$")
ax.plot(vce_ax, 1e3 * (VCC - vce_ax) / RC, lw=2.5, color="tab:orange",
        label=r"Lastgerade $I_C=(V_{CC}-V_{CE})/R_C$")
ax.plot(vce, 1e3 * ic, "o", ms=12, color="crimson", zorder=5)
ax.annotate("Arbeitspunkt\n$V_{CE}=%.1f\\,$V, $I_C=%.0f\\,$mA" % (vce, 1e3*ic),
            xy=(vce, 1e3 * ic), xytext=(vce + 2.2, 1e3 * ic + 40),
            fontsize=12, color="crimson",
            arrowprops=dict(arrowstyle="->", color="crimson"))
ax.set_xlabel(r"$V_{CE}$ in V")
ax.set_ylabel(r"$I_C$ in mA")
ax.set_title("Lösung des Gleichungssystems: Schnittpunkt von Kennlinie "
             "und Lastgerade")
ax.set_ylim(0, 260)
ax.grid(alpha=0.3)
ax.legend(fontsize=11)
fig.tight_layout()
fig.savefig("bilder/kap08_lastgerade.png")
plt.close(fig)

# --------------------------------------------------- Konvergenz ------------
fig, axe = plt.subplots(1, 2, figsize=(9.6, 4.2), dpi=160)
axe[0].semilogy(range(len(prot)), prot, "o-", lw=2, color="tab:blue")
axe[0].set_xlabel("Newton-Iteration $k$")
axe[0].set_ylabel(r"$\|F(x_k)\|$")
axe[0].set_title("Newton-Raphson: quadratische Konvergenz")
axe[0].grid(alpha=0.3, which="both")
axe[1].semilogy(range(1, len(verlauf_bisekt) + 1), verlauf_bisekt, "s-",
                lw=2, color="tab:orange")
axe[1].set_xlabel("Bisektions-Schritt")
axe[1].set_ylabel(r"$|V_{CE}-V_{CC}/2|$ in V")
axe[1].set_title("Bisektion: lineare Konvergenz\n(eine Halbierung je Schritt)")
axe[1].grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig("bilder/kap08_konvergenz.png")
plt.close(fig)

print("3 Abbildungen erzeugt.")
