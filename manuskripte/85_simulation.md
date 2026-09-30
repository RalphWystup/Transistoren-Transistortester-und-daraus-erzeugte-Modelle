---
title: "Kapitel 9 — Simulation mit den ermittelten Parametern"
subtitle: "Transistortechnik — von der Messung zum Modell"
author: "Prof. Dr.-Ing. Ralph Wystup"
lang: de
---

# 9 Simulation mit den ermittelten Parametern

## 9.1 Warum dieser Dreifachvergleich?

Die vorangegangenen Kapitel haben eine geschlossene Kette aufgebaut:
Kapitel 6 hat das Gummel-Poon-Modell mit seinen SPICE-Parametern
eingeführt, Kapitel 7 hat diese Parameter aus echten Messungen am
BC547 extrahiert, und Kapitel 8 hat gezeigt, wie das
Newton-Raphson-Verfahren aus Modell und Beschaltung den Arbeitspunkt
berechnet. Damit ist im Prinzip alles vorhanden, was ein
Schaltungssimulator braucht — denn nichts anderes tut ein Simulator:
Er löst die Modellgleichungen zusammen mit den Netzwerkgleichungen der
Schaltung, und zwar mit genau dem Verfahren, das wir in Kapitel 8 von
Hand implementiert haben.

Dieses Kapitel schließt den Kreis mit einem **Dreifachvergleich**.
Ein und dieselbe Aufgabe — die Arbeitspunkt-Einstellung eines
Transistors in Emitterschaltung — wird auf drei Wegen gelöst:

1. mit unserem **eigenen Python-Löser** (Newton-Raphson und
 Bisektion, wie in Kapitel 8 entwickelt),
2. mit **LTspice**, dem Industriestandard-Schaltungssimulator,
3. mit einem selbst aufgebauten **Simulink-Modell**, das die
 Gummel-Poon-Gleichungen als Blockschaltbild nachbildet.

Wenn drei unabhängige Implementierungen — eigener Code, kommerzieller
Simulator, grafische Modellierung — auf dieselben Zahlen führen,
haben wir zweierlei gewonnen: Vertrauen in unsere eigene Rechnung und
ein tiefes Verständnis dafür, was der Simulator „unter der Haube"
tatsächlich tut. Der Simulator verliert seinen Black-Box-Charakter.

## 9.2 Die Testschaltung und die Aufgabe

Als Testschaltung dient die Emitterschaltung mit Basisvorwiderstand
(Fixed Bias) aus Kapitel 8:

* Versorgungsspannung $V_{CC} = 25\,\mathrm{V}$, wobei die Basis über
 $R_B$ ebenfalls aus $V_{CC}$ versorgt wird ($V_{BB} = V_{CC}$),
* Kollektorwiderstand $R_C = 100\,\Omega$,
* Basiswiderstand $R_B$: **gesucht**.

Die Entwurfsaufgabe lautet: $R_B$ ist so zu bestimmen, dass der
Arbeitspunkt in der Mitte der Lastgeraden liegt,

$$V_{CE} \overset{!}{=} \frac{V_{CC}}{2} = 12{,}5\,\mathrm{V},$$

denn dort ist die symmetrische Aussteuerbarkeit des späteren
Verstärkers am größten. Als Toleranz sind $\pm 5\,\%$ zugelassen.

Der Transistor wird durch die Gummel-Poon-Gleichungen beschrieben,
in zwei Ausbaustufen, die wir aus Kapitel 6 kennen:

**Einfaches Modell** (Shockley-Kern mit Early-Effekt):

$$I_C = I_S \, e^{\,V_{BE}/(n V_T)} \left(1 + \frac{V_{CE}}{V_A}\right),
\qquad
I_B = \frac{I_S}{\beta_F} \, e^{\,V_{BE}/(n V_T)}$$

**Erweitertes Modell** (zusätzlich Hochstrom-Abfall, Basis-Early-Effekt
und interner Basiswiderstand):

$$\beta_{\mathrm{eff}} = \frac{\beta_F}{\sqrt{1 + I_C/I_{KF}}},
\qquad
V_{BE,\mathrm{eff}} = V_{BE} - I_B \, R_{B,\mathrm{int}},$$

$$I_B = \frac{I_S}{\beta_{\mathrm{eff}}}
 \, e^{\,V_{BE,\mathrm{eff}}/(n V_T)}
 \left(1 + \frac{V_{CE}}{V_{AB}}\right),
\qquad
I_C = I_S \, e^{\,V_{BE,\mathrm{eff}}/(n V_T)}
 \left(1 + \frac{V_{CE}}{V_A}\right)$$

