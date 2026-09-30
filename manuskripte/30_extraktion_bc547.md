**Vorlesungsmanuskript**

**Halbleiter-Elektronik**

**Von der Kennlinienmessung zur Arbeitspunktberechnung:**

**SPICE-Parameterextraktion am Beispiel BC547**

+---------------------------------------------+---------------------------------------+
| **Messkette:**                              | **Prüfling:**                         |
|                                             |                                       |
| ▸ Kennlinienschreiber-Messung               | BC547 (npn, Si-Kleinsignaltransistor) |
|                                             |                                       |
| ▸ Gummel-Plot-Auswertung (IS, NF)           | **Messmittel:**                       |
|                                             |                                       |
| ▸ Stromverstärkung (BF) aus hFE-Kurve       | Kennlinienschreiber (Curve Tracer)    |
|                                             |                                       |
| ▸ Early-Spannung (VAF) aus Ausgangskennfeld | **Begleitprogramm:**                  |
|                                             |                                       |
| ▸ Hochstrom-Knick (IKF)                     | Erweitere_Spice_Parameter_1.py        |
|                                             |                                       |
| ▸ Basiswiderstand (RBM)                     |                                       |
|                                             |                                       |
| ▸ Arbeitspunktberechnung in Python          |                                       |
+---------------------------------------------+---------------------------------------+

Lehrstuhl Halbleiterelektronik \| Hochschule \| 2026

**1 Einleitung: Von der Messung zum Modell**

In der vorangegangenen Einheit wurde das erweiterte SPICE-Modell des Bipolartransistors (Gummel-Poon mit Early-Effekt, Hochstrom-Beta-Abfall und internem Basiswiderstand) ausschließlich mit **vorgegebenen Parametern** behandelt. In dieser Einheit schließen wir die Lücke zwischen Theorie und Praxis: Wir bestimmen alle SPICE-Parameter aus realen Messungen mit dem Kennlinienschreiber (Curve Tracer) und speisen sie in das Python-Modell ein, um den Arbeitspunkt einer konkreten Schaltung zu berechnen.

+-----------+---------------------------------------------------------------------------------------------------------+
| **Ziele** | **Nach dieser Einheit können Sie:**                                                                     |
|           |                                                                                                         |
|           | -   die Funktionsweise eines Kennlinienschreibers und die relevanten Messmodi erläutern,                |
|           |                                                                                                         |
|           | -   aus einer Gummel-Plot-Messung den Sättigungsstrom I_S und den Idealfaktor n extrahieren,            |
|           |                                                                                                         |
|           | -   die Stromverstärkung beta_F aus dem Verhältnis I_C/I_B bestimmen,                                   |
|           |                                                                                                         |
|           | -   die Early-Spannung V_A durch Extrapolation des Ausgangskennfelds ermitteln,                         |
|           |                                                                                                         |
|           | -   den Knickstrom I_KF aus dem Abknicken der beta-Kurve bei hohen Strömen ablesen,                     |
|           |                                                                                                         |
|           | -   den internen Basiswiderstand R_B,int aus der Kompression der Eingangskennlinie bestimmen,           |
|           |                                                                                                         |
|           | -   die so gewonnenen Parameter in das Python-Arbeitspunktprogramm einsetzen und das Ergebnis bewerten. |
+-----------+---------------------------------------------------------------------------------------------------------+

**2 Der Kennlinienschreiber als Messinstrument**

**2.1 Funktionsprinzip**

Ein Kennlinienschreiber (Curve Tracer) legt an die Anschlüsse eines Transistors definierte Spannungs- bzw. Stromrampen an und zeichnet den resultierenden Stromfluss auf. Für den BJT werden typischerweise zwei Messmodi benötigt:

-   Basis-Emitter-Kennlinie I_B(V_BE) bzw. I_C(V_BE): Basis wird spannungs- oder stromgesteuert durchgefahren, V_CE wird konstant gehalten (z. B. V_CE = 5 V, um den aktiven Bereich sicherzustellen).

