---
title: "Kapitel 6 — Das Gummel-Poon-Modell und seine SPICE-Parameter"
subtitle: "Buchentwurf zur Freigabe · Teil III: Vom Messwert zum Modell"
author: "Prof. Dr.-Ing. Ralph Wystup"
date: "Entwurf, Stand 4. August 2026"
lang: de
---

# 6 Das Gummel-Poon-Modell und seine SPICE-Parameter

## 6.1 Wo wir stehen — und wohin dieses Kapitel führt

In Teil I haben wir den Transistor **vermessen**: Der Kennlinienschreiber
lieferte die Eingangs-, Übertragungs- und Ausgangskennlinien als
Zahlenkolonnen, und das Vierquadranten-Kennlinienfeld hat diese Daten
geordnet. In Teil II haben wir das **numerische Handwerkszeug**
erarbeitet: Wir können nichtlineare Gleichungen mit Newton-Raphson lösen
und ganze Netzwerke über das Knotenpotentialverfahren aufstellen — geübt
an der Diode, deren Exponentialkennlinie uns dort zum ersten Mal
begegnet ist.

Jetzt fügen sich beide Stränge zusammen. Die Messdaten *beschreiben* den
Transistor — aber sie *erklären* ihn nicht, und sie lassen sich nicht in
einen Schaltungssimulator stecken. Dazu braucht es ein **Modell**: einen
Satz von Gleichungen mit wenigen Parametern, der die gemessenen
Kennlinien reproduziert. Das Standardmodell der Schaltungssimulation ist
das **Gummel-Poon-Modell** (1970), das jedem SPICE-Simulator — von
LTspice bis ngspice — zugrunde liegt.

Dieses Kapitel baut das Modell **Effekt für Effekt** auf. Wir beginnen
mit der idealen Exponentialkennlinie und ergänzen nacheinander genau die
Abweichungen, die in unseren Messungen sichtbar werden:

1. die endliche Steigung der Ausgangskennlinien → **Early-Effekt**
   ($V_A$, SPICE `VAF`),
2. dieselbe Erscheinung im Basisstrom → **Basis-Early-Effekt** ($V_{AB}$,
   SPICE `VAR`),
3. der Abfall der Stromverstärkung bei großen Strömen →
   **Hochinjektion** ($I_{KF}$, SPICE `IKF`),
4. der Spannungsabfall im Basisbahngebiet → **innerer Basiswiderstand**
   ($R_{B,\text{int}}$, SPICE `RBM`).

Am Ende steht ein geschlossenes Gleichungssystem mit benannten
Parametern und benannten Grenzen. Die beiden Anschlussfragen sind dann
zwingend: *Woher bekommen wir die Zahlenwerte der Parameter?* — aus der
Messung, Kapitel 7. *Und wie löst man das nichtlineare System in einer
konkreten Schaltung?* — mit Newton-Raphson, Kapitel 8.

> **Grundannahmen dieses Kapitels** (sofern nicht anders vermerkt):
> npn-Transistor im **Vorwärts-Aktivbetrieb** ($V_{BE}>0$, $V_{BC}<0$);
> Temperatur $T=300\,\text{K}$; **Quasistatik** (keine Kapazitäten — das
> Frequenzverhalten folgt in Kapitel 13); Niedriginjektion außer der in
> Abschnitt 6.6 behandelten Hochstromkorrektur. Alle Gleichungen sind in
> den **Klemmenspannungen** $V_{BE}$ und $V_{CE}$ formuliert.

## 6.2 Ausgangspunkt: der Transistor als gesteuerte Quelle

Ein npn-Transistor besteht aus zwei gegeneinander geschalteten
pn-Übergängen — Emitter–Basis und Kollektor–Basis — mit einer sehr
dünnen Basis dazwischen. Im Aktivbetrieb ist die **BE-Diode in
Flussrichtung** gepolt, die **BC-Diode in Sperrrichtung**. Die über die
BE-Diode in die Basis injizierten Elektronen diffundieren durch die
dünne Basis und werden vom Feld der gesperrten BC-Diode zum Kollektor
„abgesaugt". Der Kollektorstrom wird also von der Spannung $V_{BE}$
gesteuert — der Transistor ist eine **spannungsgesteuerte Stromquelle**.

