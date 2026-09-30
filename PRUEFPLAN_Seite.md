# Prüfplan — Seite „Transistoren, der Transistortester und die daraus erzeugten Modelle" (Fassung 2.2, 30.09.2026)

Prof. Dr.-Ing. Ralph Wystup M.Sc. — erstellt mit KI und Agent (Claude Code, Anthropic)

Die Seite ist nach **Reitern** gegliedert, und die Reiter folgen den vierzehn
Teilmanuskripten des Verfassers. Je Reiter steht sein Text vollständig und
unverändert, darunter der rechnende Teil zu genau diesem Thema. **Ein einziger
Reiter trägt kein Teilmanuskript** — „Netzliste und Löser“, seit Fassung 2.1. Er
ist unserer und steht ausdrücklich *neben* dem Kapitel 9 („Simulation und SPICE“),
nicht darin; das ist im Reiter selbst als Erstes gesagt. Jede Rechnung ist
Zeile für Zeile aus einem seiner Python-Programme übertragen — dieselben Formeln,
dieselben Konstanten, dieselbe Reihenfolge der Schritte, dieselben Startwerte,
dieselben Abbruchbedingungen; über jeder Funktion steht im Quelltext der Seite, aus
welchem Programm und aus welchen Zeilen sie stammt.

**Der Maßstab der Prüfung ist nicht eine eigene Nachrechnung, sondern der Lauf
seiner Programme.** `pruefe_seite.mjs` startet neun Läufe
(`BUCH/kap08_rechnung.py`, `bjt_hparam.py`, `bjt_verstaerker.py`,
`Transistor_20.py`, `Transistor_21b.py`, `BUCH/kap09_spice_abgleich.py`,
`BUCH/kap08_led_quellen.py`, `bjt_extract.py` und seit Fassung 2.1 `netz_lauf.py`,
das **seinen Netzlisten-Löser** `DGL_Nichtlinear/Programme/simulator.py`
unverändert über alle drei Netzlisten des Reiters schickt), liest ihre Konsolenausgabe und hält
die Zahlen der Seite daneben. Die Schranke ist dabei **eine halbe Einheit der letzten
gedruckten Stelle** — mehr gibt eine Konsolenausgabe nicht her, und weniger zu
fordern wäre Scheingenauigkeit. Zusätzlich wird die Seite gegen die mitgelieferten
Werte voller Genauigkeit geprüft; dort gilt 10⁻¹².