Die Zahlenwerte sind die didaktischen Modellwerte aus dem
Vorlesungsmanuskript — bewusst runde Werte, damit die Rechnung
nachvollziehbar bleibt:

| Parameter | SPICE-Name | Wert | Bedeutung |
|---|---|---|---|
| $I_S$ | IS | $10^{-13}\,$A | Sättigungsstrom |
| $\beta_F$ | BF | 200 | Vorwärts-Stromverstärkung |
| $n$ | NF | 1 | Emissionskoeffizient |
| $V_A$ | VAF | 100 V | Early-Spannung (Kollektor) |
| $V_{AB}$ | VAR | 200 V | Early-Spannung (Basis), nur erweitert |
| $I_{KF}$ | IKF | 0,5 A | Kniestrom des $\beta$-Abfalls, nur erweitert |
| $R_{B,\mathrm{int}}$ | RBM | 10 $\Omega$ | interner Basiswiderstand, nur erweitert |

Die Thermospannung beträgt $V_T = k_B T / q = 25{,}86\,\mathrm{mV}$
bei $T = 300\,\mathrm{K}$ — gerechnet, wie in den Python-Programmen,
mit den gerundeten Konstanten $k_B = 1{,}381\cdot 10^{-23}\,$J/K und
$q = 1{,}602\cdot 10^{-19}\,$C.

## 9.3 Weg 1: Der eigene Löser — Newton innen, Bisektion außen

### 9.3.1 Aufbau des Verfahrens

Die Struktur des Lösers folgt unmittelbar aus Kapitel 8. Für ein
**gegebenes** $R_B$ liefern Maschengleichungen und Modellgleichungen
das nichtlineare Gleichungssystem

$$F(V_{BE}, V_{CE}) =
\begin{pmatrix}
\dfrac{V_{BB} - V_{BE}}{R_B} - I_B(V_{BE}, V_{CE}) \\[2ex]
\dfrac{V_{CC} - V_{CE}}{R_C} - I_C(V_{BE}, V_{CE})
\end{pmatrix}
\overset{!}{=} \begin{pmatrix} 0 \\ 0 \end{pmatrix},$$

das mit dem zweidimensionalen **Newton-Raphson-Verfahren** und der
Jacobi-Matrix aus Kapitel 8 gelöst wird; Startwert ist wie dort
$[V_{BE}, V_{CE}] = [0{,}65\,\mathrm{V},\; V_{CC}/2]$.

Das gesuchte $R_B$ liegt aber noch nicht fest. Hier übernimmt — wie in
Kapitel 8 begründet — die **Bisektion die äußere Schleife**: Sie ist
nicht das Rechenverfahren des Buches (das ist Newton-Raphson), sondern
die robuste Absicherung der Suche über einen weiten Wertebereich. Der
Zusammenhang ist streng monoton und physikalisch anschaulich:

$$R_B \uparrow \;\Rightarrow\; I_B \downarrow \;\Rightarrow\;
I_C \downarrow \;\Rightarrow\; V_{CE} \uparrow$$

Damit funktioniert die Intervallhalbierung zuverlässig:

1. Startintervall $R_B \in [10\,\mathrm{k}\Omega,\; 500\,\mathrm{k}\Omega]$
2. Intervallmitte $R_{B,\mathrm{try}}$ bilden
3. Newton-Raphson löst den Arbeitspunkt für $R_{B,\mathrm{try}}$
4. $V_{CE} < V_{CC}/2$: Intervall-Untergrenze anheben;
 $V_{CE} > V_{CC}/2$: Obergrenze absenken
5. wiederholen, bis $V_{CE}$ im Toleranzband liegt

Ein Detail macht das Verfahren besonders effizient: Die
Newton-Lösung eines Bisektionsschritts dient als **Startwert des
nächsten** — die Arbeitspunkte benachbarter $R_B$-Werte liegen nahe
beieinander, und Newton konvergiert dann in immer weniger Schritten.

### 9.3.2 Das Protokoll der Rechnung

Der Lauf mit dem einfachen Modell ergibt:

| Schritt | $R_B$ [$\Omega$] | $V_{CE}$ [V] | Newton-Iterationen |
|---|---|---|---|
| 1 | 255 000,00 | 22,6595 | 6 |
| 2 | 132 500,00 | 20,5753 | 6 |
| 3 | 71 250,00 | 17,0196 | 6 |
| 4 | 40 625,00 | 11,6534 | 6 |
| 5 | 55 937,50 | 15,0119 | 5 |
| 6 | 48 281,25 | 13,5745 | 5 |
| 7 | **44 453,12** | **12,6885** | 4 |