Das klassische **Ebers-Moll-Modell** beschreibt beide Übergänge durch
ihre Diodengleichungen. Im Vorwärts-Aktivbetrieb dominiert der
Vorwärts-Transportstrom

$$
I_{CC} = I_S\left(e^{V_{BE}/V_T}-1\right),
$$

mit dem **Transport-Sättigungsstrom** $I_S$. Idealerweise ist
$I_C \approx I_{CC}$ und $I_B = I_{CC}/\beta_F$. Was Ebers-Moll **nicht**
erfasst — Early-Effekt, Hochinjektion, Bahnwiderstände — ergänzt das
Gummel-Poon-Modell. Genau diese Lücken schließen wir jetzt Schritt für
Schritt.

## 6.3 Die ideale Kennlinie und die Thermospannung

Der Kollektorstrom im Aktivbetrieb folgt der Shockley-Gleichung (für
$V_{BE}\gg V_T$ ist die $-1$ vernachlässigbar):

$$
I_C = I_S \cdot e^{V_{BE}/(n\,V_T)}
$$

Darin ist $n$ der **Emissionskoeffizient** (SPICE `NF`, ideal
$n\approx 1$) und $V_T$ die **Thermospannung**. Sie ist keine
Materialeigenschaft, sondern eine Naturkonstanten-Kombination — und
damit der Anker, an dem später die Steigung des Gummel-Plots hängt:

$$
V_T = \frac{k_B\,T}{q}
    = \frac{1{,}381\cdot10^{-23}\,\text{J/K}\;\cdot\;300\,\text{K}}
           {1{,}602\cdot10^{-19}\,\text{C}}
    = 25{,}85\,\text{mV}\quad(T = 300\,\text{K}).
$$

Zwei Eigenschaften dieser Kennlinie tragen das ganze Kapitel:

* Sie ist **steil**: pro $n\,V_T\ln 10 \approx 60\,\text{mV}$
  Spannungserhöhung wächst $I_C$ um den Faktor 10. Deshalb erscheint
  die Kennlinie im halblogarithmischen **Gummel-Plot** als Gerade
  (Abbildung 6.1) — das nutzen wir in Kapitel 7 zur Bestimmung von
  $I_S$ und $n$.
* Sie ist **nichtlinear**: Jede Schaltungsrechnung mit ihr führt auf
  transzendente Gleichungen — deshalb brauchten wir Teil II.

![**Abbildung 6.1** — Der Gummel-Plot: halblogarithmisch aufgetragen
wird die Exponentialkennlinie zur Geraden mit der Steigung
$1/(n\,V_T)$ — eine Dekade Stromzuwachs je
$n\,V_T\ln 10\approx 60\,\text{mV}$. Steigung und Achsenabschnitt
dieser Geraden sind die Messgrößen für $n$ und $I_S$
(Kapitel 7).](../bilder/kap06_gummel_ideal.png){width=88%}

> **Rechenbeispiel 6.1 — die Steilheit greifbar gemacht.** Der
> BC337-25 ($I_S=4{,}1\cdot10^{-14}\,$A, $n=1$) soll
> $I_C = 5\,\text{mA}$ führen. Auflösen der Kennlinie nach $V_{BE}$:
> $$V_{BE} = n\,V_T\,\ln\frac{I_C}{I_S}
> = 25{,}85\,\text{mV}\cdot\ln\frac{5\cdot10^{-3}}{4{,}1\cdot10^{-14}}
> = 25{,}85\,\text{mV}\cdot 25{,}52 = 660\,\text{mV}.$$
> Für den **doppelten** Strom ($10\,$mA) braucht es nur
> $25{,}85\,\text{mV}\cdot\ln 2 = 17{,}9\,\text{mV}$ mehr — die
> gesamte Nutzstromspanne eines Kleinsignaltransistors spielt sich in
> wenigen zehn Millivolt $V_{BE}$ ab. Das erklärt, warum
> Arbeitspunkte nie über $V_{BE}$ „eingestellt", sondern immer über
> Widerstände **stabilisiert** werden (Kapitel 8).

Der Basisstrom folgt im idealen Modell mit konstanter Stromverstärkung
$\beta_F$ (SPICE `BF`):

