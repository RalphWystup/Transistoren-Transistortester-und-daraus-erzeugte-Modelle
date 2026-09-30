# -*- coding: utf-8 -*-
"""
kap06_plots.py — Abbildungen fuer Buchkapitel 6 (Gummel-Poon-Modell).
Erzeugt aus dem Modell mit den BC337-25-Parametern:
  kap06_early.png        Ausgangskennlinien mit Extrapolation auf -V_A
  kap06_betaeff.png      beta_eff ueber I_C mit Kniestrom I_KF
  kap06_gummel_ideal.png Gummel-Plot: Gerade mit 60-mV/Dekade-Steigung
  kap06_vergleich.png    ideales vs. erweitertes Modell (Uebertragung)
Nur numpy/matplotlib — reproduzierbar wie alle bjt_*-Werkzeuge.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- Modellparameter BC337-25 (aus Kapitel 7 bestimmt bzw. Datenblatt) ----
IS   = 4.1e-14      # A     Transport-Saettigungsstrom
NF   = 1.0          # -     Emissionskoeffizient
BETA = 292.0        # -     ideale Stromverstaerkung
VA   = 146.0        # V     Early-Spannung
IKF  = 0.9          # A     Kniestrom
VT   = 0.02585      # V     Thermospannung bei 300 K

def ic_modell(vbe, vce):
    return IS * np.exp(vbe / (NF * VT)) * (1.0 + vce / VA)

def beta_eff(ic):
    return BETA / np.sqrt(1.0 + ic / IKF)

STIL = dict(figsize=(7.2, 4.2), dpi=160)

# ---------------------------------------------------------------- Early ----
fig, ax = plt.subplots(**STIL)
vce = np.linspace(0.3, 12, 200)
vce_ext = np.linspace(-VA, 12, 400)
for ib_uA in (10, 20, 30, 40):
    # V_BE so, dass I_C = beta*I_B bei V_CE = 5 V getroffen wird
    ic_ziel = BETA * ib_uA * 1e-6
    vbe = NF * VT * np.log(ic_ziel / (IS * (1 + 5.0 / VA)))
    ax.plot(vce, 1e3 * ic_modell(vbe, vce), lw=2,
            label=r"$I_B$ = %d µA" % ib_uA)
    ax.plot(vce_ext, 1e3 * ic_modell(vbe, vce_ext), lw=0.8, ls="--",
            color="gray")
ax.axvline(-VA, color="crimson", lw=1.5)
ax.annotate(r"$-V_A \approx -146\,$V", xy=(-VA, 0.5), xytext=(-120, 6),
            color="crimson", fontsize=11,
            arrowprops=dict(arrowstyle="->", color="crimson"))
ax.set_xlim(-160, 12)
ax.set_ylim(0, 15)
ax.set_xlabel(r"$V_{CE}$ in V")
ax.set_ylabel(r"$I_C$ in mA")
ax.set_title("Early-Effekt: Extrapolation der Ausgangskennlinien auf $-V_A$")
ax.grid(alpha=0.3)
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
fig.savefig("bilder/kap06_early.png")
plt.close(fig)

# ------------------------------------------------------------- beta_eff ----
fig, ax = plt.subplots(**STIL)
ic = np.logspace(-4, 1, 400)
ax.semilogx(ic, beta_eff(ic), lw=2, color="tab:blue")
ax.axvline(IKF, color="crimson", ls="--", lw=1.5)
ax.axhline(BETA, color="gray", ls=":", lw=1)
ax.axhline(BETA / np.sqrt(2), color="gray", ls=":", lw=1)
ax.annotate(r"$I_{KF}=0{,}9\,$A", xy=(IKF, 100), xytext=(0.08, 60),
            color="crimson", fontsize=11,
            arrowprops=dict(arrowstyle="->", color="crimson"))
ax.annotate(r"$\beta_F$", xy=(2e-4, BETA), xytext=(2e-4, BETA + 8),
            fontsize=11, color="gray")
ax.annotate(r"$\beta_F/\sqrt{2}$", xy=(2e-4, BETA / np.sqrt(2)),
            xytext=(2e-4, BETA / np.sqrt(2) + 8), fontsize=11, color="gray")
ax.axvspan(1e-4, 11e-3, color="tab:green", alpha=0.15)
ax.text(1.1e-3, 30, "Messbereich\nKap. 7", color="tab:green",
        ha="center", fontsize=10)
ax.set_xlabel(r"$I_C$ in A")
ax.set_ylabel(r"$\beta_{\mathrm{eff}}$")
ax.set_title(r"Hochinjektion: $\beta_{\mathrm{eff}} = \beta_F/\sqrt{1+I_C/I_{KF}}$"
             "  (BC337-25)")
ax.set_ylim(0, 320)
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig("bilder/kap06_betaeff.png")
plt.close(fig)

# --------------------------------------------------------- Gummel-Plot ----
fig, ax = plt.subplots(**STIL)
vbe = np.linspace(0.45, 0.75, 200)
ic = ic_modell(vbe, 5.0)
ax.semilogy(1e3 * vbe, ic, lw=2, color="tab:blue")
# Steigungsdreieck: eine Dekade je n*VT*ln(10) = 59,5 mV
v0 = 0.55
i0 = ic_modell(v0, 5.0)
dv = NF * VT * np.log(10)
ax.plot([1e3*v0, 1e3*(v0+dv), 1e3*(v0+dv), 1e3*v0],
        [i0, i0, 10*i0, i0], color="crimson", lw=1.2)
ax.annotate("1 Dekade", xy=(1e3*(v0+dv)+3, 3*i0), color="crimson",
            fontsize=10, rotation=90, va="center")
ax.annotate(r"$\approx 60\,$mV", xy=(1e3*v0 + 1e3*dv/2, 0.55*i0),
            color="crimson", fontsize=10, ha="center", va="top")
ax.set_xlabel(r"$V_{BE}$ in mV")
ax.set_ylabel(r"$I_C$ in A")
ax.set_title("Gummel-Plot: die Exponentialkennlinie wird halblogarithmisch "
             "zur Geraden")
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig("bilder/kap06_gummel_ideal.png")
plt.close(fig)

# ---------------------------------------------- ideal vs. erweitert --------
fig, axe = plt.subplots(1, 2, figsize=(9.6, 4.0), dpi=160)
# links: Ausgangskennlinie ideal (waagerecht) vs. Early
vce = np.linspace(0.3, 12, 200)
ic5 = BETA * 20e-6
vbe5 = NF * VT * np.log(ic5 / (IS * (1 + 5.0 / VA)))
axe[0].plot(vce, 1e3 * np.full_like(vce, IS * np.exp(vbe5/(NF*VT))), lw=2,
            ls="--", color="gray", label="ideal (ohne Early)")
axe[0].plot(vce, 1e3 * ic_modell(vbe5, vce), lw=2, color="tab:blue",
            label=r"erweitert ($V_A=146\,$V)")
axe[0].set_xlabel(r"$V_{CE}$ in V")
axe[0].set_ylabel(r"$I_C$ in mA")
axe[0].set_title("Ausgangskennlinie")
axe[0].legend(fontsize=9)
axe[0].grid(alpha=0.3)
# rechts: beta ideal konstant vs. beta_eff
ic = np.logspace(-4, 1, 300)
axe[1].semilogx(ic, np.full_like(ic, BETA), lw=2, ls="--", color="gray",
                label=r"ideal ($\beta_F$ konstant)")
axe[1].semilogx(ic, beta_eff(ic), lw=2, color="tab:blue",
                label=r"erweitert ($I_{KF}$)")
axe[1].set_xlabel(r"$I_C$ in A")
axe[1].set_ylabel(r"$\beta$")
axe[1].set_title("Stromverstärkung")
axe[1].legend(fontsize=9)
axe[1].grid(alpha=0.3, which="both")
fig.suptitle("Ideales Modell und Gummel-Poon-Erweiterungen im Vergleich",
             y=1.02)
fig.tight_layout()
fig.savefig("bilder/kap06_vergleich.png", bbox_inches="tight")
plt.close(fig)

print("4 Abbildungen erzeugt.")
