---
title: "Berichtigungen"
subtitle: "Was nach der Befundliste an den Manuskripten berichtigt wurde — jede Änderung einzeln"
author: "Prof. Dr.-Ing. Ralph Wystup M.Sc. — erstellt mit KI und Agent (Claude Code, Anthropic)"
date: "29.09.2026"
lang: de
---

# Wozu dieses Blatt

Beim Zusammenstellen dieser Arbeit sind zwölf Stellen aufgefallen, an denen zwei
Manuskripte dieselbe Größe verschieden angeben, an denen eine Abbildung etwas
anderes zeigt als der Text daneben, oder an denen ein Manuskript und ein Programm
auseinandergehen. Jede Stelle wurde nachgerechnet und dem Verfasser vorgelegt; er
hat die Vorschläge angenommen.

Umgesetzt ist **genau das, was vorgeschlagen war, und sonst nichts**. Wo ein
Vorschlag zwei Wege offenließ, ist der gewählt, der den **Zahlenwert unangetastet**
lässt. Alles übrige steht Wort für Wort, wie es stand.

Die Berichtigungen greifen **nur in der Auslieferung**; die Dateien im
Arbeitsbereich des Verfassers sind unberührt geblieben.


# Die Änderungen einzeln

## B1 — 11_led.md, Formelkasten der Übersicht

**Vorher:**

```
**V_T = k·T / q ≈ 25,85 mV bei 25 °C**
```

**Nachher:**

```
**V_T = k·T / q ≈ 25,85 mV bei 300 K**
```

**Grund:** 25,85 mV gehört zu 300 K; bei 25 °C (298,15 K) wäre V_T = 25,69 mV. Berichtigt wird die Temperaturangabe, der Zahlenwert bleibt stehen.

## B1 — 11_led.md, Symboltabelle, Zeile V_T

**Vorher:**

```
Temperaturspannung k·T/q. Bei 25°C = 25,85 mV.
```

**Nachher:**

```
Temperaturspannung k·T/q. Bei 300 K = 25,85 mV.
```

**Grund:** Dieselbe Temperaturangabe wie im Formelkasten, gleich berichtigt.

## B2 — 86_gummel_poon_h_parameter.md, Abschnitt 2.5, hinter den Annahmen zum vollständigen Gleichungssystem

**Vorher:**

```
**Annahmen:** Aktivbetrieb (keine Sättigung, kein Inversbetrieb), $T=300\,\text{K}$, Niedriginjektion außer der über $I_{KF}$ erfassten Hochstromkorrektur.
```

**Nachher:**

```
**Annahmen:** Aktivbetrieb (keine Sättigung, kein Inversbetrieb), $T=300\,\text{K}$, Niedriginjektion außer der über $I_{KF}$ erfassten Hochstromkorrektur.

**Zwei Formulierungen nebeneinander.** Im Exponenten des *Kollektor*stroms steht hier die Klemmenspannung $V_{BE}$; das Vorlesungsmanuskript *BJT-SPICE* setzt an derselben Stelle die innere Spannung $V_{BE,\text{eff}}$ ein, weil der Übergang für beide Ströme dieselbe innere Spannung sieht. Beide Rechnungen sind in sich richtig — $I_S$ nimmt den Unterschied auf —, aber die Parameter der einen Form dürfen nicht in das Programm der anderen eingesetzt werden. Der Unterschied ist der Faktor $\exp\!\big(I_B R_{B,\text{int}}/(n V_T)\big)$: beim BC337-25 mit $I_C=5\,$mA, $V_{CE}=5\,$V ($I_B=18{,}58\,\mu$A, $R_{B,\text{int}}=60\,\Omega$) sind das 1,115 mV und damit **+4,4 %** in $I_C$; beim BC547 im Fixed-Bias-Arbeitspunkt ($I_C=125\,$mA, $I_B=650{,}5\,\mu$A, $R_{B,\text{int}}=15\,\Omega$) sind es 9,758 mV und **+45,3 %**.
```

**Grund:** Zwei Manuskripte setzen im Exponenten des Kollektorstroms verschiedene Spannungen ein. Die Befundliste schlägt vor, keine Formel zu ändern, sondern an einer der beiden Stellen einen Satz zu ergänzen, der den Unterschied beziffert — das ist hier geschehen.

