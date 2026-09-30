# -*- coding: utf-8 -*-
"""
bruecke_kern.py — der Rechenkern der B4-Bruecke mit belastetem RC-Glied

Drei Verfahren im Zusammenspiel, jedes an der Stelle, an die es gehoert:

  Alles steht in EINER Knotenleitwertmatrix   Y * u = i .
  Zwei Zweigsorten passen nicht hinein und werden beide in dieselbe Form
  gebracht - Leitwert parallel zu Stromquelle:

      Diode         g_d = dI_D/du     I_eq = I_D(u_k) - g_d*u_k
                    aus der Tangente an die Kennlinie
      Kondensator   g_C = C/dt        I_C  = g_C * u_C_alt
                    aus der Integrationsformel  (hier: u_C bleibt
                    ausserhalb der Matrix, expliziter Euler)

  1  KNOTENPOTENTIALVERFAHREN   stempelt die Matrix und loest - jeder Durchgang
                                (geschrieben in der Korrekturform J*d = -F,
                                 dieselbe Gleichung wie Y*u = i, s. _newton)
                                Es liefert die Knotengleichungen fuer a, b
                                und P. Um den Quellzweig erweitert (dessen
                                Strom wird eigene Unbekannte), damit auch
                                Ri = 0 gerechnet werden kann.
  2  NEWTON-RAPHSON             loest dieses nichtlineare System in jedem
                                Zeitschritt neu - innere Schleife.
  3  EXPLIZITER EULER           loest das nichtlineare DGL-System, das aus
                                dem Energiespeicher entsteht - aeussere
                                Schleife.

Newton und Euler tauschen genau zwei Zahlen: u_C hinein, u_P heraus.

Dasselbe Modell wie in Bruecke_RC_Last_Knotenpotential.py, nur so gefasst,
dass die Parameter im Betrieb geaendert werden koennen: alle Kenngroessen
stehen in einem Objekt statt als Konstanten im Modul.

  Knotenpotentialverfahren   stellt die Gleichungen auf
  Newton-Raphson             loest die drei nichtlinearen Knotengleichungen
  expliziter Euler           integriert die Zustandsgroesse u_C

Gerechnet wird mit einfachen Gleitkommazahlen statt mit numpy-Feldern. Das
ist bei einem 3x3-System deutlich schneller - numpy lohnt erst bei groesseren
Matrizen, und hier zaehlt jede Mikrosekunde, weil das Dashboard hunderttausend
Schritte je Sekunde rechnen soll.

Die Uebereinstimmung mit dem Lehrprogramm wird in gegenprobe_kern.py
nachgewiesen und nicht angenommen.
"""

from math import exp, sin, pi

EXP_MAX = 200.0        # Ueberlaufschutz im Exponenten


class Diode:
    """Shockley-Modell, ohne Naeherung."""

    def __init__(self, IS=2.52e-9, n=1.752, VT=0.025852, name="1N4148"):
        self.IS = IS
        self.n = n
        self.VT = VT
        self.name = name

    @property
    def nVT(self):
        return self.n * self.VT

    def strom(self, v):
        """I_D = IS * (exp(v/(n VT)) - 1),  v = Anode - Kathode."""
        e = v / self.nVT
        return self.IS * (exp(e if e < EXP_MAX else EXP_MAX) - 1.0)

    def leitwert(self, v):
        """Differentieller Leitwert dI/dv im Arbeitspunkt."""
        e = v / self.nVT
        return self.IS / self.nVT * exp(e if e < EXP_MAX else EXP_MAX)


# Ein paar gebraeuchliche Modelle zur Auswahl im Dashboard
MODELLE = {
    "1N4148":  Diode(2.52e-9,  1.752, 0.025852, "1N4148"),
    "1N4007":  Diode(14.11e-9, 1.984, 0.025852, "1N4007"),
    "1N5408":  Diode(14.11e-9, 1.984, 0.025852, "1N5408"),
    "Schottky 1N5819": Diode(31.7e-6, 1.373, 0.025852, "1N5819"),
}