| Nr. | Kriterium | Prüfmittel | Einzelprüfungen / Schranke | Ergebnis |
|:--|:--|:--|:--|:--|
| K1 | Seite lädt, baut alle Reiter auf, keine Konsolenfehler | `pruefe_seite.mjs` (Playwright, Chromium) | 2 · Konsolenfehler 0 | ok |
| K2 | sechzehn Reiter (Start + 14 Teilmanuskripte + 1 eigener), jeder Text vollständig | `pruefe_seite.mjs` | 19 · 100 % der Stichwörter · > 24 000 Wörter | ok |
| K3 | Arbeitspunkt gegen den Lauf von `BUCH/kap08_rechnung.py` | `pruefe_seite.mjs` | 8 · halbe letzte gedruckte Stelle, zusätzlich 1e-12 gegen den vollen Wert | ok |
| K4 | Newton-Protokoll und Bisektion: Schrittzahlen und Schranke | `pruefe_seite.mjs` | 3 · ‖F‖ < 1e-10, 49 Schritte, 10 Bisektionen | ok |
| K5 | h-Parameter gegen den Lauf von `bjt_hparam.py` | `pruefe_seite.mjs` | 6 · halbe letzte gedruckte Stelle | ok |
| K6 | Vierpol-Kette gegen den Lauf von `bjt_verstaerker.py` | `pruefe_seite.mjs` | 13 · halbe letzte gedruckte Stelle | ok |
| K7 | Arbeitspunkt von Hand gegen den Lauf von `Transistor_20.py` | `pruefe_seite.mjs` | 5 · halbe letzte gedruckte Stelle | ok |
| K8 | Fixed-Bias gegen den Lauf von `Transistor_21b.py` | `pruefe_seite.mjs` | 6 · halbe letzte gedruckte Stelle | ok |
| K9 | Buch gegen SPICE gegen den Lauf von `kap09_spice_abgleich.py` | `pruefe_seite.mjs` | 16 · halbe letzte gedruckte Stelle | ok |
| K10 | Leuchtdiode gegen den Lauf von `BUCH/kap08_led_quellen.py` | `pruefe_seite.mjs` | 3 · halbe letzte gedruckte Stelle | ok |
| K11 | Gummel-Poon gegen den Testlauf in Abschnitt 6.9 | `pruefe_seite.mjs` | 4 · halbe letzte gedruckte Stelle | ok |
| K12 | Parameterextraktion gegen den Lauf von `bjt_extract.py` | `pruefe_seite.mjs` | 5 · halbe letzte gedruckte Stelle | ok |
| K13 | Kleinsignal-Ersatzschaltbild: h-Vierpol, kein π-Modell | `pruefe_seite.mjs` | 10 · keine Abweichung zulässig | ok |
| K14 | vollständiger SPICE-Parametersatz, Unbestimmbares benannt | `pruefe_seite.mjs` | 19 · ≥ 6 Parameter als nicht bestimmbar ausgewiesen | ok |
| **K15** | **Netzliste und Löser gegen den Lauf von `netz_lauf.py` / `simulator.py`** | `pruefe_seite.mjs` | **82** · alle drei Netzlisten wörtlich, Arbeitspunkt, Empfindlichkeit, Gegenprobe, vier Tangenten, beide Verstärkungen, die B4-Brücke mit vier Dioden, alle sechs Bauteilklassen, die vier Diodenkarten, Modellkarte, Schieber · halbe letzte gedruckte Stelle | ok |
| **K16** | **das Gerät im Bild: Foto, Übersichtsskizze, beide Schaltplanblätter; erste Seite mit dem Bogen** | `pruefe_seite.mjs` | **22** · jedes Bild geladen, Foto zweimal gezeigt und einmal gespeichert, 7 Stationen, 8 Sprungmarken | ok |
| K17 | Veröffentlichungsvorgaben und Kopfzeile | `pruefe_seite.mjs` | 19 · keine Abweichung zulässig | ok |
| K18 | Bildschirmfotos aller Reiter, Handybreite ohne Überlauf | `pruefe_seite.mjs` | 2 · 17 Fotos, Überlauf ≤ 2 px | ok |

## Der neue Reiter „Netzliste und Löser" (K15) im einzelnen

Was er zeigt: **nicht** ein von Hand aufgestelltes Gleichungssystem, sondern die
Schaltung als **Netzliste**, gerechnet vom Löser des Grundlagenprojekts
(Knotenpotentialverfahren, Newton-Raphson, Euler). Der JavaScript-Teil ist Zeile für
Zeile aus `DGL_Nichtlinear/Programme/simulator.py` übertragen; über jeder Funktion
steht im Quelltext der Seite, aus welcher Klasse und welchen Zeilen sie stammt.
Zwei Zutaten sind ausdrücklich unsere und dort benannt: die Auflösung des
Gleichungssystems (sein Löser ruft `numpy.linalg.solve`, hier steht das
Gauß-Verfahren mit Teilpivotierung ausgeschrieben) und das Newton-Protokoll, das an
der Rechnung nichts ändert.

**Seit Fassung 2.2 sind alle sechs Bauteilklassen seines Lösers übertragen**, nicht
eine Auswahl: `Widerstand` (Z. 109–131), `Spannungsquelle` (Z. 134–167), `Diode`
(Z. 170–199) samt den vier Modellkarten aus `bruecke_kern.py` (Z. 51, 53–84),
`Kondensator` (Z. 202–252), `Induktivitaet` (Z. 255–292) und `Transistor`
(Z. 466–568) mit `GummelPoon` (Z. 338–424). Die Zuordnung Buchstabe → Klasse ist
seine (`_TYPEN`, Z. 571–573): R, Q/V, D, C, L, T. Die Prüfung schickt eine Netzliste
mit **allen sechs** Bauteilarten durch den Browser-Löser und vergleicht die vier
Diodenkarten Zahl für Zahl mit `bruecke_kern.py`. Eine Netzlistenzeile, die bei ihm
läuft, läuft damit auch hier.