und mit dem erweiterten Modell:

| Schritt | $R_B$ [$\Omega$] | $V_{CE}$ [V] | Newton-Iterationen |
|---|---|---|---|
| 1 | 255 000,00 | 22,9375 | 6 |
| 2 | 132 500,00 | 21,1267 | 6 |
| 3 | 71 250,00 | 18,0783 | 7 |
| 4 | 40 625,00 | 13,5360 | 8 |
| 5 | 25 312,50 | 7,8352 | 9 |
| 6 | 32 968,75 | 11,2630 | 8 |
| 7 | **36 796,88** | **12,5036** | 7 |

Ein Wort zu den auffälligen Nachkommastellen der Endwerte, denn sie
erklären, **was diese Zahlen eigentlich sind**: Die Bisektion kennt
nur Intervallmittelpunkte. Das Startintervall
$[10\,\mathrm{k}\Omega,\, 500\,\mathrm{k}\Omega]$ hat die Breite
$490\,\mathrm{k}\Omega$; nach $k$ Halbierungen liegen alle
erreichbaren Werte auf einem Raster der Schrittweite
$490\,000/2^k\;\Omega$. Im siebten Schritt beträgt dieses Raster
$490\,000/2^7 = 3\,828{,}125\,\Omega$, und die exakten Endwerte sind

$$R_B = 44\,453{,}125\,\Omega
\qquad\text{bzw.}\qquad
R_B = 36\,796{,}875\,\Omega$$

(in den Protokollen auf zwei Nachkommastellen gerundet angezeigt).
Die Bruchteile eines Ohms sind also **reine Halbierungsarithmetik**
und keine physikalische Genauigkeit: Das Toleranzband von
$\pm 5\,\%$ um $V_{CC}/2$ lässt ohnehin $\pm 625\,\mathrm{mV}$
Spielraum, und ein realer Widerstand würde als nächstliegender
Normwert der E-Reihe mit eigener Fertigungstoleranz gewählt. Für den
Vergleich mit LTspice wurden trotzdem bewusst die Rechenwerte
übernommen (auf ganze Ohm abgeschnitten) — denn nur wenn beide
Werkzeuge dasselbe $R_B$ verwenden, ist die Übereinstimmung der
Arbeitspunkte ein echter Test der Löser.

Abbildung 9.1 zeigt beide Läufe grafisch: Der $R_B$-Wert (blau)
halbiert sich Schritt für Schritt in das Ziel hinein, die zugehörige
Kollektor-Emitter-Spannung (rot) pendelt sich in das grau hinterlegte
Toleranzband um $V_{CC}/2$ ein. Nach sieben Schritten ist das Ziel
jeweils erreicht.

![Abbildung 9.1: Bisektionsverlauf für beide Modellstufen. Blau: der
untersuchte Basiswiderstand, rot: die von Newton-Raphson berechnete
Kollektor-Emitter-Spannung, grau: das Zielband
$V_{CC}/2 \pm 5\,\%$.](../bilder/kap09_bisektion.png)

### 9.3.3 Die Endergebnisse des eigenen Lösers

| Größe | einfaches Modell | erweitertes Modell |
|---|---|---|
| $R_B$ | 44 453 $\Omega$ | 36 797 $\Omega$ |
| $V_{BE}$ | 0,71687 V | 0,72389 V |
| $V_{BE,\mathrm{eff}}$ | — | 0,71729 V |
| $V_{CE}$ | 12,68847 V | 12,50358 V |
| $I_B$ | 0,5463 mA | 0,6597 mA |
| $I_C$ | 123,115 mA | 124,964 mA |
| $\beta$ am AP | 200 (konstant) | $\beta_{\mathrm{eff}}$ = 178,9 |

Abbildung 9.2 zeigt beide Arbeitspunkte im Kennlinienfeld: Die
Modellkennlinie $I_C(V_{CE})$ beim jeweiligen Basis-Emitter-Wert des
Arbeitspunktes schneidet die Lastgerade
$I_C = (V_{CC} - V_{CE})/R_C$ — der Schnittpunkt ist der
Arbeitspunkt, und er liegt in beiden Fällen wie gefordert nahe der
Mitte der Lastgeraden.

![Abbildung 9.2: Modellkennlinie, Lastgerade und berechneter
Arbeitspunkt für das einfache (links) und das erweiterte Modell
(rechts).](../bilder/kap09_kennlinie_ap.png)

