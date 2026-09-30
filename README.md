# Transistoren, der Transistortester und die daraus erzeugten Modelle

<img src="Foto_Ralph_Wystup.jpg" align="right" width="140" alt="Prof. Dr.-Ing. Ralph Wystup">

Prof. Dr.-Ing. Ralph Wystup M.Sc. — erstellt mit KI und Agent (Claude Code, Anthropic)

**Seite öffnen:** https://ralphwystup.github.io/Transistoren-Transistortester-und-daraus-erzeugte-Modelle/ — **von der Messung zum eigenen Berechnungsverfahren.**
Aus selbst gemessenen Kennlinien werden selbst ermittelte Parameter, und mit diesen
Parametern rechnet ein selbst geschriebener Löser eine ganze Schaltung durch. Vierzehn
der fünfzehn Reiter tragen **ein Teilmanuskript** vollständig und unverändert, darunter
den **rechnenden Teil zu genau diesem Thema**; die Manuskripte sind der Hintergrund und
der Lernapparat, der rechnende Teil darüber ist die Probe darauf. Läuft offline, ohne
Nachladen.

Ein selbstgebauter Transistortester nimmt die Kennlinien auf. Aus ihnen wird ein
Gummel-Poon-Modell bestimmt — einmal von Hand aus zwei abgelesenen Punkten, einmal als
Gesamtausgleich über alle Kurven, jedes Mal mit der Frage, welcher Parameter aus diesen
Daten überhaupt bestimmbar ist. Mit dem Modell wird der Arbeitspunkt einer Schaltung
gerechnet (Newton-Raphson innen, Bisektion außen), daraus das Kleinsignalverhalten
abgeleitet, und daraus über Kettenmatrizen der Verstärker. Gegengeprüft wird gegen
LTspice.

## Der fünfzehnte Reiter: „Netzliste und Löser"

Er trägt als einziger **kein** Teilmanuskript und steht ausdrücklich *neben* dem
Kapitel 9, nicht darin. Dort wird die Schaltung **nicht mehr als von Hand
aufgestelltes Gleichungssystem** gelöst, sondern **als Netzliste durch den eigenen
Löser** — Knotenpotentialverfahren, Newton-Raphson, Euler —, und zwar mit den selbst
ermittelten Parametern. Drei Fälle: einmal nur der Arbeitspunkt (fünf Zeilen
Netzliste), einmal die komplette Verstärkerstufe mit Kollektor-, Last- und
Basiswiderstand, Koppelkondensatoren und Signalquelle — und einmal **seine B4-Brücke**
mit vier Dioden, wörtlich aus `rechnung/bruecke.netz`. Der dritte Fall ist der Beleg
dafür, dass hier sein *allgemeines* Verfahren steht und kein Transistor-Sonderfall:
derselbe Quelltext löst beides, geändert wird die Netzliste. Die Signalverstärkung wird auf
**zwei** Wegen gerechnet — kleinsignalig aus den vier Tangenten, die der Stempel im
Arbeitspunkt ohnehin bildet, und großsignalig aus dem Euler-Lauf —, und der
Unterschied zwischen beiden ist die Aussage: Spitze zu Spitze 0,048 %, aber **8,50 %
Unsymmetrie** zwischen oberem und unterem Hub, wo eine lineare Stufe exakt 0,00 %
hätte.

Der JavaScript-Teil ist Zeile für Zeile aus `rechnung/simulator.py` übertragen (dem
Löser des Grundlagenprojekts, Teil XII, unverändert mitgeliefert); über jeder Funktion
steht, aus welcher Klasse und welchen Zeilen sie stammt. **Alle sechs Bauteilklassen
sind übertragen** — R, Q/V, D, C, L und T, die Dioden samt ihren Modellkarten aus
`rechnung/bruecke_kern.py`; eine Netzlistenzeile, die bei ihm läuft, läuft auch hier. Geprüft wird gegen den Lauf
genau dieses Programms: `seite/netz_lauf.py` schickt dieselben Netzlisten hindurch, und
`seite/pruefe_seite.mjs` hält beide Zahlen nebeneinander.

## Worauf das aufbaut

Das Verfahren, mit dem eine Schaltung aus nichtlinearen Bauteilen überhaupt gerechnet
wird — Knotenpotentialverfahren, Newton-Raphson und Euler —, ist in einer eigenen Arbeit
hergeleitet: **Schaltungssimulation von nichtlinearen Differentialgleichungssystemen**,
https://ralphwystup.github.io/Schaltungssimulation-von-nichtlinearen-Differentialgleichungssystemen/ . Dort steht, warum aus den
Bauteilgleichungen ein Gleichungssystem wird, wie die Ableitung eines nichtlinearen
Bauteils als Leitwert in die Matrix gestempelt wird und wie der Zeitschritt dazukommt.
Diese Arbeit hier setzt dort an, wo das Verfahren steht, und füllt es mit einem
gemessenen Transistor.