-   Ausgangskennfeld I_C(V_CE) bei I_B = const.: Für mehrere feste Basisstrom-Stufen wird V_CE von 0 V bis zur Versorgungsspannungsgrenze durchgefahren.

Wichtig ist, dass der Kennlinienschreiber die Selbsterwärmung des Transistors während der Messung gering hält (kurze Pulsmessung oder Strombegrenzung), da sich sonst I_S und damit alle abgeleiteten Parameter mit der Messzeit verschieben (thermische Drift).

**2.2 Benötigte Messreihen**

Für die vollständige Parameterextraktion werden drei Messreihen benötigt:

  -----------------------------------------------------------------------------------------------------------
  **Messreihe**       **Bedingung**                                                   **Liefert Parameter**
  ------------------- --------------------------------------------------------------- -----------------------
  Gummel-Plot         I_C, I_B vs. V_BE bei V_CE = const. (z. B. 5 V), log. I-Achse   I_S, NF, BF, IKF

  Ausgangskennfeld    I_C vs. V_CE bei mehreren I_B-Stufen, V_CE = 0\...V_CC          VAF (Early-Spg.)

  Eingangskennlinie   V_BE vs. I_B bei festem V_CE, hoher Auflösung im Knick          RBM (Basis-R)
  -----------------------------------------------------------------------------------------------------------

Eine vierte Größe, die Basis-Early-Spannung V_AB (VAR), ist messtechnisch deutlich aufwendiger zu bestimmen (sie erfordert die V_CE-Abhängigkeit von I_B bei konstantem V_BE mit sehr hoher Strommessauflösung) und wird in der Praxis häufig aus Datenblattangaben übernommen oder per Faustregel mit V_AB ≈ 2\*V_AF abgeschätzt, da sie für die meisten Schaltungsanalysen einen vernachlässigbar kleinen Einfluss hat.

**3 Parameterextraktion 1: Sättigungsstrom I_S und Idealfaktor n**

**3.1 Der Gummel-Plot**

Der Gummel-Plot zeigt I_C und I_B halblogarithmisch über V_BE bei konstantem V_CE. Im mittleren Strombereich (weder Leckströme bei sehr kleinem I_C, noch Hochinjektion bei sehr großem I_C) verläuft I_C(V_BE) als ideale Exponentialfunktion und erscheint im halblogarithmischen Diagramm als Gerade:

  -----------------------------------------------------------------------
  I_C = I_S \* exp( V_BE / (n \* V_T) )

  =\> ln(I_C) = ln(I_S) + V_BE / (n \* V_T)

  Geradengleichung: y = m\*x + b mit y = ln(I_C), x = V_BE

  Steigung: m = 1 / (n \* V_T)

  Achsenabschnitt: b = ln(I_S)
  -----------------------------------------------------------------------

**3.2 Auswertung über zwei Messpunkte**

In der Praxis wertet man zwei Punkte (V_BE1, I_C1) und (V_BE2, I_C2) aus dem linearen Bereich des Gummel-Plots aus:

  -----------------------------------------------------------------------
  n = (V_BE2 - V_BE1) / ( V_T \* ln(I_C2 / I_C1) )

  I_S = I_C1 / exp( V_BE1 / (n\*V_T) )
  -----------------------------------------------------------------------

+------------------------+-------------------------------------------------------------------------------------+
| **Messbeispiel BC547** | Aus zwei Punkten im linearen Bereich des Gummel-Plots (V_CE = 5 V, Raumtemperatur): |
|                        |                                                                                     |
|                        | Punkt 1: V_BE1 = 0.600 V -\> I_C1 = 0.5 mA                                          |
|                        |                                                                                     |
|                        | Punkt 2: V_BE2 = 0.660 V -\> I_C2 = 5.0 mA                                          |
|                        |                                                                                     |
|                        | n = (0.660-0.600) / (0.02586 \* ln(10)) = 1.008 \~= 1.0                             |
|                        |                                                                                     |
|                        | I_S = 0.5mA / exp(0.600/(1.008\*0.02586)) = 5.0e-14 A                               |
+------------------------+-------------------------------------------------------------------------------------+

