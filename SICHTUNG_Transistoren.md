---
title: "Sichtung der Transistor-Unterlagen"
subtitle: "Was in die Veröffentlichung geht, was nicht, und warum — mit Doppelungen und ihrer Auflösung"
author: "Prof. Dr.-Ing. Ralph Wystup M.Sc. — erstellt mit KI und Agent (Claude Code, Anthropic)"
date: "29.09.2026"
lang: de
---

# Wozu dieses Blatt

Vorgabe des Verfassers: **„nur die neuesten Varianten nehmen"** und **„auch
durchsehen, ob etwas doppelt ist"**. Gesichtet wurde der Arbeitsbereich
rekursiv, nicht nur die oberste Ebene; Doppelungen wurden zweifach gesucht —
bitgleich über eine Prüfsumme (SHA-256 über 229 transistorbezogene Dateien)
und inhaltlich über Titel, Gliederung und Rechenweg.

**Der Text der Manuskripte ist an keiner Stelle gekürzt oder geändert worden.**
Dass dieselbe Herleitung in mehreren Manuskripten steht, ist deshalb **keine**
aufzulösende Doppelung, sondern Absicht: jedes Manuskript soll für sich
lesbar bleiben. Aufgelöst wurden nur **Datei**-Doppelungen: bitgleiche Kopien
liegen in der Auslieferung genau einmal.

---

# 1 Die eigenen Manuskripte mit Markdown als Quelle

| Datei | Datum | Thema | jünger/älter | Doppelung | Entscheidung |
|:--|:--|:--|:--|:--|:--|
| `MANUSKRIPT_Transistor_v2.md` | 10.07.2026 | Gummel-Poon → h-Parameter, BC337-25, Vierquadrantenfeld | — | `MANUSKRIPT_Transistor_v2.pdf` liegt auf C: zweimal | **genommen** als `manuskripte/86_gummel_poon_h_parameter.md`, Reiter „Kleinsignal und h-Parameter" |
| `MANUSKRIPT_Vierpol_Verstaerker.md` | 26.09.2026 | Emitterschaltung als Vierpol-Kette, Kettenmatrizen, Kenngrößen | jünger als die `.docx` vom 27.07. | `MANUSKRIPT_Vierpol_Verstaerker.docx` (27.07.) ist die ältere Fassung | **genommen** als `manuskripte/87_vierpol_verstaerker.md`, Reiter „Vierpol-Verstärker"; die `.docx` bleibt draußen |
| `BUCH/kapitel_06_gummel_poon.md` | 04.08.2026 | Gummel-Poon mit vollständigen Herleitungen | — | — | **genommen** als `manuskripte/60_gummel_poon.md`, Reiter „Gummel-Poon" |
| `BUCH/kapitel_07_parameterextraktion.md` | 26.09.2026 | Extraktion am BC337-25, Identifizierbarkeit | — | — | **genommen** als `manuskripte/70_parameterextraktion.md`, Reiter „Parameterextraktion" |
| `BUCH/kapitel_08_arbeitspunkt_newton.md` | 26.09.2026 | blaue LED, Fixed-Bias, Newton, Bisektion | — | — | **genommen** als `manuskripte/80_arbeitspunkt_newton.md`, Reiter „Arbeitspunkt Newton" |
| `BUCH/kapitel_09_simulation.md` | 26.09.2026 | eigener Löser gegen LTspice gegen Simulink | — | — | **genommen** als `manuskripte/85_simulation.md`, Reiter „Simulation und SPICE" |
| `SICHTUNGSBERICHT_Transistor_Buch.md` | 04.08.2026 | Bewertung aller Quellen für das Buchprojekt | — | `.docx` derselben Datei daneben | **nicht veröffentlicht**: er verweist durchgehend auf die Klausur- und Musterlösungsunterlagen, die draußen bleiben; als Eingangsmaterial dieser Sichtung benutzt |

# 2 Die nur als .docx vorliegenden Manuskripte (von C: geholt)

Alle sieben sind nach Markdown umgesetzt worden — **inhaltstreu**, mit
Gegenprobe Wort für Wort (Ergebnis in Abschnitt 5).

