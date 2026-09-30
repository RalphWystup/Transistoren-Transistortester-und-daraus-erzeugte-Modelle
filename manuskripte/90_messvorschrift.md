**Praxisleitfaden / Laborunterlage**

**Einfache Messvorschrift**

**SPICE-Parameter aus Transistorkennlinien**

*(allgemeingültig für beliebige bipolare Kleinsignal-Transistoren, npn und pnp)*

+------------------------------------+-----------------------------------+
| **Benötigte Messungen:**           | **Ergebnis:**                     |
|                                    |                                   |
| ▸ Gummel-Plot (I_C, I_B vs. V_BE)  | ▸ I_S, NF (n)                     |
|                                    |                                   |
| ▸ Ausgangskennfeld (I_C vs. V_CE)  | ▸ BF (beta_F)                     |
|                                    |                                   |
| ▸ Eingangskennlinie (V_BE vs. I_B) | ▸ VAF (V_A)                       |
|                                    |                                   |
|                                    | ▸ IKF                             |
|                                    |                                   |
|                                    | ▸ RBM (R_B,int)                   |
+------------------------------------+-----------------------------------+

Lehrstuhl Halbleiterelektronik \| Hochschule \| 2026

**0 Vorbereitung**

+-------+------------------------------------------------------------------------------------------------------+
| **⚠** | **Wichtig vor Beginn:**                                                                              |
|       |                                                                                                      |
|       | -   Transistor-Pinout (E, B, C) im Datenblatt prüfen -- Verpolung zerstört das Bauteil.              |
|       |                                                                                                      |
|       | -   Bei npn: alle Spannungen positiv. Bei pnp: alle Vorzeichen umkehren (Messverfahren identisch).   |
|       |                                                                                                      |
|       | -   Strombegrenzung am Kennlinienschreiber aktivieren (I_C,max laut Datenblatt nicht überschreiten). |
|       |                                                                                                      |
|       | -   Kurze Messpulse oder Pausen zwischen Messpunkten verwenden -- Selbsterwärmung verfälscht I_S.    |
|       |                                                                                                      |
|       | -   Raumtemperatur notieren (alle folgenden Formeln gelten für T ≈ 300 K / 25-27°C).                 |
+-------+------------------------------------------------------------------------------------------------------+

**Benötigte Werte vorab**

Notieren Sie folgende Konstante, sie wird in allen Auswertungen gebraucht:

  -----------------------------------------------------------------------
  V_T = 25.86 mV (Temperaturspannung bei T = 300 K, fest)

  -----------------------------------------------------------------------

**1 Messung: Gummel-Plot aufnehmen**

+-------+------------------------------------------------------------------------------------------------+
| **1** | **Gummel-Plot messen**                                                                         |
|       |                                                                                                |
|       | Ziel: I_C und I_B in Abhängigkeit von V_BE bei konstantem V_CE aufzeichnen.                    |
|       |                                                                                                |
|       | ☐ V_CE fest einstellen (z. B. 5 V -- Wert im aktiven Bereich, weit weg von Sättigung).         |
|       |                                                                                                |
|       | ☐ V_BE von ca. 0.4 V in kleinen Schritten (5-10 mV) bis zur Strombegrenzung hochfahren.        |
|       |                                                                                                |
|       | ☐ Bei jedem Schritt I_C UND I_B notieren (Kennlinienschreiber zeigt meist beide gleichzeitig). |
|       |                                                                                                |
|       | ☐ Mindestens 15-20 Messpunkte über den gesamten Spannungsbereich aufnehmen.                    |
|       |                                                                                                |
|       | ☐ Werte tabellarisch notieren: V_BE \| I_C \| I_B                                              |
+-------+------------------------------------------------------------------------------------------------+

Falls der Kennlinienschreiber kein direktes Gummel-Plot-Display besitzt, kann diese Messung auch als normale Eingangskennlinie I_C(V_BE) bei festem V_CE aufgenommen werden -- der Basisstrom I_B wird dann separat mit einem Amperemeter im Basiszweig mitgemessen.

**2 Messung: Ausgangskennfeld aufnehmen**