Für Siliziumtransistoren wie den BC547 ergibt sich praktisch immer n ≈ 1.0 (idealer Diffusionsstrom dominiert). Werte n \> 1.05 deuten auf einen relevanten Rekombinationsanteil im Sperrschichtbereich hin (zweiter, paralleler Diodenast mit n ≈ 2, im einfachen Modell hier nicht berücksichtigt).

**3.3 Gültigkeitsbereich und typische Fehlerquellen**

-   Bei sehr kleinem I_C (typisch \< 1 µA) dominieren Leckströme -- die Gerade krümmt sich nach oben ab. Diesen Bereich nicht zur Auswertung verwenden.

-   Bei hohem I_C (Hochinjektion) krümmt sich die Gerade nach unten ab. Auch dieser Bereich ist für die Bestimmung von I_S und n ungeeignet.

-   Der Basisstrom I_B(V_BE) verläuft im Gummel-Plot meist nicht exakt parallel zu I_C(V_BE) -- das Verhältnis I_C/I_B liefert direkt beta_F.

**4 Parameterextraktion 2: Stromverstärkung beta_F (BF)**

**4.1 Bestimmung aus dem Gummel-Plot**

Da im Gummel-Plot sowohl I_C als auch I_B über V_BE aufgetragen werden, lässt sich beta_F bei jedem Arbeitspunkt direkt als Verhältnis ablesen:

  -----------------------------------------------------------------------
  beta_F(V_BE) = I_C(V_BE) / I_B(V_BE)

  -----------------------------------------------------------------------

Da beta_F selbst stromabhängig ist (Webster-Effekt), wählt man als BF-Wert für SPICE üblicherweise den **Maximalwert** von beta im mittleren Strombereich -- also dort, wo die beta-I_C-Kurve ihr Plateau erreicht, bevor der Hochstrom-Abfall einsetzt.

**4.2 Messbeispiel BC547**

+------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Messbeispiel BC547** | Aus dem Plateau-Bereich der beta(I_C)-Kurve (typisch I_C = 1\...10 mA für BC547):                                                                                                                |
|                        |                                                                                                                                                                                                  |
|                        | I_C = 2.0 mA I_B = 6.9 µA -\> beta_F = 2.0mA / 6.9µA \~= 290                                                                                                                                     |
|                        |                                                                                                                                                                                                  |
|                        | Dieser Wert liegt im Datenblatt-Bereich der hFE-Klassifikation B (200-450) für den BC547. Da hFE serienstreuungsbedingt erheblich variiert, ist eine Messung am konkreten Exemplar unerlässlich. |
+------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**5 Parameterextraktion 3: Early-Spannung V_A (VAF)**

**5.1 Extrapolationsverfahren**

Die Early-Spannung wird aus dem Ausgangskennfeld I_C(V_CE) bei mehreren I_B-Stufen bestimmt. Im aktiven Bereich (V_CE oberhalb der Sättigungsspannung) verlaufen die Kennlinien näherungsweise linear mit kleiner positiver Steigung. Extrapoliert man diese Geraden nach links, schneiden sie sich näherungsweise in einem gemeinsamen Punkt auf der negativen V_CE-Achse bei V_CE = -V_A:

  -----------------------------------------------------------------------
  I_C(V_CE) = I_C0 \* (1 + V_CE/V_A) \[Gerade im aktiven Bereich\]

  Aus zwei Punkten derselben Kennlinie (gleiches I_B):

  V_A = (V_CE2\*I_C1 - V_CE1\*I_C2) / (I_C2 - I_C1)
  -----------------------------------------------------------------------

**5.2 Praktisches Auswerteverfahren**

**1.** Wählen Sie eine I_B-Kurve aus dem Ausgangskennfeld (z. B. I_B = 20 µA).

**2.** Lesen Sie zwei Punkte im aktiven Bereich ab, z. B. bei V_CE = 5 V und V_CE = 20 V (möglichst weit auseinander für geringen Ablesefehler).

**3.** Setzen Sie beide Punkte in die Formel für V_A ein.

**4.** Wiederholen Sie dies für 2-3 weitere I_B-Stufen und mitteln Sie die Ergebnisse.

