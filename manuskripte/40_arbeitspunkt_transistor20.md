**Numerische Simulation eines Bipolartransistors**

*Arbeitspunktberechnung mit Newton-Raphson und Bisektionsverfahren*

Begleitmaterial zur Lehrveranstaltung

Elektronik / Numerische Methoden in der Elektrotechnik

Programm: Transistor_20.py

Sprache: Python 3 \| Bibliotheken: NumPy, Matplotlib

**1 Einleitung und Zielsetzung**

Dieses Skript erläutert Schritt für Schritt das Programm Transistor_20.py. Das Programm berechnet den Arbeitspunkt eines NPN-Bipolartransistors in einer einfachen Kollektorschaltung -- und zwar vollständig numerisch, ohne Vereinfachungen wie die oft verwendete Beta-Näherung.

**Ziel des Programms:** Den Basiswiderstand R_B so bestimmen, dass der Transistor im Mittelpunkt seiner Aussteuerbarkeit arbeitet, d. h. V_CE ≈ V_CC / 2.

Dazu werden zwei numerische Verfahren kombiniert:

-   **Newton-Raphson-Verfahren** (innere Schleife): Löst das nichtlineare Gleichungssystem für einen festen Wert von R_B.

-   **Bisektionsverfahren** (äußere Schleife): Sucht iterativ den optimalen R_B-Wert.

**2 Physikalischer Hintergrund**

**2.1 Die Transistorschaltung**

Betrachtet wird ein NPN-Bipolartransistor mit Basiswiderstand R_B und Kollektorwiderstand R_C, gespeist von der Versorgungsspannung V_CC:

  -----------------------------------------------------------------------
  **Schaltungsaufbau (vereinfacht)**

  V_CC

  \|

  \[R_C\] \<- Kollektorwiderstand

  \|

  +\-\--\[C\] NPN-Transistor

  \|

  \[R_B\] \<- Basiswiderstand

  \|

  V_BB (= V_CC)

  \|

  GND (Emitter)
  -----------------------------------------------------------------------

Die Knoten- und Maschengleichungen dieser Schaltung liefern:

**I_B = (V_BB - V_BE) / R_B \[Maschengleichung Basis\]**

**I_C = (V_CC - V_CE) / R_C \[Maschengleichung Kollektor\]**

**2.2 Das Shockley-Diodenmodell**

Der Basis-Emitter-Übergang verhält sich wie eine Diode. Der Basisstrom folgt der Shockley-Gleichung:

**I_B = I_S · exp( q · V_BE / (k_B · T) )**

mit den Konstanten:

  ------------------ ------------------- ---------------------------------------
  **Parameter**      **Wert**            **Bedeutung**

  I_S                1 · 10⁻¹³ A         Sättigungssperrstrom des Transistors

  q                  1,602 · 10⁻¹⁹ C     Elementarladung

  k_B                1,381 · 10⁻²³ J/K   Boltzmann-Konstante

  T                  300 K               Absolute Temperatur (Raumtemperatur)
  ------------------ ------------------- ---------------------------------------

Die Größe **V_T = k_B · T / q ≈ 25,85 mV** bei 300 K wird als Temperaturspannung bezeichnet und taucht in allen Dioden- und Transistorgleichungen auf.

**2.3 Das Ebers-Moll-Modell mit Early-Effekt**

Im realen Transistor hängt der Kollektorstrom nicht nur vom Basisstrom, sondern auch von der Kollektor-Emitter-Spannung V_CE ab. Diesen Effekt beschreibt der Early-Effekt:

**I_C = I_B · ( 1 + V_CE / V_A )**

Die **Early-Spannung V_A** (hier 100 V) charakterisiert, wie stark der Kollektorstrom mit V_CE ansteigt. Ein großes V_A bedeutet einen nahezu idealen, spannungsunabhängigen Transistor.

**3 Das nichtlineare Gleichungssystem**