$$
I_B = \frac{I_C}{\beta_F} = \frac{I_S}{\beta_F}\,e^{V_{BE}/(n\,V_T)}.
$$

In der Praxis ist $\beta$ jedoch strom- und spannungsabhängig — die
Messung in Kapitel 3 hat das bereits gezeigt. Die folgenden Abschnitte
bauen diese Abhängigkeiten einzeln ins Modell ein.

## 6.4 Erste Erweiterung: der Early-Effekt ($V_A$, SPICE `VAF`)

**(1) Beobachtung in der Messung.** Die gemessenen Ausgangskennlinien
$I_C(V_{CE})$ sind im aktiven Bereich nicht exakt waagerecht — sie
steigen leicht mit $V_{CE}$ an. Das ideale Modell aus 6.3 kennt aber gar
keine $V_{CE}$-Abhängigkeit. Hier fehlt also ein Effekt.

**(2) Physikalische Ursache.** Steigt $V_{CE}$, weitet sich die
Raumladungszone des gesperrten Kollektor-Basis-Übergangs in die Basis
hinein aus. Die **effektive Basisweite sinkt** (Basisweitenmodulation),
der Diffusionsgradient der Elektronen in der Basis wird steiler — und
mit ihm steigt der Kollektorstrom. Dieser Effekt heißt nach James Early
(1952) **Early-Effekt**.

**(3) Modellterm.** Die Kennlinie erhält einen linearen Korrekturfaktor:

$$
\boxed{\,I_C = I_S\,e^{V_{BE}/(n\,V_T)}\left(1+\frac{V_{CE}}{V_A}\right)\,}
$$

mit der **Early-Spannung** $V_A$ (SPICE `VAF`, typisch 50–200 V).

**(4) Geometrische Deutung — zugleich Messvorschrift.** Extrapoliert
man die flachen Äste aller Ausgangskennlinien nach links, schneiden sie
die $V_{CE}$-Achse (näherungsweise) in **einem gemeinsamen Punkt**
$V_{CE}=-V_A$ (Abbildung 6.2). Je größer $V_A$, desto flacher die
Kennlinien, desto idealer der Transistor. Genau diese Konstruktion wird
in Kapitel 7 zur Bestimmung von $V_A$ verwendet — der Modellterm
liefert seine Messvorschrift also gleich mit.

![**Abbildung 6.2** — Early-Konstruktion am Modell (BC337-25,
$V_A=146\,$V): Die im Messbereich (rechts, durchgezogen) fast flachen
Ausgangskennlinien treffen sich rückwärts verlängert (gestrichelt) im
gemeinsamen Punkt $-V_A$ auf der
$V_{CE}$-Achse.](../bilder/kap06_early.png){width=92%}

> **Rechenbeispiel 6.2 — wie groß ist der Effekt?** Arbeitspunkt
> $I_C = 5\,\text{mA}$ bei $V_{CE}=5\,\text{V}$, $V_A=146\,$V. Steigt
> $V_{CE}$ um $5\,\text{V}$ auf $10\,\text{V}$, wächst der
> Kollektorstrom um den Faktor
> $$\frac{1+10/146}{1+5/146} = \frac{1{,}0685}{1{,}0342} = 1{,}033,$$
> also um **3,3 %** auf $5{,}17\,\text{mA}$. Klein — aber genau diese
> 3 % sind die endliche Steigung, die der Kurventracer sichtbar macht,
> und ihr Kehrwert bestimmt den Ausgangswiderstand:
> $r_{CE}\approx V_A/I_C = 146\,\text{V}/5\,\text{mA} = 29\,\text{k}\Omega$.

**(5) Konsequenz für das Kleinsignalverhalten.** Ableiten der
Early-Gleichung nach $V_{CE}$ ergibt den differentiellen
Ausgangsleitwert

$$
g_{CE} = \frac{\partial I_C}{\partial V_{CE}}
       = I_S\,e^{V_{BE}/(n\,V_T)}\cdot\frac{1}{V_A}
       \;\approx\; \frac{I_C}{V_A},
$$

denn der Ausdruck vor $1/V_A$ ist gerade der
Arbeitspunkt-Kollektorstrom. Der Early-Effekt ist damit der physikalische
Ursprung des endlichen Ausgangswiderstands $r_{CE}\approx V_A/I_C$ —
diesen Faden nehmen wir in Kapitel 11 ($h_{22e}$) wieder auf.