| Datei | Datum | Thema | jünger/älter | Doppelung | Entscheidung |
|:--|:--|:--|:--|:--|:--|
| `Manuskript_Diodenkennlinie_1.docx` | 30.06.2026 | Shockley, Ausgleichsrechnung, Newton, Bisektion an der Diode | — | liegt **zweimal**: `BUCH/` und `Transistoren/Quellen/` — **bitgleich** | **genommen** als `manuskripte/10_diodenkennlinie.md`, Reiter „Diodenkennlinie"; in der Auslieferung einmal |
| `LED_Manuskript_v2.docx` (`pi_stream_setup/`) | 23.06.2026 | erweiterte Shockley-Gleichung, blaue LED | jünger als `LED_Vorlesungsmanuskript.docx` | das zugehörige Programm liegt zweimal: `pi_stream_setup/Aproximation_AP_LED_5_erweiterte_Shockly.py` und `bilder/Aproximation_AP_LED_5.py`, **bitgleich** | **v2 genommen** als `manuskripte/11_led.md`, Reiter „Leuchtdiode"; das Programm wird nicht mitgeliefert (die Rechnung steckt in `rechnung/kap08_led_quellen.py`) |
| `Vorlesungsmanuskript_BJT_SPICE_RW.docx` | 30.06.2026 | erweitertes SPICE-Modell, Jacobi-Matrix, Bisektion | — | liegt in zwei Ordnern auf C: | **genommen** als `manuskripte/20_bjt_spice.md`, Reiter „BJT und SPICE" |
| `Vorlesungsmanuskript_Parameterextraktion_BC547.docx` | 30.06.2026 | Extraktion Schritt für Schritt am BC547 | — | — | **genommen** als `manuskripte/30_extraktion_bc547.md`, Reiter „Extraktion BC547" |
| `Transistor_Manuskript (1).docx` | 07.06.2026 | Arbeitspunkt der Kollektorschaltung, `Transistor_20.py` | — | **keine** Vorstufe von `MANUSKRIPT_Transistor_v2.md` — anderes Thema, anderes Programm (siehe unten) | **genommen** als `manuskripte/40_arbeitspunkt_transistor20.md`, Reiter „Arbeitspunkt von Hand" |
| `Für ein einfaches statisches BJT.docx` | 24.06.2026 | welche Kennfelder man mindestens braucht | — | vier eingebettete Dateien (2 × `.asc`, `.py`, `.pdf`) liegen als Symbole im Text | **genommen** als `manuskripte/41_minimaler_datensatz.md`, Reiter „Minimaler Datensatz"; die Symbole durch einen Hinweis ersetzt, die Dateien selbst liegen in `spice/` bzw. `pc/` |
| `Messvorschrift_SPICE_Parameter_Transistor.docx` | 30.06.2026 | Laborunterlage, npn und pnp | — | — | **genommen** als Anhang A |
| `Kennlinienschreiber_ESP32_Code_Arduino.docx` | 29.09.2026 (geholt) | Beschreibung des ESP32-Programms | — | der Sketch selbst liegt entpackt in `Kennlinienschreiber/sketch/` | **genommen** als `manuskripte/50_esp32_programm.md`, Reiter „Der Transistortester"; der Sketch gehört zum Repositorium des Kennlinienschreibers und wird hier nicht noch einmal mitgeliefert |

**Zur angenommenen Vorstufe.** Der Auftrag nannte
`Transistor_Manuskript (1).docx` (07.06.) als Vorstufe von
`MANUSKRIPT_Transistor_v2.md` (10.07.). Die Prüfung am Inhalt ergibt etwas
anderes: die `.docx` heißt *Numerische Simulation eines Bipolartransistors —
Arbeitspunktberechnung mit Newton-Raphson und Bisektionsverfahren* und
beschreibt `Transistor_20.py`; die `.md` heißt *Vom Gummel-Poon-Modell zu den
h-Parametern* und beschreibt Modell, Parameterbestimmung und Kleinsignalverhalten.
Gemeinsam ist nur das Bauelement. **Beide sind übernommen**, als Reiter „Arbeitspunkt von Hand"
und Reiter „Kleinsignal und h-Parameter".