+------------------------+-----------------------------------------------------------------------------------------------------------------------+
| **Messbeispiel BC547** | Ausgangskennlinie bei I_B = 20 µA:                                                                                    |
|                        |                                                                                                                       |
|                        | Punkt 1: V_CE1 = 5 V I_C1 = 5.80 mA                                                                                   |
|                        |                                                                                                                       |
|                        | Punkt 2: V_CE2 = 20 V I_C2 = 6.67 mA                                                                                  |
|                        |                                                                                                                       |
|                        | V_A = (20\*5.80m - 5\*6.67m)/(6.67m - 5.80m)                                                                          |
|                        |                                                                                                                       |
|                        | = (116m - 33.35m)/0.87m = 82.65/0.87 \~= 95 V                                                                         |
|                        |                                                                                                                       |
|                        | Typischer BC547-Bereich laut Literatur: V_A \~= 70\...100 V. Der gemessene Wert von 95 V liegt im erwarteten Bereich. |
+------------------------+-----------------------------------------------------------------------------------------------------------------------+

In dieser Vorlesung verwenden wir für die anschließende Python-Berechnung den gemessenen Wert V_A = 95 V (statt des fiktiven Demonstrationswerts V_A = 100 V aus der vorigen Einheit).

**6 Parameterextraktion 4: Knickstrom I_KF (IKF)**

**6.1 Erkennung im Gummel-Plot**

Bei hohen Kollektorströmen weicht die I_C(V_BE)-Kurve im Gummel-Plot zunehmend nach unten von der idealen Geraden ab (Hochinjektion). Gleichzeitig fällt die aus I_C/I_B berechnete beta(I_C)-Kurve vom Plateau ab. Der Knickstrom I_KF ist definitionsgemäß der Strom, bei dem beta auf **70.7 %** (= 1/sqrt(2)) des Plateauwerts gefallen ist:

  -------------------------------------------------------------------------------------
  beta_eff(I_C) = beta_F / sqrt(1 + I_C/I_KF)

  Bei I_C = I_KF: beta_eff = beta_F / sqrt(2) = 0.707 \* beta_F

  =\> I_KF ist exakt der Strom, bei dem beta_eff auf 70.7% des Plateaus gefallen ist.
  -------------------------------------------------------------------------------------

**6.2 Praktisches Auswerteverfahren**

**1.** Tragen Sie beta = I_C/I_B über I_C halblogarithmisch auf (typisches Diagramm aus dem Gummel-Plot abgeleitet).

**2.** Bestimmen Sie den Plateauwert beta_F im mittleren Strombereich.

**3.** Suchen Sie den Strom I_C, bei dem beta auf 0.707 \* beta_F gefallen ist -- das ist I_KF.

+------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Messbeispiel BC547** | Aus der beta(I_C)-Kurve des BC547:                                                                                                                         |
|                        |                                                                                                                                                            |
|                        | beta_F (Plateau) = 290                                                                                                                                     |
|                        |                                                                                                                                                            |
|                        | 0.707 \* beta_F = 205                                                                                                                                      |
|                        |                                                                                                                                                            |
|                        | Abgelesener I_C bei beta=205: I_KF \~= 80 mA                                                                                                               |
|                        |                                                                                                                                                            |
|                        | Dies passt zur Datenblattgrenze I_C,max = 100 mA des BC547 -- der Hochstrom-Abfall setzt also bereits unterhalb der absoluten Strombegrenzung spürbar ein. |
+------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+

**7 Parameterextraktion 5: Interner Basiswiderstand R_B,int (RBM)**

**7.1 Auswerteprinzip**

Der interne Basiswiderstand verursacht bei hohen Basisströmen einen zusätzlichen Spannungsabfall, der die Eingangskennlinie V_BE(I_B) gegenüber der idealen Diodenkennlinie zu höheren V_BE-Werten hin \"aufbiegt\" (Kompression der Kennlinie bei hohem Strom -- ähnlich wie der Vorwiderstandseffekt bei einer LED-Kennlinie):

  -----------------------------------------------------------------------
  V_BE,gemessen = V_BE,ideal + I_B \* R_B,int

  =\> R_B,int = ( V_BE,gemessen - V_BE,ideal ) / I_B
  -----------------------------------------------------------------------

