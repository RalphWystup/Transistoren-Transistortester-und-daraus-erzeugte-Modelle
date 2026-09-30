# -*- coding: utf-8 -*-
"""
kap09_plots.py — Abbildungen fuer Buchkapitel 9 (Simulation mit den
ermittelten Parametern). QUELLENTREU:
  - Newton-/Bisektionsalgorithmus und alle Parameter wortgetreu aus
    Transistor_21b.py (einfaches Modell) und
    Erweitere_Spice_Parameter_1.py (erweitertes Modell)
  - OP-Wellenformen direkt aus den LTspice-Ergebnisdateien
    OP_1.raw / OP_2.raw (echte Simulationsdaten des Autors)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 12, "axes.titlesize": 13})

q, k_B, T = 1.602e-19, 1.381e-23, 300.0
VT = k_B * T / q

# Parameter wie in den Originalprogrammen
I_S, beta_F, n, V_A = 1e-13, 200.0, 1.0, 100.0          # einfaches Modell
V_AB, I_KF, R_B_int = 200.0, 0.5, 10.0                  # Erweiterung
R_C, V_CC = 100.0, 25.0
V_BB = V_CC

KLAUSUR = "<Pfad zum Ordner mit den Klausurunterlagen — nicht veröffentlicht>"

# ---------- Modellgleichungen (wortgetreu) ---------------------------------
def beta_eff(I_C):
    return beta_F / np.sqrt(1.0 + max(I_C, 0.0) / I_KF)

def F_einfach(v, R_B):
    V_BE, V_CE = v
    I_B = (V_BB - V_BE) / R_B
    I_C = (V_CC - V_CE) / R_C
    e = np.exp(V_BE / VT)
    return np.array([I_B - (I_S / beta_F) * e,
                     I_C - I_S * e * (1 + V_CE / V_A)])

def F_erweitert(v, R_B):
    V_BE, V_CE = v
    I_B = (V_BB - V_BE) / R_B
    I_C = (V_CC - V_CE) / R_C
    b = beta_eff(I_C)
    V_eff = V_BE - I_B * R_B_int
    e = np.exp(V_eff / VT)
    return np.array([I_B - (I_S / b) * e * (1 + V_CE / V_AB),
                     I_C - I_S * e * (1 + V_CE / V_A)])

def newton(Ffun, R_B, start, tol=1e-10, max_iter=100):
    x = np.array(start, float)
    for i in range(max_iter):
        f = Ffun(x, R_B)
        if np.all(np.abs(f) < tol):
            return x, i + 1
        h = 1e-8
        J = np.zeros((2, 2))
        for j in range(2):
            d = x.copy(); d[j] += h
            J[:, j] = (Ffun(d, R_B) - f) / h
        x = x + np.linalg.solve(J, -f)
    raise ValueError("keine Konvergenz")

def bisektion(Ffun, toleranz_rel=0.05, R_B_min=10e3, R_B_max=500e3):
    """Bisektion wie im Original: Ziel V_CE = V_CC/2, Toleranz 5 %."""
    ziel = V_CC / 2
    start = [0.65, V_CC / 2]
    protokoll = []
    for i in range(30):
        R_B_try = (R_B_min + R_B_max) / 2
        loesung, iters = newton(Ffun, R_B_try, start)
        V_BE, V_CE = loesung
        protokoll.append((i + 1, R_B_try, V_CE, iters))
        start = loesung
        if abs(V_CE - ziel) <= toleranz_rel * ziel:
            return R_B_try, V_BE, V_CE, protokoll
        if V_CE < ziel:
            R_B_min = R_B_try
        else:
            R_B_max = R_B_try
    raise RuntimeError("kein R_B gefunden")

RB1, VBE1, VCE1, prot1 = bisektion(F_einfach)
RB2, VBE2, VCE2, prot2 = bisektion(F_erweitert)
IC1, IB1 = (V_CC - VCE1) / R_C, (V_BB - VBE1) / RB1
IC2, IB2 = (V_CC - VCE2) / R_C, (V_BB - VBE2) / RB2
print("einfach:   R_B=%.2f  V_BE=%.5f  V_CE=%.5f  I_B=%.4f mA  I_C=%.3f mA"
      % (RB1, VBE1, VCE1, 1e3 * IB1, 1e3 * IC1))
print("erweitert: R_B=%.2f  V_BE=%.5f  V_CE=%.5f  I_B=%.4f mA  I_C=%.3f mA"
      % (RB2, VBE2, VCE2, 1e3 * IB2, 1e3 * IC2))
print("beta_eff(AP) = %.2f   V_BE,eff = %.5f" %
      (beta_eff(IC2), VBE2 - IB2 * R_B_int))
print("Bisektionsprotokoll einfach:")
for z in prot1:
    print("  Versuch %d: R_B=%9.2f  V_CE=%8.4f  (Newton=%d)" % z)
print("Bisektionsprotokoll erweitert:")
for z in prot2:
    print("  Versuch %d: R_B=%9.2f  V_CE=%8.4f  (Newton=%d)" % z)

# ---------- Abb. 1: Bisektionsverlauf --------------------------------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=160)
for a, prot, titel, rb in [(a1, prot1, "einfaches Modell", RB1),
                           (a2, prot2, "erweitertes Modell", RB2)]:
    v = [p[0] for p in prot]
    r = [p[1] / 1e3 for p in prot]
    vc = [p[2] for p in prot]
    ax2 = a.twinx()
    a.plot(v, r, "o-", color="tab:blue", label="$R_B$ (Versuch)")
    ax2.plot(v, vc, "s--", color="tab:red", label="$V_{CE}$")
    ax2.axhline(V_CC / 2, color="k", lw=1)
    ax2.axhspan(V_CC / 2 * 0.95, V_CC / 2 * 1.05, color="k", alpha=0.08)
    ax2.annotate("Ziel $V_{CC}/2$ ±5 %", xy=(v[0] + 0.1, V_CC / 2 + 0.4),
                 fontsize=10)
    a.set_xlabel("Bisektionsschritt")
    a.set_ylabel("$R_B$ [k$\\Omega$]", color="tab:blue")
    ax2.set_ylabel("$V_{CE}$ [V]", color="tab:red")
    a.set_title("%s: $R_B$ = %.2f $\\Omega$" % (titel, rb))
    a.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("bilder/kap09_bisektion.png")
plt.close(fig)

# ---------- Abb. 2: Kennlinie, Lastgerade, Arbeitspunkt --------------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=160)
V = np.linspace(0, V_CC, 400)
for a, VBE, VCE, IC, titel, eff in [
        (a1, VBE1, VCE1, IC1, "einfaches Modell", None),
        (a2, VBE2, VCE2, IC2, "erweitertes Modell", VBE2 - IB2 * R_B_int)]:
    vbe_nutz = VBE if eff is None else eff
    Ic_mod = I_S * np.exp(vbe_nutz / VT) * (1 + V / V_A)
    a.plot(V, 1e3 * Ic_mod, "r-", lw=2,
           label="Kennlinie $I_C(V_{CE})$ bei $V_{BE}$ des AP")
    a.plot(V, 1e3 * (V_CC - V) / R_C, "g-", lw=2, label="Lastgerade")
    a.plot(VCE, 1e3 * IC, "bo", ms=9, label="Arbeitspunkt")
    a.annotate("AP: (%.2f V, %.1f mA)" % (VCE, 1e3 * IC),
               xy=(VCE, 1e3 * IC), xytext=(12, 14),
               textcoords="offset points", color="blue",
               arrowprops=dict(arrowstyle="->", color="blue"))
    a.set_xlabel("$V_{CE}$ [V]")
    a.set_ylabel("$I_C$ [mA]")
    a.set_title(titel)
    a.set_xlim(0, V_CC)
    a.set_ylim(0, 300)
    a.grid(True, alpha=0.3)
    a.legend(fontsize=9, loc="upper right")
fig.tight_layout()
fig.savefig("bilder/kap09_kennlinie_ap.png")
plt.close(fig)

# ---------- Abb. 3: beta_eff-Abfall durch IKF ------------------------------
fig, a = plt.subplots(figsize=(8, 4.6), dpi=160)
Ic = np.logspace(-4, 0, 400)
a.semilogx(1e3 * Ic, beta_F / np.sqrt(1 + Ic / I_KF), "r-", lw=2,
           label=r"$\beta_{\rm eff}=\beta_F/\sqrt{1+I_C/I_{KF}}$")
a.axhline(beta_F, color="gray", ls="--", lw=1, label=r"$\beta_F$ = 200")
a.plot(1e3 * IC2, beta_eff(IC2), "bo", ms=9, zorder=5,
       label="Arbeitspunkt (%.0f mA, %.1f)" % (1e3 * IC2, beta_eff(IC2)))
a.set_xlabel("$I_C$ [mA]")
a.set_ylabel(r"$\beta_{\rm eff}$")
a.set_title("Hochstrom-Abfall der Stromverstärkung ($I_{KF}$ = 0,5 A)")
a.grid(True, which="both", alpha=0.3)
a.legend(fontsize=10)
fig.tight_layout()
fig.savefig("bilder/kap09_beta_abfall.png")
plt.close(fig)

# ---------- Abb. 4: OP-Wellenformen aus den echten RAW-Dateien -------------
def lese_ltspice_raw(pfad):
    roh = open(pfad, "rb").read()
    marke = "Binary:\n".encode("utf-16-le")
    pos = roh.find(marke)
    kopf = roh[:pos].decode("utf-16-le", errors="replace")
    n_var = n_pkt = 0
    namen = []
    in_vars = False
    for z in kopf.splitlines():
        if z.startswith("No. Variables:"):
            n_var = int(z.split(":")[1])
        elif z.startswith("No. Points:"):
            n_pkt = int(z.split(":")[1])
        elif z.startswith("Variables:"):
            in_vars = True
        elif in_vars and z.startswith("\t"):
            namen.append(z.strip().split("\t")[1])
    daten = roh[pos + len(marke):]
    satz = 8 + 4 * (n_var - 1)
    w = np.zeros((n_pkt, n_var))
    for i in range(n_pkt):
        b = daten[i * satz:(i + 1) * satz]
        w[i, 0] = np.frombuffer(b[:8], dtype="<f8")[0]
        w[i, 1:] = np.frombuffer(b[8:], dtype="<f4")
    return namen, w

n1, w1 = lese_ltspice_raw(KLAUSUR + "OP_1.raw")
n2, w2 = lese_ltspice_raw(KLAUSUR + "OP_2.raw")
t1, ein1, aus1 = w1[:, 0], w1[:, n1.index("V(n007)")], w1[:, n1.index("V(n005)")]
t2, ein2, aus2 = w2[:, 0], w2[:, n2.index("V(n008)")], w2[:, n2.index("V(n006)")]

def amplitude(t, s):
    m = t > 0.002
    return (s[m].max() - s[m].min()) / 2

v1 = amplitude(t1, aus1) / amplitude(t1, ein1)
v2 = amplitude(t2, aus2) / amplitude(t2, ein2)
print("OP_1: v = %.1f   OP_2: v = %.2f  (theoretisch 1+R9/R10 = 10)"
      % (v1, v2))

fig, (a1, a2) = plt.subplots(2, 1, figsize=(9.5, 7.2), dpi=160, sharex=True)
a1.plot(1e3 * t1, 1e3 * ein1, "b-", lw=1.2, label="Eingang [mV]")
a1.plot(1e3 * t1, 1e3 * aus1 / v1, "r--", lw=1.0,
        label="Ausgang, durch v geteilt [mV]")
a1b = a1.twinx()
a1b.plot(1e3 * t1, aus1, "r-", lw=1.4, alpha=0.35)
a1b.set_ylabel("Ausgang [V]", color="tab:red")
a1.set_title("OP_1 ohne Gegenkopplung: v $\\approx$ %.0f" % v1)
a1.set_ylabel("Eingang [mV]", color="tab:blue")
a1.grid(True, alpha=0.3)
a1.legend(fontsize=9, loc="lower right")
a2.plot(1e3 * t2, 1e3 * ein2, "b-", lw=1.2, label="Eingang [mV]")
a2.plot(1e3 * t2, 1e3 * aus2, "r-", lw=1.4, label="Ausgang [mV]")
a2.set_title("OP_2 mit Gegenkopplung $R_9/R_{10}$ = 9 k$\\Omega$/1 k$\\Omega$: "
             "v $\\approx$ %.2f (Sollwert 10)" % v2)
a2.set_xlabel("Zeit [ms]")
a2.set_ylabel("Spannung [mV]")
a2.grid(True, alpha=0.3)
a2.legend(fontsize=9, loc="lower right")
a2.set_xlim(0, 10)
fig.tight_layout()
fig.savefig("bilder/kap09_op_signale.png")
plt.close(fig)

print("4 Abbildungen erzeugt.")