**(6) Zahlenbeispiel BC337-25.** Aus den Messungen (Kapitel 7) folgt
$V_A \approx 146\,\text{V}$; das Datenblatt-SPICE-Modell nennt
145,7 V — eine erste Bestätigung, dass Modellterm und Wirklichkeit
zusammenpassen.

## 6.5 Zweite Erweiterung: der Basis-Early-Effekt ($V_{AB}$, SPICE `VAR`)

Die Basisweitenmodulation verändert nicht nur den Kollektorstrom,
sondern auch den **Basisstrom** — dieselbe Ursache, ein zweiter
Wirkungsort. SPICE modelliert dies analog mit der
**Basis-Early-Spannung** $V_{AB}$ (SPICE `VAR`, typisch 100–500 V):

$$
I_B = \frac{I_S}{\beta_{\text{eff}}}\,
      e^{V_{BE,\text{eff}}/(n\,V_T)}
      \left(1+\frac{V_{CE}}{V_{AB}}\right)
$$

(Die Größen $\beta_{\text{eff}}$ und $V_{BE,\text{eff}}$ werden in den
nächsten beiden Abschnitten eingeführt; für den Moment gilt
$\beta_{\text{eff}}=\beta_F$ und $V_{BE,\text{eff}}=V_{BE}$.)

Für $V_{AB}\to\infty$ verschwindet der Effekt. In der Praxis ist
$V_{AB}$ meist deutlich größer als $V_A$ — der Basis-Early-Effekt ist
also schwächer als sein Kollektor-Gegenstück. Er wirkt unscheinbar,
trägt aber eine wichtige Konsequenz: Er ist die physikalische Quelle
der **Spannungsrückwirkung** $h_{12e}$ im Vierpolmodell (Kapitel 11).
Ein Modell ohne `VAR` hat zwingend $h_{12e}=0$ — das werden wir dort
als benannte Modellgrenze wiederfinden.

## 6.6 Dritte Erweiterung: Hochinjektion ($I_{KF}$, SPICE `IKF`)

**(1) Beobachtung.** Trägt man die gemessene Stromverstärkung
$h_{FE}=I_C/I_B$ über $I_C$ auf, fällt sie bei großen Strömen ab
(Abbildung 6.3). Das ideale Modell mit konstantem $\beta_F$ kann das
nicht erklären.

![**Abbildung 6.3** — Hochinjektion beim BC337-25: unterhalb des
Kniestroms $I_{KF}=0{,}9\,$A gilt $\beta\approx\beta_F$; bei
$I_C=I_{KF}$ ist die Verstärkung auf $\beta_F/\sqrt2$ gefallen, weit
darüber sinkt sie mit $1/\sqrt{I_C}$. Grün markiert: der Messbereich
des Kennlinienschreibers aus Kapitel 7 — er endet zwei Dekaden **vor**
dem Knie.](../bilder/kap06_betaeff.png){width=88%}

**(2) Physikalische Ursache.** Bei großen Kollektorströmen wird die
injizierte Ladungsträgerdichte in der Basis mit der
**Basisdotierung vergleichbar** — man spricht von **Hochinjektion**.
Zwei Mechanismen drücken dann die Verstärkung:

* **Webster-Effekt:** Die Rekombination in der Basis wächst
  überproportional, das Verhältnis $I_C/I_B$ sinkt.
* **Kirk-Effekt:** Bei sehr hohen Stromdichten verlagert sich die
  Kollektor-Raumladungszone in die Epitaxieschicht — die Basis „weitet
  sich aus".

**(3) Herleitung des Modellterms.** Das Gummel-Poon-Modell fasst beide
Mechanismen über die **normierte Basisladung** $q_B = Q_B/Q_{B0}$
zusammen. Näherungsweise gilt

$$
q_B \approx \frac{1}{2} + \sqrt{\left(\frac{1}{2}\right)^{2}
      + \frac{I_C}{I_{KF}}},
$$

mit den beiden Grenzfällen