**7.2 Praktisches Auswerteverfahren**

**1.** Berechnen Sie aus IS und n den idealen V_BE-Verlauf: V_BE,ideal(I_B) = n\*V_T\*ln(beta_F\*I_B/I_S).

**2.** Vergleichen Sie bei hohem I_B (z. B. nahe I_KF) den idealen Wert mit dem tatsächlich gemessenen V_BE.

**3.** Die Differenz, dividiert durch I_B, ergibt R_B,int.

+------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Messbeispiel BC547** | Bei hohem Basisstrom I_B = 1 mA (entspricht I_C \~= 290 mA im idealen Modell, praktisch durch IKF begrenzt -- hier wird der reine R_B,int-Effekt isoliert betrachtet): |
|                        |                                                                                                                                                                        |
|                        | V_BE,ideal = n\*V_T\*ln(beta_F\*I_B/I_S) \~= 0.768 V                                                                                                                   |
|                        |                                                                                                                                                                        |
|                        | V_BE,gemessen = 0.783 V                                                                                                                                                |
|                        |                                                                                                                                                                        |
|                        | R_B,int = (0.783 - 0.768) / 1mA = 15 Ohm                                                                                                                               |
|                        |                                                                                                                                                                        |
|                        | Typische Werte für Kleinsignal-npn-Transistoren wie den BC547 liegen im Bereich 5\...30 Ohm -- der gemessene Wert von 15 Ohm ist plausibel.                            |
+------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Diese Methode setzt voraus, dass IS, n und beta_F bereits aus den vorigen Schritten bekannt sind -- die Parameterextraktion erfolgt also in der gezeigten Reihenfolge (I_S, n -\> beta_F -\> V_A -\> I_KF -\> R_B,int), da spätere Parameter auf früheren aufbauen.

**8 Zusammengefasster Parametersatz für den BC547**

Die folgende Tabelle fasst alle aus den Messungen extrahierten Parameter zusammen, im direkten Vergleich zum fiktiven Demonstrationsdatensatz der Vorgängereinheit:

  ---------------------------------------------------------------------------------------------------
  **Parameter**   **Demo-Wert (vorige Einheit)**   **Gemessen (BC547)**           **Quelle**
  --------------- -------------------------------- ------------------------------ -------------------
  IS              1e-13 A                          5.0e-14 A                      Gummel-Plot

  NF              1.0                              1.01                           Gummel-Plot

  BF              200                              290                            I_C/I_B Plateau

  VAF             100 V                            95 V                           Ausgangskennfeld

  VAR             200 V                            190 V (\~2\*VAF, Faustregel)   geschätzt

  IKF             0.5 A                            0.08 A                         beta(I_C)-Abfall

  RBM             10 Ohm                           15 Ohm                         Eingangskennlinie
  ---------------------------------------------------------------------------------------------------

Auffällig ist der deutlich kleinere Knickstrom I_KF des realen BC547 (80 mA) gegenüber dem Demo-Wert (500 mA). Das bedeutet: Bei den im Folgenden berechneten Arbeitspunkten muss geprüft werden, ob I_C in die Nähe von I_KF kommt -- dann wäre auch die in der letzten Einheit diskutierte Webster-Näherung (im Gegensatz zur exakten Gummel-Poon-Formel) kritischer zu hinterfragen.

**9 Arbeitspunktberechnung mit gemessenen Parametern**

**9.1 Anpassung des Python-Programms**

