---
title: "Die Emitterschaltung als Vierpol-Kette"
subtitle: "Vom Kurventracer über Arbeitspunkt und h-Parameter zur Kettenmatrix – Dokumentation zu bjt_verstaerker.py, mit allen Herleitungen und Zahlen zum Nachrechnen von Hand"
author: "Prof. Dr.-Ing. Ralph Wystup M.Sc."
date: "Stand: 27. Juli 2026"
lang: de
---

> **Autor:** Prof. Dr.-Ing. Ralph Wystup M.Sc. · **Vorlesungsmanuskript zur Transistortechnik**

# 1. Überblick

Dieses Manuskript beschreibt vollständig, wie das Programm `bjt_verstaerker.py`
eine Transistor-Emitterschaltung berechnet – vom gemessenen Transistor bis zu
Eingangswiderstand, Ausgangswiderstand und Verstärkung. Der Rechenweg folgt
der klassischen Vierpoltheorie in fünf Schritten:

1. Arbeitspunkt der Schaltung mit dem Newton-Raphson-Verfahren
2. h-Parameter durch Ableiten der gefitteten Kennliniengleichungen
3. Umrechnung aller Glieder in Kettenmatrizen (A-Parameter)
4. Kettenschaltung: Matrixmultiplikation zu einem Gesamtvierpol
5. Beschaltung mit Last R_L und Quelle R_i, daraus die Kenngrößen

Jeder Schritt wird hergeleitet und anschließend mit den Zahlen eines
konkreten Programmlaufs vorgerechnet, so dass sich jede Zeile mit dem
Taschenrechner nachprüfen lässt. Kapitel 2 stellt vorab die benötigten
Grundbegriffe der Vierpoltheorie zusammen; wer sie kennt, kann direkt bei
Kapitel 3 einsteigen.

## 1.1 Die Schaltung

```
                  +Vcc = 15 V
                   │        │
                  [Rb]     [Rc]          Rb = 510 kΩ (automatisch bestimmt)
                 510 kΩ    1 kΩ          Rc = 1 kΩ
                   │        │
                   │        ├────┤C├────o Ausgang ──[RL = 10 kΩ]── Masse
                   │        │ Koppel-C
                   │        │ C (Kollektor)
 ~ Uq ──[Ri]──┤C├──┴──── B ─┤   BC337-25
 Quelle 1 kΩ Koppel-C       │ E (Emitter)
                            │
                           Masse
```

Der Koppelkondensator liegt zwischen Quelle und Basisknoten; R_b greift
**hinter** dem Kondensator direkt am Basisknoten an. Nur so erreicht die
Gleichvorspannung die Basis, und die Quelle bleibt gleichstromfrei.

Der Emitter liegt direkt an Masse, die Basis wird über einen einzelnen
Widerstand R_b aus V_cc vorgespannt, Quelle und Last sind über
Koppelkondensatoren angeschlossen (für die Rechnung als ideal, d. h.
unendlich groß angenommen).

Für das Wechselsignal (Kleinsignal) gilt: Die Versorgung V_cc ist ein
Knoten ohne Spannungsänderung, also **wechselstrommäßig Masse**. Deshalb
wirken R_b und R_c im Kleinsignal-Ersatzbild als Querwiderstände von Basis
bzw. Kollektor nach Masse.

## 1.2 Vorgabewerte des Beispiellaufs

| Größe | Wert | Bedeutung |
|---|---|---|
| V_cc | 15 V | Versorgungsspannung |
| R_c | 1 kΩ | Kollektorwiderstand |
| R_b | 510 kΩ | Basiswiderstand (automatisch, siehe 4.6) |
| R_L | 10 kΩ | Lastwiderstand am Ausgang |
| R_i | 1 kΩ | Innenwiderstand der Signalquelle |
| V_BB | = V_cc | Basisspeisung aus V_cc |

# 2. Grundbegriffe der Vierpoltheorie

## 2.1 Was ist ein Vierpol?

Ein Vierpol (Zweitor) ist ein „schwarzer Kasten" mit zwei Klemmenpaaren:
Tor 1 (Eingang) und Tor 2 (Ausgang). Sein elektrisches Verhalten bei
kleinen Signalen ist vollständig durch **vier Zahlen** beschrieben, die
angeben, wie die vier Klemmengrößen U1, I1, U2, I2 zusammenhängen. Welche
zwei Größen man als „gegeben" und welche als „gesucht" auffasst, ist
Geschmackssache – und genau daraus entstehen die verschiedenen
Parameterdarstellungen.

## 2.2 Zählpfeile

Bei den symmetrischen Darstellungen (Y, Z, H) zeigen beide Ströme **in**
den Vierpol hinein. Bei der Kettendarstellung (A) benutzt man den
**Kettenpfeil**: I1 fließt in Tor 1 hinein, I2 fließt aus Tor 2 **heraus**
– weiter zum nächsten Glied. Dieser kleine Unterschied ist der Grund für
einige Minuszeichen bei den Umrechnungen; wer ihn übersieht, bekommt
falsche Vorzeichen.