# 3 Die neu hinzugekommenen Quellen (29.09.2026)

| Datei | Thema | Entscheidung |
|:--|:--|:--|
| `Schematic_Kennlinien-Schreiber_2025-07-24.pdf` | der gezeichnete Schaltplan des Geräts, zwei Blätter | **genommen**: als PDF in `bilder/` und als zwei PNG im Manuskript; der Name im Schriftfeld ist buchstabengleich durch „x" ersetzt |
| `transistor_kennlinie 5_neu.py` | Python-Fassung des Schreibers, neueste der Reihe 2…5 | **genommen** nach `pc/`; die älteren Fassungen 2…4 bleiben draußen |
| `Kennlinienschreiber_1.py` | frühere Fassung derselben Steuerung | **genommen** nach `pc/` — sie ist keine Vorstufe von `transistor_kennlinie 5_neu.py`, sondern ein eigener Aufruf mit Kommandozeile |
| `Messungen/*.csv` (neun Reihen) | echte Kennlinienaufnahmen vom 10./16.06.2026 | **genommen** nach `messungen/`, ausgewertet in Reiter „Der Transistortester" und auf der Seite |
| `Trendows.exe`, `.ELA`-Projektdateien, `Kennlinien-Schreiber.zip` | Fremdsoftware bzw. Bindeformat | **draußen** |

# 4 Vorlesungsunterlagen — alle draußen, mit Begründung

Die Alt-Vorlesungen im `.docx`-Format und die Foliensätze tragen ihre Formeln
**ausschließlich als Bilder** in den Formaten WMF und EMF. Die Zahl steht in
Klammern:

| Datei | Wörter | Bilder | Befund |
|:--|--:|--:|:--|
| `1_Transistoren Einleitung_b.docx` | 948 | 24 (12 WMF) | Geschichte des Transistors, echte Prosa |
| `2_Vierpole für Transistortheorie_b.docx` | 2435 | 90 (68 WMF, 12 EMF) | umfangreichste Alt-Quelle; liegt **zweimal**: Wurzel und `bilder/`, **bitgleich** |
| `3b_Transistoren Modelle_Grossignalverhalten_Zusatz.docx` | 566 | 27 (12 WMF) | Ebers-Moll, Transportmodell |
| `4_Transitor Kennfelder_Grossignalverhalten.docx` | 112 | 13 (8 WMF) | fast nur Abbildungen |
| `6_Transistoren Kleinsignalverhalten_b.docx` | 618 | 28 (21 WMF) | durchgerechnete Aufgabe, Zahlen nur im Bild |
| `7_Transistoren Millereffekt und Grenzfrequenzen_a.docx` | 38 | 7 (5 WMF) | nur Bilder |
| `Transistormodell_Newton_2.docx` | 922 | 46 (3 EMF) | Newton am Transistormodell, 41 PNG-Formeln |
| zwölf Foliensätze (`*.pptx`) | 10…30 je Folie | teils über 1000 Fragmente | Abbildungen und Gliederung, kaum Fließtext |

**Entscheidung: nicht veröffentlicht.** Zwei Gründe, beide hart:

1. Auf diesem Rechner steht **kein Umsetzer für WMF/EMF** zur Verfügung
   (kein LibreOffice, kein Inkscape, keine passende Bibliothek). Eine
   Umsetzung nach Markdown wäre also nicht inhaltstreu — die Formeln fielen
   weg. Der Auftrag verlangt aber ausdrücklich Inhaltstreue.
2. Vorgabe 15 lautet: **jedes Bild ansehen.** Ein Bild, das sich nicht
   darstellen lässt, lässt sich nicht ansehen — und was man nicht angesehen
   hat, wird nicht veröffentlicht. Bei rund 250 solchen Bildern ist das keine
   Formsache.