Der Arbeitspunkt des Transistors ist derjenige Betriebszustand, in dem alle Strom- und Spannungsbedingungen gleichzeitig erfüllt sind. Dies führt auf ein System von zwei nichtlinearen Gleichungen in den Unbekannten V_BE und V_CE:

**eq1 = (V_BB - V_BE)/R_B - I_S · exp(q·V_BE/(k_B·T)) = 0**

**eq2 = (V_CC - V_CE)/R_C - I_S · exp(q·V_BE/(k_B·T)) · (1 + V_CE/V_A) = 0**

**Gleichung 1** setzt die Maschengleichung für den Basiskreis gleich dem Shockley-Ausdruck. **Gleichung 2** setzt die Kollektormaschengleichung gleich dem Ebers-Moll-Ausdruck.

Da exp(·) eine stark nichtlineare Funktion ist, kann dieses System nicht analytisch gelöst werden -- hier kommt das Newton-Raphson-Verfahren ins Spiel.

**4 Das Newton-Raphson-Verfahren**

**4.1 Wozu brauchen wir das Verfahren?**

In Kapitel 3 haben wir das Gleichungssystem aufgestellt:

**eq1(V_BE, V_CE) = 0**

**eq2(V_BE, V_CE) = 0**

Beide Gleichungen enthalten den Term exp(q·V_BE / k_B·T). Die Exponentialfunktion macht eine analytische (exakte) Lösung nach V_BE und V_CE unmöglich -- es gibt keine algebraische Umformung, die zu einer geschlossenen Formel führt.

Wir brauchen daher ein numerisches Verfahren, das iterativ eine Näherungslösung berechnet. Das Newton-Raphson-Verfahren ist hierfür besonders geeignet, weil es sehr schnell konvergiert (quadratisch, s. Abschnitt 4.6) und weil wir die Ableitungen analytisch kennen.

**4.2 Grundidee: Linearisierung um den aktuellen Punkt**

Die Idee ist einfach: Eine nichtlineare Funktion lässt sich in der Nähe eines Punktes durch ihre Tangente annähern. Das ist die Taylor-Entwicklung erster Ordnung.

Für eine einzelne Funktion f(x) gilt in der Nähe von xₙ:

**f(x) ≈ f(xₙ) + f\'(xₙ) · (x - xₙ)**

Wir suchen die Nullstelle, also f(x) = 0. Einsetzen und nach x auflösen:

**0 = f(xₙ) + f\'(xₙ) · (x - xₙ)**

**x - xₙ = -f(xₙ) / f\'(xₙ)**

**x\_{n+1} = xₙ - f(xₙ) / f\'(xₙ) \[1D Newton-Formel\]**

Das ist der klassische Newton-Schritt für eine einzelne Gleichung. Wir haben aber zwei Gleichungen und zwei Unbekannte -- wir müssen auf ein Vektorsystem verallgemeinern.

**4.3 Verallgemeinerung auf Systeme: Die Jacobi-Matrix**

Unser Zustandsvektor ist:

**x = \[V_BE, V_CE\]\^T (ein Spaltenvektor mit 2 Einträgen)**

Unser Fehlervektor ist:

**F(x) = \[eq1(V_BE, V_CE), eq2(V_BE, V_CE)\]\^T**

Die Taylor-Entwicklung erster Ordnung für ein Vektorsystem lautet:

**F(x) ≈ F(xₙ) + J(xₙ) · (x - xₙ)**

Dabei ist J die Jacobi-Matrix -- das mehrdimensionale Analogon zur Ableitung. Sie enthält alle partiellen Ableitungen von F nach den Komponenten von x:

**J = \| ∂eq1/∂V_BE ∂eq1/∂V_CE \|**

**\| ∂eq2/∂V_BE ∂eq2/∂V_CE \|**

Jeder Eintrag J\[i\]\[j\] beantwortet die Frage: \"Wenn ich die j-te Variable (V_BE oder V_CE) ein kleines Stück verändere -- wie stark ändert sich die i-te Gleichung (eq1 oder eq2)?\"