+-------+-----------------------------------------------------------------------------------------------------------------------+
| **2** | **Ausgangskennfeld messen**                                                                                           |
|       |                                                                                                                       |
|       | Ziel: I_C in Abhängigkeit von V_CE bei mehreren festen I_B-Stufen.                                                    |
|       |                                                                                                                       |
|       | ☐ 3-5 verschiedene Basisstrom-Stufen wählen (z. B. 10, 20, 40, 80 µA), gleichmäßig verteilt.                          |
|       |                                                                                                                       |
|       | ☐ Für jede I_B-Stufe: V_CE von 0 V bis zur gewünschten Maximalspannung durchfahren.                                   |
|       |                                                                                                                       |
|       | ☐ Besonders im Bereich V_CE = 0\...1 V (Sättigung) und V_CE \> 2 V (aktiver Bereich) Punkte aufnehmen.                |
|       |                                                                                                                       |
|       | ☐ Pro Stufe mindestens 8-10 Punkte, davon mind. 2 Punkte bei hohem V_CE (z. B. 5V und 20V) für spätere Extrapolation. |
|       |                                                                                                                       |
|       | ☐ Werte tabellarisch notieren: I_B-Stufe \| V_CE \| I_C                                                               |
+-------+-----------------------------------------------------------------------------------------------------------------------+

**3 Messung: Eingangskennlinie bei hohem Strom**

+-------+----------------------------------------------------------------------------------------------------------+
| **3** | **Eingangskennlinie im Hochstrombereich messen**                                                         |
|       |                                                                                                          |
|       | Ziel: V_BE bei möglichst hohem I_B genau erfassen (für R_B,int später).                                  |
|       |                                                                                                          |
|       | ☐ V_CE fest einstellen (gleicher Wert wie in Schritt 1, z. B. 5 V).                                      |
|       |                                                                                                          |
|       | ☐ I_B möglichst nah an die zulässige Strombegrenzung des Transistors heranfahren.                        |
|       |                                                                                                          |
|       | ☐ V_BE bei diesem hohen I_B-Wert genau ablesen und notieren.                                             |
|       |                                                                                                          |
|       | ☐ Zusätzlich einen Punkt bei niedrigem I_B (z. B. 1/10 des Maximalwerts) notieren -- dient als Referenz. |
+-------+----------------------------------------------------------------------------------------------------------+

Damit ist die Messphase abgeschlossen. Alle folgenden Schritte sind reine Auswertung der notierten Zahlenwerte am Schreibtisch -- kein weiterer Gerätekontakt nötig.

**4 Auswertung: Sättigungsstrom I_S und Idealfaktor n**

+-------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **4** | **I_S und n aus Gummel-Plot berechnen**                                                                                                                            |
|       |                                                                                                                                                                    |
|       | Aus der Gummel-Plot-Tabelle (Schritt 1) zwei Punkte im mittleren, geraden Bereich wählen.                                                                          |
|       |                                                                                                                                                                    |
|       | **Auswahlregel:** Punkte meiden, bei denen I_C sehr klein ist (\< 1 µA, Leckströme) oder sehr groß (nahe Strombegrenzung, Hochinjektion). Mittelbereich verwenden. |
+-------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  -----------------------------------------------------------------------
  Zwei Punkte: (V_BE1, I_C1) und (V_BE2, I_C2) mit I_C2 \> I_C1

  Schritt A: n = (V_BE2 - V_BE1) / ( V_T \* ln(I_C2/I_C1) )

  Schritt B: I_S = I_C1 / exp( V_BE1 / (n\*V_T) )
  -----------------------------------------------------------------------

Plausibilitätscheck: n sollte für Si-Transistoren zwischen 1.0 und 1.1 liegen. Werte deutlich darüber oder darunter deuten auf einen Ablesefehler oder ungeeignete Messpunkte hin.

**5 Auswertung: Stromverstärkung beta_F**

+-------+------------------------------------------------------------------------------------------------------------------------+
| **5** | **beta_F aus dem Plateau bestimmen**                                                                                   |
|       |                                                                                                                        |
|       | Für jeden Messpunkt aus Schritt 1 beta = I_C / I_B berechnen und über I_C auftragen (oder einfach als Tabellenspalte). |
+-------+------------------------------------------------------------------------------------------------------------------------+

  -----------------------------------------------------------------------
  beta(I_C) = I_C / I_B (für jeden Messpunkt einzeln berechnen)

  beta_F = Maximalwert von beta im mittleren Strombereich (Plateau)
  -----------------------------------------------------------------------

Der höchste stabile Wert über mehrere benachbarte Messpunkte (nicht der absolute Einzelmaximalwert, der durch Messrauschen verfälscht sein kann) wird als BF in SPICE eingetragen.

**6 Auswertung: Early-Spannung V_A**