## B3 — 20_bjt_spice.md, Abschnitt 3.1.3, hinter der Näherung für den Ausgangsleitwert

**Vorher:**

```
Da der Ausdruck vor $1/V_{A}$ genau der Arbeitspunkt‑Kollektorstrom ist, gilt:

$$g_{CE} \approx \frac{I_{C}}{V_{A}}$$
```

**Nachher:**

```
Da der Ausdruck vor $1/V_{A}$ genau der Arbeitspunkt‑Kollektorstrom ist, gilt:

$$g_{CE} \approx \frac{I_{C}}{V_{A}}$$

Exakt ist dabei

$$g_{CE} = \frac{I_{C}}{V_{A} + V_{CE}},$$

denn $I_{C}$ enthält bereits den Faktor $(1+V_{CE}/V_{A})$. Der relative Abstand zwischen Näherung und exaktem Ausdruck ist genau $V_{CE}/V_{A}$: bei $V_{A}=146\text{ V}$ und $V_{CE}=5\text{ V}$ sind das 3,4 %, bei $V_{A}=95\text{ V}$ und $V_{CE}=12{,}5\text{ V}$ schon 13,2 %.
```

**Grund:** Die Näherung $I_C/V_A$ und der exakte Ausdruck $I_C/(V_A+V_{CE})$ stehen in zwei Manuskripten nebeneinander. Vorschlag der Befundliste: den exakten Ausdruck danebenstellen und den Abstand $V_{CE}/V_A$ nennen. Keine Formel geändert, nur ergänzt.

## B4 — 30_extraktion_bc547.md, Abschnitt 9.3, Bewertung der idealen Abschätzung von R_B

**Vorher:**

```
weicht davon typischerweise um wenige Prozent ab
```

**Nachher:**

```
weicht davon je nach Lage zum Kniestrom ab — im vorliegenden Fall ($I_C/I_{KF}$ = 1,56) um ein Drittel: der Abschätzung 56,3 kΩ steht der Modellwert 37,3 kΩ gegenüber
```

**Grund:** Die Abschätzung liegt nicht um wenige Prozent, sondern um 34 % neben dem Modellwert, weil I_C in die Nähe des Kniestroms I_KF kommt (β_eff = 181 statt 290). Wortlaut nach dem Vorschlag der Befundliste.

## B5 — 80_arbeitspunkt_newton.md, Bildunterschrift zu Abbildung 8.5

**Vorher:**

```
![**Abbildung 8.5** — Konvergenzverhalten: links Newton-Raphson
(quadratisch — die Fehlerkurve stürzt nach wenigen Schritten unter
$10^{-10}$), rechts die Bisektion (linear — eine Halbierung je
Schritt).]
```

**Nachher:**

```
![**Abbildung 8.5** — Konvergenzverhalten: links Newton-Raphson. Vom
Startwert $V_{BE}=0{,}65\,$V aus schießt der erste Schritt über die
$e$-Funktion hinaus; danach folgen rund 42 Schritte gedämpfter Abstieg mit
dem Faktor $1/e$ je Schritt (eine Gerade im logarithmischen Bild, denn jeder
Schritt senkt $V_{BE}$ um genau $n V_T$), und erst die letzten vier Schritte
sind quadratisch: bei $k=48$ fällt $\|F\|$ unter $10^{-10}$. Rechts die
Bisektion (linear — eine Halbierung je Schritt), die nach zehn Schritten im
Toleranzband liegt. Die Überschrift im Bild selbst nennt nur den letzten,
quadratischen Abschnitt; sie stammt aus `kap08_rechnung.py` und ist dort
unverändert geblieben.]
```

**Grund:** Das Protokoll aus kap08_rechnung.py zeigt 42 Schritte linearen Abstiegs und erst vier quadratische; unter 10⁻¹⁰ fällt ‖F‖ bei k = 48, nicht „nach wenigen Schritten“. Die Bildüberschrift im PNG stammt aus seinem Programm und bleibt, weil seine Programme unverändert ausgeliefert werden.

## B5 — 80_arbeitspunkt_newton.md, Abschnitt 8.7, Rechenbeispiel zum Startpunkt

**Vorher:**