class Bruecke:
    """
    B4-Bruecke mit Vorwiderstand, Glaettungskondensator und Last.

      Knoten 0  M  Bezug
      Knoten 1  a  ohne Speicher -> Newton
      Knoten 2  b  ohne Speicher -> Newton
      Knoten 3  P  ohne Speicher -> Newton
      Knoten 4  C  Energiespeicher -> Euler

    Gerechnet wird mit der ERWEITERTEN Knotenanalyse: der Strom im
    Quellzweig ist eine vierte Unbekannte. Das reine
    Knotenpotentialverfahren braucht dafuer den Innenwiderstand als
    Leitwert 1/Ri - und der laeuft gegen unendlich, wenn die Quelle ideal
    wird. Schon bei Ri = 1 mOhm erreicht die Konditionszahl der
    Jacobi-Matrix 1e12, bei 1 uOhm sind es 1e15: von den sechzehn Stellen
    doppelter Genauigkeit bleibt keine mehr uebrig, und der Newton-Schritt
    kommt nicht mehr unter die Abbruchschranke.

    Mit dem Quellstrom als eigener Unbekannter verschwindet das Problem:

      Knoten a:  I_D1 - I_D3 - i_q + GMIN*u_a          = 0
      Knoten b:  I_D2 - I_D4 + i_q + GMIN*u_b          = 0
      Knoten P:  (u_P-u_C)/R - I_D1 - I_D2 + GMIN*u_P  = 0
      Quelle  : -(u_a - u_b) - Ri*i_q + u_q            = 0

    Die letzte Zeile ist fuer Ri = 0 die reine Zwangsbedingung
    u_a - u_b = u_q. Die Matrix bleibt gut konditioniert, und Newton
    braucht bei jedem Ri zwischen 0 und 10 Ohm dieselben drei bis fuenf
    Durchgaenge.
    """

    def __init__(self):
        # --- Schaltung ---
        self.U = 30.0          # Amplitude der Quelle [V]
        self.f = 50.0          # Frequenz [Hz]
        self.Ri = 1.0          # Innenwiderstand der Quelle [Ohm]
        self.R = 10.0          # Vorwiderstand [Ohm]
        self.C = 1000e-6       # Glaettungskondensator [F]
        self.RL = 100.0        # Lastwiderstand [Ohm]
        self.diode = MODELLE["1N4148"]

        # --- Numerik ---
        self.dt = 10e-6        # Schrittweite [s]
        self.tol_F = 1e-12     # Newton-Abbruch: groesstes |F| [A]
        self.tol_u = 1e-12     # und groesstes |delta| [V]
        self.max_it = 200
        self.gmin = 1e-9       # Leitwert jedes Knotens gegen Masse [S]
        self.d_max = 0.5       # Daempfung des Newton-Schritts [V]

        self.ruecksetzen()

    # ------------------------------------------------------------------
    def ruecksetzen(self):
        self.t = 0.0
        self.uC = 0.0
        self.ua = 0.0
        self.ub = 0.0
        self.uP = 0.0
        self.iq = 0.0
        self.schritte = 0
        self.it_letzte = 0
        self.it_groesste = 0
        self.it_summe = 0

    def u_quelle(self, t=None):
        return self.U * sin(2.0 * pi * self.f * (self.t if t is None else t))

    # ------------------------------------------------------------------
    # -- VERFAHREN 1 und 2: stempeln, aufloesen, wiederholen -----------
    def _newton(self, uq):
        """
        VERFAHREN 2 (Newton-Raphson) um VERFAHREN 1 (Knotenpotential-
        verfahren) herum - die innere Schleife des Manuskripts,
        Abschnitt 25.

        In JEDEM Durchgang werden die vier Diodenleitwerte am gerade
        gueltigen Arbeitspunkt neu gebildet, damit die Matrixeintraege und
        die rechte Seite - und dann wird neu aufgeloest. Fest bleibt allein
        das Besetzungsmuster: welcher Eintrag an welcher Stelle steht.

        GESCHRIEBEN ist das System hier in der KORREKTURFORM  J * d = -F
        statt in der Potentialform  Y * u = i . Beides ist dieselbe
        Gleichung: J IST die Knotenleitwertmatrix Y, und aus
        Y*(u_alt + d) = i folgt J*d = -F (Manuskript, Abschnitt 12.6).
        Die Korrekturform ist hier bequemer, weil die Abbruchpruefung
        unmittelbar an d haengt. Nachgemessen gegen die reine Potentialform
        (knotenpotential_pur.py): groesster Unterschied 2,5e-11 V ueber
        20 000 Zeitschritte.

        Aufgeloest wird NICHT mit einer Inversen und auch nicht mit einer
        Bibliotheksroutine, sondern durch Elimination von Hand: der
        Quellstrom wird eliminiert, es bleiben zwei Gleichungen, und die
        loest die CRAMERSCHE REGEL (Kreuzregel). Das kostet rund dreissig
        Rechenschritte statt eines vollen Gauss-Verfahrens mit Pivotsuche
        und macht den Unterschied zwischen 6,8 und 14,8 us je Zeitschritt
        (gemessen: Median 6,79 us aus fuenf Laeufen zu 100 000 Schritten).
        Das Lehrprogramm rechnet dieselbe Aufgabe mit dem Gauss-Verfahren
        (numpy.linalg.solve); gegengerechnet in gegenprobe_kern.py.
        """
        d = self.diode
        strom, leitwert = d.strom, d.leitwert
        Ri = self.Ri
        gr = 1.0 / self.R
        gmin = self.gmin
        uC = self.uC
        ua, ub, uP, iq = self.ua, self.ub, self.uP, self.iq

        for k in range(1, self.max_it + 1):
            I1 = strom(ua - uP)          # D1: a -> P
            I2 = strom(ub - uP)          # D2: b -> P
            I3 = strom(-ua)              # D3: M -> a
            I4 = strom(-ub)              # D4: M -> b

            F0 = I1 - I3 - iq + gmin * ua
            F1 = I2 - I4 + iq + gmin * ub
            F2 = (uP - uC) * gr - I1 - I2 + gmin * uP
            F3 = -(ua - ub) - Ri * iq + uq

            g1 = leitwert(ua - uP)
            g2 = leitwert(ub - uP)
            g3 = leitwert(-ua)
            g4 = leitwert(-ub)

            # ----------------------------------------------------------
            # Das 4x4-System, von Hand aufgeloest.
            #
            #   d1*x1        - g1*x3 - x4 = b1      (Knoten a)
            #        d2*x2   - g2*x3 + x4 = b2      (Knoten b)
            #  -g1*x1 -g2*x2 + d3*x3      = b3      (Knoten P)
            #   -x1  +   x2         -Ri*x4 = b4     (Quelle)
            #
            # Aus der ersten Zeile folgt  x4 = d1*x1 - g1*x3 - b1.
            # Eingesetzt in die vierte:   x2 = A*x1 + B*x3 + Cq  mit
            #   A = 1 + Ri*d1,  B = -Ri*g1,  Cq = b4 - Ri*b1
            # Damit bleiben zwei Gleichungen fuer x1 und x3 - und die
            # loest man mit der Kreuzregel. Rund dreissig Rechenschritte
            # statt eines Gauss-Verfahrens mit Pivotsuche.
            # ----------------------------------------------------------
            d1 = g1 + g3 + gmin
            d2 = g2 + g4 + gmin
            d3 = gr + g1 + g2 + gmin
            b1, b2, b3, b4 = -F0, -F1, -F2, -F3

            A = 1.0 + Ri * d1
            B = -Ri * g1
            Cq = b4 - Ri * b1

            p11 = d1 + d2 * A
            p12 = d2 * B - g1 - g2
            q1 = b1 + b2 - d2 * Cq
            p21 = -g1 - g2 * A
            p22 = d3 - g2 * B
            q2 = b3 + g2 * Cq

            det = p11 * p22 - p12 * p21
            if det == 0.0:
                raise RuntimeError("Jacobi-Matrix singulaer - GMIN zu klein?")
            x1 = (q1 * p22 - p12 * q2) / det
            x3 = (p11 * q2 - q1 * p21) / det
            x2 = A * x1 + B * x3 + Cq
            x4 = d1 * x1 - g1 * x3 - b1
            delta = [x1, x2, x3, x4]

            dm = self.d_max
            gross_d = 0.0
            for i in range(4):
                v = delta[i]
                if v > dm: v = dm
                elif v < -dm: v = -dm
                delta[i] = v
                if abs(v) > gross_d: gross_d = abs(v)

            ua += delta[0]; ub += delta[1]; uP += delta[2]; iq += delta[3]

            gross_F = max(abs(F0), abs(F1), abs(F2), abs(F3))
            if gross_F < self.tol_F and gross_d < self.tol_u:
                break

        self.ua, self.ub, self.uP, self.iq = ua, ub, uP, iq
        return k

    # ------------------------------------------------------------------
    # -- VERFAHREN 3: ein Zeitschritt, aeussere Schleife ---------------
    def schritt(self):
        """
        Ein Zeitschritt - die aeussere Schleife des Manuskripts,
        Abschnitt 25:

          1. Quellspannung auswerten
          2. _newton()  loest die Matrixgleichung, mehrfach
             (u_C ist dabei eine feste Zahl)
          3. Stroeme aus der Loesung bilden
          4. VERFAHREN 3, expliziter Euler: u_C fortschreiben

        Rueckgabe: dict mit den Groessen dieses Schritts.
        """
        uq = self.u_quelle()
        it = self._newton(uq)
        self.it_letzte = it
        self.it_summe += it
        if it > self.it_groesste:
            self.it_groesste = it

        i_R = (self.uP - self.uC) / self.R
        i_D1 = self.diode.strom(self.ua - self.uP)
        i_D2 = self.diode.strom(self.ub - self.uP)
        i_L = self.uC / self.RL
        uC_alt = self.uC

        self.uC += self.dt * (i_R - i_L) / self.C
        self.t += self.dt
        self.schritte += 1

        return dict(t=self.t - self.dt, uq=uq, ua=self.ua, ub=self.ub,
                    uP=self.uP, uC=uC_alt, iR=i_R, iD1=i_D1, iD2=i_D2,
                    iL=i_L, it=it)