Der Unterschied der beiden $R_B$-Werte ist kein Rechenfehler, sondern
Physik — und er ist erheblich: **17 Prozent**. Die Ursache liegt fast
vollständig beim Hochstrom-Parameter $I_{KF}$. Am Arbeitspunkt fließen
rund 125 mA; mit $I_{KF} = 0{,}5\,\mathrm{A}$ ist die
Stromverstärkung dort bereits auf

$$\beta_{\mathrm{eff}}
= \frac{200}{\sqrt{1 + 0{,}125/0{,}5}}
= 178{,}9$$

abgesunken (Abbildung 9.3). Für denselben Kollektorstrom wird also
mehr Basisstrom gebraucht — der Basiswiderstand muss entsprechend
kleiner ausfallen. Der interne Basiswiderstand wirkt in dieselbe
Richtung: Am Arbeitspunkt fallen an ihm
$I_B \cdot R_{B,\mathrm{int}} = 0{,}66\,\mathrm{mA} \cdot 10\,\Omega
\approx 6{,}6\,\mathrm{mV}$
ab, sodass die wirksame Basis-Emitter-Spannung um genau diesen Betrag
unter der äußeren liegt. Wer den Arbeitspunkt mit dem einfachen Modell
entwirft und die Schaltung dann mit einem realen Transistor aufbaut,
verfehlt das Ziel entsprechend — dieselbe Lehre, die uns in Kapitel 8
die 34-Prozent-Abweichung der idealen Schätzung eingebracht hat.

![Abbildung 9.3: Hochstrom-Abfall der Stromverstärkung nach dem
$I_{KF}$-Gesetz. Am Arbeitspunkt (125 mA) ist $\beta$ bereits von 200
auf 178,9 gefallen.](../bilder/kap09_beta_abfall.png)

## 9.4 Weg 2: LTspice

### 9.4.1 Von unseren Parametern zur .MODEL-Karte

In LTspice wird der Transistor durch eine Modellkarte beschrieben.
Unsere beiden Modellstufen lauten als SPICE-Karten — wörtlich so, wie
sie in den Simulationsschaltungen des Begleitmaterials stehen:

```
.MODEL simple_npn NPN(IS=1e-13 BF=200 NF=1 VAF=100)

.MODEL simple_npn NPN(IS=1e-13 BF=200 NF=1 VAF=100
+                     VAR=200 IKF=0.5 RB=10)
```

Das ist der entscheidende Punkt dieses Kapitels: **Die Parameter, die
wir in Kapitel 7 aus Messungen extrahiert und in Kapitel 6 verstanden
haben, sind exakt die Größen, die ein Simulator als Eingabe erwartet.**
Zwischen unserer Handrechnung und dem professionellen Werkzeug liegt
nur noch die Schreibweise.

### 9.4.2 Die Simulationsschaltungen

Das Begleitmaterial enthält vier LTspice-Schaltungen, die genau die
Kette dieses Buches abbilden:

| Schaltung | Modell | Inhalt |
|---|---|---|
| `Eigen_RW_1d.asc` | einfach | reine Arbeitspunktschaltung |
| `Eigen_RW_1e.asc` | erweitert | reine Arbeitspunktschaltung |
| `Eigen_RW_1c.asc` | einfach | Verstärker mit Signalquelle |
| `Eigen_RW_1f.asc` | erweitert | Verstärker mit Signalquelle |

Die Arbeitspunktschaltungen 1d und 1e bestehen aus der Versorgung
$V_1 = 25\,\mathrm{V}$, dem Kollektorwiderstand
$R_1 = 100\,\Omega$, dem Transistor mit der jeweiligen Modellkarte —
und dem Basiswiderstand $R_2$. Und hier zeigt sich der rote Faden
dieses Buches in seiner schönsten Form: In `Eigen_RW_1d` steht

$$R_2 = 44\,453\,\Omega,$$

in `Eigen_RW_1e` steht

$$R_2 = 36\,796\,\Omega.$$