```
Der Startpunkt liegt daneben, wie erwartet. Nach **sechs
> Newton-Raphson-Schritten** ist $\|F\|<10^{-10}$ (Abbildung 8.5
> links) — jede Iteration in Millisekunden.
```

**Nachher:**

```
Der Startpunkt liegt daneben, wie erwartet. Nach **48
> Newton-Raphson-Schritten** ist $\|F\|<10^{-10}$ (Abbildung 8.5
> links) — jede Iteration in Millisekunden.
```

**Grund:** Dieselbe Zahl wie in der Bildunterschrift: das Protokoll zählt 48 Schritte, nicht sechs. Ohne diese Stelle widerspräche der Text der berichtigten Bildunterschrift.

## B6 — 86_gummel_poon_h_parameter.md, Abschnitt 5.6, Rechenbeispiel BC337-25

**Vorher:**

```
h_{12e}\approx 0.
$$
```

**Nachher:**

```
h_{12e}\approx 0.
$$

**Warum das Programm 1,45 kΩ ausgibt.** Die kompakte Formel $h_{11e}=\beta\,nV_T/I_C$ enthält den Basisbahnwiderstand nicht. `bjt_hparam.py` leitet dieselbe Größe aus dem gefitteten Modell ab, in dem $R_{B,\text{int}}=60\,\Omega$ steckt, und kommt deshalb auf $h_{11e}=1452{,}7\,\Omega$ und $h_{21e}=279{,}8$ — rund 2 % über dem Wert der kompakten Formel. Von Hand nachgerechnet: $nV_T/I_B + R_{B,\text{int}} = 1396{,}7\,\Omega + 60\,\Omega = 1456{,}7\,\Omega$.
```

**Grund:** Text und Bild nennen verschiedene h-Parameter (274 / 1,42 kΩ gegen 280 / 1,45 kΩ). Von den beiden Wegen, die die Befundliste offenlässt, ist der gewählt, der den Zahlenwert im Text unangetastet lässt und den Unterschied erklärt.

## B11 — 20_bjt_spice.md, Abschnitt 2.1, Einführung des Sättigungsstroms

**Vorher:**

```
Der Sättigungsstrom *I*₂ (SPICE: IS)
```

**Nachher:**

```
Der Sättigungsstrom *I*ₛ (SPICE: IS)
```

**Grund:** Das tiefgestellte S ist beim Speichern der Vorlage zur Ziffer 2 geworden; gemeint ist I_S, wie die Klammer „SPICE: IS“ daneben zeigt.

## B11 — 20_bjt_spice.md, Abschnitt 7.2, Jacobi-Matrix

**Vorher:**

```
\frac{\partial f_{1}}{\partial V_{BE}} & \frac{\partial f_{1}}{\partial V_{CE}}\ \text{\textbackslash}\frac{\partial f_{2}}{\partial V_{BE}} & \frac{\partial f_{2}}{\partial V_{CE}}
```

**Nachher:**

```
\frac{\partial f_{1}}{\partial V_{BE}} & \frac{\partial f_{1}}{\partial V_{CE}} \\
\frac{\partial f_{2}}{\partial V_{BE}} & \frac{\partial f_{2}}{\partial V_{CE}}
```

**Grund:** Der Zeilenumbruch der Matrix ist beim Speichern der Vorlage zu einem hineingeratenen \textbackslash geworden; die Matrix erschien als 1 × 4 statt als 2 × 2.

# Befunde ohne Textänderung

Nicht jeder Befund war eine Stelle im Text. Diese hier sind auf anderem Weg erledigt — oder ausdrücklich **nicht** erledigt, mit Begründung.

## B7 — drei Zahlenpaare für denselben Transistor (`kennwerte.json`, `bjt_dashboard.png`, Manuskript 86)

**Getan:** Die beiden abweichenden Sätze („Arbeitssatz“, „Fitsatz“) stammten aus einem Hilfsskript, das nicht vom Verfasser ist; es ist samt `kennwerte.json` aus der Auslieferung entfernt. Damit bleiben nur seine eigenen Parametersätze. Welcher Satz aus welchem seiner Programme kommt und wo er verwendet wird, steht jetzt als Tabelle im Reiter „Parameterextraktion“ der Seite — nicht in seinen Manuskripten.