Nullstelle der linearisierten Gleichung suchen, also F(x) = 0 setzen:

**0 = F(xₙ) + J(xₙ) · Δx**

**J(xₙ) · Δx = -F(xₙ) \[Das lineare Gleichungssystem\]**

**x\_{n+1} = xₙ + Δx \[Aktualisierungsschritt\]**

Das ist die Newton-Raphson-Formel für Systeme. Das Symbol Δx bezeichnet den Korrekturvektor \[ΔV_BE, ΔV_CE\]ᵀ.

**4.4 Herleitung der partiellen Ableitungen (Jacobi-Einträge)**

Jetzt leiten wir jeden der vier Jacobi-Einträge Schritt für Schritt her. Zur Erinnerung die beiden Gleichungen:

**eq1 = (V_BB - V_BE)/R_B - I_S · exp(q·V_BE/(k_B·T))**

**eq2 = (V_CC - V_CE)/R_C - I_S · exp(q·V_BE/(k_B·T)) · (1 + V_CE/V_A)**

Zur Abkürzung definieren wir zwei Hilfsgrößen, die im Programm ebenfalls verwendet werden:

**exp_term = exp(q · V_BE / (k_B · T))**

**factor = I_S · (q / (k_B · T)) · exp_term \[= Ableitung des Shockley-Terms\]**

**4.4.1 Ableitung ∂eq1/∂V_BE**

eq1 besteht aus zwei Termen. Wir leiten beide nach V_BE ab:

**d/dV_BE \[ (V_BB - V_BE)/R_B \] = -1/R_B**

Der zweite Term ist eine Exponentialfunktion. Mit der Kettenregel gilt:

**d/dV_BE \[ I_S · exp(q·V_BE/(k_B·T)) \] = I_S · (q/(k_B·T)) · exp(\...) = factor**

Da eq1 das Minus-Zeichen trägt, ergibt sich insgesamt:

**∂eq1/∂V_BE = -1/R_B - factor**

Im Programm steht genau das:

> d_eq1_dV_BE = -1/R_B - factor

**4.4.2 Ableitung ∂eq1/∂V_CE**

In eq1 taucht V_CE überhaupt nicht auf -- weder im Maschenterms noch im Shockley-Ausdruck. Daher ist die partielle Ableitung exakt null:

**∂eq1/∂V_CE = 0**

Das bedeutet: Die erste Gleichung (Basiskreis) ist vollständig unabhängig von V_CE. Im Programm:

> d_eq1_dV_CE = 0.0

**4.4.3 Ableitung ∂eq2/∂V_BE**

eq2 enthält V_BE nur im Exponentialterm. Der Maschen-Term (V_CC - V_CE)/R_C ist konstant bezüglich V_BE. Wir leiten nur den Ebers-Moll-Ausdruck ab:

**d/dV_BE \[ I_S · exp(q·V_BE/(k_B·T)) · (1 + V_CE/V_A) \]**

Der Faktor (1 + V_CE/V_A) ist bezüglich V_BE eine Konstante. Mit der Kettenregel:

**= I_S · (q/(k_B·T)) · exp(\...) · (1 + V_CE/V_A) = factor · (1 + V_CE/V_A)**

Da eq2 auch hier ein Minuszeichen trägt:

**∂eq2/∂V_BE = -factor · (1 + V_CE/V_A)**

Im Programm:

> d_eq2_dV_BE = -factor \* (1 + V_CE / V_A)

**4.4.4 Ableitung ∂eq2/∂V_CE**

eq2 enthält V_CE an zwei Stellen: im Maschen-Term und im Early-Faktor. Wir leiten beide ab:

**d/dV_CE \[ (V_CC - V_CE)/R_C \] = -1/R_C**

Für den Ebers-Moll-Term gilt -- exp_term ist bezüglich V_CE eine Konstante:

**d/dV_CE \[ I_S · exp_term · (1 + V_CE/V_A) \] = I_S · exp_term · (1/V_A) = I_S/V_A · exp_term**

Da eq2 das Minuszeichen trägt, wird dieser Term positiv subtrahiert:

**∂eq2/∂V_CE = -1/R_C + (I_S/V_A) · exp_term**

Im Programm:

> d_eq2_dV_CE = -1/R_C + (I_S / V_A) \* exp_term

**4.4.5 Die vollständige Jacobi-Matrix**

Alle vier Ableitungen zusammengesetzt ergeben:

**J = \| -1/R_B - factor 0 \|**

**\| -factor·(1 + V_CE/V_A) -1/R_C + I_S/V_A·exp_term \|**

Diese 2×2-Matrix wird in jedem Newton-Schritt neu berechnet, weil sich exp_term und factor mit jedem neuen Schätzwert für V_BE ändern.

> def J(vars):
>
> V_BE, V_CE = vars
>
> exp_term = np.exp(q \* V_BE / (k_B \* T)) \# e\^(q\*V_BE/k_B\*T)
>
> factor = I_S \* q / (k_B \* T) \* exp_term \# Ableitung Shockley
>
> d_eq1_dV_BE = -1/R_B - factor \# s. 4.4.1
>
> d_eq1_dV_CE = 0.0 \# s. 4.4.2
>
> d_eq2_dV_BE = -factor \* (1 + V_CE / V_A) \# s. 4.4.3
>
> d_eq2_dV_CE = -1/R_C + (I_S / V_A) \* exp_term \# s. 4.4.4
>
> return np.array(\[\[d_eq1_dV_BE, d_eq1_dV_CE\],
>
> \[d_eq2_dV_BE, d_eq2_dV_CE\]\])

**4.5 Das lineare Gleichungssystem lösen -- warum nicht J⁻¹ berechnen?**

Die Newton-Formel lautet:

**Δx = -J(xₙ)⁻¹ · F(xₙ)**

Man könnte J invertieren und dann Δx berechnen. Das tut man in der Praxis jedoch nicht -- aus zwei Gründen:

-   **Numerische Stabilität:** Die direkte Matrixinversion verstärkt Rundungsfehler. Lineare Gleichungslöser (wie LU-Zerlegung) sind stabiler.

-   **Rechenaufwand:** Für n×n-Systeme kostet Inversion O(n³), ein Gleichungslöser ebenfalls O(n³), aber mit kleinerem Vorfaktor.

Stattdessen löst man das äquivalente lineare System:

**J(xₙ) · Δx = -F(xₙ)**

Das entspricht der Frage: \"Welche Korrektur Δx muss ich anwenden, damit J·Δx den Fehler -F genau ausgleicht?\" NumPy löst das mit LU-Zerlegung:

> delta = np.linalg.solve(J_val, -f_val) \# löst J·Δx = -F
>
> xy += delta \# x\_{n+1} = x_n + Δx

**4.6 Schritt-für-Schritt durch eine vollständige Iteration**

