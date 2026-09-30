**VORLESUNGSMANUSKRIPT**

**LED-Kennlinien---Erweiterte Shockley-Gleichung**

*Arbeitspunktberechnung mit dem Newton-Raphson-Verfahren*

  -- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
     **Lernziele:** Die Shockley-Gleichung herleiten und ihre Grenzen kennen --- die Erweiterung für reale LEDs (insbes. blaue GaN-LEDs) physikalisch begründen --- verstehen, warum V(I) statt I(V) gewählt wird und was das für den Newton-Raphson-Ansatz bedeutet.

  -- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**1 Die ideale Shockley-Gleichung**

**1.1 Herleitung und Formel**

William Shockley leitete 1949 aus dem Drift-Diffusions-Modell des p-n-Übergangs die Strom-Spannungs-Kennlinie ab. Der Strom folgt dem Überschuss an Minoritätsträgern, die durch Diffusion den Übergang passieren:

  ------------- -------------------------------------------------- -----------------------------
  **(GL. 1)**   **I_D = I_S · \[ exp( V_D / (n·V_T) ) − 1 \]**     *Ideale Shockley-Gleichung*

                                                                   

                **V_T = k·T / q ≈ 25,85 mV bei 300 K**             *Temperaturspannung*
  ------------- -------------------------------------------------- -----------------------------

  -------------------- --------------------------------------------------------------------------------------------------------------
  **Symbol**           **Bedeutung und typischer Wert (blaue GaN-LED)**

  I_S                  Sättigungssperrstrom. Thermisch generiert. Für GaN: 10⁻²⁰ ... 10⁻¹⁶ A (wegen großer Bandlücke extrem klein).

  n                    Idealitätsfaktor. n=1: reine Diffusion (ideal). n=2: RLZ-Rekombination dominiert. Bei GaN: 1,8 ... 3,5.

  V_T                  Temperaturspannung k·T/q. Bei 300 K = 25,85 mV. Steigt linear mit der absoluten Temperatur.
  -------------------- --------------------------------------------------------------------------------------------------------------

Für V_D ≫ V_T vereinfacht sich die Gleichung zur reinen Exponentialfunktion. Im halblogarithmischen I-V-Diagramm ergibt das eine Gerade mit der Steigung 1/(n·V_T·ln 10) ≈ 1 Dekade / (n · 59,5 mV). Diese „60-mV-Regel“ ist eine wichtige Faustregel.

**1.2 Wo das Modell versagt --- und warum**

Die ideale Gleichung setzt voraus: keine Rekombination in der Raumladungszone, keine ohmschen Bahnwiderstände, reine Minoritätssträgerinjektion. Bei realen LEDs sind alle drei Annahmen verletzt:

  --------------------- -------------------------------------------------------------------------------- -------------------------------
  **Effekt**            **Physikalische Ursache**                                                        **Konsequenz im Modell**

  n \> 1                Strahlende Rekombination + SRH-Rekombination in der RLZ (bei GaN: Auger-Terme)   n als freier Parameter (1--5)

  Kennlinie knickt ab   Ohmscher Spannungsabfall an Bahnwiderständen, ITO-Elektrode, Bonddrähten         Serienwiderstand R_S addieren

  I_S extrem klein      Große Bandlücke von GaN (3,4 eV) → I_S ∼ exp(−E_g/kT)                            log₁₀(I_S) als Fitparameter
  --------------------- -------------------------------------------------------------------------------- -------------------------------

**2 Die erweiterte Shockley-Gleichung**

**2.1 Ersatzschaltbild und Gleichung**

Das erweiterte Modell ergänzt die ideale Diode durch einen Serienwiderstand R_S, der alle ohmschen Verluste zwischen Klemme und p-n-Übergang zusammenfasst. Die Klemmenspannung setzt sich additiv zusammen:

  ------------- -------------------------------------------------- ---------------------------
  **(GL. 2)**   **V_D = n·V_T·ln( I_D/I_S + 1 ) + I_D·R_S**        *Erweiterte Shockley-Gl.*

                **└──────────────────────┴──────────────────**     

                **ideale Diode (Shockley) Serienanteil**           
  ------------- -------------------------------------------------- ---------------------------