+-------+------------------------------------------------------------------------------------------------------------------------------------------+
| **6** | **V_A aus dem Ausgangskennfeld extrapolieren**                                                                                           |
|       |                                                                                                                                          |
|       | Eine I_B-Kurve aus Schritt 2 auswählen. Die beiden Messpunkte bei hohem V_CE verwenden (mindestens 10V auseinander für geringen Fehler). |
+-------+------------------------------------------------------------------------------------------------------------------------------------------+

  -----------------------------------------------------------------------
  Zwei Punkte derselben I_B-Kurve: (V_CE1, I_C1) und (V_CE2, I_C2)

  V_A = ( V_CE2 \* I_C1 - V_CE1 \* I_C2 ) / ( I_C2 - I_C1 )
  -----------------------------------------------------------------------

Diese Berechnung für 2-3 verschiedene I_B-Stufen wiederholen und die Ergebnisse mitteln -- das erhöht die Genauigkeit, da die Extrapolation empfindlich auf Ablesefehler reagiert.

**7 Auswertung: Knickstrom I_KF**

+-------+-----------------------------------------------------------------+
| **7** | **I_KF aus dem beta-Abfall bestimmen**                          |
|       |                                                                 |
|       | Die beta(I_C)-Werte aus Schritt 5 bei hohen Strömen betrachten. |
+-------+-----------------------------------------------------------------+

  -----------------------------------------------------------------------
  Schritt A: Zielwert berechnen: beta_Ziel = 0.707 \* beta_F

  Schritt B: In der beta(I_C)-Tabelle den I_C-Wert suchen, bei dem

  beta auf beta_Ziel gefallen ist.

  Dieser Strom ist I_KF.
  -----------------------------------------------------------------------

Falls kein Messpunkt genau auf beta_Ziel fällt, zwischen den zwei nächstgelegenen Messpunkten linear interpolieren.

**8 Auswertung: Interner Basiswiderstand R_B,int**

+-------+-------------------------------------------------------------------------------------------------------------+
| **8** | **R_B,int aus dem Hochstrom-Messpunkt berechnen**                                                           |
|       |                                                                                                             |
|       | Den Hochstrom-Messpunkt aus Schritt 3 (V_BE bei hohem I_B) verwenden, sowie I_S und beta_F aus Schritt 4/5. |
+-------+-------------------------------------------------------------------------------------------------------------+

  -----------------------------------------------------------------------
  Schritt A: Idealen V_BE-Wert berechnen (ohne Widerstandseffekt):

  V_BE,ideal = n \* V_T \* ln( beta_F \* I_B / I_S )

  Schritt B: Mit dem TATSÄCHLICH gemessenen V_BE vergleichen:

  R_B,int = ( V_BE,gemessen - V_BE,ideal ) / I_B
  -----------------------------------------------------------------------

Diese Berechnung nur bei möglichst hohem I_B durchführen, da der Effekt bei kleinem Strom im Messrauschen untergeht (Spannungsabfall I_B·R_B,int ist dann zu klein zum sicheren Erfassen).

**9 Ergebnis-Checkliste**

Am Ende sollten folgende sieben Werte vorliegen:

  ---------------------------------------------------------------------------------
  **Parameter**   **SPICE-Name**   **Aus Schritt**   **Ihr Wert**
  --------------- ---------------- ----------------- ------------------------------
  I_S             IS               4                 

  n               NF               4                 

  beta_F          BF               5                 

  V_A             VAF              6                 

  I_KF            IKF              7                 

  R_B,int         RBM              8                 
  ---------------------------------------------------------------------------------

Die Basis-Early-Spannung VAR/V_AB ist messtechnisch aufwendiger zu bestimmen und wird in der Praxis häufig per Faustregel mit V_AB ≈ 2 · V_A abgeschätzt, falls keine separate Messung erfolgt.

**10 Plausibilitätsbereiche für Kleinsignal-Si-Transistoren**

Liegt Ihr Ergebnis weit außerhalb dieser Bereiche, prüfen Sie Messpunkte und Rechnung auf Fehler:

  ----------------------------------------------------------------------------------------------------------
  **Parameter**   **Typischer Bereich**   **Hinweis bei Abweichung**
  --------------- ----------------------- ------------------------------------------------------------------
  n               1.00 - 1.10             deutlich höher: ungeeignete Messpunkte (zu kleiner/großer Strom)

  I_S             1e-15 - 1e-12 A         stark temperaturabhängig, Messtemperatur prüfen

  beta_F          50 - 800                Datenblatt-Klassengrenzen des Transistors beachten

  V_A             30 - 200 V              negativer Wert: Punkte vertauscht oder Ablesefehler

  I_KF            10 mA - 1 A             abhängig vom Bauteil, vgl. I_C,max im Datenblatt

  R_B,int         1 - 50 Ω                negativer Wert: Hochstrompunkt nicht hoch genug gewählt
  ----------------------------------------------------------------------------------------------------------