Hier verfolgen wir eine Newton-Iteration mit konkreten Zahlenwerten (R_B = 3000 Ω, V_CC = 15 V):

  -----------------------------------------------------------------------
  **Iteration 0: Startwert**

  x₀ = \[V_BE, V_CE\] = \[0.9 V, 8.0 V\]

  Berechne F(x₀):

  I_B(Masche) = (15 - 0.9) / 3000 = 4.700e-3 A

  I_B(Shockley) = 1e-13 · exp(0.9/0.02585) = 4.140e-3 A

  eq1 = 4.700e-3 - 4.140e-3 = +5.60e-4 (noch nicht null!)

  I_C(Masche) = (15 - 8.0) / 1000 = 7.000e-3 A

  I_C(Ebers) = 4.140e-3 · (1 + 8/100) = 4.471e-3 A

  eq2 = 7.000e-3 - 4.471e-3 = +2.53e-3 (noch nicht null!)

  =\> Fehlervektor noch weit von null entfernt =\> weiter iterieren
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  **Iteration 0: Jacobi-Matrix und Korrekturschritt**

  Berechne J(x₀):

  exp_term = exp(0.9/0.02585) = 4.140e10

  factor = 1e-13 · (1/0.02585) · exp_term = 1.601e-1

  J\[0\]\[0\] = -1/3000 - 0.1601 = -0.1604

  J\[0\]\[1\] = 0.0

  J\[1\]\[0\] = -0.1601 · (1 + 8/100) = -0.1729

  J\[1\]\[1\] = -1/1000 + (1e-13/100)·exp = -0.0010

  Löse J·Δx = -F:

  Δx = np.linalg.solve(J, -F) =\> \[ΔV_BE, ΔV_CE\]

  Aktualisiere:

  V_BE_neu = 0.9 + ΔV_BE

  V_CE_neu = 8.0 + ΔV_CE

  =\> nächste Iteration beginnt mit verbessertem Schätzwert
  -----------------------------------------------------------------------

Nach 5--8 solcher Iterationen sind beide Fehlerkomponenten kleiner als 10⁻¹⁰ -- das Verfahren hat konvergiert.

**4.7 Konvergenzverhalten und Konvergenzrate**

Newton-Raphson hat unter geeigneten Bedingungen quadratische Konvergenz. Das bedeutet: Wenn der Fehler in Iteration n gleich εₙ ist, dann gilt näherungsweise:

**ε\_{n+1} ≈ C · εₙ² \[quadratische Konvergenz\]**

In der Praxis sieht das so aus:

  ------------------ ---------------- ---------------------------------------
  **Parameter**      **Wert**         **Bedeutung**

  Iteration 1        Fehler ≈ 10⁻¹    Erster grober Schritt

  Iteration 2        Fehler ≈ 10⁻²    Deutliche Verbesserung

  Iteration 3        Fehler ≈ 10⁻⁴    Fehler quadriert sich

  Iteration 4        Fehler ≈ 10⁻⁸    Sehr schnelle Annäherung

  Iteration 5        Fehler ≈ 10⁻¹⁶   Maschinengenauigkeit erreicht
  ------------------ ---------------- ---------------------------------------

**Warum quadratisch?** Der Taylor-Entwicklung erster Ordnung bleibt ein Restterm zweiter Ordnung übrig: F(x) = F(xₙ) + J·Δx + O(Δx²). Newton eliminiert exakt den linearen Term -- was übrig bleibt, ist O(Δx²). Der nächste Fehler ist also proportional zum Quadrat des aktuellen Fehlers.

**Wichtige Voraussetzung:** Der Startwert muss in der Nähe der echten Lösung liegen. Weit entfernte Startwerte können zu Divergenz oder Konvergenz zu einer falschen Lösung führen. Im Programm werden deshalb physikalisch sinnvolle Startwerte \[0.9 V, 8.0 V\] gewählt.

**4.8 Vollständiger Algorithmus im Programm (newton_method)**

Alle Schritte zusammengefasst als Ablaufdiagramm:

  -----------------------------------------------------------------------
  **Ablauf newton_method(initial_guess, tol=1e-10, max_iter=100)**

  EINGABE: Startwert \[V_BE⁰, V_CE⁰\], Toleranz, max. Iterationen

  SCHRITT 0: x = \[0.9, 8.0\] (oder adaptiver Startwert)

  SCHLEIFE (i = 0, 1, 2, \...):

  SCHRITT 1: Fehlervektor berechnen

  f_val = F(x) = \[eq1(x), eq2(x)\]

  SCHRITT 2: Konvergenzprüfung

  WENN \|eq1\| \< 1e-10 UND \|eq2\| \< 1e-10:

  RÜCKGABE x, Anzahl Iterationen

  SCHRITT 3: Jacobi-Matrix berechnen

  J_val = J(x) \[4 partielle Ableitungen, s. Kap. 4.4\]

  SCHRITT 4: Korrekturvektor lösen

  delta = np.linalg.solve(J_val, -f_val)

  \[löst J·Δx = -F ohne explizite Matrixinversion\]

  SCHRITT 5: Schätzwert aktualisieren

  x = x + delta

  SCHRITT 6: Physikalische Plausibilität prüfen

  WENN V_CE \< 0: FEHLER (unphysikalische Lösung)

  NACH max_iter Schritten ohne Konvergenz: FEHLER
  -----------------------------------------------------------------------