Der Serienterm I_D·R_S ist bei kleinen Strömen vernachlässigbar, wächst aber linear und dominiert bei hohen Strömen. Das erklärt das charakteristische „Abknicken“ der LED-Kennlinie im linearen I-V-Diagramm.

**3 Warum V(I) statt I(V)? --- Eine entscheidende Modellwahl**

**3.1 Die zwei Formulierungen im Vergleich**

GL. 2 ist explizit in V --- gegeben I berechnen wir V direkt. Die inverse Formulierung I(V) ist dagegen implizit: I taucht sowohl linear als auch im Argument des Logarithmus auf und lässt sich nicht analytisch auflösen.

  ------------ ------------------------------------------------------ ----------------------------------------
  **V(I) ✔**   **V_D = n·V_T·ln(I_D/I_S + 1) + I_D·R_S**              *explizit, direkt berechenbar*

                                                                      

  **I(V) ✘**   **I_D = I_S·\[ exp((V_D − I_D·R_S)/(n·V_T)) − 1 \]**   *implizit, I steht auf beiden Seiten!*
  ------------ ------------------------------------------------------ ----------------------------------------

Die implizite Form I(V) existiert zwar (mit der Lambert-W-Funktion lösbar), ist aber für einen Kurvenfit ungeeignet. Warum?

**3.2 Numerische Begründung für die V(I)-Wahl**

scipy.curve_fit minimiert die Summe der quadrierten Abweichungen in der abhängigen Variable:

  --------------- ---------------------------------------------------------- ----------------------
  **V(I)-Fit:**   **min Σ \[ V_gemessen(i) − V_modell(I_gemessen(i)) \]²**   *Residuen in Volt*

                                                                             

  **I(V)-Fit:**   **min Σ \[ I_gemessen(i) − I_modell(V_gemessen(i)) \]²**   *Residuen in Ampere*
  --------------- ---------------------------------------------------------- ----------------------

+---+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **Problem beim I(V)-Fit:** Der Strom I_D variiert über 5--6 Größenordnungen (0,001 mA bis 100 mA). Ein Messpunkt bei 100 mA trägt mit (100 mA)² = 10⁴ zum Fehler bei, ein Punkt bei 0,01 mA nur mit (0,01 mA)² = 10⁻⁸. Der Fit wäre praktisch blind für kleine Ströme. |
|   |                                                                                                                                                                                                                                                                        |
|   | **Vorteil beim V(I)-Fit:** Die Spannung V_D ändert sich bei der blauen LED nur von ca. 2,5 V bis 3,5 V. Alle Messpunkte tragen in ähnlicher Größenordnung bei. Der Fit ist gleichmäßig gewichtet und numerisch gut konditioniert.                                      |
+---+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Zusätzlich bedeutet eine kleine Spannungänderung ΔV bei einer Exponentialfunktion eine sehr große Stromänderung. Der Fehler propagiert asymmetrisch --- beim V(I)-Fit ist diese Asymmetrie unkritisch, beim I(V)-Fit verursacht sie numerische Instabilität.

**3.3 Konsequenz: Zwei verschiedene Newton-Raphson-Probleme**

Die Wahl der Formulierung bestimmt direkt, wie wir später die Schaltungsgleichung lösen --- und damit den Ansatz für das Newton-Raphson-Verfahren.

  ------------------- -------------------------------------- ------------------------------------------
                      **Ansatz V(I) ✔ (gewählt)**            **Ansatz I(V) ✘ (Alternative)**

  Gesucht bei Fit     Parameter aus V=f(I)                   Parameter aus I=f(V, I) --- implizit!

  Fit-Residuen        Fehler in Volt → gut konditioniert     Fehler in Ampere → schlecht gewichtet

  Newton f-Funktion   f(I_D) = V_D(I_D) + I_D·R − U_ges      f(V_D) = I_D(V_D)·R − (U_ges − V_D)

  Ableitung f\'       analytisch einfach (s. Abschn. 4)      zusätzl. implizite Differentiation nötig

  Startwert           I_D aus Kurzschlussnäherung → robust   V_D-Schätzung unsicherer
  ------------------- -------------------------------------- ------------------------------------------

