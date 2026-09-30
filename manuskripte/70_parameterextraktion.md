---
title: "Kapitel 7 — Parameterextraktion: vom Messwert zum Zahlenwert"
subtitle: "Buchentwurf zur Freigabe · Teil III: Vom Messwert zum Modell"
author: "Prof. Dr.-Ing. Ralph Wystup"
date: "Entwurf, Stand 4. August 2026"
lang: de
---

# 7 Parameterextraktion: vom Messwert zum Zahlenwert

## 7.1 Sinn und Ziel dieses Kapitels

**Warum dieses Kapitel das Scharnier des Buches ist:** Kapitel 6 hat
das Modell aufgebaut — aber seine Parameter sind Buchstaben. Wer sie
aus dem Datenblatt oder einer heruntergeladenen `.model`-Karte
übernimmt, simuliert einen **Katalog-Transistor**, nicht das Bauteil
auf seinem Tisch: $h_{FE}$ streut in der Serie um den Faktor 4, und ob
die Katalogwerte je an einem Exemplar gemessen wurden, weiß niemand.
Dieses Kapitel schließt die Lücke zwischen Theorie und Praxis: **Es
macht aus den selbst gemessenen Kennlinien (Teil I) den Parametersatz
des eigenen, konkreten Transistors** — nachvollziehbar bis in jede
Formel und jeden Ablesewert. Erst damit werden die Simulationen der
Kapitel 8 und 9 zu überprüfbaren Aussagen über *dieses* Bauteil.

> **Nach diesem Kapitel können Sie:**
>
> * aus dem Gummel-Plot den Sättigungsstrom $I_S$ und den Idealfaktor
> $n$ extrahieren — grafisch per Geradenfit und von Hand über zwei
> Messpunkte,
> * die Stromverstärkung $\beta_F$ aus dem $I_C/I_B$-Plateau
> bestimmen,
> * die Early-Spannung $V_A$ durch Extrapolation des
> Ausgangskennfelds ermitteln,
> * den Knickstrom $I_{KF}$ über das 70,7-%-Kriterium ablesen — und
> erkennen, wann er **nicht** ablesbar ist,
> * den inneren Basiswiderstand $R_{B,\text{int}}$ aus der Kompression
> der Eingangskennlinie berechnen,
> * mit globalem Fit und **Identifizierbarkeitsanalyse** beurteilen,
> welche Parameter wirklich „aus den Daten" kommen — und welche nur
> gesetzt sind.

**Der Fahrplan.** Die Extraktion folgt einer **festen Reihenfolge**,
denn spätere Parameter bauen auf früheren auf:

Die Extraktion folgt einer **festen Reihenfolge**, denn spätere
Parameter bauen auf früheren auf:

$$
I_S,\,n \;\longrightarrow\; \beta_F \;\longrightarrow\; V_A
\;\longrightarrow\; I_{KF} \;\longrightarrow\; R_{B,\text{int}}
$$

Und wir gehen den Weg **zweimal**, mit Absicht:

* **Durchlauf 1 — BC337-25 am Kurventracer:** Hier entwickeln wir die
 Methode Schritt für Schritt und erweitern sie am Ende um zwei
 Werkzeuge, die über das übliche Vorgehen hinausgehen: den **globalen
 Fit** über alle Kennlinienfelder und die
 **Identifizierbarkeitsanalyse**.
* **Durchlauf 2 — BC547 am eigenen Kennlinienschreiber (Kapitel 2):**
 Derselbe Weg, eigenständig durchgerechnet mit Zwei-Punkt-Auswertungen, die sich vollständig von Hand nachvollziehen
 lassen — der Beleg, dass die Methode nicht am Gerät hängt.

Dass beide Durchläufe teils **unterschiedliche Antworten auf dieselbe
Frage** geben (beim einen ist $I_{KF}$ bestimmbar, beim anderen nicht),
ist kein Makel, sondern die zentrale Lektion dieses Kapitels — sie wird
in Abschnitt 7.11 auf den Punkt gebracht.

## 7.2 Die Messdatenbasis

**Messprinzip.** Ein Kennlinienschreiber legt definierte Spannungs-
bzw. Stromrampen an den Prüfling und zeichnet die Ströme auf. Für die
vollständige Extraktion braucht es drei Messreihen:

