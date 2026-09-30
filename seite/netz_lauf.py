#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Laesst SEINEN Netzlisten-Loeser ueber die drei Netzlisten des Reiters
„Netzliste und Loeser" laufen und druckt die Zahlen, gegen die die Seite
geprueft wird.

Dieses Programm rechnet NICHTS selbst.  Es stellt nur die beiden Netzlisten
zusammen, ruft

    DGL_Nichtlinear/Programme/simulator.py   (Simulator, Transistor,
                                              GummelPoon, MODELLE_BJT)

auf — unveraendert, Byte fuer Byte, so wie es im Arbeitsbereich liegt — und
schreibt die Ergebnisse so aus, dass das Pruefprogramm sie lesen kann.

Die einzige Rechnung, die hier ueber seinen Loeser hinausgeht, ist die
Kleinsignalverstaerkung aus den vier Tangenten: sie holt die Tangenten mit
`GummelPoon.tangenten` aus seinem Modell und loest das 2x2-System des
Arbeitspunkts.  Genau dieselben vier Zeilen stehen auch auf der Seite; die
Pruefung vergleicht also die Uebertragung nach JavaScript gegen den Python-Lauf.

  python3 netz_lauf.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# simulator.py und bruecke_kern.py liegen im Arbeitsbereich beim Grundlagen-
# projekt, in der Ausfuhr daneben in rechnung/.  Keine festen Rechnerpfade.
H = Path(__file__).resolve().parent
for _k in ("", "../rechnung", "../../DGL_Nichtlinear/Programme",
           "../../../DGL_Nichtlinear/Programme"):
    _p = (H / _k).resolve()
    if (_p / "simulator.py").is_file():
        sys.path.insert(0, str(_p))
        break
else:                                                   # pragma: no cover
    raise SystemExit("simulator.py nicht gefunden")

from simulator import Simulator, MODELLE_BJT             # noqa: E402
from bruecke_kern import MODELLE                         # noqa: E402

# ------------------------------------------------------------------ Vorgaben
# Dieselben Werte wie die Voreinstellung der Schieber auf der Seite.
VCC, RB, RC, RL = 12.0, 470e3, 1e3, 10e3
US, FS = 0.005, 2000.0
CK = CA = 10e-6
DT, PERIODEN = 100e-9, 12
MOD = "BC337"                                # der selbst ermittelte Satz

# Fall 3: SEINE Netzliste der B4-Bruecke, woertlich aus der Datei gelesen.
BR_DT, BR_ENDE, BR_F = 10e-6, 0.2, 50.0
for _k in ("", "../rechnung", "../../DGL_Nichtlinear/Programme",
           "../../../DGL_Nichtlinear/Programme"):
    _b = (H / _k / "bruecke.netz").resolve()
    if _b.is_file():
        BRUECKE = _b.read_text(encoding="utf-8")
        break
else:                                                   # pragma: no cover
    raise SystemExit("bruecke.netz nicht gefunden")


def fall1_netz(vcc=VCC, rb=RB, rc=RC, modell=MOD) -> str:
    """Fall 1 — nur der Arbeitspunkt.  Fuenf Zeilen."""
    return (f"* Fall 1 — nur der Arbeitspunkt\n"
            f"V1  vcc 0     dc {vcc:g}\n"
            f"RB  vcc b     {rb:g}\n"
            f"RC  vcc c     {rc:g}\n"
            f"T1  c   b  0  {modell}\n")


def fall2_netz(uck, uca, vcc=VCC, rb=RB, rc=RC, rl=RL, us=US, fs=FS,
               modell=MOD) -> str:
    """Fall 2 — die vollstaendige Verstaerkerstufe.  Die Anfangswerte der
    beiden Koppelkondensatoren sind die Spannungen, die im Arbeitspunkt ueber
    ihnen stehen — genau wie in seiner Netzliste bjt_emitter_zeit.netz."""
    return (f"* Fall 2 — die vollstaendige Verstaerkerstufe\n"
            f"V1  vcc 0     dc {vcc:g}\n"
            f"RB  vcc b     {rb:g}\n"
            f"RC  vcc c     {rc:g}\n"
            f"T1  c   b  0  {modell}\n"
            f"Vs  s   0     sinus {us:g} {fs:g}\n"
            f"Ck  s   b     {CK*1e6:g}u  {uck:.12f}\n"
            f"Ca  c   a     {CA*1e6:g}u  {uca:.12f}\n"
            f"RL  a   0     {rl:g}\n")