Im Python-Programm wird konsequent der V(I)-Ansatz gewählt: Das Modell liefert V aus I, der Fit minimiert Spannungsresiduen, und auch das Newton-Raphson-Verfahren formuliert die Fehlerfunktion in I als Unbekannte.

**4 Newton-Raphson-Verfahren zur Arbeitspunktberechnung**

**4.1 Schaltungsgleichung (Maschenregel)**

Im Reihenstromkreis (Spannungsquelle U_ges, Vorwiderstand R, LED) liefert die Maschenregel:

  ------------- -------------------------------------------------- ----------------
  **(GL. 3)**   **U_ges = V_R + V_D = I_D·R + V_D(I_D)**           *Maschenregel*

  ------------- -------------------------------------------------- ----------------

Einsetzen des V(I)-Modells (GL. 2) ergibt die zu lösende Gleichung. Da V_D(I_D) nichtlinear ist, kann I_D nicht direkt isoliert werden --- wir suchen die Nullstelle der Fehlerfunktion:

  ------------- ---------------------------------------------------------------- ------------------
  **(GL. 4)**   **f(I_D) = n·V_T·ln(I_D/I_S + 1) + I_D·(R + R_S) − U_ges = 0**   *Fehlerfunktion*

  ------------- ---------------------------------------------------------------- ------------------

**4.2 Newton-Raphson-Iteration**

Das Newton-Raphson-Verfahren approximiert f(I_D) lokal durch die Tangente und bestimmt deren Nullstelle als nächsten Iterationspunkt:

  ------------- ------------------------------------------------------------- --------------------
  **(GL. 5)**   **I_D\^(k+1) = I_D\^(k) − f( I_D\^(k) ) / f\'( I_D\^(k) )**   *Newton-Iteration*

  ------------- ------------------------------------------------------------- --------------------

Die Ableitung f\'(I_D) wird analytisch berechnet --- das ist ein wesentlicher Vorteil der V(I)-Formulierung. Beim I(V)-Ansatz wäre eine implizite Differentiation nötig (I taucht auf beiden Seiten auf):

  ------------- -------------------------------------------------- -------------------------
  **(GL. 6)**   **f\'(I_D) = n·V_T / (I_D + I_S) + R + R_S**       *Analytische Ableitung*

                                                                   

                **└────────────────┴─────────────────**            

                **Dioden-Differenzwiderstand ohmscher Anteil**     
  ------------- -------------------------------------------------- -------------------------

Die Ableitung ist immer positiv (alle Terme \> 0), was gewährleistet, dass das Verfahren in die richtige Richtung schreitet --- es gibt keine Nullstelle der Ableitung und damit keine Divergenz für I_D \> 0.

**4.3 Startwert und Konvergenz**

Als Startwert wird der genäherte Kurzschlussstrom verwendet:

  ------------- -------------------------------------------------- ----------------------------------------
  **(GL. 7)**   **I_D\^(0) = U_ges / ( R + R_S + 1 )**             *Startwert (1Ω ≈ Diode bei kleinem I)*

  ------------- -------------------------------------------------- ----------------------------------------

Newton-Raphson konvergiert quadratisch: Die Anzahl korrekter Dezimalstellen verdoppelt sich pro Iteration. Typisch werden 5--10 Iterationen für eine Genauigkeit von 10⁻⁷ A benötigt.