Das sind die Ergebnisse unserer Bisektionsläufe aus Abschnitt 9.3
(44 453,12 $\Omega$ und 36 796,88 $\Omega$), übernommen mit
abgeschnittenen Nachkommastellen — die Abweichung liegt also unter
einem Ohm. Die Werte im Schaltplan wurden nicht geschätzt und nicht
aus einer Faustformel übernommen, sondern vom eigenen Python-Löser
berechnet und dann in LTspice eingetragen.
Der Simulator dient anschließend als unabhängige Kontrolle: Sein
eingebauter Newton-Löser (LTspice meldet im Protokoll wörtlich
„Direct Newton iteration for .op point succeeded") muss auf denselben
Arbeitspunkt kommen.

Abbildung 9.4 zeigt die Arbeitspunktschaltung, wie sie in der
Simulationsdatei steht:

![Abbildung 9.4: Die LTspice-Arbeitspunktschaltung `Eigen_RW_1d`
(nach der Original-Simulationsdatei gezeichnet): Fixed Bias mit dem
per Bisektion berechneten Basiswiderstand und der Modellkarte
`simple_npn`. Die Variante `Eigen_RW_1e` verwendet
$R_B = 36\,796\,\Omega$ und die erweiterte
Modellkarte.](../bilder/kap09_fixedbias_ltspice.png)

### 9.4.3 Der direkte Abgleich: zwei Löser, dieselbe Modellkarte

Die Modellkarte ist lesbar, die Schaltung ist bekannt — also lässt
sich der Abgleich vollständig durchrechnen. LTspice wertet die
Gummel-Poon-Gleichungen allerdings in der **SPICE-Konvention** aus,
die sich in drei Punkten von der anschaulichen Form unserer Kapitel
unterscheidet: Der Early-Effekt wird über die
Basis-Kollektor-Spannung geschrieben ($1 - V_{BC}/V_{AF}$ statt
$1 + V_{CE}/V_A$), der Hochstromeffekt $I_{KF}$ wirkt über die
normierte Basisladung $q_b$ direkt im **Kollektorstrom** (statt als
$\beta_{\mathrm{eff}}$ im Basisstrom), und gerechnet wird bei
$27\,^\circ\mathrm{C}$ mit exakten Naturkonstanten. Löst man die
Fixed-Bias-Schaltung mit den Widerständen **aus den Schaltplänen**
einmal mit den Buchgleichungen und einmal in der SPICE-Konvention
(Rechnung: `kap09_spice_abgleich.py`), ergibt sich:

**Einfaches Modell** (`Eigen_RW_1d`, $R_B = 44\,453\,\Omega$):

| Größe | Buchgleichungen | SPICE-Konvention | Abweichung |
|---|---|---|---|
| $V_{BE}$ | 0,71687 V | 0,71696 V | +0,01 % |
| $V_{CE}$ | 12,688 V | 12,759 V | +0,071 V |
| $I_B$ | 0,54627 mA | 0,54626 mA | $-$0,00 % |
| $I_C$ | 123,116 mA | 122,409 mA | $-$0,57 % |

**Erweitertes Modell** (`Eigen_RW_1e`, $R_B = 36\,796\,\Omega$):

| Größe | Buchgleichungen | SPICE-Konvention | Abweichung |
|---|---|---|---|
| $V_{BE}$ | 0,72389 V | 0,72844 V | +0,63 % |
| $V_{CE}$ | 12,503 V | 12,879 V | +0,376 V |
| $I_B$ | 0,65975 mA | 0,65963 mA | $-$0,02 % |
| $I_C$ | 124,967 mA | 121,206 mA | $-$3,01 % |

Das Ergebnis bestätigt den Abgleich — und es lehrt Maßhalten:

* **Beim einfachen Modell stimmen beide Löser auf ein halbes Prozent
 überein.** Die verbleibenden $-0{,}57\,\%$ in $I_C$ sind fast
 vollständig der Early-Konvention zuzuschreiben (Abschnitt 9.4.4,
 Punkt 4: erwartet waren $\approx V_{BE}/V_A = 0{,}7\,\%$, leicht
 gemildert durch den Thermospannungs-Effekt). Der Arbeitspunkt der
 Handrechnung ist damit durch den unabhängigen Simulator bestätigt.
* **Beim erweiterten Modell beträgt der Unterschied 3 %** — nicht
 wegen anderer Parameter (die Karte enthält exakt die Werte des
 Python-Programms), sondern wegen der Gleichungsform: Die
 Vorlesungsform setzt den $I_{KF}$-Abfall als
 $\beta_{\mathrm{eff}} = \beta_F/\sqrt{1 + I_C/I_{KF}}$ im
 Basisstrom an, SPICE dividiert stattdessen den Kollektorstrom
 durch die Basisladung $q_b$, in die $I_{KF}$, $V_{AF}$ und
 $V_{AR}$ gemeinsam eingehen. Bei $I_C \approx 125\,\mathrm{mA} =
 0{,}25\,I_{KF}$ macht diese Formulierungsfrage rund 3 % aus. Beide
 Formen beschreiben dieselbe Physik; die Vorlesungsform ist die
 anschauliche Näherung der SPICE-Ladungsformulierung.

Für die Praxis heißt das: Wer seinen eigenen Löser gegen einen
Simulator stellt, muss **Parameter und Gleichungsform** abgleichen —
gleiche Parameter allein garantieren erst Übereinstimmung im
Prozentbereich, gleiche Gleichungen dann Übereinstimmung bis auf
Rundung und Toleranzen.

### 9.4.4 Woher kommen die Abweichungen?

Ein Vergleich ist nur so viel wert wie das Verständnis seiner
Abweichungen. Deshalb gehen wir die Fehlerquellen einzeln durch und
geben jeweils die Größenordnung an — jede lässt sich aus den Zahlen
dieses Kapitels nachrechnen.

**1. Die Bisektionstoleranz (die größte gewollte Abweichung).**
Das Verfahren stoppt, sobald $V_{CE}$ im Toleranzband
$V_{CC}/2 \pm 5\,\%$ liegt — also irgendwo zwischen 11,875 V und
13,125 V. Beim einfachen Modell endet der Lauf bei
$V_{CE} = 12{,}69\,\mathrm{V}$, das sind 1,5 % über dem Idealwert;
beim erweiterten Modell landet der siebte Schritt zufällig fast exakt
auf dem Ziel (12,504 V). Diese Abweichung ist kein Fehler, sondern
die vereinbarte Genauigkeit: Wer sie verkleinern will, verschärft die
Toleranz und erhält weitere Bisektionsschritte.

**2. Das Abschneiden beim Übertrag nach LTspice (vernachlässigbar).**
Im Schaltplan stehen 44 453 statt 44 453,12 $\Omega$ und 36 796
statt 36 796,88 $\Omega$. Die Empfindlichkeit lässt sich direkt aus
den Protokolltabellen ablesen: Zwischen den letzten Bisektionsschritten
ändert sich $V_{CE}$ um rund 0,9 V je 3,8 k$\Omega$, also etwa
**0,25 mV pro Ohm**. Ein abgeschnittenes Ohm verschiebt den
Arbeitspunkt demnach um weniger als eine Millivolt-Viertel — drei
Größenordnungen unter der Bisektionstoleranz.

**3. Die Modellstufe (die größte physikalische Abweichung).**
Einfaches und erweitertes Modell unterscheiden sich im Ergebnis um
17 % in $R_B$. Die Ursachen — Hochstrom-Abfall der Stromverstärkung
($I_{KF}$), interner Basiswiderstand ($R_{B,\mathrm{int}}$) und
Basis-Early-Effekt ($V_{AB}$) — hat Abschnitt 9.3.3 quantifiziert.
Diese Abweichung ist die Kernaussage des Kapitels: Sie zeigt, welche
Parameter man nicht weglassen darf.

**4. Die SPICE-interne Early-Formulierung (Prozentbereich).**
SPICE schreibt den Early-Faktor über die Basis-Kollektor-Spannung,
$\left(1 - V_{BC}/V_{AF}\right)$, unsere Gleichungen über
$\left(1 + V_{CE}/V_A\right)$. Wegen $V_{BC} = V_{BE} - V_{CE}$
unterscheiden sich beide Faktoren am Arbeitspunkt um

$$\frac{V_{BE}}{V_A} = \frac{0{,}717\,\mathrm{V}}{100\,\mathrm{V}}
\approx 0{,}7\,\%$$

im Kollektorstrom; über die Lastgerade übersetzt sich das in
Verschiebungen von $V_{CE}$ in der Größenordnung von einem Zehntel
Volt. Deshalb erwarten wir von LTspice Übereinstimmung im
Prozentbereich, nicht auf die letzte Stelle.

**5. Die $q_b$-Formulierung des Hochstromeffekts (3 % beim
erweiterten Modell).** Wie der direkte Abgleich in Abschnitt 9.4.3
gezeigt hat, setzen Vorlesungsform ($\beta_{\mathrm{eff}}$ im
Basisstrom) und SPICE (Basisladung $q_b$ im Kollektorstrom) den
Parameter $I_{KF}$ an unterschiedlicher Stelle an. Bei
$I_C \approx 0{,}25\,I_{KF}$ macht das rund 3 % im Kollektorstrom
aus — die größte Konventionsabweichung des Vergleichs. Sie betrifft
nur das erweiterte Modell; im einfachen Modell existiert der Effekt
nicht.

**6. Thermospannungs-Konventionen (überraschend wichtig).**
Unser Löser und LTspice verwenden nicht exakt dieselbe
Thermospannung, aus zwei kleinen Gründen: Erstens rechnen die
Python-Programme mit $T = 300\,\mathrm{K}$, LTspice standardmäßig mit
$27\,^\circ\mathrm{C} = 300{,}15\,\mathrm{K}$ (+0,05 %). Zweitens
verwenden die Programme gerundete Naturkonstanten
($k_B = 1{,}381\cdot 10^{-23}$, $q = 1{,}602\cdot 10^{-19}$), deren
Quotient um $-0{,}035\,\%$ vom exakten Wert abweicht. Netto:
$V_T = 25{,}861\,\mathrm{mV}$ (unser Löser) gegenüber
$V_T = 25{,}865\,\mathrm{mV}$ (LTspice) — ein Unterschied von nur
0,016 %. Aber er steht im **Exponenten**: Bei festem $V_{BE}$ ändert
sich der Kollektorstrom um

$$\frac{\Delta I_C}{I_C}
\approx \frac{V_{BE}}{V_T}\cdot\frac{\Delta V_T}{V_T}
\approx 27{,}7 \cdot 0{,}00016 \approx 0{,}4\,\%.$$

Die Exponentialfunktion verstärkt winzige Konventionsunterschiede um
den Faktor $V_{BE}/V_T \approx 28$ — dieselbe Empfindlichkeit, die
uns in Kapitel 7 bei der $I_S$-Extraktion begegnet ist. Wer
Simulator und Handrechnung bis in die Nachkommastellen vergleichen
will, muss deshalb zuerst Temperatur und Konstanten abgleichen.

**7. Numerik (bedeutungslos).** Die Newton-Toleranz von $10^{-10}$
und die Maschinengenauigkeit liegen viele Größenordnungen unter allen
obigen Effekten.

Die Rangfolge ist damit klar: Modellstufe (17 %) $\gg$
Bisektionstoleranz (bis 5 %) $>$ $q_b$-Formulierung ($\approx$ 3 %,
nur erweitertes Modell) $>$ Early-Formulierung ($\approx$ 0,7 %)
$>$ Thermospannungs-Konventionen ($\approx$ 0,4 % in $I_C$) $\gg$
Übertrags-Rundung und Numerik. Wer diese Rangfolge kennt, weiß bei
jedem Vergleich zwischen Handrechnung und Simulator, welche
Abweichung normal ist — und welche auf einen echten Fehler deutet.

### 9.4.5 Ausblick: die Verstärkerschaltungen 1c und 1f

Die Schaltungen 1c und 1f erweitern die Arbeitspunktschaltung zum
vollständigen Verstärker: eine Sinusquelle
(100 mV Amplitude, 50 Hz) speist über einen Koppelkondensator
$C_1 = 0{,}5\,\mu\mathrm{F}$ in die Basis, ein zweiter
Koppelkondensator $C_2 = 1\,\mu\mathrm{F}$ führt das verstärkte
Signal auf den Lastwiderstand $R_5 = 1\,\mathrm{M}\Omega$; simuliert
wird das Zeitverhalten (`.tran 0.1`). Damit verlassen wir die reine
Gleichstromrechnung — die Frage, welche Spannungsverstärkung sich am
so eingestellten Arbeitspunkt ergibt und welche Rolle die
Koppelkondensatoren spielen, ist die Leitfrage der
Kleinsignalanalyse in Teil IV dieses Buches. Die beiden Schaltungen
stehen dort als Simulationsreferenz bereit.

## 9.5 Weg 3: Das Simulink-Modell

Der dritte Weg verzichtet auf jeden fertigen Schaltungssimulator und
baut die Modellgleichungen selbst auf — als Blockschaltbild in
Simulink (Abbildung 9.5). Das Modell implementiert exakt die
Gleichungen des erweiterten Modells aus Abschnitt 9.2; jede Formel
findet sich als Blockgruppe wieder:

![Abbildung 9.5: Das Gummel-Poon-Modell als Simulink-Blockschaltbild
(Bildschirmfoto aus dem Begleitmaterial). Links die implementierten
Gleichungen, rechts die Blockstruktur mit den beiden gesteuerten
Stromquellen an den Anschlüssen.](../bilder/kap09_simulink_modell.jpg)

* **Kollektorstrom-Pfad:** Die Klemmenspannung $V_{CE}$ läuft durch
 einen Verstärkungsblock $1/V_A$, ein Summierer bildet
 $1 + V_{CE}/V_A$; parallel dazu entsteht aus $V_{BE,\mathrm{eff}}$
 über den Block $1/(n V_T)$ und den Exponentialblock $e^u$ der
 Shockley-Kern. Ein Multiplizierer und die Verstärkung $I_S$ ergeben
 $I_C$ nach der Early-Gleichung.
* **Stromverstärkungs-Pfad:** Der berechnete Kollektorstrom wird über
 $1/I_{KF}$ zurückgeführt, ein Summierer bildet $1 + I_C/I_{KF}$,
 der Wurzelblock $\sqrt{u}$ und die Konstante $\beta_F$ liefern
 $\beta_{\mathrm{eff}}$ — die Rückkopplungsschleife im Diagramm ist
 wörtlich die implizite Kopplung, die wir in Kapitel 8 mit der
 Fixpunkt- bzw. Newton-Iteration aufgelöst haben.
* **Basisstrom-Pfad:** Aus $V_{BE}$ wird über den Block $R_B$ der
 Spannungsabfall $I_B \cdot R_{B,\mathrm{int}}$ abgezogen
 ($V_{BE,\mathrm{eff}}$-Definition), der Basis-Early-Faktor
 $1 + V_{CE}/V_{AB}$ entsteht über den Block $1/V_{AB}$, und
 zusammen mit $I_S/\beta_{\mathrm{eff}}$ ergibt sich $I_B$.
* **Anschluss an die Außenwelt:** Zwei **gesteuerte Stromquellen**
 prägen die berechneten Ströme $I_C$ und $I_B$ an den Klemmen ein —
 der Block verhält sich nach außen wie ein Transistor mit den
 Anschlüssen Kollektor, Basis und Emitter und kann in einer
 Simulink-Physical-Modeling-Schaltung genau wie das LTspice-Modell in
 die Fixed-Bias-Beschaltung eingebaut werden.

Was bei Simulink von außen zu sehen ist, macht sichtbar, was LTspice
im Inneren verbirgt: Ein „Transistormodell" ist nichts weiter als die
konsequente Verdrahtung einer Handvoll Gleichungen. Wer das
Blockschaltbild lesen kann, hat das Gummel-Poon-Modell verstanden —
und umgekehrt.

## 9.6 Zusammenfassung

* Ein Schaltungssimulator tut nichts Geheimnisvolles: Er löst die
 Gummel-Poon-Gleichungen zusammen mit den Netzwerkgleichungen — mit dem Newton-Raphson-Verfahren, das wir seit Kapitel 8 selbst
 beherrschen.
* Der eigene Löser bestimmt per Bisektion (äußere Schleife) und
 Newton-Raphson (innere Schleife) den Basiswiderstand für den
 Arbeitspunkt $V_{CE} = V_{CC}/2$: **44 453,12 $\Omega$** mit dem
 einfachen, **36 796,88 $\Omega$** mit dem erweiterten Modell. Diese
 Werte stehen — mit abgeschnittenen Nachkommastellen — in den
 LTspice-Vergleichsschaltungen des Begleitmaterials.
* Der Unterschied von 17 % zwischen beiden Modellstufen entsteht
 fast vollständig durch den Hochstrom-Abfall der Stromverstärkung
 ($\beta_{\mathrm{eff}} = 178{,}9$ statt 200 bei 125 mA) — wer die
 erweiterten Parameter ignoriert, verfehlt den Arbeitspunkt.
* Der direkte Abgleich mit denselben Modellkarten bestätigt die
 Handrechnung: Beim einfachen Modell stimmen Buchgleichungen und
 SPICE-Konvention auf ein halbes Prozent überein
 ($V_{CE}$ 12,688 V gegenüber 12,759 V); beim erweiterten Modell
 bleibt eine erklärbare 3-%-Differenz, weil SPICE den
 $I_{KF}$-Effekt über die Basisladung $q_b$ im Kollektorstrom
 ansetzt, die Vorlesungsform als $\beta_{\mathrm{eff}}$ im
 Basisstrom.
* Die Rangfolge der Abweichungsquellen — Modellstufe,
 Bisektionstoleranz, Gleichungskonventionen, Thermospannung — macht
 jeden Vergleich zwischen Handrechnung und Simulator bewertbar.
* Das Simulink-Blockschaltbild macht die Modellgleichungen sichtbar:
 Exponentialblock, Early-Faktoren, $\beta$-Rückkopplung und zwei
 gesteuerte Stromquellen — mehr ist ein Transistormodell nicht.

Damit ist der Bogen von Teil III geschlossen: von der Messung
(Kapitel 7) über das Modell (Kapitel 6) und die eigene numerische
Lösung (Kapitel 8) bis zur professionellen Simulation (dieses
Kapitel). Teil IV wechselt nun die Perspektive: vom Großsignal- zum
Kleinsignalverhalten — was passiert, wenn wir den sorgfältig
eingestellten Arbeitspunkt mit einem kleinen Signal auslenken?