def arbeitspunkt(netz):
    """Ein Newton-Durchgang ohne Zeitschritt — der Gleichstrom-Arbeitspunkt."""
    s = Simulator(netz)
    it = s._newton()
    return s, s.messwerte("T1"), it


def kleinsignal(M, v1, v2, rc, rl, rbi):
    """Die Kleinsignalverstaerkung aus den VIER TANGENTEN, die der Stempel im
    Arbeitspunkt ohnehin bildet (simulator.py, GummelPoon.tangenten, Z. 384-405).

    Koppelkondensatoren sind bei 2 kHz Kurzschluesse, die Betriebsspannung ist
    Wechselstrom-Masse.  Damit bleiben zwei Knotengleichungen:

        b' : (u1 - u_s)/R_BI + g21 u1 + g22 u2 = 0
        c  :  u2/(R_C || R_L) + g11 u1 + g12 u2 = 0

    mit u_s = 1 V; u2 ist dann unmittelbar die Verstaerkung.
    """
    g11, g12, g21, g22 = M.tangenten(v1, v2)
    rac = 1.0 / (1.0 / rc + 1.0 / rl)
    A = np.array([[1.0 / rbi + g21, g22],
                  [g11, 1.0 / rac + g12]])
    u = np.linalg.solve(A, np.array([1.0 / rbi, 0.0]))
    return (g11, g12, g21, g22), rac, u[0], u[1]


def z(name, wert, stellen=11):
    print(f"{name} = {wert:.{stellen}g}")