+---+---------------------------------------------------------------------+
|   | **Numerische Absicherungen im Code:**                               |
|   |                                                                     |
|   | -   I_D ≤ 0: Zurücksetzen auf 10⁻¹² A (Logarithmus undefiniert)     |
|   |                                                                     |
|   | -   \|f\'(I_D)\| \< 10⁻³⁰: Abbruch (Division durch nahezu Null)     |
|   |                                                                     |
|   | -   Kein Ergebnis nach 1000 Iterationen: Rückgabe None mit Warnung  |
|   |                                                                     |
|   | -   Ergebnis I_D ≤ 0: Verworfen (physikalisch unmöglich)            |
+---+---------------------------------------------------------------------+

**4.4 Grafische Interpretation: Lastgerade**

Die Arbeitsgleichung (GL. 3) lässt sich umschreiben zu V_D = U_ges − I_D·R. Das ist die Gleichung einer Geraden im I-V-Diagramm --- der Lastgeraden:

  ------------- -------------------------------------------------- --------------
  **(GL. 8)**   **V_D = U_ges − I_D · R**                          *Lastgerade*

                                                                   

                **I_D = 0 ➤ V_D = U_ges (Leerlauf-Punkt)**         

                **V_D = 0 ➤ I_D = U_ges/R (Kurzschluss-Punkt)**    
  ------------- -------------------------------------------------- --------------

Der Arbeitspunkt ist der Schnittpunkt von LED-Kennlinie V_D(I_D) und Lastgeraden. Das Newton-Raphson-Verfahren findet diesen Schnittpunkt numerisch, indem es iterativ die Differenz beider Kurven --- also f(I_D) --- zu null treibt.

**5 Umsetzung im Python-Programm**

**5.1 Kernfunktionen und ihre Aufgaben**

  ----------------------------------- ----------------------------------------------------------------------------
  **Funktion / Abschnitt**            **Aufgabe und Bezug zur Theorie**

  extended_shockley_voltage(I, ...)   Berechnet V_D aus I_D nach GL. 2 --- die V(I)-Formulierung

  curve_fit(...)                      Fittet log₁₀(I_S), n, R_S an Messdaten. Minimiert Fehler in V (nicht in I)

  solve_for_Id(...)                   Newton-Raphson: Löst GL. 4 iterativ. Nutzt GL. 5 und GL. 6

  Diagramm 1                          Gesamtkennlinie: alle Messpunkte + Fit-Kurve aus GL. 2

  Diagramm 2                          Arbeitspunkt: Kennlinie + Lastgerade (GL. 8) + AP-Markierung
  ----------------------------------- ----------------------------------------------------------------------------

**5.2 Warum log₁₀(I_S) statt I_S direkt fitten?**

I_S liegt für blaue GaN-LEDs im Bereich 10⁻²⁰ A. curve_fit würde versuchen, diesen Wert direkt zu optimieren --- bei Parameterschritten im Bereich des Absolutwerts extrem schlechte Konditionierung. log₁₀(I_S) liegt dagegen im handhabbaren Bereich −20 bis −10, und ein Schritt von 0,1 entspricht einer Multiplikation von I_S mit 10⁰ʸ¹ ≈ 1,26 --- physikalisch sinnvoll.

**5.3 Korrekturen der verbesserten Version**

  ------------------------------------ --------------------------------------------------
  **Problem (Original)**               **Korrektur**

  except: pass --- alle Fehler stumm   except ValueError mit Zeilennummer-Ausgabe

  Keine Dateiexistenzprüfung           os.path.isfile() + sys.exit(1) mit Meldung

  I_D = 0 als gültig akzeptiert        Prüfung I_D ≤ 0 mit Warnung und continue

  Kein sauberer Exit                   \'q\' beendet Schleife, plt.close() nach Plot

  Division durch df ≈ 0 möglich        Guard: if abs(df) \< 1e-30 → return None
  ------------------------------------ --------------------------------------------------

**6 Übungsaufgaben**

**Aufgabe 1 --- Idealitätsfaktor aus Kennlinie**