$$
I_C \ll I_{KF}:\; q_B \approx 1 \quad\text{(normale Basisladung)},
\qquad
I_C \gg I_{KF}:\; q_B \approx \sqrt{\frac{I_C}{I_{KF}}}.
$$

Da der Transportstrom umgekehrt proportional zur Basisladung ist
($I_C \propto 1/q_B$), wird die wirksame Verstärkung durch $q_B$
geteilt:

$$
\boxed{\;\beta_{\text{eff}} = \frac{\beta_F}{q_B}
\;\approx\; \frac{\beta_F}{\sqrt{1+\dfrac{I_C}{I_{KF}}}}\;}
$$

Der **Vorwärts-Kniestrom** $I_{KF}$ (SPICE `IKF`, typisch
10 mA–1 A) markiert die Grenze: Bei $I_C=I_{KF}$ ist $\beta$ um den
Faktor $\sqrt{2}$ gefallen; weit darüber sinkt $\beta$ mit
$1/\sqrt{I_C}$.

**(4) Zahlenbeispiel — und eine wichtige Vorwegnahme.** Für den
BC337-25 gilt $I_{KF}\approx 0{,}9\,\text{A}$. Unsere Kennlinien wurden
bis $I_C \le 11\,\text{mA}$ gemessen, also $I_C/I_{KF} \lesssim 0{,}01$:

$$
\beta_{\text{eff}} = \frac{292}{\sqrt{1+0{,}011/0{,}9}}
                   = \frac{292}{\sqrt{1{,}0122}} = 290{,}2
$$

— ein Abfall um **0,6 %**, unterhalb jeder Messauflösung. Erst bei
$I_C = I_{KF} = 0{,}9\,$A fiele $\beta$ auf
$292/\sqrt2 = 206$. Der Abfall liegt also **außerhalb des
Messfensters** (grüner Bereich in Abbildung 6.3). Das hat eine
Konsequenz, die in Kapitel 7 zum Prinzip erhoben wird: Ein Parameter,
dessen Effekt im Messbereich nicht sichtbar ist, kann aus diesen
Messungen auch **nicht bestimmt** werden.

## 6.7 Vierte Erweiterung: der innere Basiswiderstand ($R_{B,\text{int}}$, SPICE `RBM`)

**(1) Physikalische Ursache.** Das Basisgebiet ist dünn und lateral
ausgedehnt; der Basisstrom muss durch dessen Bahnwiderstand fließen.
Dieser **innere Basiswiderstand** $R_{B,\text{int}}$ (SPICE `RBM`,
typisch 1–50 Ω) verursacht einen ohmschen Spannungsabfall — die am
Übergang **wirksame** Basis-Emitter-Spannung ist kleiner als die
Klemmenspannung:

$$
\boxed{\,V_{BE,\text{eff}} = V_{BE} - I_B\,R_{B,\text{int}}\,}
$$

Nur $V_{BE,\text{eff}}$ treibt den Übergang; in allen Exponentialtermen
des Basisstroms ist fortan $V_{BE}$ durch $V_{BE,\text{eff}}$ zu
ersetzen.

> **Rechenbeispiel 6.3 — Millivolt, die zählen.** BC337-25 im
> Arbeitspunkt $I_C=5\,$mA: $I_B \approx 5\,\text{mA}/290 =
> 17{,}2\,\mu$A. Mit $R_{B,\text{int}} = 60\,\Omega$ folgt
> $$\Delta V = I_B\,R_{B,\text{int}} = 17{,}2\,\mu\text{A}\cdot 60\,\Omega
> = 1{,}03\,\text{mV}.$$
> Ein einziges Millivolt — aber die Exponentialkennlinie übersetzt es
> in $e^{1{,}03/25{,}85}-1 \approx 4\,\%$ Stromänderung. Bei zehnfachem
> Strom sind es bereits 10 mV und über 40 %: Der innere
> Basiswiderstand wird zum dominanten Effekt des Hochstrombereichs —
> dort krümmt er den Gummel-Plot sichtbar nach unten (Kapitel 7 nutzt
> genau diese Signatur, um seine Bestimmbarkeit zu beurteilen).