| Messreihe | Bedingung | liefert |
|---|---|---|
| Gummel-Plot ($I_C$, $I_B$ über $V_{BE}$) | $V_{CE}=\text{const.}$ (z. B. 5 V), log. Stromachse | $I_S$, $n$, $\beta_F$, $I_{KF}$ |
| Ausgangskennfeld ($I_C$ über $V_{CE}$) | mehrere feste $I_B$-Stufen | $V_A$ |
| Eingangskennlinie ($V_{BE}$ über $I_B$) | festes $V_{CE}$, hohe Auflösung | $R_{B,\text{int}}$ |

Die Basis-Early-Spannung $V_{AB}$ (`VAR`) ist messtechnisch deutlich
aufwendiger (sie verlangt die $V_{CE}$-Abhängigkeit von $I_B$ bei sehr
hoher Stromauflösung); in der Praxis übernimmt man sie aus dem
Datenblatt oder schätzt sie mit der Faustregel
$V_{AB}\approx 2\,V_A$ — ihr Einfluss auf die Schaltungsanalyse ist
klein (Kapitel 6.5).

**Zwei Fallstricke schon bei der Messung:**

* **Thermische Drift:** $I_S$ verdoppelt sich näherungsweise alle
 8–10 K. Der Kennlinienschreiber muss die Selbsterwärmung klein
 halten (Pulsmessung, Strombegrenzung), sonst verschieben sich alle
 abgeleiteten Parameter mit der Messzeit.
* **Serienstreuung:** $h_{FE}$ streut beim BC547 herstellerseitig um
 den Faktor 4 (Klassengrenzen 110–800). **Jede Extraktion gilt nur
 für das konkrete Exemplar** — genau deshalb misst man selbst, statt
 Katalogwerte zu übernehmen.

Für Durchlauf 1 liegen fünf Kennlinienfelder des BC337-25 als
Kurventracer-Dateien vor (`Ic_Vbe`, `Ic_Vce`, `Ic_Ib`, `hFE_Ic`,
`hFE_Vce`); Durchlauf 2 nutzt die Messreihen des eigenen
Kennlinienschreibers aus Kapitel 2.

## 7.3 Schritt 1: $I_S$ und $n$ aus dem Gummel-Plot

**Prinzip.** Im halblogarithmischen Gummel-Plot wird die
Exponentialkennlinie zur Geraden (Abbildung 6.1):

$$
\ln I_C = \underbrace{\ln\!\big[I_S(1+V_{CE}/V_A)\big]}_{\text{Achsenabschnitt}}
 + \underbrace{\frac{1}{n\,V_T}}_{\text{Steigung}}\cdot V_{BE}.
$$

Steigung und Achsenabschnitt sind die beiden Messgrößen:

$$
n = \frac{1}{V_T}\cdot\frac{1}{\text{Steigung}},\qquad
I_S = \frac{e^{\text{Achsenabschnitt}}}{1+V_{CE}/V_A}.
$$

**Praktische Auswertung über zwei Punkte.** Für die Handauswertung
genügen zwei Punkte $(V_{BE1},I_{C1})$, $(V_{BE2},I_{C2})$ aus dem
linearen Bereich:

$$
\boxed{\;n=\frac{V_{BE2}-V_{BE1}}{V_T\,\ln(I_{C2}/I_{C1})},\qquad
I_S=\frac{I_{C1}}{e^{V_{BE1}/(n V_T)}}\;}
$$

![**Abbildung 7.1** — Schritt 1 an der echten Messung (BC337-25,
$V_{CE}=6\,$V): Die Messpunkte liegen im Auswertefenster (grün) exakt
auf der Fitgeraden; ihre Steigung liefert $n=0{,}999$, der
Achsenabschnitt $I_S=4{,}4\cdot10^{-14}\,$A. Unterhalb des
Rauschbodens (≈ 5 µA) und oberhalb des Fensters darf nicht
ausgewertet werden.](../bilder/kap07_gummel_mess.png){width=92%}

![**Abbildung 7.2** — Dieselbe Auswertung von Hand: Zwei-Punkt-Methode
am BC547 (Rechenbeispiel 7.1). Zwei abgelesene Punkte genügen; 60 mV
Abstand und Faktor 10 im Strom ergeben unmittelbar
$n\approx1$.](../bilder/kap07_zweipunkt.png){width=92%}