**Gegeben:** Eine blaue LED zeigt im halblogarithmischen I-V-Diagramm eine Steigung von 1 Dekade / 120 mV. Berechnen Sie n bei T = 25 °C.

  -- ---------------------------------------------------------------------------------
     Hinweis: 1 Dekade / 120 mV ➤ n = 120 mV / (V_T · ln 10) = 120 mV / 59,5 mV = ??

  -- ---------------------------------------------------------------------------------

**Aufgabe 2 --- Vorwiderstand dimensionieren**

**Gegeben:** U_ges = 5 V, blaue LED mit V_F = 3,1 V bei I_F = 20 mA, R_S = 20 Ω.

**Aufgabe:** (a) Berechnen Sie R aus der Lastgeraden-Gleichung. (b) Welche Verlustleistung entsteht an R? (c) Welcher Normwert (E12-Reihe) wäre zu wählen?

**Aufgabe 3 --- Newton-Raphson per Hand**

**Gegeben:** n = 2,0, I_S = 10⁻²⁰ A, R_S = 20 Ω, R = 100 Ω, U_ges = 5 V, V_T = 25,85 mV.

**Aufgabe:** Führen Sie 3 Iterationen des Newton-Raphson-Verfahrens durch. Startwert: I_D⁻⁰ = U_ges / (R + R_S + 1) ≈ 41,0 mA. Tragen Sie f(I_D), f\'(I_D) und I_D⁻ⁿ⁺¹ tabellarisch ein.

**Aufgabe 4 --- Vergleich V(I) vs. I(V) beim Fit**

**Aufgabe:** Erklären Sie in eigenen Worten, warum ein Fit mit I(V) als abhängiger Variable bei LED-Messdaten zu schlechten Ergebnissen führt. Welche Messpunkte würden übergewichtet, welche vernachlässigt?

**7 Zusammenfassung der Kernaussagen**

+---+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | 1.  Die ideale Shockley-Gleichung I_D = I_S·\[exp(V_D/n·V_T)−1\] gilt für ideale p-n-Übergänge. Bei LEDs versagt sie wegen RLZ-Rekombination (n\>1) und Serienwiderstands-Effekten.                                                      |
|   |                                                                                                                                                                                                                                          |
|   | 2.  Die Erweiterung V_D = n·V_T·ln(I_D/I_S+1) + I_D·R_S beschreibt reale LEDs durch drei Parameter: I_S (Materialabhängig), n (Rekombinationsmechanismus), R_S (parasitäre Widerstände).                                                 |
|   |                                                                                                                                                                                                                                          |
|   | 3.  Die Formulierung V(I) statt I(V) ist eine bewusste numerische Entscheidung: Spannungsresiduen sind gleichmäßig verteilt, der Fit ist gut konditioniert. Beim I(V)-Ansatz dominieren große Ströme den Fehler.                         |
|   |                                                                                                                                                                                                                                          |
|   | 4.  Beim Newton-Raphson-Verfahren wirkt sich die V(I)-Wahl direkt aus: Die Fehlerfunktion f(I_D) und ihre analytische Ableitung f\'(I_D) sind beide einfach und numerisch stabil. Beim I(V)-Ansatz wäre implizite Differentiation nötig. |
|   |                                                                                                                                                                                                                                          |
|   | 5.  Das Verfahren konvergiert quadratisch und findet den Arbeitspunkt (Schnittpunkt von Kennlinie und Lastgerade) typisch in 5--10 Iterationen mit einer Genauigkeit von \< 10⁻⁷ A.                                                      |
+---+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Literatur**

6.  Shockley, W. (1949): The Theory of p-n Junctions. Bell System Technical Journal 28(3), 435--489.

7.  Sze, S.M., Ng, K.K. (2007): Physics of Semiconductor Devices. 3rd ed., Wiley.

8.  Schubert, E.F. (2018): Light-Emitting Diodes. 3rd ed., Cambridge University Press.

9.  Press, W.H. et al. (2007): Numerical Recipes. 3rd ed., Cambridge. \[Kap. 9: Root Finding, Kap. 15: Curve Fitting\]