**Was dadurch fehlt und wo es trotzdem steht:** Die Sachverhalte dieser
Unterlagen — Ebers-Moll und Transportmodell, Vierpolbegriff, Linearisierung
über die zweidimensionale Taylorreihe, h-Parameter als Hybridparameter,
Kettenschaltung, Miller-Effekt und Grenzfrequenzen — stehen **vollständig
hergeleitet** in den übernommenen Manuskripten (Reiter „BJT und SPICE", „Gummel-Poon", „Kleinsignal und h-Parameter", „Vierpol-Verstärker") und
als rechnendes Werkzeug auf der Seite (Reiter „Kleinsignal" und
„Verstärker & Miller"). Es geht also kein Inhalt verloren, nur diese
bestimmten Dateien.

**Ein konkreter Fund dazu:** In
`2b_Kennlinienschreiber_Trendows_2.pptx` steht auf **Folie 2** ein
Firmenverweis (eine Netzadresse eines Unternehmens). Der Foliensatz wäre
allein deshalb zu neutralisieren gewesen; er bleibt ohnehin draußen.

# 5 Die Gegenprobe der Umsetzung .docx → Markdown

Gezählt wird vor und nach der Umsetzung: jedes Wort des
Originals außerhalb der Formeln, die Zahl der abgesetzten und der im Text
stehenden Formeln, die Zahl der Bilder. Gemeldet wird jedes Wort, das im
Markdown fehlt.

| Dokument | Wörter docx / md | Formeln docx / md | Bilder docx / md | fehlende Wörter |
|:--|--:|--:|--:|--:|
| 10_diodenkennlinie | 1995 / 2000 | 1 / 1 | 0 / 0 | **0** |
| 11_led | 1597 / 1606 | 0 / 0 | 0 / 0 | **0** |
| 20_bjt_spice | 1670 / 1670 | 70 / 70 | 2 / 2 | **0** |
| 30_extraktion_bc547 | 2217 / 2217 | 0 / 0 | 0 / 0 | **0** |
| 40_arbeitspunkt_transistor20 | 2354 / 2366 | 0 / 0 | 0 / 0 | **0** |
| 41_minimaler_datensatz | 1315 / 1350 | 119 / 119 | 7 / 3 (+ 4 Dateisymbole) | **0** |
| 50_esp32_programm | 988 / 988 | 0 / 0 | 0 / 0 | **0** |
| 90_messvorschrift | 924 / 924 | 0 / 0 | 0 / 0 | **0** |

Dass die Markdown-Seite gelegentlich ein paar Wörter **mehr** hat, liegt an
den Beschriftungen, die pandoc beim Setzen von Tabellen einfügt. Entscheidend
ist die letzte Spalte: **kein Wort des Originals fehlt**, und keine Formel.

Die vier „Dateisymbole" in `41_minimaler_datensatz` sind keine Abbildungen,
sondern die EMF-Symbole eingebetteter Dateien (`Eigen_RW_1c.asc`,
`Eigen_RW_1d.asc`, `Transistor_21b.py`, `Transistor_Manuskript (1).pdf`). Sie
zeigen nur ein Aktensymbol mit dem Dateinamen; an ihrer Stelle steht jetzt ein
Hinweis, und die Dateien selbst liegen in `spice/` und `pc/`.

# 6 Datei-Doppelungen und ihre Auflösung

Gesucht über SHA-256 über 229 transistorbezogene Dateien des Arbeitsbereichs.
**41 Prüfsummen kamen mehrfach vor.** Die meisten davon sind harmlos, weil
Arbeitskopie und Ausfuhrkopie naturgemäß gleich sind. Die echten:

| Doppelung | Fundorte | Entscheidung |
|:--|:--|:--|
| `Manuskript_Diodenkennlinie_1.docx` | `BUCH/`, `Transistoren/Quellen/` | eine Quelle, **einmal** in der Auslieferung (als `manuskripte/10_diodenkennlinie.md`) |
| `2_Vierpole für Transistortheorie_b.docx` | Wurzel, `bilder/` | bleibt ganz draußen (Abschnitt 4) |
| `Aproximation_AP_LED_5*.py` | `pi_stream_setup/`, `bilder/` | bleibt draußen; die Rechnung steckt in `rechnung/kap08_led_quellen.py` |
| `bjt_*.py`, `Ic_*.txt`, `hFE_*.txt` | Wurzel, `Kennlinienschreiber/rechnung/`, Ausfuhr | **ein Ablageort**: `Kennlinienschreiber/rechnung/` ist die Quelle, aus der das Bauskript kopiert; in der Auslieferung liegt jede Datei **einmal** |
| `bjt_4quadrant.png`, `bjt_hparam.png`, `bjt_verstaerker.png` | je fünfmal, u. a. `Musterloesung_Bilder/` | die Musterlösungsbilder bleiben draußen; im Werk liegt jedes Bild einmal, erzeugt aus seinem Programm |
| `bjt_gesamt.png` (209 482 B) gegen `BUCH/bilder/kap06_kennlinien.png` = die gleichnamige Datei im Wurzelverzeichnis des Arbeitsbereichs (209 489 B) | zwei Wiedergaben derselben Abbildung | **aufgelöst**: der Lauf vom 29.09.2026 ist maßgeblich; Reiter „Gummel-Poon" fordert `kap06_kennlinien.png` gar nicht an, also geht nur die aktuelle mit. Der Unterschied ist in `BERICHTIGUNGEN.md` unter B10 festgehalten |
| `kap07_dashboard.png` / `bjt_dashboard.png`, `kap07_extraktion.png` / `bjt_extraction.png` | zwei Wiedergaben | beide Namen werden von Teilmanuskripten angefordert; **beide gehen mit**, der Befund steht in `BERICHTIGUNGEN.md` unter B10. Den Text zu ändern wäre ein Eingriff in das Manuskript |

**Probe am Ergebnis:** im Ausfuhrordner gibt es unter 115 Dateien
**null bitgleiche Doppelungen**.

27 Dateien sind bitgleich mit dem Nachbar-Repositorium des
Kennlinienschreibers (die `bjt_*.py`, die Messdateien, das Foto, LICENSE). Das
ist gewollt: jede Veröffentlichung muss **ohne Gegenstelle vollständig** sein.

# 7 Inhaltliche Doppelungen — bewusst stehen gelassen

Nach der Klarstellung des Verfassers („nicht kürzen, nicht im Inhalt ändern")
bleibt jede Herleitung dort, wo sie steht. Gefunden und **nicht** angetastet:

| Sachverhalt | steht in | Umgang |
|:--|:--|:--|
| Shockley-Gleichung | Reiter „Diodenkennlinie" (Diode), 5 (LED), 6 (BJT), 7 | alle vier bleiben; jede ist für ihren Zweck geschrieben |
| Gummel-Poon mit Early, Webster und $R_{B,\text{int}}$ | Reiter „BJT und SPICE", „Gummel-Poon", „Minimaler Datensatz", „Kleinsignal und h-Parameter" | alle vier bleiben |
| Newton-Raphson | Reiter „Diodenkennlinie", „BJT und SPICE", „Arbeitspunkt von Hand", „Arbeitspunkt Newton", „Vierpol-Verstärker" | alle fünf bleiben |
| Bisektion | Reiter „Diodenkennlinie", „BJT und SPICE", „Arbeitspunkt von Hand", „Arbeitspunkt Newton", „Simulation und SPICE" | alle fünf bleiben |
| h-Parameter aus den Leitwerten | Reiter „Kleinsignal und h-Parameter", „Vierpol-Verstärker" | beide bleiben |
| Umrechnung h → A | Reiter „Vierpol-Verstärker" | einmal |

Der Eröffnungsreiter der Seite sagt das ausdrücklich, damit der Leser es
nicht für ein Versehen hält.

# 8 Was ausdrücklich draußen bleibt

* `Musterloesung_Probeklausur_Transistoren_SS2026.*` und die zugehörigen
  `Musterloesung_Bilder/fig_a*` — Klausurmaterial, kein Einverständnis.
* `BUCH/kap09_op_schaltbild.py` — greift auf ein Sitzungsverzeichnis mit
  Klausurmaterial zu und erzeugt zwei Bilder, die kein Kapitel einbindet
  (Befund B9, festgehalten in `BERICHTIGUNGEN.md`).
* Alle Unterlagen ohne Transistorbezug (Leistungselektronik, Operations-
  verstärker, Monte-Carlo, FEM, Bahnkurven) — sie gehören in andere Arbeiten.
* Fremdsoftware und deren Projektdateien.