## Die vierzehn Teilmanuskripte

Jedes ist ein eigenständiges Dokument und bleibt es. Sie sind **nicht** zu einem Werk
zusammengezogen, und es gibt keine Nummerierung quer über sie hinweg — jedes ist für
sich lesbar, so wie der Verfasser sie geschrieben hat.

| Nr. | Datei | Reiter der Seite | Ursprung |
|--:|:--|:--|:--|
| 1 | [`10_diodenkennlinie.md`](manuskripte/10_diodenkennlinie.md) | Diodenkennlinie | Manuskript_Diodenkennlinie_1.docx |
| 2 | [`11_led.md`](manuskripte/11_led.md) | Leuchtdiode | LED_Manuskript_v2.docx |
| 3 | [`20_bjt_spice.md`](manuskripte/20_bjt_spice.md) | BJT und SPICE | Vorlesungsmanuskript_BJT_SPICE_RW.docx |
| 4 | [`30_extraktion_bc547.md`](manuskripte/30_extraktion_bc547.md) | Extraktion BC547 | Vorlesungsmanuskript_Parameterextraktion_BC547.docx |
| 5 | [`40_arbeitspunkt_transistor20.md`](manuskripte/40_arbeitspunkt_transistor20.md) | Arbeitspunkt von Hand | Transistor_Manuskript (1).docx |
| 6 | [`41_minimaler_datensatz.md`](manuskripte/41_minimaler_datensatz.md) | Minimaler Datensatz | Für ein einfaches statisches BJT.docx |
| 7 | [`50_esp32_programm.md`](manuskripte/50_esp32_programm.md) | Der Transistortester | Kennlinienschreiber_ESP32_Code_Arduino.docx |
| 8 | [`60_gummel_poon.md`](manuskripte/60_gummel_poon.md) | Gummel-Poon | BUCH/kapitel_06_gummel_poon.md (Markdown-Quelle) |
| 9 | [`70_parameterextraktion.md`](manuskripte/70_parameterextraktion.md) | Parameterextraktion | BUCH/kapitel_07_parameterextraktion.md (Markdown-Quelle) |
| 10 | [`80_arbeitspunkt_newton.md`](manuskripte/80_arbeitspunkt_newton.md) | Arbeitspunkt Newton | BUCH/kapitel_08_arbeitspunkt_newton.md (Markdown-Quelle) |
| 11 | [`85_simulation.md`](manuskripte/85_simulation.md) | Simulation und SPICE | BUCH/kapitel_09_simulation.md (Markdown-Quelle) |
| 12 | [`86_gummel_poon_h_parameter.md`](manuskripte/86_gummel_poon_h_parameter.md) | Kleinsignal und h-Parameter | MANUSKRIPT_Transistor_v2.md (Markdown-Quelle) |
| 13 | [`87_vierpol_verstaerker.md`](manuskripte/87_vierpol_verstaerker.md) | Vierpol-Verstärker | MANUSKRIPT_Vierpol_Verstaerker.md (Markdown-Quelle) |
| 14 | [`90_messvorschrift.md`](manuskripte/90_messvorschrift.md) | Messvorschrift | Messvorschrift_SPICE_Parameter_Transistor.docx |

Jedes liegt als `.md` (Quelle), `.pdf` und `.docx` in `manuskripte/`.

## Was sonst drin ist

| Datei | Inhalt |
|:--|:--|
| [`Transistortechnik_2.2.html`](Transistortechnik_2.2.html) | die Seite: je Reiter ein Teilmanuskript und der rechnende Teil dazu |
| [`BERICHTIGUNGEN.md`](BERICHTIGUNGEN.md) | jede Berichtigung einzeln: Fundstelle, Wortlaut vorher, Wortlaut nachher, Grund |
| [`SICHTUNG_Transistoren.pdf`](SICHTUNG_Transistoren.pdf) | was aufgenommen wurde und was nicht, mit Begründung, Doppelungen und der Gegenprobe der Umsetzung .docx → Markdown |
| [`PRUEFPLAN_Seite.md`](PRUEFPLAN_Seite.md) | was an der Seite geprüft wurde, mit Schranken und Zahlen |
| `pc/` | seine Auswerteprogramme (`bjt_*.py`), die beiden Arbeitspunktprogramme und die Python-Fassung des Testers — **unverändert** |
| `rechnung/` | seine Rechen- und Bilderzeuger der Buchkapitel (`kap0*.py`) sowie sein Netzlisten-Löser `simulator.py` mit `bruecke_kern.py` und zwei Netzlisten — **unverändert** |
| `messungen/` | die Messdaten: fünf Kennfelder des BC337-25 vom Kurventracer und neun Ausgangskennfelder des Testers als CSV |
| `spice/` | die LTspice-Schaltungen mit der selbst ermittelten `.model`-Karte |
| `bilder/` | alle Abbildungen, dazu das Foto des Testers, seine Funktionsübersicht und der Schaltplan als PDF |
| `seite/` | Erzeuger und Prüfmittel der Seite |
| `index.html` | leitet auf die Seite weiter, damit GitHub Pages sie unter der Adresse oben zeigt |