**(2) Die implizite Kopplung — eine strukturelle Eigenschaft.** Hier
entsteht eine Besonderheit, die uns durch die Kapitel 8 und 9 begleiten
wird: $I_B$ hängt von $V_{BE,\text{eff}}$ ab, und $V_{BE,\text{eff}}$
über den Spannungsabfall wiederum von $I_B$. Die Gleichung ist
**implizit** — es gibt keine geschlossene Auflösung. In einem
Simulationsmodell (Simulink, Kapitel 9) äußert sich das als
**algebraische Schleife**. Sauber löst man sie

* **physikalisch**, indem man eine kleine Basis-Kapazität einführt
  (Knotengleichung
  $C\,\dot V_{BE,\text{eff}} = (V_{BE}-V_{BE,\text{eff}})/R_{B,\text{int}} - I_B$;
  im stationären Zustand exakt), oder
* **numerisch** durch einen Fixpunkt- oder Newton-Löser — genau das
  Verfahren aus Teil II, und genau so macht es SPICE intern.

Ein bloßes Verzögerungsglied ($z^{-1}$) bricht die Schleife zwar auf,
ist wegen der steilen Exponentialfunktion aber instabilitätsgefährdet.
Wenn schon, dann bricht man die Schleife **an der Spannung**
$V_{BE,\text{eff}}$ auf, nicht am Strom — die Spannung ändert sich
zwischen zwei Iterationen um Millivolt, der Strom um Größenordnungen.

## 6.8 Das vollständige Modell

Alle vier Erweiterungen zusammengenommen — jede einzeln hergeleitet,
jede mit benannter Ursache — ergeben das Gleichungssystem dieses Buches:

$$
\boxed{
\begin{aligned}
I_C &= I_S\,e^{V_{BE}/(n\,V_T)}\left(1+\frac{V_{CE}}{V_A}\right)\\[4pt]
\beta_{\text{eff}} &= \frac{\beta_F}{\sqrt{1+I_C/I_{KF}}}, \qquad
V_{BE,\text{eff}} = V_{BE}-I_B\,R_{B,\text{int}}\\[4pt]
I_B &= \frac{I_S}{\beta_{\text{eff}}}\,
       e^{V_{BE,\text{eff}}/(n\,V_T)}
       \left(1+\frac{V_{CE}}{V_{AB}}\right)
\end{aligned}}
$$

**Gültigkeitsbereich:** Vorwärts-Aktivbetrieb (keine Sättigung, kein
Inversbetrieb), $T=300\,\text{K}$, Quasistatik, Niedriginjektion bis auf
die über $I_{KF}$ erfasste Hochstromkorrektur.

> **Benannte Modellgrenze.** Reale Kleinsignaltransistoren zeigen bei
> **kleinen** Strömen einen leichten $h_{FE}$-**Anstieg** (Rekombination
> in der BE-Sperrschicht; im vollen Gummel-Poon-Modell über den Leckterm
> `ISE`/`NE` beschrieben). Unser Modell **enthält diesen Effekt bewusst
> nicht** — er bleibt in Kapitel 7 als kleine, ausgewiesene
> Restabweichung zwischen Modell und Messung sichtbar. Ein Modell, dessen
> Grenzen benannt sind, ist mehr wert als ein scheinbar vollständiges,
> dessen Terme man nicht bestimmen kann.

## 6.9 Das Modell zum Anfassen: die Python-Implementierung

Ein Modell versteht man erst, wenn man es rechnen lässt. Das komplette
Gleichungssystem aus 6.8 passt in wenige Zeilen Python — genau diese
Funktionen bilden den Kern aller Werkzeuge dieses Buches (von der
Parameterextraktion in Kapitel 7 bis zur Arbeitspunktsuche in
Kapitel 8):