> **Rechenbeispiel 7.1 — BC547, von Hand.** Zwei Punkte aus dem
> linearen Ast ($V_{CE}=5\,$V, Raumtemperatur):
> $V_{BE1}=0{,}600\,$V → $I_{C1}=0{,}5\,$mA und
> $V_{BE2}=0{,}660\,$V → $I_{C2}=5{,}0\,$mA.
> $$n=\frac{0{,}060}{0{,}02586\cdot\ln 10}
> =\frac{0{,}060}{0{,}05954}=1{,}008\approx 1{,}0,$$
> $$I_S=\frac{0{,}5\,\text{mA}}{e^{0{,}600/(1{,}008\cdot 0{,}02586)}}
> =\frac{5\cdot10^{-4}}{9{,}9\cdot10^{9}}=5{,}0\cdot10^{-14}\,\text{A}.$$
> Zum Vergleich Durchlauf 1 (BC337-25, Geradenfit statt zwei Punkte):
> $n=1{,}004$, $I_S=4{,}8\cdot10^{-14}\,$A — zwei Bauteile, zwei
> Messgeräte, dieselbe Größenordnung und $n\approx 1$: der
> Diffusionsstrom dominiert, wie es die Theorie für Silizium verlangt.

**Die Fensterwahl ist die halbe Auswertung.** Ausgewertet werden darf
nur der **rein exponentielle Ast**:

* Nach unten begrenzen Leckströme und der Rausch-/Quantisierungsboden
 des Messgeräts die Gerade (beim Kurventracer $\approx 5\,\mu$A) —
 darunter krümmt sie sich nach oben.
* Nach oben krümmen Hochinjektion und $R_{B,\text{int}}$ die Gerade
 nach unten.

Wie empfindlich das ist, zeigte Durchlauf 1 drastisch: Ein zu weit
gewähltes Fenster lieferte zunächst $n\approx 3{,}5$ — ein
unphysikalischer Wert (Silizium: $n\approx1{,}0$; $n>1{,}05$ deutet auf
Sperrschicht-Rekombination hin, $n=3{,}5$ auf nichts als ein falsches
Fenster). **Plausibilitätskontrolle gegen die Physik gehört zu jedem
Extraktionsschritt.**

## 7.4 Schritt 2: $\beta_F$ aus dem Verstärkungs-Plateau

Da der Gummel-Plot $I_C$ **und** $I_B$ über $V_{BE}$ enthält, liefert
er die Stromverstärkung gleich mit:

$$
\beta(V_{BE}) = \frac{I_C(V_{BE})}{I_B(V_{BE})}.
$$

Weil $\beta$ stromabhängig ist (Kapitel 6.6), nimmt man als
SPICE-Wert `BF` das **Plateau** der $\beta(I_C)$-Kurve im mittleren
Strombereich — dort, wo weder Kleinstrom-Rekombination noch
Hochinjektion stören.

> **Rechenbeispiel 7.2 — BC547.** Im Plateaubereich (typisch
> $I_C=1\ldots10\,$mA): $I_C=2{,}0\,$mA, $I_B=6{,}9\,\mu$A →
> $$\beta_F = \frac{2{,}0\,\text{mA}}{6{,}9\,\mu\text{A}} \approx 290.$$
> Das liegt in der $h_{FE}$-Klasse B (200–450) des BC547.
> Durchlauf 1 (BC337-25): Plateau $\beta_F\approx 250\ldots275$.

## 7.5 Schritt 3: $V_A$ aus dem Ausgangskennfeld

**Prinzip.** Im aktiven Bereich ist jede Ausgangskennlinie
näherungsweise eine Gerade $I_C = I_{C0}\,(1+V_{CE}/V_A)$; rückwärts
verlängert schneiden alle die $V_{CE}$-Achse bei $-V_A$
(Abbildung 6.2). Aus **zwei Punkten derselben Kennlinie** (gleiches
$I_B$) folgt $V_A$ geschlossen — man setzt beide Punkte in die
Geradengleichung ein und eliminiert $I_{C0}$:

$$
\boxed{\;V_A = \frac{V_{CE2}\,I_{C1} - V_{CE1}\,I_{C2}}{I_{C2}-I_{C1}}\;}
$$

