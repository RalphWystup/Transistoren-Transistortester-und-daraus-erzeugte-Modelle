# -*- coding: utf-8 -*-
"""
kap09_fixedbias_schaltbild.py — rendert die LTspice-Arbeitspunkt-
Schaltung Eigen_RW_1d (Fixed Bias) direkt aus der Original-.asc-Datei.
Gleiche Render-Grundfunktionen wie kap09_op_schaltbild.py.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

ASC = "/workspace/BUCH/Eigen_RW_1d.asc"
LW, FS = 1.6, 12

def drehe(px, py, rot):
    if rot == "R0":   return px, py
    if rot == "R90":  return -py, px
    if rot == "R180": return -px, -py
    return py, -px

def lese_asc(pfad):
    wires, flags, syms, texte = [], [], [], []
    sym = None
    for zeile in open(pfad, encoding="utf-8", errors="replace"):
        t = zeile.split()
        if not t:
            continue
        if t[0] == "WIRE":
            wires.append(tuple(int(v) for v in t[1:5]))
        elif t[0] == "FLAG":
            flags.append((int(t[1]), int(t[2]), t[3]))
        elif t[0] == "TEXT":
            texte.append(" ".join(t[5:]))
        elif t[0] == "SYMBOL":
            sym = {"typ": t[1].replace("\\\\", "\\"), "x": int(t[2]),
                   "y": int(t[3]), "rot": t[4], "name": "?", "wert": ""}
            syms.append(sym)
        elif t[0] == "SYMATTR" and sym is not None:
            if t[1] == "InstName":
                sym["name"] = t[2]
            elif t[1] == "Value":
                sym["wert"] = " ".join(t[2:])
    return wires, flags, syms, texte

def T(s, px, py):
    dx, dy = drehe(px, py, s["rot"])
    return s["x"] + dx, s["y"] + dy

def linie(ax, p1, p2, lw=LW):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], "k-", lw=lw,
            solid_capstyle="round")

def zickzack(ax, p1, p2):
    p1, p2 = np.array(p1, float), np.array(p2, float)
    v = p2 - p1
    L = np.hypot(*v)
    e = v / L
    n = np.array([-e[1], e[0]])
    a, b = p1 + e * L * 0.22, p2 - e * L * 0.22
    linie(ax, p1, a)
    linie(ax, b, p2)
    pts = [a]
    for i in range(6):
        f = (i + 0.5) / 6
        pts.append(a + (b - a) * f + n * (9 if i % 2 == 0 else -9))
    pts.append(b)
    pts = np.array(pts)
    ax.plot(pts[:, 0], pts[:, 1], "k-", lw=LW, solid_joinstyle="miter")

def transistor(ax, s, pnp=False):
    P = lambda px, py: T(s, px, py)
    linie(ax, P(0, 48), P(30, 48))
    linie(ax, P(30, 24), P(30, 72), lw=3.0)
    linie(ax, P(64, 0), P(64, 26))
    linie(ax, P(64, 26), P(30, 42))
    linie(ax, P(64, 96), P(64, 70))
    linie(ax, P(64, 70), P(30, 54))
    ax.add_patch(Circle(P(48, 48), 32, fill=False, lw=LW))
    a = np.array(P(30, 54), float)
    b = np.array(P(64, 70), float)
    v = (b - a) / np.hypot(*(b - a))
    n = np.array([-v[1], v[0]])
    sp = a + v * 30
    ax.add_patch(Polygon([sp, sp - v * 14 + n * 7, sp - v * 14 - n * 7],
                         closed=True, fc="k"))

def quelle(ax, s):
    P, M = T(s, 0, 16), T(s, 0, 96)
    m = ((P[0] + M[0]) / 2, (P[1] + M[1]) / 2)
    ax.add_patch(Circle(m, 28, fill=False, lw=LW))
    linie(ax, P, (m[0], m[1] - 28))
    linie(ax, M, (m[0], m[1] + 28))
    ax.text(m[0] + 38, m[1] - 16, "+", fontsize=FS + 1, ha="center",
            va="center")

def masse(ax, x, y):
    linie(ax, (x, y), (x, y + 14))
    for i, b in enumerate([22, 14, 6]):
        linie(ax, (x - b, y + 14 + i * 7), (x + b, y + 14 + i * 7), lw=2.0)

wires, flags, syms, texte = lese_asc(ASC)
fig, ax = plt.subplots(figsize=(7.6, 5.6), dpi=160)

for x1, y1, x2, y2 in wires:
    linie(ax, (x1, y1), (x2, y2))
enden = {}
for x1, y1, x2, y2 in wires:
    for p in [(x1, y1), (x2, y2)]:
        enden[p] = enden.get(p, 0) + 1
for p, anz in enden.items():
    auf = anz
    for x1, y1, x2, y2 in wires:
        if (x1, y1) == p or (x2, y2) == p:
            continue
        if x1 == x2 == p[0] and min(y1, y2) < p[1] < max(y1, y2):
            auf += 2
        if y1 == y2 == p[1] and min(x1, x2) < p[0] < max(x1, x2):
            auf += 2
    if auf >= 3:
        ax.add_patch(Circle(p, 7, fc="k"))
for x, y, name in flags:
    if name == "0":
        masse(ax, x, y)

BESCHRIFTUNG = {
    "R1": ("$R_C$ = 100 $\\Omega$", (36, 40)),
    "R2": ("$R_B$ = 44 453 $\\Omega$\n(aus der Bisektion)", (-440, 40)),
    "V1": ("$V_{CC}$ = 25 V", (44, 44)),
    "Q1": ("Q1\nsimple_npn", (80, 40)),
}
for s in syms:
    if s["typ"] == "res":
        zickzack(ax, T(s, 16, 16), T(s, 16, 96))
    elif s["typ"] == "npn":
        transistor(ax, s)
    elif s["typ"] == "voltage":
        quelle(ax, s)
    txt, (dx, dy) = BESCHRIFTUNG[s["name"]]
    mx = (T(s, 0, 0)[0] + T(s, 64, 96)[0]) / 2
    my = (T(s, 0, 0)[1] + T(s, 64, 96)[1]) / 2
    ax.text(mx + dx, my + dy, txt, fontsize=FS, ha="left", va="center",
            linespacing=1.2)

ax.text(-140, 500,
        ".MODEL simple_npn NPN(IS=1e-13 BF=200 NF=1 VAF=100)",
        fontsize=FS - 1, family="monospace", ha="left")
ax.text(-140, 560,
        "Eigen_RW_1e: $R_B$ = 36 796 $\\Omega$ und zusätzlich "
        "VAR=200 IKF=0.5 RB=10",
        fontsize=FS - 1, ha="left")

ax.set_xlim(-560, 1300)
ax.set_ylim(620, -140)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
fig.savefig("bilder/kap09_fixedbias_ltspice.png", bbox_inches="tight")
print("Schaltbild gespeichert.")