```python
import numpy as np

# ---- Modellparameter BC337-25 (aus Kapitel 7 bzw. Datenblatt) ----
IS   = 4.1e-14   # A   Transport-Saettigungsstrom      (SPICE IS)
NF   = 1.0       # -   Emissionskoeffizient            (SPICE NF)
BETA = 292.0     # -   ideale Stromverstaerkung        (SPICE BF)
VA   = 146.0     # V   Early-Spannung                  (SPICE VAF)
VAB  = 200.0     # V   Basis-Early-Spannung            (SPICE VAR)
IKF  = 0.9       # A   Kniestrom Hochinjektion         (SPICE IKF)
RBI  = 60.0      # Ohm innerer Basiswiderstand         (SPICE RBM)
VT   = 0.02585   # V   Thermospannung bei 300 K

def beta_eff(ic):
    """Webster-Formel: stromabhaengige Verstaerkung (Abschn. 6.6)."""
    return BETA / np.sqrt(1.0 + ic / IKF)

def v_be_eff(v_be, i_b):
    """wirksame BE-Spannung nach Abfall an R_B,int (Abschn. 6.7)."""
    return v_be - i_b * RBI

def i_c_modell(v_be, v_ce):
    """Kollektorstrom mit Early-Effekt (Abschn. 6.4)."""
    return IS * np.exp(v_be / (NF * VT)) * (1.0 + v_ce / VA)

def i_b_modell(v_be_wirksam, v_ce, ic):
    """Basisstrom mit Basis-Early und beta_eff (Abschn. 6.5/6.6)."""
    return (IS / beta_eff(ic)) * np.exp(v_be_wirksam / (NF * VT)) \
           * (1.0 + v_ce / VAB)
```

Man beachte, wie die **implizite Kopplung** aus Abschnitt 6.7 hier
sichtbar wird: `i_b_modell` braucht die wirksame Spannung
`v_be_eff(v_be, i_b)` — die aber den Basisstrom `i_b` bereits enthält.
Wer die Funktionen naiv nacheinander aufruft, rechnet mit dem
Basisstrom der *vorigen* Iteration; die konsistente Lösung liefert erst
der Newton-Löser in Kapitel 8. Für den Aktivbetrieb bei moderaten
Strömen konvergiert alternativ eine einfache Fixpunktiteration
($I_B^{(0)}=0$, dann wenige Male $I_B^{(k+1)}$ aus
$V_{BE}-I_B^{(k)}R_{B,\text{int}}$ berechnen) — die Korrektur ist ja
nur millivoltklein (Rechenbeispiel 6.3).

Ein kurzer Testlauf im Arbeitspunkt aus den Rechenbeispielen
($V_{BE}=660\,$mV, $V_{CE}=5\,$V) verankert die Zahlen:

```python
vbe, vce = 0.660, 5.0
ic = i_c_modell(vbe, vce)                 # -> 5.20 mA (5 mA ideal + 3.4 % Early)
ib = ic / beta_eff(ic)                    # -> 17.9 uA  (Startwert)
ib = i_b_modell(v_be_eff(vbe, ib), vce, ic)   # eine Fixpunkt-Korrektur
print(ic, ib, ic/ib)                      # 5.20 mA, 17.0 uA, beta ~ 305
```

Schon dieser Dreizeiler zeigt das Zusammenspiel der Effekte: Der
Early-Faktor hebt den idealen 5-mA-Punkt um 3,4 % an
(Rechenbeispiel 6.2), der innere Basiswiderstand drückt den Basisstrom
um gut 4 % (Rechenbeispiel 6.3), und $\beta_{\text{eff}}$ bleibt bei
diesen Strömen praktisch $\beta_F$ (Rechenbeispiel in 6.6).

Sämtliche Abbildungen dieses Kapitels sind mit genau diesen Funktionen
erzeugt (`kap06_plots.py` im Begleitmaterial) — es gibt keine
„Illustrationen", nur gerechnetes Modell. Das ist das
Reproduzierbarkeits-Prinzip des Buches: **Jede Kurve lässt sich aus
Code und Parametern nachvollziehen.**

## 6.10 Die SPICE-Parameter im Überblick

Damit ist jeder Parameter des Modells eingeführt, physikalisch begründet
und einem SPICE-Namen zugeordnet:

| SPICE | Symbol | Bedeutung | Herkunft im Modell | BC337-25 (Referenz) |
|---|---|---|---|---|
| `IS`  | $I_S$ | Transport-Sättigungsstrom | Abschn. 6.3 | $4{,}1\cdot10^{-14}$ A |
| `NF`  | $n$ | Vorwärts-Emissionskoeffizient | Abschn. 6.3 | $1{,}0$ |
| `BF`  | $\beta_F$ | ideale Vorwärts-Stromverstärkung | Abschn. 6.3 | $292$ |
| `VAF` | $V_A$ | Vorwärts-Early-Spannung | Abschn. 6.4 | $146$ V |
| `VAR` | $V_{AB}$ | Basis-(Rückwärts-)Early-Spannung | Abschn. 6.5 | (Rückwirkung) |
| `IKF` | $I_{KF}$ | Vorwärts-Kniestrom (Hochinjektion) | Abschn. 6.6 | $0{,}9$ A |
| `RBM` | $R_{B,\text{int}}$ | innerer Basisbahnwiderstand | Abschn. 6.7 | $\sim 60\ \Omega$ |