**Vorgehen:** zwei möglichst weit auseinanderliegende Punkte im
aktiven Bereich wählen (kleiner Ablesefehler!), für 2–3 weitere
$I_B$-Stufen wiederholen, Ergebnisse mitteln.

![**Abbildung 7.3** — Schritt 3 an der echten Messung (BC337-25): Die
fünf gemessenen Ausgangskennlinien ($I_B=8\ldots40\,\mu$A), jeweils im
flachen Ast linear gefittet und rückwärts verlängert — die Geraden
treffen sich nahe $-V_A\approx-150\,$V. Man sieht auch die Streuung
der einzelnen Schnittpunkte: $V_A$ ist nur schwach
bestimmt.](../bilder/kap07_early_mess.png){width=92%}

> **Rechenbeispiel 7.3 — BC547.** Kennlinie $I_B=20\,\mu$A:
> $(5\,\text{V},\,5{,}80\,\text{mA})$ und
> $(20\,\text{V},\,6{,}67\,\text{mA})$:
> $$V_A=\frac{20\cdot5{,}80-5\cdot6{,}67}{6{,}67-5{,}80}\,\text{V}
> =\frac{82{,}65}{0{,}87}\,\text{V}\approx 95\,\text{V}.$$
> Literaturbereich BC547: 70…100 V — passt. Durchlauf 1 (BC337-25)
> ergab $V_A\approx110\ldots150\,$V mit deutlicher Streuung über die
> $I_B$-Stufen: $V_A$ ist prinzipbedingt nur **schwach bestimmt**, weil
> eine kleine Steigung gemessen und weit extrapoliert wird — das
> quantifiziert die Identifizierbarkeitsanalyse in 7.11.

## 7.6 Schritt 4: $I_{KF}$ aus dem Verstärkungsabfall

**Prinzip.** Die Webster-Formel (Kapitel 6.6) macht aus der Definition
eine Messvorschrift: Bei $I_C=I_{KF}$ ist

$$
\beta_{\text{eff}} = \frac{\beta_F}{\sqrt{2}} = 0{,}707\,\beta_F.
$$

**Vorgehen:** $\beta=I_C/I_B$ halblogarithmisch über $I_C$ auftragen,
Plateauwert $\beta_F$ ablesen, dann den Strom suchen, bei dem $\beta$
auf 70,7 % des Plateaus gefallen ist — das **ist** $I_{KF}$.

> **Rechenbeispiel 7.4 — BC547.** Plateau $\beta_F=290$ →
> $0{,}707\cdot290 = 205$. Abgelesen: $\beta=205$ bei
> $$I_{KF}\approx 80\,\text{mA}.$$
> Das passt zur Datenblattgrenze $I_{C,\max}=100\,$mA — der
> Hochstromabfall setzt beim BC547 also schon **innerhalb** des
> zulässigen Strombereichs spürbar ein.

**Der Kontrast, auf den es ankommt:** In Durchlauf 1 endet die Messung
bei $I_C=11\,$mA — der BC337-25 hat sein Knie aber erst bei
$\approx0{,}9\,$A. Der Abfall liegt zwei Dekaden außerhalb des
Messfensters (Abbildung 7.4): $I_{KF}$ ist dort **nicht bestimmbar**,
nur eine untere Schranke lässt sich angeben; der Wert kommt aus dem
Datenblatt. **Derselbe Parameter, dieselbe Methode — einmal messbar,
einmal nicht.** Was ihn bestimmbar macht, ist allein das Verhältnis
von Messfenster zu Kniestrom.

![**Abbildung 7.4** — Schritte 2 und 4 an der echten Messung
(BC337-25): Das $\beta$-Plateau bei $\approx270$ liefert $\beta_F$;
ein Hochstromabfall ist bis zur Messgrenze von 11 mA **nicht**
erkennbar — $I_{KF}$ liegt zwei Dekaden außerhalb und ist aus diesen
Daten nicht bestimmbar. Beim BC547 (Messbereich bis 100 mA) gelang
die Ablesung dagegen (Rechenbeispiel 7.4).](../bilder/kap07_beta_mess.png){width=92%}

## 7.7 Schritt 5: $R_{B,\text{int}}$ aus der Eingangskennlinie