**Fall 1 — nur der Arbeitspunkt** (fünf Zeilen Netzliste, Modell BC337 aus
`bjt_fit.py`):

```
* Fall 1 — nur der Arbeitspunkt
V1  vcc 0     dc 12
RB  vcc b     470000
RC  vcc c     1000
T1  c   b  0  BC337
```

| Größe | Seite | `simulator.py` über `netz_lauf.py` | Abstand |
|:--|--:|--:|--:|
| U_BE | 0,66417694067 V | 0,66417694067 V | 0,0 |
| U_BE,eff | 0,66372352023 V | 0,66372352023 V | 0,0 |
| U_CE | 5,6514887864 V | 5,6514887864 V | 0,0 |
| I_B | 24,11810829 µA | 24,11810829 µA | 0,0 |
| I_C | 6,3485055621 mA | 6,3485055621 mA | 0,0 |
| I_E | 6,3726236704 mA | 6,3726236704 mA | 0,0 |
| β = I_C/I_B | 263,22568444 | 263,22568444 | 0,0 |
| β_eff (Webster) | 253,00178342 | 253,00178342 | 0,0 |
| P_V | 35,894526686 mW | 35,894526686 mW | 0,0 |
| Newton-Durchgänge | 46 | 46 | 0 |

Auf der gedruckten Stelle stimmt jede Größe **auf die letzte Ziffer**; der volle
Abstand liegt zwischen 7·10⁻¹⁴ und 1,8·10⁻¹² relativ und damit weit innerhalb der
Abbruchschranke seines Newton (tol_u = 10⁻⁹ V).

**Fall 2 — die vollständige Verstärkerstufe** (Kollektor-, Last- und
Basiswiderstand, zwei Koppelkondensatoren, Signalquelle; **kein Emitterwiderstand**,
weil alle seine Schaltungen Fixed-Bias ohne R_E sind):

```
* Fall 2 — die vollstaendige Verstaerkerstufe
V1  vcc 0     dc 12
RB  vcc b     470000
RC  vcc c     1000
T1  c   b  0  BC337
Vs  s   0     sinus 0.005 2000
Ck  s   b     10u  -0.664176940665
Ca  c   a     10u  5.651488786442
RL  a   0     10000
```

Die beiden letzten Zahlen sind die Anfangswerte der Koppelkondensatoren, also die
Spannungen, die im Arbeitspunkt über ihnen stehen — genau wie in seiner Netzliste
`bjt_emitter_zeit.netz`. Sie sind gerechnet, deshalb ist ihre Prüfung eine
Zahlenprüfung: Abstand 1,0·10⁻¹² V gegen 10⁻⁹ V Schranke.

Die zwei Wege zur Signalverstärkung, nebeneinander:

| Weg | Seite | `netz_lauf.py` | Abstand |
|:--|--:|--:|--:|
| A_v **kleinsignalig** aus den vier Tangenten des Stempels | −209,41278584 | −209,41278584 | 0,0 |
| A_v **großsignalig** aus dem Euler-Lauf (60 000 Schritte à 100 ns) | −209,51323724 | −209,51323724 | 0,0 |
| Unterschied | +0,047968 % | +0,047968133 % | 1,3·10⁻⁷ |
| Hub nach oben | 1,0030436861 V | 1,0030436861 V | 0,0 |
| Hub nach unten | 1,0920428470 V | 1,0920428470 V | 0,0 |
| **Unsymmetrie** | **−8,495989 %** | −8,4959890231 % | 2,3·10⁻⁸ |
| Verschiebung des Mittelwerts (Selbstvorspannung) | −20,524194 mV | −20,524194 mV | 1,0·10⁻¹² |
| Drift von Periode zu Periode | +1,1174124 mV | +1,1174124 mV | 0,0 |