Die weiteren Gummel-Poon-Parameter (`BR`, `ISC`, `NC`, `IKR`, `RC`,
`RE` für Invers- und Sperrbetrieb; `CJE`, `CJC`, `TF`, `TR` für die
Dynamik) werden erst gebraucht, wenn Inversbetrieb oder
Frequenzverhalten ins Spiel kommen — Letzteres in Kapitel 13. Für den
Vorwärts-Aktivbetrieb bei Gleichstrom ist der obige Satz vollständig.

## 6.11 Ideal gegen erweitert — was das Modell leistet

![**Abbildung 6.4** — Was die Erweiterungen bewirken: links die
Ausgangskennlinie (ideal waagerecht, erweitert mit Early-Steigung),
rechts die Stromverstärkung (ideal konstant, erweitert mit
Hochstrom-Knie). Beide Kurven aus der Python-Implementierung von
Abschnitt 6.9 gerechnet.](../bilder/kap06_vergleich.png){width=100%}

| Eigenschaft | ideales Modell (6.3) | erweitertes Modell (6.8) |
|---|---|---|
| Ausgangskennlinie | exakt waagerecht | Steigung $I_C/V_A$ (`VAF`) |
| Basisstrom | $V_{CE}$-unabhängig | Faktor $(1+V_{CE}/V_{AB})$ (`VAR`) |
| Stromverstärkung | konstant $\beta_F$ | $\beta_{\text{eff}}(I_C)$ mit Kniestrom (`IKF`) |
| Basisbahngebiet | widerstandsfrei | $V_{BE,\text{eff}}=V_{BE}-I_B R_{B,\text{int}}$ (`RBM`) |
| Arbeitspunkt | analytisch lösbar | implizit → Newton-Raphson (Kap. 8) |
| Genauigkeit | Orientierung | SPICE-Niveau |

Der Preis der Genauigkeit steht in der vorletzten Zeile: Das erweiterte
Modell ist **analytisch nicht mehr auflösbar**. Was im idealen Modell
eine Zeile Rechnung war, wird zum nichtlinearen Gleichungssystem — und
damit zur Aufgabe für das Handwerkszeug aus Teil II.

## 6.12 Zusammenfassung und Ausblick

1. Das Gummel-Poon-Modell erweitert die ideale Exponentialkennlinie um
   vier messbare Effekte: Early ($V_A$), Basis-Early ($V_{AB}$),
   Hochinjektion ($I_{KF}$) und inneren Basiswiderstand
   ($R_{B,\text{int}}$) — durchgehend formuliert in den
   Klemmenspannungen $V_{BE}$, $V_{CE}$.
2. Jeder Modellterm bringt seine **Messvorschrift** mit: die
   Gummel-Plot-Gerade für $I_S$ und $n$, den gemeinsamen
   Achsenschnittpunkt für $V_A$, das $h_{FE}$-Plateau für $\beta_F$,
   den Hochstromabfall für $I_{KF}$.
3. Zwei strukturelle Eigenschaften prägen alles Weitere: die
   **Nichtlinearität** (kein geschlossener Arbeitspunkt) und die
   **implizite Kopplung** über $V_{BE,\text{eff}}$ (algebraische
   Schleife).

Damit ist das Modell vollständig — aber es ist noch eine Hülle: Seine
Parameter sind Buchstaben. **Kapitel 7** füllt sie mit Zahlen: aus den
selbst gemessenen Kennlinien, Schritt für Schritt, mit jeder Annahme
und jeder Grenze der Bestimmbarkeit. Danach löst **Kapitel 8** das
Modell in einer realen Schaltung, und **Kapitel 9** lässt es in LTspice
und Simulink gegen die Messung antreten.