## Wie man es selbst nachrechnet

Jede Zahl der Seite ist aus einem dieser Programme übertragen, und das Prüfmittel
`seite/pruefe_seite.mjs` startet sie und hält beide Zahlen nebeneinander:

```
cd pc && ln -s ../messungen/*.txt .
python3 bjt_extract.py          # die Ablesungen: n, I_S, V_A, beta_F
python3 bjt_hparam.py           # die h-Parameter im Arbeitspunkt
python3 bjt_verstaerker.py      # die ganze Vierpol-Kette
python3 Transistor_20.py        # Arbeitspunkt, einfachstes Modell
python3 Transistor_21b.py       # Arbeitspunkt mit beta_F
cd ../rechnung && mkdir -p bilder
python3 kap08_rechnung.py       # Newton-Raphson und Bisektion, BC547
python3 kap09_spice_abgleich.py # Buchgleichungen gegen SPICE-Konvention
python3 simulator.py bjt_fixedbias.netz   # sein Netzlisten-Löser, seine Netzliste
python3 simulator.py bruecke.netz         # dieselbe Klasse, vier Dioden statt Transistor
python3 simulator_abnahme.py              # seine sieben Abnahmen des Lösers
cd ../seite
python3 netz_lauf.py            # die drei Netzlisten des Reiters durch seinen Löser
```

Die Auswerteprogramme in `pc/` erwarten die fünf Kennliniendateien **im selben Ordner** —
unter Linux genügt der Verweis oben, unter Windows kopiert man sie aus `messungen/`
daneben. Gebraucht werden nur `numpy` und `matplotlib`; `pc/Kennlinienschreiber_1.py` und
`pc/transistor_kennlinie_5_neu.py` brauchen zusätzlich `pyserial`, weil sie mit dem Gerät
sprechen, und `rechnung/kap08_led_quellen.py` zusätzlich `scipy`.

## Drei verschiedene Transistoren

In diesen Manuskripten kommen drei Prüflinge vor: der **BC547** (Extraktion und
Arbeitspunkt, β_F = 290), der **BC337-25** (Kurventracer, Kleinsignal und Verstärker,
β_F ≈ 250…275) und der nicht benannte Prüfling der neun CSV-Reihen des Testers
(β_F ≈ 53). Dass ihre Parameter auseinanderliegen, ist deshalb kein Widerspruch — es sind
verschiedene Bauteile.

## Der Weg in einem Satz

Messgerät → Kennlinienfeld → Parametersatz → Arbeitspunkt → Kleinsignal → Vierpol →
Verstärker, und an jeder Stelle die Frage, wie genau die Zahl eigentlich ist.

## Das Messgerät selbst

Aufbau, Kaskadenregelung, Firmware, Registerplan und Bedienung des Testers sind in einer
eigenen Arbeit beschrieben: **Kennlinienschreiber für Transistoren mit ESP32 und
BJT-Modell**, https://ralphwystup.github.io/Kennlinienschreiber-fuer-Transistoren-mit-ESP32-und-BJT-Modell/ . Diese Arbeit hier setzt dort an,
wo die Messwerte vorliegen.

## Was nicht mitgeliefert wird

* Die Klausur- und Musterlösungsunterlagen zur Probeklausur SS 2026.
* Die Vorlesungsfolien und die Alt-Vorlesungen im `.docx`-Format: ihre Formeln liegen
  ausschließlich als Bilder im Format WMF/EMF vor und sind ohne einen Umsetzer dafür nicht
  inhaltstreu übertragbar. Ein Bild, das sich nicht ansehen lässt, wird nicht veröffentlicht.
* Fremdsoftware und deren Projektdateien.

Der Name im Schriftfeld des Schaltplans ist der eines Dritten und in dieser Fassung
buchstabengleich durch „x" ersetzt.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