> def newton_method(initial_guess, tol=1e-10, max_iter=100):
>
> xy = np.array(initial_guess, dtype=float) \# Schritt 0
>
> for i in range(max_iter):
>
> f_val = F(xy) \# Schritt 1
>
> if np.all(np.abs(f_val) \< tol): \# Schritt 2
>
> return xy, i+1
>
> J_val = J(xy) \# Schritt 3
>
> delta = np.linalg.solve(J_val, -f_val) \# Schritt 4
>
> xy += delta \# Schritt 5
>
> if xy\[1\] \< 0: \# Schritt 6
>
> raise ValueError(\'V_CE negativ!\')
>
> raise ValueError(\'Keine Konvergenz!\')

**5 Das Bisektionsverfahren für R_B**

**5.1 Grundprinzip**

Das Newton-Raphson-Verfahren löst das innere Problem für ein festes R_B. Das äußere Problem ist: Welcher Wert von R_B führt zu V_CE = V_CC/2?

Das Bisektionsverfahren nutzt aus, dass V_CE eine monotone Funktion von R_B ist:

-   **R_B zu groß** → wenig Basisstrom → Transistor kaum leitend → V_CE ≈ V_CC (hoch)

-   **R_B zu klein** → viel Basisstrom → Transistor stark leitend → V_CE ≈ 0 (niedrig)

Es existiert also genau ein R_B, für den V_CE = V_CC/2 gilt.

**5.2 Algorithmus**

**R_B_try = (R_B_min + R_B_max) / 2**

1.  Setze Startwerte: R_B_min = 500 Ω, R_B_max = 100 kΩ

2.  Berechne Mittelpunkt R_B_try = (R_B_min + R_B_max) / 2

3.  Löse inneres System mit Newton-Raphson → V_CE

4.  **Toleranzprüfung:** Falls \|V_CE - V_CC/2\| ≤ 5% · V_CC/2 → Fertig!

5.  **Aktualisierung:** V_CE zu klein → R_B_max = R_B_try; V_CE zu groß → R_B_min = R_B_try

6.  Zurück zu Schritt 2

Nach n Bisektionsschritten hat sich das Suchintervall auf (R_B_max - R_B_min) / 2ⁿ verkleinert. Nach 30 Schritten aus 100 kΩ Startbreite: Genauigkeit ≈ 0,1 mΩ.

**6 Programmstruktur im Überblick**

  -----------------------------------------------------------------------
  **Modularer Aufbau von Transistor_20.py**

  F(vars) Fehlerfunktion: gibt \[eq1, eq2\] zurück

  J(vars) Jacobi-Matrix: gibt 2×2-Matrix zurück

  newton_method() Newton-Raphson-Solver (innere Schleife)

  finde_R_B() Bisektionsoptimierer (äußere Schleife)

  \_\_main\_\_ Hauptprogramm + Ergebnisplot
  -----------------------------------------------------------------------

Eine Besonderheit: R_B ist im Programm als globale Variable deklariert, damit F() und J() den aktuellen Wert der äußeren Bisektion kennen. Dies ist funktional, in modernem Python würde man R_B besser als Parameter übergeben.

**7 Ergebnisplot und Arbeitspunkt**

Nach Konvergenz beider Verfahren wird ein Diagramm mit drei Elementen erstellt:

-   **Transistorkennlinie I_C(V_CE):** Für den berechneten Basisstrom I_B gilt: I_C(V_CE) = I_B · (1 + V_CE/V_A). Dies ist eine leicht ansteigende Gerade (wegen des Early-Effekts).

-   **Arbeitsgerade (Lastlinie):** I_C = (V_CC - V_CE)/R_C. Eine fallende Gerade von (0, V_CC/R_C) bis (V_CC, 0).

-   **Arbeitspunkt (roter Punkt):** Der Schnittpunkt beider Linien -- der einzige Betriebszustand, der alle Gleichungen gleichzeitig erfüllt.

**Optimaler Arbeitspunkt:** Der Punkt sollte in der Mitte der Lastlinie liegen (V_CE = V_CC/2), um maximale unverzerrte Aussteuerung zu ermöglichen.

**8 Hinweise zur Implementierung**

**8.1 Stärken des Programms**

-   Analytische Jacobi-Matrix: genauer und schneller als numerische Differentiation

-   Adaptive Startwerte: Das Newton-Verfahren startet beim nächsten Bisektionsschritt mit dem letzten konvergierten Ergebnis -- verbessert Stabilität

-   Physikalische Plausibilitätsprüfung: V_CE \< 0 wird als Fehler erkannt

-   Klare Trennung: Gleichungssystem (F, J) ist unabhängig vom Solver (newton_method)

**8.2 Verbesserungspotenzial**

-   **Globale Variable R_B:** Sollte als Parameter an F() und J() übergeben werden. Empfehlung: Closures oder Klassenstruktur verwenden.

-   **Fehlende Rückgabe bei Newton-Fehler:** Wenn Newton nicht konvergiert, wird V_CE = -1 gesetzt, aber V_BE bleibt undefiniert -- bei Schleifenabbruch würde ein NameError auftreten.

-   **Plot-Funktion:** Ist als innere Funktion im \_\_main\_\_-Block definiert; besser auf Modulebene auslagern für Wiederverwendbarkeit.

**9 Übungsaufgaben**

Zur Vertiefung des Verständnisses:

7.  Berechnen Sie V_T = k_B·T/q bei 300 K per Hand und vergleichen Sie mit dem Wert im Programm.

8.  Wie verändert sich der Arbeitspunkt, wenn R_C auf 2 kΩ verdoppelt wird? Schätzen Sie ab, welches R_B dann benötigt wird.

9.  Warum konvergiert Newton-Raphson schneller mit adaptiven Startwerten? Erklären Sie anhand der Konvergenzbedingung.

10. Skizzieren Sie das Bisektionsverfahren grafisch: V_CE als Funktion von R_B, und markieren Sie den Zielbereich.

11. Ergänzen Sie das Programm so, dass R_B nicht als globale Variable, sondern als Parameter übergeben wird (Hinweis: Lambda-Funktion oder Closure).

12. Was passiert, wenn V_A → ∞ gesetzt wird? Welches Modell ergibt sich dann?

**10 Zusammenfassung**

  ----------------------------------------------------------------------------------
  **Kernpunkte dieses Skripts**

  1\. Transistorarbeitspunkt = Lösung eines nichtlinearen 2x2-Gleichungssystems

  2\. Shockley-Gleichung beschreibt den exponentiellen Basisstrom

  3\. Ebers-Moll + Early-Effekt beschreiben den Kollektorstrom

  4\. Newton-Raphson löst das innere Problem (festes R_B) quadratisch konvergent

  5\. Bisektionsverfahren optimiert R_B für den Arbeitspunkt V_CE = V_CC/2

  6\. Analytische Jacobi-Matrix ist essenziell für Genauigkeit und Geschwindigkeit

  7\. Ziel: maximale Aussteuerbarkeit =\> V_CE liegt in der Mitte der Lastlinie
  ----------------------------------------------------------------------------------

*Ende des Skripts*