## 2.3 Die wichtigsten Darstellungsformen

```
 Leitwertform (Y):        [I1]   [y11 y12] [U1]           beide Ströme aus
                          [I2] = [y21 y22]·[U2]           beiden Spannungen

 Hybridform (H):          [U1]   [h11 h12] [I1]           gemischt: I1 und U2
                          [I2] = [h21 h22]·[U2]           sind die Eingangsgrößen

 Kettenform (A):          [U1]   [A11 A12] [U2]           Eingangsgrößen aus
                          [I1] = [A21 A22]·[I2]           Ausgangsgrößen (I2 heraus!)
```

Alle Formen beschreiben denselben Vierpol und lassen sich ineinander
umrechnen (Standardtabellen; die hier benötigte Umrechnung H → A wird in
Kapitel 6 vollständig hergeleitet).

## 2.4 Welche Form für welche Zusammenschaltung?

Der ganze Reiz der Parameterformen liegt darin, dass jede Art, zwei
Vierpole zu verbinden, in genau einer Form trivial wird:

| Zusammenschaltung | Regel |
|---|---|
| Parallel-Parallel (beide Tore parallel) | Y-Matrizen **addieren** |
| Reihe-Reihe (beide Tore in Reihe) | Z-Matrizen **addieren** |
| Kette (Ausgang an Eingang des nächsten) | A-Matrizen **multiplizieren** |

Unsere Verstärkerstufe ist eine Kette: Basiswiderstand → Transistor →
Kollektorwiderstand. Deshalb wird alles in A-Parameter gewandelt und
multipliziert. Der Transistor selbst wird traditionell in der Hybridform
angegeben (h-Parameter, so stehen sie in Datenblättern und so misst man
sie am Kennlinienfeld) – daher die Kombination: **h messen, nach A
umrechnen, Kette multiplizieren.**

# 3. Das Transistormodell aus der Messung

Grundlage ist der mit dem Kurventracer vermessene BC337-25 (Dateien
`Ic_Vce.txt`, `Ic_Ib.txt`, `Ic_Vbe.txt`). An diese Messpunkte wurden die
Transistorgleichungen angepasst (Fit in `bjt_dashboard.py`); heraus kamen
sechs Modellzahlen:

| Parameter | Wert | Bedeutung |
|---|---|---|
| n | 1,004 | Emissionskoeffizient |
| I_S | 4,726·10⁻¹⁴ A | Sättigungssperrstrom |
| B_F | 249,9 | ideale Stromverstärkung |
| V_A | 146 V | Early-Spannung |
| I_KF | 0,9 A | Hochstrom-Knickpunkt |
| R_BB | 60 Ω | Basisbahnwiderstand |

Dazu die Temperaturspannung V_T = 25,852 mV (T = 300 K). Die gefitteten
Kennliniengleichungen lauten:

```
 Ic(Vbe, Vce) = IS · exp( Vbe / (n·VT) ) · (1 + Vce/VA)               (Gl. 1)

 Ib(Vbe, Vce) = (IS/Beff) · exp( (Vbe − Ib·RBB) / (n·VT) )            (Gl. 2)
                mit Beff = BF / sqrt(1 + Ic/IKF)
```

Gl. 2 ist implizit (Ib steht auf beiden Seiten wegen des Spannungsabfalls
am Basisbahnwiderstand) und wird im Programm durch wenige
Fixpunkt-Iterationen gelöst. Diese beiden Gleichungen SIND die Kennlinien –
nur als Formel statt als Punktetabelle. Die Messdateien werden im Programm
nur noch geladen, um im Diagramm die Messpunkte zur Kontrolle neben die
Modellkurve zu legen.

# 4. Schritt 1: Arbeitspunkt mit Newton-Raphson

## 4.1 Das Gleichungssystem

Gesucht ist das Wertepaar (V_BE, V_CE), bei dem die äußere Beschaltung und
der Transistor zusammenpassen. Zwei Maschengleichungen, jeweils gegen das
Modell gestellt (wie in `Transistor_20.py`):

```
 eq1(VBE, VCE) = (VBB − VBE)/Rb − Ib(VBE, VCE) = 0         (Basismasche)
 eq2(VBE, VCE) = (Vcc − VCE)/Rc − Ic(VBE, VCE) = 0         (Kollektormasche)
```

Anschaulich: eq1 vergleicht den Basisstrom, den der Widerstand R_b
„liefern kann", mit dem, den der Transistor bei dieser Spannung „haben
will" – im Arbeitspunkt sind beide gleich, der Fehler ist null. Ebenso eq2
für den Kollektorkreis.

## 4.2 Die Idee des Newton-Raphson-Verfahrens

