# -*- coding: utf-8 -*-
"""
kap09_spice_abgleich.py — Direkter Abgleich fuer Buchkapitel 9:
Fixed-Bias-Schaltung (V_CC=25V, R_C=100 Ohm, R_B aus dem Schaltplan)
geloest (a) mit den Buchgleichungen (wie Transistor_21b.py bzw.
Erweitere_Spice_Parameter_1.py) und (b) mit den SPICE-Gummel-Poon-
Gleichungen, wie sie LTspice mit der .MODEL-Karte auswertet
(Early ueber V_BC, qb-Formulierung, T=27 Grad C, exakte Konstanten).
"""
import numpy as np

V_CC, R_C = 25.0, 100.0
V_BB = V_CC
IS, BF, NF, VAF = 1e-13, 200.0, 1.0, 100.0
VAR, IKF, RBint = 200.0, 0.5, 10.0

VT_PY = 1.381e-23 * 300.0 / 1.602e-19          # Buch/Python-Programme
VT_LT = 1.380649e-23 * 300.15 / 1.602176634e-19  # LTspice (27 C, exakt)
print("VT Python = %.4f mV,  VT LTspice = %.4f mV" %
      (1e3 * VT_PY, 1e3 * VT_LT))

def newton2(F, start, tol=1e-12, it=400):
    """Newton-Raphson, gedaempft: Schrittweite je Groesse begrenzt."""
    x = np.array(start, float)
    for _ in range(it):
        f = F(x)
        if np.all(np.abs(f) < tol):
            return x
        h = 1e-9
        J = np.zeros((2, 2))
        for j in range(2):
            d = x.copy(); d[j] += h
            J[:, j] = (F(d) - f) / h
        delta = np.linalg.solve(J, -f)
        delta[0] = np.clip(delta[0], -0.02, 0.02)   # V_BE vorsichtig
        delta[1] = np.clip(delta[1], -2.0, 2.0)     # V_CE
        x = x + delta
    raise ValueError("keine Konvergenz")

def ap(F, R_B):
    V_BE, V_CE = newton2(F, [0.65, V_CC / 2])
    I_B = (V_BB - V_BE) / R_B
    I_C = (V_CC - V_CE) / R_C
    return V_BE, V_CE, I_B, I_C

# ---------- Buchgleichungen (identisch zu den Originalprogrammen) ----------
def F_buch_einfach(R_B):
    def F(v):
        V_BE, V_CE = v
        e = np.exp(V_BE / (NF * VT_PY))
        return np.array([(V_BB - V_BE) / R_B - IS / BF * e,
                         (V_CC - V_CE) / R_C - IS * e * (1 + V_CE / VAF)])
    return F

def F_buch_erweitert(R_B):
    def F(v):
        V_BE, V_CE = v
        I_B = (V_BB - V_BE) / R_B
        I_C = (V_CC - V_CE) / R_C
        beta = BF / np.sqrt(1 + max(I_C, 0) / IKF)
        e = np.exp((V_BE - I_B * RBint) / (NF * VT_PY))
        return np.array([I_B - IS / beta * e * (1 + V_CE / VAR),
                         I_C - IS * e * (1 + V_CE / VAF)])
    return F

# ---------- SPICE-Gummel-Poon (wie LTspice die Karte auswertet) ------------
def F_spice_einfach(R_B):
    def F(v):
        V_BE, V_CE = v
        V_BC = V_BE - V_CE
        e_be = np.exp(V_BE / (NF * VT_LT))
        e_bc = np.exp(V_BC / (NF * VT_LT))
        qb = 1.0 / (1.0 - V_BC / VAF)          # nur VAF gesetzt
        return np.array([(V_BB - V_BE) / R_B - IS / BF * (e_be - 1),
                         (V_CC - V_CE) / R_C - IS * (e_be - e_bc) / qb])
    return F

def F_spice_erweitert(R_B):
    def F(v):
        V_BE, V_CE = v                          # aeussere Klemmenspannungen
        I_B = (V_BB - V_BE) / R_B
        Vbe_i = V_BE - I_B * RBint              # innerer Basisknoten
        V_BC = Vbe_i - V_CE
        e_be = np.exp(np.clip(Vbe_i / (NF * VT_LT), -80, 80))
        e_bc = np.exp(np.clip(V_BC / (NF * VT_LT), -80, 80))
        q1 = 1.0 / (1.0 - V_BC / VAF - Vbe_i / VAR)
        q2 = IS / IKF * (e_be - 1)
        qb = q1 / 2.0 * (1.0 + np.sqrt(1.0 + 4.0 * q2))
        return np.array([I_B - IS / BF * (e_be - 1),
                         (V_CC - V_CE) / R_C - IS * (e_be - e_bc) / qb])
    return F

# ---------- Abgleich mit den R_B-Werten AUS DEN SCHALTPLAENEN --------------
for titel, R_B, Fb, Fs in [
        ("EINFACH   (Eigen_RW_1d, R2=44453)", 44453.0,
         F_buch_einfach, F_spice_einfach),
        ("ERWEITERT (Eigen_RW_1e, R2=36796)", 36796.0,
         F_buch_erweitert, F_spice_erweitert)]:
    vb = ap(Fb(R_B), R_B)
    vs = ap(Fs(R_B), R_B)
    print("\n===", titel, "===")
    print("                Buchgleichungen   SPICE-Konvention   Differenz")
    for i, (name, f) in enumerate([("V_BE [V]", 1), ("V_CE [V]", 1),
                                   ("I_B [mA]", 1e3), ("I_C [mA]", 1e3)]):
        d = vs[i] - vb[i]
        rel = 100 * d / vb[i]
        print("  %-9s  %12.5f  %15.5f   %+8.5f (%+.2f %%)" %
              (name, f * vb[i], f * vs[i], f * d, rel))