**Prinzip.** Der innere Basiswiderstand „verbiegt" die
Eingangskennlinie bei hohen Strömen zu größeren $V_{BE}$-Werten — wie
ein Vorwiderstand an einer LED:

$$
V_{BE,\text{gemessen}} = V_{BE,\text{ideal}} + I_B\,R_{B,\text{int}}
\;\;\Rightarrow\;\;
\boxed{\;R_{B,\text{int}} =
\frac{V_{BE,\text{gemessen}}-V_{BE,\text{ideal}}}{I_B}\;}
$$

Dabei wird der ideale Verlauf aus den **bereits bestimmten** Parametern
berechnet: $V_{BE,\text{ideal}}(I_B)=n\,V_T\ln(\beta_F I_B/I_S)$ —
deshalb steht dieser Schritt zwingend am Ende der Reihenfolge.

> **Rechenbeispiel 7.5 — BC547.** Bei $I_B=1\,$mA:
> $$V_{BE,\text{ideal}} = 1{,}01\cdot25{,}86\,\text{mV}\cdot
> \ln\frac{290\cdot10^{-3}}{5{,}0\cdot10^{-14}} \approx 0{,}768\,\text{V},
> \qquad V_{BE,\text{gemessen}} = 0{,}783\,\text{V}$$
> $$R_{B,\text{int}} = \frac{0{,}783-0{,}768}{1\,\text{mA}} = 15\,\Omega.$$
> Typisch für Kleinsignal-npn sind 5…30 Ω — plausibel.
> **Messtechnische Warnung:** Kontaktwiderstände der Messspitzen gehen
> ununterscheidbar in dieselbe Differenz ein und lassen
> $R_{B,\text{int}}$ systematisch zu groß erscheinen —
> Vierleitermessung oder Kalibrierung ist hier Pflicht. In
> Durchlauf 1 (Messung nur bis 11 mA) blieb der Hochstrom-Knick des
> Gummel-Plots unsichtbar: $R_B$ dort **nicht bestimmbar** →
> Datenblattwert.

## 7.8 Die Parametersätze beider Durchläufe

**BC547 (eigener Kennlinienschreiber, Zwei-Punkt-Auswertungen):**

| Parameter | Demo-Wert (Kap. 6/8-Beispiele) | **gemessen BC547** | Quelle |
|---|---|---|---|
| `IS` | $1\cdot10^{-13}$ A | $5{,}0\cdot10^{-14}$ A | Gummel-Plot |
| `NF` | 1,0 | 1,01 | Gummel-Plot-Steigung |
| `BF` | 200 | 290 | $I_C/I_B$-Plateau |
| `VAF` | 100 V | 95 V | Ausgangskennfeld |
| `VAR` | 200 V | 190 V | Faustregel $2\,V_A$ |
| `IKF` | 0,5 A | **0,08 A** | $\beta$-Abfall auf 70,7 % |
| `RBM` | 10 Ω | 15 Ω | Eingangskennlinie |

Auffälligster Realitätsabgleich: Der echte Kniestrom (80 mA) liegt
sechsmal niedriger als der Demo-Wert — bei Arbeitspunkten oberhalb
einiger zehn Milliampere ist der $\beta$-Abfall beim BC547 also
**nicht** vernachlässigbar. Kapitel 8 rechnet mit genau diesem
gemessenen Satz.

**BC337-25 (Kurventracer, Geradenfits):** $I_S=4{,}8\cdot10^{-14}\,$A,
$n=1{,}004$, $\beta_F\approx274$, $V_A\approx146\,$V (Mittel);
$I_{KF}$ und $R_B$ nicht bestimmbar → Datenblatt (0,9 A; 60 Ω).

## 7.9 Über die Handauswertung hinaus: der globale Fit

Die Feature-für-Feature-Extraktion (Gerade hier, Plateau dort) nutzt
jeweils nur einen Ausschnitt der Daten. Man kann stattdessen **alle
fünf Kennlinienfelder gleichzeitig** an das komplette Modell aus
Kapitel 6.8 anpassen. In Durchlauf 1 geschieht das mit dem
**Nelder-Mead-Verfahren** (ableitungsfrei — es braucht nur
Funktionswerte, keine Gradienten). Die Kostenfunktion ist das mittlere
quadratische Residuum, datensatzweise gewichtet: der Gummel-Plot im
**logarithmischen** Maß (sonst dominieren die großen Ströme alles),
die übrigen Felder im **relativen** Maß.