In einer Dimension: Um die Nullstelle von f(x) zu finden, legt man im
aktuellen Schätzpunkt die Tangente an und geht dorthin, wo die Tangente
die Achse schneidet: x_neu = x − f(x)/f′(x). In zwei Dimensionen wird aus
der einen Ableitung die **Jacobi-Matrix** J (die vier partiellen
Ableitungen von eq1/eq2 nach V_BE und V_CE), und aus der Division wird das
Lösen eines linearen 2×2-Systems:

```
 J · delta = −F          dann         (VBE, VCE) := (VBE, VCE) + delta
```

F ist der Fehlervektor (eq1, eq2). Das wiederholt man, bis F praktisch
null ist. In der Nähe der Lösung konvergiert Newton quadratisch: Die Zahl
der richtigen Stellen verdoppelt sich etwa pro Schritt (in der
Iterationstabelle unten gut zu sehen).

## 4.3 Exkurs: zentrale Differenzen

Die Jacobi-Matrix wird numerisch gebildet, weil Gl. 2 implizit ist und
sich nicht bequem geschlossen ableiten lässt. Eine Ableitung wird dabei
durch eine **zentrale Differenz** angenähert – Funktion ein kleines Stück
links und rechts auswerten und die Sekantensteigung bilden:

```
 f'(x) ≈ [ f(x+d) − f(x−d) ] / (2d)
```

Zentral (links UND rechts) statt einseitig, weil sich dabei die
Krümmungsfehler beider Seiten wegheben – der Restfehler schrumpft mit d²
statt mit d. Dieselbe Technik wird in Kapitel 5 für die h-Parameter
benutzt (dort mit d = 0,1 mV bzw. 10 mV).

## 4.4 Dämpfung

Wegen der Exponentialfunktion in Gl. 1 kann ein voller Newton-Schritt weit
übers Ziel hinausschießen (30 mV mehr V_BE bedeuten schon Faktor ~3 im
Strom!). Deshalb wird der Schritt begrenzt: |ΔV_BE| ≤ 50 mV,
|ΔV_CE| ≤ 2 V. Das kostet im schlimmsten Fall ein paar Iterationen,
verhindert aber Zahlenüberläufe und Pendeln.

## 4.5 Die Iterationen des Beispiellaufs

Startwert (V_BE, V_CE) = (0,65 V, V_cc/2 = 7,5 V). Die Fehler eq1/eq2 sind
in Ampere angegeben:

| Iter. | ΔV_BE | ΔV_CE | → V_BE | → V_CE | eq1 | eq2 |
|---|---|---|---|---|---|---|
| Start | – | – | 0,6500 V | 7,5000 V | +1,4·10⁻⁵ | +3,8·10⁻³ |
| 1 | +27,67 mV | −0,212 V | 0,6777 V | 7,2883 V | −1,0·10⁻⁵ | −3,1·10⁻³ |
| 2 | −7,34 mV | −0,055 V | 0,6703 V | 7,2330 V | −1,1·10⁻⁶ | −4,0·10⁻⁴ |
| 3 | −1,06 mV | −0,060 V | 0,6693 V | 7,1734 V | −2,0·10⁻⁸ | −6,8·10⁻⁶ |
| 4 | −0,02 mV | −0,001 V | 0,6693 V | 7,1726 V | −6,7·10⁻¹² | −2,3·10⁻⁹ |
| 5 | ≈ 0 | ≈ 0 | 0,6693 V | 7,1726 V | < 10⁻¹⁸ | < 10⁻¹⁵ |