Das Programm Erweitere_Spice_Parameter_1.py aus der Vorgängereinheit wird unverändert in seiner Struktur (Newton-Raphson, Bisektion) übernommen. Lediglich der Parameterblock am Anfang wird durch die gemessenen Werte ersetzt:

  -----------------------------------------------------------------------
  \# \-\-- Gemessene Parameter (BC547, Kennlinienschreiber) \-\--

  I_S = 5.0e-14 \# Sättigungsstrom (Gummel-Plot)

  beta_F = 290.0 \# Stromverstärkung (Plateau I_C/I_B)

  n = 1.01 \# Idealfaktor (Gummel-Plot-Steigung)

  V_A = 95.0 \# Early-Spannung (Ausgangskennfeld)

  V_AB = 190.0 \# Basis-Early-Spg. (Faustregel: 2\*VAF)

  I_KF = 0.08 \# Knickstrom (beta-Abfall auf 70.7%)

  R_B_int = 15.0 \# Interner Basiswiderstand (Eingangskl.)
  -----------------------------------------------------------------------

**9.2 Schaltungsdimensionierung für den Arbeitspunkt**

Wir verwenden zur Veranschaulichung dieselbe Fixed-Bias-Schaltung wie zuvor (R_C = 100 Ohm, V_CC = V_BB = 25 V), mit dem Ziel V_CE = V_CC/2 = 12.5 V. Die Bisektion sucht erneut den passenden R_B.

**9.3 Erwartetes Ergebnis und Plausibilitätsprüfung**

Mit beta_F = 290 (statt 200) wird bei gleichem R_B mehr Kollektorstrom fließen -- die Bisektion wird also tendenziell einen **größeren** R_B finden als im Demo-Beispiel, um denselben Arbeitspunkt V_CE = 12.5 V einzustellen. Quantitativ lässt sich das näherungsweise abschätzen:

  -----------------------------------------------------------------------
  Vereinfachte Abschaetzung (ideales Modell, ohne Early/RBM):

  I_C,ziel = V_CC/(2\*R_C) = 25/(2\*100) = 125 mA

  I_B,ziel = I_C,ziel / beta_F = 125mA/290 = 431 µA

  V_BE \~= n\*V_T\*ln(I_C,ziel/I_S) = 1.01\*25.86mV\*ln(125mA/5e-14A)

  \~= 0.746 V

  R_B = (V_BB - V_BE)/I_B,ziel = (25-0.746)/431µA \~= 56.3 kOhm
  -----------------------------------------------------------------------

Dieser Schätzwert dient als Startwert/Plausibilitätscheck; das tatsächliche Ergebnis der Newton-Raphson-Bisektion mit allen Korrekturtermen (Early-Effekt, RBM) weicht davon je nach Lage zum Kniestrom ab — im vorliegenden Fall ($I_C/I_{KF}$ = 1,56) um ein Drittel: der Abschätzung 56,3 kΩ steht der Modellwert 37,3 kΩ gegenüber und sollte in der Übung explizit berechnet und mit diesem Schätzwert verglichen werden.

**10 Fehler- und Unsicherheitsbetrachtung**

**10.1 Messunsicherheiten**

-   Ableseunsicherheit am Kennlinienschreiber: typisch ±2-5% bei analogen Geräten, deutlich geringer bei digitaler Datenerfassung.

-   Thermische Drift: I_S verdoppelt sich näherungsweise alle 8-10 K Temperaturanstieg. Messungen sollten bei konstanter, dokumentierter Temperatur erfolgen.

-   Bauteilstreuung: hFE (beta_F) streut bei BC547 herstellerseitig um den Faktor 4 (Klassengrenzen 110-800). Jede Messung gilt nur für das konkrete Exemplar.

-   Kontaktwiderstände der Messspitzen können R_B,int systematisch überschätzen lassen -- Vierleitermessung oder Kalibrierung empfohlen.

**10.2 Fortpflanzung in die Arbeitspunktberechnung**

Da I_C exponentiell von V_BE abhängt, wirken sich bereits kleine Unsicherheiten in I_S und n stark auf den berechneten Arbeitspunkt aus. Eine Unsicherheit von ±10% in I_S verschiebt V_BE um etwa:

  ---------------------------------------------------------------------------------------
  Aus I_C = I_S\*exp(V_BE/(n\*V_T)):

  dV_BE = n\*V_T \* d(ln(I_S)) = n\*V_T \* ln(1.1) \~= 1.01\*25.86mV\*0.0953 \~= 2.5 mV

  =\> 10% Fehler in I_S verschiebt V_BE nur um ca. 2.5 mV (geringe Sensitivität).

  Der Kollektorstrom selbst reagiert dagegen direkt proportional auf einen I_S-Fehler,

  wenn V_BE festgehalten wird - in der geschlossenen Arbeitspunktrechnung kompensiert

  sich dies aber teilweise durch die Rueckkopplung ueber R_B.
  ---------------------------------------------------------------------------------------