Der globale Fit hat zwei Vorzüge — und eine Falle:

* Er nutzt die gesamte Information und mittelt Ablesefehler heraus.
* Er liefert **ein konsistentes Parameterset** statt einzeln
 bestimmter, potenziell widersprüchlicher Werte.
* Aber: Er konvergiert **immer** — auch auf Parameter, die die Daten
 gar nicht hergeben. Ob ein Wert dem Datensatz entstammt oder nur dem
 Startwert, sieht man dem Fit nicht an. Genau dafür braucht es den
 nächsten Abschnitt.

## 7.10 Der Transparenzschritt: Identifizierbarkeit

Ein Parameter ist nur dann *aus den Daten* bestimmbar, wenn die
Kostenfunktion **empfindlich** auf ihn reagiert. Der Test ist
denkbar einfach: jeden Parameter einzeln um $+20\,\%$ stören und
messen, um welchen Faktor die Kosten steigen. Für Durchlauf 1
(BC337-25):

| Parameter | Kostenfaktor bei $+20\,\%$ | bestimmbar? |
|---|---|---|
| $n$ | $\times\,2774$ | ja — dominant |
| $\beta_F$ | $\times\,28$ | ja |
| $I_S$ | $\times\,7{,}2$ | ja |
| $V_A$ | $\times\,1{,}07$ | schwach |
| $R_B$ | $\times\,1{,}19$ | schwach |
| $I_{KF}$ | $\times\,1{,}0$ | **nein** — Kostenfunktion flach |

Die Tabelle bestätigt quantitativ, was die Einzelschritte qualitativ
zeigten: $n$ ist über die Gummel-Steigung exzellent verankert, $I_S$
und $\beta_F$ solide; $V_A$ hängt an einer kleinen Steigung, $R_B$ an
einem kaum erreichten Hochstrombereich — und $I_{KF}$ hinterlässt im
Messfenster **keinerlei Signatur**. Man kann ihn nicht „aus dem Fehler
herausziehen"; jeder vom Fit gelieferte Wert wäre Scheingenauigkeit.

**Die Konsequenz als Regel:** *Nicht bestimmbare Parameter werden
offen als gesetzt deklariert (Datenblatt/Default) — und wer sie messen
will, braucht gezielte Zusatzmessungen* (Hochstrom-$\beta$ für
$I_{KF}$, Hochstrom-Gummel für $R_B$ — Durchlauf 2 hat für den BC547
genau das getan und $I_{KF}$ damit bestimmt).

## 7.11 Validierung: Modell gegen Messung

Der bestimmte Parametersatz muss sich an den Daten beweisen — an
**allen**, nicht nur an denen, aus denen er gewonnen wurde. In
Durchlauf 1 trifft das Modell alle fünf Kennlinienfelder mit
**1–2 % RMS-Abweichung**; die sichtbare Restabweichung bei kleinen
Strömen ist der in Kapitel 6.8 bewusst weggelassene Leckterm — sie ist
benannt statt versteckt. Der unabhängigste Test ist der Abgleich mit
dem Hersteller-SPICE-Modell: $I_S$, $V_A$ und $\beta_F$ des BC337-25
treffen die Datenblattwerte auf wenige Prozent.

![**Abbildung 7.5** — Gesamtschau der Extraktion (Durchlauf 1,
BC337-25), erzeugt mit `bjt_dashboard.py`: alle fünf Kennlinienfelder
mit Messpunkten und Modellkurven, Parametersatz, RMS-Fehler,
Identifizierbarkeits-Ampel und Datenblattabgleich. Dieses Bild dient
als kompakte Ergebnisübersicht — die lesbaren Einzelschritte zeigen
die Abbildungen 7.1 bis 7.4.](../bilder/kap07_dashboard.png){width=100%}

## 7.12 Unsicherheiten — und wie weit sie tragen

Wie genau müssen die Parameter überhaupt sein? Die Antwort fällt je
nach Blickrichtung verschieden aus — der Grund ist wieder die steile
Exponentialfunktion:

* **$V_{BE}$ ist robust gegen $I_S$-Fehler.** Aus
 $I_C=I_S\,e^{V_{BE}/(nV_T)}$ folgt für $\pm10\,\%$ Unsicherheit in
 $I_S$:
 $$\Delta V_{BE} = n\,V_T\,\ln(1{,}1) \approx
 1{,}01\cdot25{,}86\,\text{mV}\cdot0{,}0953 \approx 2{,}5\,\text{mV}.$$
 Zehn Prozent Stromfehler kosten also nur zweieinhalb Millivolt.
* **$I_C$ ist empfindlich in Gegenrichtung:** Bei festgehaltenem
 $V_{BE}$ geht ein $I_S$-Fehler proportional in $I_C$ ein. In einer
 realen Schaltung mit Basisvorwiderstand kompensiert die Rückkopplung
 über $R_B$ einen Teil davon — quantitativ zeigt das die
 Arbeitspunktrechnung in Kapitel 8.
* Dazu kommen Ablesefehler (±2–5 % am analogen Gerät, weniger bei
 digitaler Erfassung), thermische Drift (7.2) und die Serienstreuung,
 die jede Übertragung auf ein anderes Exemplar verbietet.

## 7.13 Zusammenfassung

1. Alle Parameter des Vorwärtsmodells folgen aus **drei Messreihen**
 in **fester Reihenfolge**: $I_S, n$ (Gummel-Gerade) → $\beta_F$
 (Plateau) → $V_A$ (Extrapolation) → $I_{KF}$ (70,7-%-Kriterium) →
 $R_{B,\text{int}}$ (Kennlinien-Kompression).
2. Jeder Schritt hat ein **Gültigkeitsfenster**; wer es verfehlt,
 erhält unphysikalische Werte ($n=3{,}5$!). Plausibilitätskontrolle
 gegen die Physik ist Teil der Methode.
3. Der **globale Fit** liefert konsistente Sätze, die
 **Identifizierbarkeitsanalyse** entscheidet, welche Werte den Daten
 entstammen — und welche nur gesetzt sind. Beide zusammen machen die
 Extraktion ehrlich.
4. Zwei Bauteile, zwei Messgeräte, eine Methode: BC337-25 und BC547
 liefern konsistente $I_S$, $n$, $\beta_F$, $V_A$ — und
 demonstrieren am $I_{KF}$, dass **das Messfenster** über
 Bestimmbarkeit entscheidet, nicht die Formel.

Damit hat das Modell aus Kapitel 6 Zahlen — belegte, mit benannten
Grenzen. **Kapitel 8** setzt diesen Parametersatz in eine reale
Schaltung ein und berechnet ihren Arbeitspunkt mit Newton-Raphson;
**Kapitel 9** lässt anschließend LTspice und Simulink mit denselben
Zahlen gegen die Messung antreten.

## Übungsaufgaben zu Kapitel 7

1. **Gummel-Auswertung:** Aus $V_{BE1}=0{,}580\,$V, $I_{C1}=0{,}1\,$mA
 und $V_{BE2}=0{,}640\,$V, $I_{C2}=1{,}0\,$mA bestimme man $n$ und
 $I_S$.
2. **Early-Spannung:** Bei $I_B=40\,\mu$A wurden
 $(3\,\text{V},\,11{,}5\,\text{mA})$ und
 $(15\,\text{V},\,12{,}4\,\text{mA})$ gemessen. Man berechne $V_A$.
3. **Knickstrom:** Im Plateau wurde $\beta_F=320$ gemessen. Bei
 welchem $\beta$-Wert liest man $I_{KF}$ ab, und wie grenzt man ihn
 messtechnisch in drei Schritten ein?
4. **Vollständige Rechnung:** Man übernehme den gemessenen
 BC547-Parametersatz (Abschnitt 7.8) in das Arbeitspunktprogramm aus
 Kapitel 8, führe die Bisektion durch und vergleiche mit der
 idealen Abschätzung.
5. **Sensitivität/Serienstreuung:** Man variiere $\beta_F$ über die
 Datenblatt-Klassengrenzen des BC547 (110…800) und berechne jeweils
 das erforderliche $R_B$ der Fixed-Bias-Schaltung. Welche Konsequenz
 hat die Spannweite für die Serienfertigung?