Man sieht die quadratische Konvergenz: Ab Iteration 2 fallen die Fehler
pro Schritt um mehrere Zehnerpotenzen. Nach fünf Korrekturschritten ist
Maschinengenauigkeit erreicht (das Programm zählt die abschließende
Kontrolle mit und meldet „6 Iterationen").

**Rückfallebene:** Konvergiert Newton nicht – das passiert genau dann,
wenn kein Arbeitspunkt im aktiven Bereich existiert, z. B. wenn die
Schaltung in die Sättigung geriete –, rechnet das Programm mit einer
verschachtelten Bisektion weiter (Intervall immer halbieren; langsam, aber
unfehlbar) und warnt, falls V_CE < 0,3 V herauskommt.

## 4.6 Automatische Bestimmung von R_b

Bei der Einstellung `R_B = None` legt das Programm den Arbeitspunkt auf
V_CE = V_cc/2 (maximale symmetrische Aussteuerbarkeit) und rechnet die
Kette einfach rückwärts – hier ist kein Gleichungssystem nötig, weil
V_CE ja vorgegeben wird:

```
 VCE = 7,5 V   →   Ic = (15 − 7,5)/1 kΩ = 7,5 mA          (Kollektormasche)
               →   VBE aus Gl. 1 auflösen: VBE = 668,1 mV
               →   Ib aus Gl. 2:           Ib = 26,93 µA
               →   Rb = (VBB − VBE)/Ib = (15 − 0,6681)/26,93 µA = 532,1 kΩ
               →   nächster E24-Normwert: 510 kΩ
```

Mit dem realen Normwert 510 kΩ (statt 532 kΩ) wird der Arbeitspunkt dann
noch einmal exakt gelöst (das ist die Iterationstabelle oben). Ergebnis:

| Größe | Wert |
|---|---|
| V_BE | 669,3 mV |
| I_B | 28,10 µA |
| V_CE | 7,17 V |
| I_C | 7,83 mA |
| h_FE (Gleichstrom) | 279 |

## 4.7 Kontrolle von Hand

Beide Maschengleichungen lassen sich direkt nachrechnen:

```
 Basismasche:         Ib = (15 V − 0,6693 V) / 510 kΩ = 28,1 µA      ✓
 Kollektormasche:     Ic = (15 V − 7,17 V) / 1 kΩ     = 7,83 mA      ✓
```

# 5. Schritt 2: h-Parameter durch Ableiten der Kennlinien

## 5.1 Definition

Der Transistor wird als Vierpol in Hybriddarstellung beschrieben
(Tor 1 = Basis-Emitter, Tor 2 = Kollektor-Emitter; Kleinsignalgrößen):

```
 [vbe]   [h11e     h12e]   [ib ]
 [ic ] = [h21e     h22e] · [vce]
```

| Parameter | Definition | Bedeutung |
|---|---|---|
| h11e | dVbe/dIb bei Vce = konst. | Eingangswiderstand |
| h12e | dVbe/dVce bei Ib = konst. | Spannungsrückwirkung |
| h21e | dIc/dIb bei Vce = konst. | Stromverstärkung |
| h22e | dIc/dVce bei Ib = konst. | Ausgangsleitwert |

## 5.2 Die vier Grundsteigungen

Die Modellgleichungen Gl. 1/Gl. 2 haben (Vbe, Vce) als unabhängige
Variablen. Zuerst werden deshalb die vier Grundsteigungen im Arbeitspunkt
gebildet – numerisch als zentrale Differenzen (Kapitel 4.3) mit den
Schrittweiten ΔVbe = 0,1 mV und ΔVce = 10 mV, z. B.:

```
 dIc/dVbe = [ Ic(VBE+0,1 mV, VCE) − Ic(VBE−0,1 mV, VCE) ] / 0,2 mV
```

Werte des Beispiellaufs:

```
 S1 = dIc/dVbe = 301,6 mS          S2 = dIc/dVce = 51,10 µS
 S3 = dIb/dVbe = 1,0210 mS         S4 = dIb/dVce = 0,769 nS
```

(Kontrolle: S1 ≈ Ic/(n·VT) = 7,83 mA / 25,96 mV = 301,6 mS ✓ und
S2 ≈ Ic/(VA + VCE) = 7,83 mA / 153,2 V = 51,1 µS ✓.)

## 5.3 Vom Spannungspaar zum h-Parameter: der Variablenwechsel

Nun der Übergang auf die h-Parameter. Das Problem: Die Modellgleichungen
liefern beide Ströme als Funktion der beiden **Spannungen** (Vbe, Vce). Die
h-Parameter sind aber andersherum definiert – dort sind **ib und vce** die
Eingangsgrößen und vbe, ic die Ergebnisse (erste Hybridgleichung:
vbe = h11·ib + h12·vce). Wir müssen also die Rollen tauschen; das ist mit
„Variablenwechsel" gemeint. Das geht in drei kleinen Schritten.

**Schritt A – Linearisieren.** Für kleine Abweichungen vom Arbeitspunkt ist
jede Stromänderung „Steigung mal Spannungsänderung", und die Beiträge
beider Spannungen addieren sich (nichts anderes besagt das totale
Differential):

```
 dIc = S1·dVbe + S2·dVce
 dIb = S3·dVbe + S4·dVce
```

**Schritt B – die zweite Zeile nach dVbe auflösen:**

```
 dVbe = (dIb − S4·dVce) / S3
```

Damit ist vbe durch ib und vce ausgedrückt – der Variablenwechsel ist
geschafft. Aus dieser Zeile lassen sich zwei h-Parameter direkt ablesen:

* h11e = dVbe/dIb bei festem vce (dVce = 0): dVbe = dIb/S3 → **h11e = 1/S3**
* h12e = dVbe/dVce bei festem ib (dIb = 0): dVbe = −(S4/S3)·dVce → **h12e = −S4/S3**

**Schritt C – dVbe in die erste Zeile einsetzen:**

```
 dIc = S1·(dIb − S4·dVce)/S3 + S2·dVce
     = (S1/S3)·dIb + (S2 − S1·S4/S3)·dVce
```

Ablesen wie oben: **h21e = S1/S3** und **h22e = S2 − S1·S4/S3**.

**Der Abzugsterm in h22e, mit Zahlen durchgespielt.** h22e fragt: Um wie
viel steigt Ic, wenn Vce um 1 V erhöht wird und Ib dabei festgehalten wird?

1. Erhöht man Vce um 1 V, würde Ib von allein um S4·1 V = 0,769 nA steigen.
2. Ib soll konstant bleiben – also muss Vbe geringfügig sinken, um
 0,769 nA / 1,021 mS = 0,753 µV. (Das ist genau h12e = −0,753 µV/V.)
3. Dieses Absenken von Vbe kostet Kollektorstrom:
 S1 · 0,753 µV = 301,6 mS · 0,753 µV = 0,23 µA.
4. Netto: dIc = 51,10 µA (direkter Early-Effekt) − 0,23 µA (Vbe-Korrektur)
 = 50,87 µA je Volt → h22e = 50,87 µS.

Der Abzugsterm ist also die Buchhaltung dafür, dass „Ib festhalten" ein
kleines Nachregeln von Vbe erzwingt, das auf Ic zurückwirkt.

## 5.4 Ergebnis

```
 h11e = 1/1,0210 mS                        = 979,5 Ω
 h21e = 301,6 mS / 1,0210 mS               = 295,4
 h12e = −0,769 nS / 1,0210 mS              = −7,53·10⁻⁷
 h22e = 51,10 µS − 301,6 mS·0,769 nS/1,0210 mS
      = 51,10 µS − 0,23 µS                 = 50,87 µS
```

Zusätzlich wird die Determinante der Hybridmatrix gebraucht:

```
 Dh = h11e·h22e − h12e·h21e
    = 979,5 · 50,87·10⁻⁶ − (−7,53·10⁻⁷)·295,4
    = 0,04983 + 0,00022 = 0,05005 ≈ 0,0501
```

Plausibilität: h11e ≈ n·VT/IB + RBB = 25,96 mV/28,1 µA + 60 Ω ≈ 984 Ω –
passt zur exakten Rechnung (979,5 Ω).

# 6. Schritt 3: Umrechnung in Kettenmatrizen (A-Parameter)

## 6.1 Definition der Kettenmatrix

```
 [U1]   [A11   A12]   [U2]
 [I1] = [A21   A22] · [I2]        I2 in Kettenpfeilrichtung (aus Tor 2 heraus)
```

Die Einheiten der vier Elemente sind verschieden: A11 und A22 sind
dimensionslos, A12 ist ein Widerstand (V/A), A21 ein Leitwert (A/V).

## 6.2 Vollständige Herleitung der Umrechnung h → A

Ausgangspunkt sind die beiden Hybridgleichungen des Transistors. Die
Zuordnung der Klemmengrößen: u1 = vbe, i1 = ib, u2 = vce. Beim Strom am
Tor 2 ist Vorsicht geboten: In der Hybridform fließt ic **in** den
Kollektor hinein, in der Kettenform fließt I2 **heraus** – also gilt
**ic = −I2**. Damit lauten die Hybridgleichungen:

```
 (H1)    u1 = h11·i1 + h12·u2
 (H2)   −I2 = h21·i1 + h22·u2
```

**Ziel:** u1 und i1 durch u2 und I2 ausdrücken – denn genau das tut die
Kettenmatrix.

**Aus (H2) den Eingangsstrom i1 freistellen:**

```
 h21·i1 = −I2 − h22·u2
     i1 = −(h22/h21)·u2 − (1/h21)·I2
```

Vergleich mit der zweiten Kettenzeile i1 = A21·u2 + A22·I2 liefert sofort:

```
 A21 = −h22/h21                 A22 = −1/h21
```

**i1 in (H1) einsetzen:**

```
 u1 = h11·[ −(h22/h21)·u2 − (1/h21)·I2 ] + h12·u2
    = (h12 − h11·h22/h21)·u2 − (h11/h21)·I2
```

Der Klammerausdruck lässt sich mit der Determinante Dh = h11·h22 − h12·h21
kompakt schreiben: h12 − h11·h22/h21 = −(h11·h22 − h12·h21)/h21 = −Dh/h21.
Vergleich mit der ersten Kettenzeile u1 = A11·u2 + A12·I2:

```
 A11 = −Dh/h21                  A12 = −h11/h21
```

**Zusammengefasst (die Standard-Umrechnungstabelle):**

```
         1    [ −Dh     −h11 ]
 A_T = ───── ·[                 ]
        h21   [ −h22    −1   ]
```

**Mit den Zahlen aus Kapitel 5, Element für Element:**

```
 A11 = −0,0501 / 295,4              = −1,6945·10⁻⁴     (dimensionslos)
 A12 = −979,5 Ω / 295,4             = −3,3159 Ω
 A21 = −50,87·10⁻⁶ S / 295,4        = −1,7223·10⁻⁷ S
 A22 = −1 / 295,4                   = −3,3854·10⁻³     (dimensionslos)
```

Die durchweg negativen Einträge sind kein Fehler – sie stammen aus dem
Vorzeichenwechsel ic = −I2 und tragen die Signalinvertierung der
Emitterschaltung durch die ganze weitere Rechnung.

## 6.3 Herleitung: Querwiderstand als reduzierter Vierpol

Ein Querwiderstand R liegt quer vom Signalknoten nach Masse; der
Längszweig ist einfach durchverbunden:

```
  Tor 1 o────────┬────────o Tor 2
                 │
                [R]
                 │
  Masse o────────┴────────o Masse
```

Die beiden Klemmengleichungen folgen direkt aus Maschen- und Knotenregel:

* **Spannung:** Beide Tore liegen am selben Knoten → u1 = u2.
* **Strom (Knotenregel am oberen Knoten):** Was bei Tor 1 hineinfließt,
 teilt sich auf in den Widerstandszweig (u2/R nach Masse) und den
 Weiterfluss zu Tor 2 → i1 = u2/R + I2.

In Matrixform, durch Vergleich mit der Kettendefinition:

```
 u1 = 1·u2 + 0·I2                     [ 1         0 ]
 i1 = (1/R)·u2 + 1·I2          →      [ 1/R       1 ]
```

Da V_cc wechselstrommäßig Masse ist (Kapitel 1.1), sind R_b (Basis→Vcc)
und R_c (Kollektor→Vcc) genau solche Querwiderstände – R_b am Eingangstor,
R_c am Ausgangstor:

```
 1/Rb = 1/510 kΩ = 1,961·10⁻⁶ S                   1/Rc = 1/1 kΩ = 1,000·10⁻³ S
```

**Zum Vergleich – die kleine Werkzeugkiste der Ketten-Vierpole:**

| Element | Kettenmatrix | Herleitung in Kurzform |
|---|---|---|
| Querwiderstand R | [1 0; 1/R 1] | u1=u2; i1 = u2/R + I2 |
| Längswiderstand R | [1 R; 0 1] | i1=I2; u1 = u2 + R·I2 |
| Koppelkondensator C (längs) | [1 1/(jωC); 0 1] | wie Längswiderstand mit Z = 1/(jωC) |

Ideale Koppelkondensatoren (C → ∞) haben Z → 0, ihre Matrix wird zur
Einheitsmatrix – deshalb tauchen sie in unserer Kette nicht auf.

# 7. Schritt 4: Kettenschaltung – warum multiplizieren, und die Rechnung

## 7.1 Warum ist die Kette ein Matrixprodukt?

Zwei Vierpole in Kette: Der Ausgang des ersten ist der Eingang des
zweiten. Genau dafür ist der Kettenpfeil gemacht: Die Ausgangsgrößen
(u2, I2) des ersten Glieds sind **identisch** mit den Eingangsgrößen
(u1, i1) des zweiten – gleiche Spannung am Verbindungsknoten, und der
herausfließende Strom des einen ist der hineinfließende des anderen.
Deshalb kann man einfach einsetzen:

```
 [u1]          [u2]          [u2]           [u_aus]
 [i1] = A¹ ·   [I2] = A¹ ·   [i1]' = A¹·A² ·[I_aus]
               (Glied 1)     (= Eingang Glied 2)
```

Die Gesamtmatrix ist das Produkt der Einzelmatrizen **in Signalrichtung**.
Achtung: Matrixmultiplikation ist nicht vertauschbar – die Reihenfolge
muss der physischen Reihenfolge der Glieder entsprechen.

## 7.2 Die Rechnung von Hand

Die Kette in Signalrichtung: Basiswiderstand → Transistor →
Kollektorwiderstand.

```
 A_ges = A_Rb · A_T · A_Rc
```

**Erste Multiplikation M = A_T · A_Rc** (Regel: Zeile mal Spalte):

```
 M11 = A11·1 + A12·(1/Rc) = −1,6945·10⁻⁴ + (−3,3159)·10⁻³ = −3,4854·10⁻³
 M12 = A11·0 + A12·1      = −3,3159
 M21 = A21·1 + A22·(1/Rc) = −1,7223·10⁻⁷ + (−3,3854·10⁻⁶) = −3,5576·10⁻⁶
 M22 = A21·0 + A22·1      = −3,3854·10⁻³
```

**Zweite Multiplikation A_ges = A_Rb · M:**

```
 A11' = 1·M11 + 0·M21 = −3,4854·10⁻³
 A12' = 1·M12 + 0·M22 = −3,3159
 A21' = (1/Rb)·M11 + M21 = 1,961·10⁻⁶·(−3,4854·10⁻³) + (−3,5576·10⁻⁶)
      = −6,8·10⁻⁹ − 3,5576·10⁻⁶ = −3,5645·10⁻⁶
 A22' = (1/Rb)·M12 + M22 = 1,961·10⁻⁶·(−3,3159) + (−3,3854·10⁻³)
      = −6,50·10⁻⁶ − 3,3854·10⁻³ = −3,3919·10⁻³
```

**Der zusammengefasste Vierpol der ganzen Verstärkerstufe:**

```
           [ −3,4854·10⁻³    −3,3159    ]
 A_ges =   [                            ]
           [ −3,5645·10⁻⁶    −3,3919·10⁻³ ]
```

Man sieht schön, wie klein der Einfluss von R_b ist: Er ändert nur die
zweite Zeile, und dort nur in der dritten bzw. zweiten Stelle.

# 8. Schritt 5: Beschaltung mit R_L und R_i – die Kenngrößen

Der Gesamtvierpol wird jetzt am Ausgang mit R_L = 10 kΩ belastet, am
Eingang speist eine Quelle mit Innenwiderstand R_i = 1 kΩ.

## 8.1 Herleitung: Eingangswiderstand, Spannungs- und Stromverstärkung

Der Lastwiderstand erzwingt am Tor 2 die Bedingung **u2 = R_L·I2** (I2
fließt aus dem Tor heraus durch R_L nach Masse; Ohmsches Gesetz). In die
Kettendefinition eingesetzt:

```
 u1 = A11·RL·I2 + A12·I2 = (A11·RL + A12)·I2
 i1 = A21·RL·I2 + A22·I2 = (A21·RL + A22)·I2
```

Alle Klemmengrößen sind jetzt Vielfache von I2 – die Verhältnisse folgen
durch einfaches Teilen:

```
 r_ein = u1/i1 = (A11·RL + A12) / (A21·RL + A22)
 A_v   = u2/u1 = RL·I2 / [(A11·RL + A12)·I2] = RL / (A11·RL + A12)
 A_i   = I2/i1 = 1 / (A21·RL + A22)
```

## 8.2 Herleitung: Ausgangswiderstand

Definition: Quelle „totlegen" (u_q = 0, ihr Innenwiderstand R_i bleibt in
der Schaltung), dann vom Ausgang hineinschauen: Testspannung u2 anlegen,
den hineinfließenden Strom messen. Der Strom, der in Tor 2 **hinein**
fließt, ist in Kettenpfeilrichtung −I2.