def main() -> int:
    M = MODELLE_BJT[MOD]

    print("=" * 74)
    print("  FALL 1 — nur der Arbeitspunkt")
    print("=" * 74)
    n1 = fall1_netz()
    print(n1)
    s1, m1, it1 = arbeitspunkt(n1)
    z("F1_UBE", m1["u_be"]); z("F1_UBEEFF", m1["u_be_eff"])
    z("F1_UCE", m1["u_ce"])
    z("F1_IB", m1["i_b"]); z("F1_IC", m1["i_c"]); z("F1_IE", m1["i_e"])
    z("F1_BETA", m1["beta"]); z("F1_BETAEFF", m1["beta_eff"])
    z("F1_P", m1["u_ce"] * m1["i_c"] + m1["u_be"] * m1["i_b"])
    z("F1_UC", s1.potential("c")); z("F1_UB", s1.potential("b"))
    z("F1_NEWTON", it1, 6)

    # Empfindlichkeit gegen die drei GESETZTEN Parameter.  Jeder wird einzeln
    # deutlich verstellt, der Arbeitspunkt neu gerechnet.  Die Karte selbst
    # bleibt unberuehrt — sie wird nur fuer den Lauf umgesetzt und danach
    # wiederhergestellt.
    for kurz, feld, neu in (("IKF", "IKF", 0.405), ("RBI", "RBI", 0.0),
                            ("VAR", "VAR", 600.0), ("VAR200", "VAR", 200.0)):
        alt = getattr(M, feld)
        setattr(M, feld, neu)
        _, m, it = arbeitspunkt(fall1_netz())
        setattr(M, feld, alt)
        z(f"F1_EMP_{kurz}_UCE", m["u_ce"], 9)
        z(f"F1_EMP_{kurz}_IC", m["i_c"], 9)
        z(f"F1_EMP_{kurz}_NEWTON", it, 6)

    print()
    print("=" * 74)
    print("  FALL 2 — die vollstaendige Verstaerkerstufe")
    print("=" * 74)
    n2 = fall2_netz(-m1["u_be"], m1["u_ce"])
    print(n2)

    # Kleinsignal aus den Tangenten
    (g11, g12, g21, g22), rac, u1, av = kleinsignal(
        M, m1["u_be_eff"], m1["u_ce"], RC, RL, M.RBI)
    z("F2_G11", g11); z("F2_G12", g12); z("F2_G21", g21); z("F2_G22", g22)
    z("F2_RAC", rac)
    z("F2_AVKLEIN", av)

    # Grosssignal: SEIN Loeser rechnet den Zeitverlauf
    sim = Simulator(n2, dt=DT)
    tt, uu = sim.lauf(PERIODEN / FS)
    per = int(round((1.0 / FS) / DT))
    ua = uu["a"][-per:]
    uc = uu["c"][-per:]
    ua_max, ua_min = float(ua.max()), float(ua.min())
    uc_mit = float(uc.mean())
    oben = float(uc.max()) - uc_mit
    unten = uc_mit - float(uc.min())
    z("F2_SCHRITTE", sim.schritte, 6)
    z("F2_NEWTON_MITTEL", sim.it_summe / sim.schritte, 6)
    z("F2_NEWTON_GROESSTE", sim.it_groesste, 6)
    z("F2_ABBRUECHE", sim.abbrueche, 6)
    z("F2_UAMAX", ua_max); z("F2_UAMIN", ua_min)
    z("F2_HUB", ua_max - ua_min)
    z("F2_AVGROSS", (ua_max - ua_min) / (2.0 * US))
    z("F2_AVOBEN", oben / US); z("F2_AVUNTEN", unten / US)
    z("F2_HUBOBEN", oben); z("F2_HUBUNTEN", unten)
    z("F2_UNSYM", 100.0 * (oben - unten) / (0.5 * (oben + unten)))
    z("F2_UNTERSCHIED", 100.0 * ((ua_max - ua_min) / (2.0 * US) - abs(av)) / abs(av))
    z("F2_UCMITTEL", uc_mit)
    z("F2_UCVERSCHIEBUNG", uc_mit - m1["u_ce"], 8)
    # Verschiebung und Drift sind DIFFERENZEN zweier fast gleicher Zahlen: ihre
    # Genauigkeit ist durch die Abbruchschranke tol_u = 1e-9 V seines Newton
    # begrenzt. Sie werden deshalb mit 8 gueltigen Stellen gedruckt.
    # Periode zu Periode: steht der Arbeitspunkt?
    uc_vor = uu["c"][-2 * per:-per]
    z("F2_PERIODENDRIFT", uc_mit - float(uc_vor.mean()), 8)

    print()
    print("=" * 74)
    print("  FALL 3 — seine B4-Bruecke, woertlich aus bruecke.netz")
    print("=" * 74)
    print(BRUECKE)
    sb = Simulator(BRUECKE, dt=BR_DT)
    tb, ub = sb.lauf(BR_ENDE)
    perb = int(round((1.0 / BR_F) / BR_DT))
    K4 = ub["K4"][-perb:]          # Kondensatorknoten
    K1 = ub["K1"][-perb:]          # Brueckeneingang a
    K3 = ub["K3"][-perb:]          # Brueckenausgang P
    K5 = ub["K5"][-perb:]          # Quellknoten
    D = MODELLE["1N4148"]
    iD1 = np.array([D.strom(a - b) for a, b in zip(K1, K3)])
    iQ = (K5 - K1) / 1.0           # Ri = 1 Ohm, also zugleich der Quellstrom
    z("B_UC_MITTEL", float(K4.mean()))
    z("B_UC_MAX", float(K4.max()))
    z("B_UC_MIN", float(K4.min()))
    z("B_BRUMM", float(K4.max() - K4.min()))
    z("B_BRUMM_PROZ", 100.0 * float(K4.max() - K4.min()) / float(K4.mean()))
    z("B_IL_MITTEL", float(K4.mean()) / 100.0)
    z("B_ID1_SPITZE", float(iD1.max()))
    z("B_IQ_SPITZE", float(np.abs(iQ).max()))
    z("B_VERLUST", 30.0 - float(K4.max()))
    z("B_UC_ENDE", float(ub["K4"][-1]))
    z("B_SCHRITTE", sb.schritte, 6)
    z("B_NEWTON_MITTEL", sb.it_summe / sb.schritte, 6)
    z("B_NEWTON_GROESSTE", sb.it_groesste, 6)
    z("B_ABBRUECHE", sb.abbrueche, 6)

    print()
    print("=" * 74)
    print("  GEGENPROBE — seine Fixed-Bias-Netzliste mit dem BC547")
    print("=" * 74)
    # Genau bjt_fixedbias.netz aus DGL_Nichtlinear/Programme, woertlich.
    ng = ("V1  vcc 0     dc 25\n"
          "RB  vcc b     37275.390625\n"
          "RC  vcc c     100\n"
          "T1  c   b  0  BC547\n")
    print(ng)
    sg, mg, itg = arbeitspunkt(ng)
    z("FB_UBE", mg["u_be"]); z("FB_UBEEFF", mg["u_be_eff"])
    z("FB_UCE", mg["u_ce"]); z("FB_IB", mg["i_b"]); z("FB_IC", mg["i_c"])
    z("FB_BETAEFF", mg["beta_eff"])
    z("FB_NEWTON", itg, 6)
    print()
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