**11 Übungsaufgaben**

**Aufgabe 1 -- Gummel-Plot-Auswertung:**

-   Gegeben seien zwei Messpunkte V_BE1 = 0.580 V, I_C1 = 0.1 mA und V_BE2 = 0.640 V, I_C2 = 1.0 mA. Bestimmen Sie n und I_S.

**Aufgabe 2 -- Early-Spannung:**

-   Aus dem Ausgangskennfeld bei I_B = 40 µA wurden V_CE1 = 3 V, I_C1 = 11.5 mA und V_CE2 = 15 V, I_C2 = 12.4 mA gemessen. Berechnen Sie V_A.

**Aufgabe 3 -- Knickstrom:**

-   beta_F = 320 wurde im Plateau gemessen. Bei welchem Stromwert beta = 226 gemessen wird, entspricht I_KF. Wie würden Sie diesen Wert messtechnisch eingrenzen (Vorgehensweise in 3 Schritten beschreiben)?

**Aufgabe 4 -- Vollständige Berechnung:**

-   Übernehmen Sie die in Kapitel 8 gemessenen BC547-Parameter vollständig in das Python-Programm und führen Sie die Bisektion durch. Vergleichen Sie das Ergebnis mit der Abschätzung aus Kapitel 9.3 und erklären Sie die Abweichung.

**Aufgabe 5 -- Sensitivitätsanalyse:**

-   Variieren Sie beta_F im Bereich der Datenblatt-Klassengrenzen (110 bis 800) und berechnen Sie jeweils den resultierenden Arbeitspunkt R_B. Wie stark schwankt R_B über diesen Bereich -- und welche Konsequenz hat das für die Serienfertigung von Schaltungen mit Fixed-Bias?

**12 Zusammenfassung**

+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Kernaussagen** | -   Alle sieben SPICE-Parameter (IS, NF, BF, VAF, VAR, IKF, RBM) lassen sich aus drei Kennlinienschreiber-Messreihen extrahieren: Gummel-Plot, Ausgangskennfeld, Eingangskennlinie. |
|                  |                                                                                                                                                                                     |
|                  | -   Die Extraktion folgt einer festen Reihenfolge, da spätere Parameter auf den Ergebnissen früherer Schritte aufbauen (IS, n -\> BF -\> VAF -\> IKF -\> RBM).                      |
|                  |                                                                                                                                                                                     |
|                  | -   Reale BC547-Werte unterscheiden sich teils deutlich von den Demo-Werten der Vorgängereinheit, insbesondere der Knickstrom IKF.                                                  |
|                  |                                                                                                                                                                                     |
|                  | -   Messunsicherheiten setzen sich über die exponentielle I_C(V_BE)-Beziehung unterschiedlich stark in den Arbeitspunkt fort - V_BE reagiert robust, I_C empfindlich.               |
|                  |                                                                                                                                                                                     |
|                  | -   Das Python-Programm aus der Vorgängereinheit benötigt keine strukturelle Änderung, nur den Austausch des Parameterblocks.                                                       |
+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Literaturhinweise**

-   Datenblatt BC547 (verschiedene Hersteller, z. B. onsemi, Nexperia) -- hFE-Klassengrenzen, Grenzwerte

-   Getreu (1978): Modeling the Bipolar Transistor -- Parameterextraktionsverfahren im Detail

-   Gummel/Poon (1970): An integral charge control model of bipolar transistors, BSTJ 49(5)

-   LTspice Hilfedokumentation: .model-Statement und BJT-Parametertabelle

-   Vorgängereinheit: Vorlesungsmanuskript \'Bipolare Transistoren: Erweitertes SPICE-Modell\'