Am Eingangstor hängt jetzt nur noch R_i: Die Torspannung u1 treibt den
Strom u1/R_i durch den Widerstand nach Masse, und dieser Strom muss aus
dem Tor herauskommen – also i1 = −u1/R_i, umgestellt:

```
 u1 = −Ri·i1
```

Einsetzen der beiden Kettenzeilen:

```
 A11·u2 + A12·I2 = −Ri·(A21·u2 + A22·I2)
 u2·(A11 + Ri·A21) = −I2·(A12 + Ri·A22)
```

und damit:

```
 r_aus = u2/(−I2) = (A22·Ri + A12) / (A21·Ri + A11)
```

## 8.3 Gesamtverstärkung von der Quelle aus

Zwischen Leerlauf-Quellspannung u_q und Torspannung u1 liegt der
Spannungsteiler aus R_i und r_ein:

```
 u1 = u_q · r_ein/(r_ein + Ri)          →        A_vs = A_v · r_ein/(r_ein + Ri)
```

(Gleichwertig könnte man R_i als Längs-Vierpol [1 Ri; 0 1] vorn an die
Kette multiplizieren und A_vs direkt aus der erweiterten Matrix ablesen –
Ergebnis identisch.)

## 8.4 Einsetzen der Zahlen

```
 Zähler    Z = A11·RL + A12 = (−3,4854·10⁻³)(10⁴) + (−3,3159)
             = −34,854 − 3,316                     = −38,170
 Nenner    N = A21·RL + A22 = (−3,5645·10⁻⁶)(10⁴) + (−3,3919·10⁻³)
             = −35,645·10⁻³ − 3,392·10⁻³           = −39,037·10⁻³

 r_ein = Z/N = (−38,170)/(−0,039037)               = 977,8 Ω
 A_v   = RL/Z = 10⁴/(−38,170)                      = −262,0       (48,4 dB)
 A_i   = 1/N = 1/(−0,039037)                       = −25,6

 r_aus: Zähler    = A22·Ri + A12 = (−3,3919·10⁻³)(10³) − 3,3159 = −6,7078
        Nenner    = A21·Ri + A11 = (−3,5645·10⁻⁶)(10³) − 3,4854·10⁻³
                                 = −7,0499·10⁻³
          r_aus   = (−6,7078)/(−7,0499·10⁻³)       = 951,5 Ω

 A_vs = −262,0 · 977,8/(977,8 + 1000)              = −129,5       (42,2 dB)
```