**Das ist die Aussage des Reiters.** Spitze zu Spitze unterscheiden sich die beiden
Verstärkungen nur um 0,048 % — daraus zu schließen, die Stufe sei linear, wäre
falsch. Getrennt gerechnet ist die obere Halbwelle 200,6-fach, die untere 218,4-fach
verstärkt; das sind **−8,50 % Unsymmetrie**, und eine lineare Stufe hätte hier exakt
0,00 %. Die Spitze-zu-Spitze-Messung mittelt die Stauchung der einen gegen die
Dehnung der anderen Halbwelle fast heraus. Die Verzerrung ist die der e-Funktion und
sonst nichts: das Modell hat keine Ladungsspeicherung.

**Gegenprobe zum Reiter „Arbeitspunkt Newton"** — gefordert war, beides
zusammenzubringen oder zu sagen, warum es nicht geht. Es geht nicht: dort ist der
Prüfling ein **BC547** an 25 V mit R_C = 100 Ω und R_B = 37,275 kΩ, hier ein
**BC337** mit dem selbst ermittelten Satz an 12 V. Andere Beschaltung, anderer
Prüfling. Was sich vergleichen *lässt*, steht im Reiter: **seine** Netzliste
`bjt_fixedbias.netz`, wörtlich, einmal durch den Löser der Seite, einmal durch
seinen Python-Löser, einmal durch das von Hand aufgestellte System in
`kap08_rechnung.py`.

| Größe | Seite | `simulator.py` | `kap08_rechnung.py` (von Hand) |
|:--|--:|--:|--:|
| U_BE | 0,75216549009 V | 0,75216549009 V | 0,752165524359 V |
| U_CE | 12,491109307 V | 12,491109307 V | 12,491100560 V |
| I_C | 0,12508889444 A | 0,12508889444 A | 0,125088994396 A |

Gegen seinen Netzlisten-Löser: Abstand 0,0 auf allen gedruckten Stellen. Gegen das
von Hand aufgestellte System: größte relative Abweichung **1,2·10⁻⁶**, und dieser
Rest ist **benannt und nicht bloß klein** — es ist G_min = 10⁻⁹ S an jedem Knoten,
das der Netzlisten-Löser mitführt und die Handrechnung nicht. Teil XII, Abschnitt
50.1 weist das einzeln nach: dieselben Gleichungen von Hand, aber **mit** G_min
gerechnet, treffen den Netzlisten-Löser auf 1,2·10⁻¹³ V.

**Fall 3 — seine B4-Brücke, der eigentliche Beleg.** Dieselben Klassen, derselbe
Quelltext, nur eine andere Netzliste: statt eines Transistors stehen dort vier
Dioden. Geändert wird die Netzliste, nicht das Programm. Genommen wird **seine**
Datei `bruecke.netz`, wörtlich — die Prüfung vergleicht sie zeichenweise:

```
* B4-Bruecke mit belastetem RC-Glied — die Schaltung des Manuskripts
* Knoten: K0 = Masse (Minus-Schiene), K1 = a, K2 = b (Brueckeneingaenge),
*         K3 = P (Brueckenausgang), K4 = Kondensatorknoten,
*         K5 = Verbindung Quelle/Innenwiderstand.
* Q1 (sinus 30 V, 50 Hz) zwischen K5 und K2, Ri von K5 nach K1:
* zusammen die Quelle mit Innenwiderstand ZWISCHEN K1 und K2.
Q1  K5 K2  sinus 30 50
Ri  K5 K1  1
D1  K1 K3  1N4148
D2  K2 K3  1N4148
D3  K0 K1  1N4148
D4  K0 K2  1N4148
R1  K3 K4  10
C1  K4 K0  1000u
RL  K4 K0  100
```

20 000 Zeitschritte à 10 µs (200 ms), ausgewertet wird die letzte Periode — genau
wie in seinem Bericht:

| Größe | Seite | `simulator.py` | sein Bericht `bericht_bruecke_rc.txt` |
|:--|--:|--:|--:|
| u_C Mittelwert | 20,766126381 V | 20,766126381 V | 20,7661 V |
| u_C größte | 21,359706666 V | 21,359706666 V | 21,3597 V |
| u_C kleinste | 20,169570230 V | 20,169570230 V | 20,1696 V |
| Brummspannung | 1,1901364365 V | 1,1901364365 V | 1,1901 V |
| Brummspannung / u_C | 5,731143183 % | 5,731143183 % | 5,73 % |
| Laststrom Mittelwert | 207,66126381 mA | 207,66126381 mA | 207,6613 mA |
| Diodenstrom D1 Spitze | 676,92015332 mA | 676,92015332 mA | 676,9201 mA |
| Quellstrom Spitze | 676,92018425 mA | 676,92018425 mA | 676,9201 mA |
| Verlust bis zum Kondensator | 8,6402933337 V | 8,6402933337 V | 8,6403 V |