**Grund:** Der Vorschlag verlangte eine Übersicht vor dem Kapitel 10 des Gesamtmanuskripts; dieses Gesamtmanuskript gibt es nicht mehr, deshalb steht die Übersicht in der Seite.

## B8 — Referenzspannung des Analog-Digital-Umsetzers (Schaltplan: „Uref 4.095“, Rechnung: 4,096 V)

**Getan:** Der Schaltplan ist eine Zeichnung des Verfassers und bleibt unverändert. Der Halbsatz dazu — Nennwert der internen Referenz des AD7682 ist 4,096 V, der Vermerk im Schaltplan nennt den Vollbereich; der Unterschied beträgt 2,95 mV von 12,1 V, also 0,024 % — steht im Reiter „Der Transistortester“ der Seite.

**Grund:** Der Vorschlag nannte „im Manuskript einen Halbsatz“; in seinen Manuskripten gibt es keine Stelle dazu, deshalb steht er in der Seite.

## B9 — `kap09_plots.py` und `kap09_op_schaltbild.py` greifen auf ein Sitzungsverzeichnis mit Klausurmaterial zu

**Getan:** `kap09_op_schaltbild.py` wird nicht mitgeliefert. In der Ausfuhrkopie von `kap09_plots.py` steht an Stelle des festen Rechnerpfads ein sprechender Platzhalter; im Arbeitsbereich bleibt der Pfad stehen, damit das Programm dort weiter läuft.

**Grund:** Ein fester Rechnerpfad gehört nicht in eine Veröffentlichung, und die beiden Bilder, die danach entstehen sollen, bindet kein Kapitel ein.

## B10 — drei Abbildungen lagen unter zwei Namen vor (zwei Läufe desselben Programms)

**Getan:** In der Auslieferung liegt jedes Bild genau einmal, unter dem Namen, den das Manuskript anfordert, und in der Fassung, die das zugehörige Programm des Verfassers heute erzeugt. Im Arbeitsbereich ist nichts gelöscht.

**Grund:** Doppelt abgelegte Bilder aus zwei Läufen widersprechen der Regel, dass es für jedes Bild genau einen Ablageort gibt.

## B11 — drei Schönheitsfehler in Abbildungen: abgeschnittener Titel in `kap08_lastgerade.png`, verdeckte Beschriftung in `kap07_zweipunkt.png`, Pfeil außerhalb der Zeichenfläche in `kap07_beta_mess.png`

**Getan:** **Nicht berichtigt.** Alle drei Bilder erzeugen Programme des Verfassers (`kap08_rechnung.py`, `kap07_plots.py`); sie berichtigen hieße, in seine Programme einzugreifen.

**Grund:** Seine Programme gehen unverändert hinaus — das geht der kosmetischen Berichtigung vor. Die Stellen sind hier festgehalten, damit er selbst entscheiden kann.

## B12 — BC547, BC337-25 und der Prüfling der CSV-Reihen sind drei verschiedene Transistoren

**Getan:** Der vorgeschlagene Satz steht im Eröffnungsreiter der Seite. Sonst war an diesem Befund nichts zu tun — er hält fest, was geprüft wurde und wobei nichts aufgefallen ist.

**Grund:** Der Vorschlag nannte „ein Satz im Vorwort“; ein Vorwort gibt es nicht mehr, weil die Teilmanuskripte einzeln bleiben.

# Was sich am Bestand geändert hat

Zwei Dinge sind beim Zusammenstellen aufgefallen, die keine Befunde der Liste sind, aber dieselbe Sorgfalt verlangen — beide betreffen die **Umsetzung** von `.docx` nach Markdown, nicht den Text des Verfassers:

* Das Teilmanuskript zum ESP32-Programm bestand aus 294 Absätzen Quelltext, die der Umsetzer als Fließtext gesetzt hatte; Einrückung und Zeilenstruktur des Programms waren damit zerstört. Es ist jetzt als Quelltextblock gesetzt — **dieselbe Wortfolge**, 1533 von 1533 Zeichenketten, nur wieder lesbar.
* Das schließende deutsche Anführungszeichen („…“) war an neun Stellen zu einem geraden Zoll-Zeichen geworden. Wiederhergestellt.