## 8.5 Ergebnisübersicht und Deutung

| Kenngröße | Wert | Deutung |
|---|---|---|
| r_ein | 978 Ω | recht niederohmig – typisch für die Emitterschaltung; wird fast ganz vom Transistoreingang h11e bestimmt (R_b = 510 kΩ spielt parallel dazu kaum eine Rolle) |
| r_aus | 951 Ω | knapp unter R_c = 1 kΩ; der Kollektor selbst ist mit 1/h22e ≈ 20 kΩ viel hochohmiger, R_c dominiert die Parallelschaltung |
| A_v | −262 | Verstärkung von Basis zu Ausgang; das Minuszeichen ist die Signalinvertierung der Emitterschaltung |
| A_i | −25,6 | Stromverstärkung der ganzen Stufe; deutlich kleiner als h21e = 295, weil sich der Ausgangsstrom zwischen R_c und R_L teilt |
| A_vs | −129,5 | von der Quelle aus: an R_i = 1 kΩ geht gut die Hälfte der Quellspannung verloren, weil r_ein ähnlich groß ist |

## 8.6 Querkontrolle über die h-Parameter

Dieselben Größen lassen sich (mühsamer) auch direkt aus den h-Parametern
mit der Ersatzlast R_L' = R_c ∥ R_L = 909,1 Ω rechnen, z. B.:

```
 A_v = −h21e·RL' / (h11e + Dh·RL')
     = −295,4·909,1 / (979,5 + 0,0501·909,1)
     = −268 548 / 1025,0 = −262,0     ✓
```

Beide Wege liefern auf vier Stellen dasselbe – die Kettenrechnung ist also
konsistent.

# 9. Das Verfahren als Rezept (für beliebige Stufen)

So lässt sich jede lineare Verstärkerstufe von Hand rechnen:

1. Arbeitspunkt der Gleichstromschaltung bestimmen (Maschengleichungen
 gegen die Transistorgleichungen; Newton-Raphson oder Bisektion).
2. Die vier Grundsteigungen S1–S4 der Kennlinien im Arbeitspunkt bilden
 (analytisch oder als zentrale Differenzen).
3. Daraus die h-Parameter: h11 = 1/S3, h21 = S1/S3, h12 = −S4/S3,
 h22 = S2 − S1·S4/S3; Determinante Dh mitnotieren.
4. Kleinsignal-Ersatzschaltbild zeichnen: Versorgungsknoten zu Masse
 machen, ideale Koppel-C durch Kurzschlüsse ersetzen.
5. Jedes Glied als Kettenmatrix schreiben: Transistor mit der
 Umrechnung A = (1/h21)·[−Dh −h11; −h22 −1], Querwiderstand
 [1 0; 1/R 1], Längswiderstand [1 R; 0 1].