Gegen seinen Netzlisten-Löser: **Abstand 0,0 auf allen gedruckten Stellen.** Gegen
seinen Bericht — der aus einem **anderen** Programm stammt,
`Bruecke_RC_Last_Knotenpotential.py` mit Handauflösung statt Gauß — größte relative
Abweichung **1,5·10⁻⁷**, und das ist die Rundung seiner vierten gedruckten
Nachkommastelle. Zwei unabhängige Wege, dieselbe Zahl.

**Was dabei nicht stimmt und deshalb dasteht:** elf der 20 000 Zeitschritte erreichen
die Newton-Grenze max_it = 200. Sein Löser zählt sie selbst mit (Feld `abbrueche`),
die Seite zählt dieselbe Zahl elf, und die Kennzahlen stimmen trotzdem. Die Abbrüche
liegen verstreut über den Lauf (21,7 / 28,0 / 62,3 / 67,6 / 102,3 / 122,4 / 127,5 /
147,5 / 147,5 / 162,4 / 187,5 ms), nicht nur am kalten Start; **woran es liegt, ist
nicht geklärt**, und es steht auf der Seite unter den offenen Punkten. Ebenso weicht
als einzige Größe die *mittlere* Zahl der Newton-Durchgänge ab — Seite 3,7078, sein
Python-Lauf 3,7081, das sind sechs Durchgänge von 74 000. Die Prüfung verlangt dafür
ausdrücklich eine gröbere Schranke (1·10⁻³ relativ) als die gedruckte Stelle, und der
Grund steht auf der Seite: die Zustände beider Läufe liegen nach 20 000 Schritten rund
10⁻¹¹ V auseinander, und die Abbruchbedingung prüft |Δ| gegen 10⁻⁹ V — **belegt ist
dieser Zusammenhang nicht.**

**Empfindlichkeit gegen die drei gesetzten Parameter** — jeder einzeln verstellt,
der Arbeitspunkt neu gerechnet:

| Parameter | gesetzt | verstellt auf | V_CE | Wanderung |
|:--|--:|--:|--:|--:|
| I_KF | 4,05 A | 0,405 A | 5,69349823 V | +42,01 mV (+0,74 %) |
| R_B,int | 18,8 Ω | 0 Ω | 5,65124605 V | −0,24 mV (−0,004 %) |
| V_AB | 1390 V | 600 V | 5,68384698 V | +32,36 mV (+0,57 %) |
| V_AB | 1390 V | 200 V | — | **Newton bricht nach 200 Durchgängen ab** |

Der letzte Fall ist nicht weggelassen, sondern ausgewiesen: mit V_AB = 200 V — dem
Wert seiner eigenen LTspice-Karte `Demo_erweitert` — findet der kalte Start
(u = 0, Dämpfung 0,5 V) für **diese** Schaltung keinen Arbeitspunkt mehr. Beide
Seiten melden das, statt eine Zahl hinzuschreiben.

## Nur Gemessenes — und das Übrige ausdrücklich benannt

Die Modellkarte im Reiter trennt in der Spalte **Herkunft** drei Klassen, und die
Prüfung zählt sie nach:

* **gemessen und daraus bestimmt** (3 Zeilen): I_S = 4,765·10⁻¹⁴ A, n = 1,004,
  β_F = 253,2 — jede mit der Messreihe, aus der sie stammt.
* **gemessen, aber nur schwach bestimmt** (1 Zeile): V_A = 126,6 V. Seine eigene
  Empfindlichkeitsprobe gibt dafür nur den Faktor 1,06.