6. Matrizen in Signalrichtung multiplizieren → ein Gesamtvierpol A_ges.
7. Beschaltung ansetzen: r_ein = (A11·RL+A12)/(A21·RL+A22),
 r_aus = (A22·Ri+A12)/(A21·Ri+A11), A_v = RL/(A11·RL+A12),
 A_i = 1/(A21·RL+A22), A_vs = A_v·r_ein/(r_ein+Ri).
8. Plausibilität prüfen (z. B. Querrechnung über die h-Formeln mit RL' = Rc ∥ RL, Vorzeichen, Größenordnungen).

# 10. Zusammenfassung des Rechenwegs

```
  Messung (Kurventracer)          einmalig:
  Ic_Vce.txt, Ic_Ib.txt   ──Fit──► Modell P = (n, IS, BF, VA, IKF, RBB)
                                            │
  Schaltung Vcc, Rb, Rc   ──Newton-Raphson─┤ Arbeitspunkt (VBE, VCE, IB, IC)
                                            │
                         Ableiten (zentrale Differenzen) im Arbeitspunkt
                                            │
                               h-Vierpol [h11e h12e; h21e h22e]
                                            │
                                     h → A umrechnen
                                            │
                     A_ges = A_Rb · A_T · A_Rc    (Matrixprodukt)
                                            │
               Beschaltung: RL am Ausgang, Quelle mit Ri am Eingang
                                            │
                     r_ein, r_aus, A_v, A_i, A_vs
```

# 11. Programme und Dateien

| Datei | Rolle |
|---|---|
| `bjt_verstaerker.py` | das hier beschriebene Programm; Vorgaben V_CC, R_C, R_B (None = automatisch), R_L, R_I oben im Skript; erzeugt Konsolenprotokoll aller Schritte und das Dashboard `bjt_verstaerker.png` |
| `Transistor_20.py` | Ursprung des Newton-Raphson-Arbeitspunkts (vereinfachtes Modell) |
| `bjt_hparam.py` | Ursprung der h-Parameter-Bestimmung mit Tangenten-Diagrammen |
| `bjt_dashboard.py` | der Modell-Fit an die Kurventracer-Messungen (Quelle des Parametersatzes P) |
| `Ic_Vce.txt`, `Ic_Ib.txt`, `Ic_Vbe.txt` | Kurventracer-Rohdaten des BC337-25 |

Erweiterungen sind im Kettenbild einfach: Ein Basisspannungsteiler ersetzt
R_b durch R1 ∥ R2 (gleiche Quermatrix), ein Längswiderstand im Signalweg
bekommt die Matrix [1 R; 0 1], ein endlicher Koppelkondensator [1 1/(jωC);
0 1] (dann wird komplex gerechnet), und eine zweite Stufe wird als weitere
Matrizen hinten anmultipliziert – die fünf Schritte bleiben dieselben.