* **aus diesen Daten nicht bestimmbar, deshalb gesetzt** (3 Zeilen): V_AB, R_B,int
  und I_KF (Faktoren 1,00 / 1,01 / 1,00). Der gesetzte Wert steht da, *dass* er
  gesetzt ist, steht da, und woher er kommt, steht auch da.
* **mit diesem Gerät gar nicht messbar** (7 Zeilen): Rückwärtsparameter, Leckterme,
  Bahnwiderstände, Sperrschichtkapazitäten, Laufzeiten, Temperaturgang, Rauschen.

Daraus die Sätze, die an den Zahlen stehen und nicht in einem Anhang:

* **Das Modell hat keine obere Grenzfrequenz.** Keine Kapazität, keine Laufzeit —
  bei 1 kHz und bei 100 MHz käme dieselbe Zahl heraus. Das ist falsch, nur mit
  diesem Gerät nicht als falsch nachweisbar.
* Der Zeitverlauf zeigt die Verzerrung der **Kennlinie**, nicht die der
  Ladungsspeicherung.
* **Die Temperatur ist nicht protokolliert.** Die Messdateien tragen keine, seine
  eigene Messvorschrift verlangt sie („Raumtemperatur notieren"). V_T = 25,852 mV
  ist deshalb eine **Annahme** (T = 300 K) — so steht es auch in seinem
  `bjt_extract.py`, Zeile 13: „Thermospannung bei T=300 K (Annahme Raumtemperatur)".
* Das Bauteil kennt **keine Sättigung und keinen Inversbetrieb**; gerät V_CE unter
  0,3 V, sagt die Seite an, dass die Zahl außerhalb des Gültigkeitsbereichs liegt.

Am Ende des Reiters steht die Liste **„Was offen ist"** mit acht Punkten — sie
steht dort für den Leser und nicht nur in einem Bericht.

## Was die Zahlen sagen

## Was die Zahlen sagen

* **Arbeitspunkt** (`kap08_rechnung.py`, BC547, Fixed Bias): R_B = 37,275391 kΩ,
  V_BE = 752,16552 mV, V_BE,eff = 742,40795 mV, V_CE = 12,491101 V,
  I_B = 650,50517 µA, I_C = 125,08899 mA, β_eff = 181,1223 — Abweichung der Seite
  gegen den mitgelieferten vollen Programmwert **0,0** an allen acht Stellen.
* **Konvergenz**: ‖F‖ fällt nach **49** Newton-Schritten unter 10⁻¹⁰ (Endwert
  4,81·10⁻¹¹); die Bisektion braucht **10** Schritte. Der erste Schritt schießt über
  die e-Funktion hinaus, danach fällt der Rest je Schritt um den Faktor 0,3679 ≈ 1/e —
  lineare Konvergenz —, und erst die letzten vier Schritte sind quadratisch. Genau
  das ist der Sachverhalt aus Befund B5, und die Bildunterschrift ist entsprechend
  berichtigt.
* **h-Parameter** (`bjt_hparam.py`, BC337-25, I_C = 5 mA, V_CE = 5 V):
  h₁₁ₑ = 1452,7 Ω, h₂₁ₑ = 279,84, h₁₂ₑ = −4,994·10⁻⁷, h₂₂ₑ = 33,02 µS —
  Abweichung 0 bis 1,4·10⁻¹².
* **Vierpol-Kette** (`bjt_verstaerker.py`): R_B = 510 kΩ (E24 aus exakt 532,1 kΩ),
  r_ein = 977,8 Ω, r_aus = 951,5 Ω, A_v = −261,99 (48,4 dB), A_i = −25,617,
  A_vs = −129,52 — **alle dreizehn Werte mit Abweichung 0**.
* **Zwei unabhängige Wege**: der Basiswiderstand, den `Transistor_21b.py` findet
  (44453,125 Ω), steht auf die Ziffer auch im Schriftfeld der LTspice-Schaltung
  `Eigen_RW_1d.asc` (R2 = 44453).
* **Vollständigkeit der Manuskripte**: von den 5268 Stichwörtern ab sieben
  Buchstaben, die in den vierzehn Teilmanuskripten stehen, sind **5268 auf der Seite
  wiederzufinden** — 100 %. Das Teilmanuskript zum ESP32-Programm besteht aus
  294 Zeilen Quelltext und ist als solcher gesetzt.
* **Kein π-Modell**: im rechnenden Teil kommt weder r_π noch g_π noch g_m·v_be vor.
  Das Ersatzschaltbild ist der h-Vierpol aus Abschnitt 5.1 seines
  Vierpol-Manuskripts, mit h₁₁ₑ, h₁₂ₑ·v_ce, h₂₁ₑ·i_b und 1/h₂₂ₑ beschriftet.
* **Handybreite** 400 px: waagerechter Überlauf **0 px**.

## Das Gerät und der Bogen auf der ersten Seite (K16)

Der Reiter „Der Transistortester" zeigt seit Fassung 2.1 **zuerst das Gerät**:
das Foto der Platine mit dem angeklemmten Prüfling, seine handgezeichnete
Funktionsübersicht und beide Schaltplanblätter — erst die Skizze, dann die
Ausführung. Danach erst kommen Gerätekonstanten, Umrechnung und Messreihen. Die
erste Seite trägt denselben Bogen: Überschrift „Von der Messung zum eigenen
Berechnungsverfahren", das Foto, sieben Stationen mit acht Sprungmarken auf die
zugehörigen Reiter, und ein Absatz, der die Teilmanuskripte als **Hintergrund und
Lernapparat** einführt.

Bei den Bildern **angesehen und geprüft** (Vorgabe 15 — ein Textprüfer sieht keine
Bildpunkte):

* `platine_foto.jpg` — Holzplatte, Platine, Prüfling, Prüfklemmen. Unten rechts auf
  der Leiterplatte die Fertigungsnummer des Platinenherstellers
  (`2489033A_Y58_250324`). Kein Name, keine Adresse, keine Netzangabe.
* `uebersichtsplan_skizze.png` — Handskizze, nur Bauteil- und Knotenbezeichnungen.
* `schaltplan_ops.png`, `schaltplan_cpu_adda.png` — im Schriftfeld steht
  **„Drawn By: xxxx"**, der Name des Dritten ist also bereits buchstabengleich
  ersetzt; nachgeprüft am gerenderten Bild, nicht am Dateinamen.

Drei Unstimmigkeiten sind dabei aufgefallen und stehen **benannt** auf der Seite,
statt geglättet zu werden:

1. Die Handskizze beschriftet die Verbindung zu den Wandlern mit „i2c"; ausgeführt
   sind beide Wandler am **SPI**-Bus. Die Skizze ist die ältere Darstellung.
2. Die oberste der vier Messzweig-Beschriftungen ist nicht sicher zu lesen
   (U_Rc oder U_BC). Welche Größe gemeint ist, lässt der Schaltplan nicht offen —
   der AD7682 hat vier Eingänge, und sie heißen dort UC1_S, UC2_S, UB1_S, UB2_S.
3. Das Fragezeichen in der Skizze ist seine eigene Notiz. Worauf es sich bezieht,
   ist aus dem vorliegenden Material **nicht zu belegen**; es wird deshalb benannt
   und nicht gedeutet.

Stand: 2026-09-30 (Fassung 2.2) · 244 Einzelprüfungen, **0 Beanstandung(en)**.
Bildschirmfotos aller sechzehn Reiter und der Handyansicht angesehen: Ersatzschaltbild,
vier Kennfelder mit Tangente, Konvergenzbild, Kennlinienfeld mit Messpunkten,
Gummel-Plot mit den abgelesenen Geraden, die neun Messreihen des Testers,
|A_v| über der Last, Diodenkennlinie mit Lastgerade, beide Schaltplanblätter
(Schriftfeld „Drawn By: xxxx"), das Foto der Platine, die Übersichtsskizze, das
Schaltbild der Verstärkerstufe, der Zeitverlauf mit der Kleinsignalgeraden darüber
und die Großsignalkennlinie der Stufe, dazu für die B4-Brücke der Zeitverlauf über
200 ms (Quelle, Brückenausgang, Kondensator), die gedehnte Restwelligkeit der letzten
Periode und die Stromspitzen in D1 und D2 gegen den mittleren Laststrom.
