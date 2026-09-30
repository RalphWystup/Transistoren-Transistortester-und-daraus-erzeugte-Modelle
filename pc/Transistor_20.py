import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Physikalische Konstanten und Parameter
# ----------------------------

q = 1.602e-19    # Elementarladung in Coulomb [C]
k_B = 1.381e-23  # Boltzmann-Konstante in Joule pro Kelvin [J/K]
T = 300          # absolute Temperatur in Kelvin [K]
I_S = 1e-13      # Transistor-Sättigungsstrom (kleiner Strom bei Sperrung) [A]
V_A = 100        # Early-Spannung (beschreibt Auswirkung der Kollektor-Emitter-Spannung auf IC) [V]

R_C = 1e3        # Kollektorwiderstand in Ohm [Ohm]
V_CC = 15        # Versorgungsspannung am Kollektor in Volt [V]
V_BB = V_CC      # Versorgungsspannung an der Basis (hier gleich V_CC)

# ----------------------------
# Variable zur Steuerung des Basiswiderstands
# Dieser Wert wird von der äußeren Optimierungsschleife verändert
# ----------------------------
R_B = 2e3  # Startwert Basiswiderstand in Ohm [Ohm]

# -------------------------------------------------------------------------
# Funktion F(vars) - Fehlerfunktion des nichtlinearen Gleichungssystems
# vars = [V_BE, V_CE]  (Basis-Emitter-Spannung, Kollektor-Emitter-Spannung)
#
# Diese Funktion definiert die zwei Gleichungen, deren Schnittpunkt den
# Arbeitspunkt des Transistors bestimmt:
#
# 1) Maschengleichung an der Basis (Ohmsches Gesetz) vs. Shockley-Gleichung
# 2) Maschengleichung am Kollektor vs. Ebers-Moll Modell mit Early-Effekt
#
# Rückgabe: Fehlervektor [eq1, eq2]
# -------------------------------------------------------------------------
def F(vars):
    V_BE, V_CE = vars
    
    # Basisstrom berechnet über Maschengleichung (Spannungsteiler mit Basiswiderstand)
    I_B = (V_BB - V_BE) / R_B
    
    # Kollektorstrom berechnet über Maschengleichung (Kollektorwiderstand)
    I_C = (V_CC - V_CE) / R_C
    
    # Shockley-Gleichung erweitert für Basisstrom (exponentielle Diodenkennlinie)
    I_B_shockley = I_S * np.exp(q * V_BE / (k_B * T))
    eq1 = I_B - I_B_shockley
    
    # Ebers-Moll-Gleichung für den Kollektorstrom mit Early-Effekt
    # Der Faktor (1 + V_CE / V_A) beschreibt den Stromanstieg mit V_CE (Early-Effekt)
    I_C_ebers = I_B_shockley * (1 + V_CE / V_A)
    eq2 = I_C - I_C_ebers
    
    return np.array([eq1, eq2])

# -------------------------------------------------------------------------
# Funktion J(vars) - Jacobi-Matrix der partiellen Ableitungen des Gleichungssystems
# Wird benötigt für das Newton-Raphson-Verfahren, um das Gleichungssystem zu linearisieren.
#
# Matrix:
# [d(eq1)/d(V_BE), d(eq1)/d(V_CE)]
# [d(eq2)/d(V_BE), d(eq2)/d(V_CE)]
# -------------------------------------------------------------------------
def J(vars):
    V_BE, V_CE = vars
    
    # Exponentielle Hilfsgröße für häufige Berechnung
    exp_term = np.exp(q * V_BE / (k_B * T))
    factor = I_S * q / (k_B * T) * exp_term
    
    # Ableitungen von eq1 (Basisstrom-Differenz)
    d_eq1_dV_BE = -1 / R_B - factor
    d_eq1_dV_CE = 0.0  # Keine Abhängigkeit von V_CE in der ersten Gleichung
    
    # Ableitungen von eq2 (Kollektorstrom-Differenz)
    d_eq2_dV_BE = -factor * (1 + V_CE / V_A)
    d_eq2_dV_CE = -1 / R_C + (I_S / V_A) * exp_term
    
    return np.array([[d_eq1_dV_BE, d_eq1_dV_CE],
                     [d_eq2_dV_BE, d_eq2_dV_CE]])

# -------------------------------------------------------------------------
# Newton-Raphson-Verfahren zur Lösung des nichtlinearen Gleichungssystems
#
# Parameters:
#  - initial_guess: Startwerte [V_BE, V_CE] für Iteration
#  - tol: Toleranz für die Nullstellensuche (Fehlervektor norm)
#  - max_iter: Maximale Anzahl Iterationen zur Vermeidung unendlicher Schleife
#
# Algorithmus Ablauf:
# 1. Initialisiere Variablen mit Startwerten
# 2. Berechne Fehlervektor und prüfe Toleranz (Abbruch bei Erfolg)
# 3. Berechne Jacobi-Matrix und löse lineares System J * delta = -F
# 4. Aktualisiere Schätzung: vars += delta
# 5. Prüfe physikalische Plausibilität (V_CE >= 0)
# 6. Wiederhole bis Konvergenz oder max_iter erreicht
#
# Rückgabe: Lösung [V_BE, V_CE] und Anzahl Iterationen
# -------------------------------------------------------------------------
def newton_method(initial_guess, tol=1e-10, max_iter=100):
    xy = np.array(initial_guess, dtype=float)

    for i in range(max_iter):
        f_val = F(xy)              # Fehlervektor bei aktuellem Schätzwert
        if np.all(np.abs(f_val) < tol):  # Konvergenzkriterium: Alle Fehlerkomponenten klein genug
            return xy, i+1

        J_val = J(xy)              # Jacobi-Matrix an aktueller Stelle
        delta = np.linalg.solve(J_val, -f_val)  # Löse lineares Gleichungssystem
        xy += delta                # Aktualisiere Variablen

        # Schutz vor unphysikalischen Werten (negative Kollektor-Emitter-Spannung)
        if xy[1] < 0:
            raise ValueError(f"Unphysikalische Lösung in Iteration {i+1}: V_CE = {xy[1]:.5f}")

    # Wenn max_iter überschritten und keine Konvergenz, Fehler werfen
    raise ValueError("Keine Konvergenz!")

# -------------------------------------------------------------------------
# Äußere Schleife zur Anpassung von R_B (Basiswiderstand)
#
# Ziel: Den Basiswiderstand so bestimmen, dass der Arbeitspunkt für V_CE 
# innerhalb von ±5% um die halbe Versorgungsspannung V_CC liegt.
#
# Methode: Bisektionsverfahren über R_B in einem definierten Intervall.
#
# Ablauf:
# 1. Setze Anfangsgrenzen für R_B (R_B_min, R_B_max)
# 2. Mittlerer Wert R_B_try = (R_B_min + R_B_max)/2 wird probiert
# 3. Führe inneres Newton-Verfahren aus, bestimme V_CE bei R_B_try
# 4. Wenn V_CE im Toleranzbereich, Lösung gefunden
# 5. Wenn V_CE zu groß, R_B_min auf R_B_try setzen (Basisstrom zu hoch → R_B erhöhen)
# 6. Wenn V_CE zu klein, R_B_max auf R_B_try setzen (Basisstrom zu niedrig → R_B verringern)
# 7. Startwerte für Newton werden adaptiv mit letztem Ergebnis aktualisiert
# 8. Schleife bis Lösung oder Abbruch nach max_iter Versuchen
#
# Rückgabe: Optimales R_B, V_BE, V_CE
# -------------------------------------------------------------------------
def finde_R_B_fuer_ap(V_CC, toleranz_rel=0.05, R_B_min=500, R_B_max=100e3, max_iter=30):
    V_CE_ziel = V_CC / 2
    tol_abs = toleranz_rel * V_CE_ziel
    
    # Initialer Startwert für die Newton-Raphson Methode (typischer Arbeitspunkt)
    initial_guess = [0.9, 8.0]

    for i in range(max_iter):
        R_B_try = (R_B_min + R_B_max) / 2
        global R_B
        R_B = R_B_try  # Setze globalen Basiswiderstand für Newton-Verfahren
        
        try:
            # Löse inneres Gleichungssystem mit aktueller R_B
            solution, iters = newton_method(initial_guess)
            V_BE, V_CE = solution
            # Setze adaptiv Startwert für nächsten Newton-Durchlauf auf letztes Ergebnis
            initial_guess = solution
            
            print(f"R_B Versuch {i+1}: R_B={R_B:.2f} Ohm, V_CE={V_CE:.4f} V (Newton-Iterationen: {iters})")
        except Exception as e:
            # Fall Newton-Konvergenzproblem
            print(f"R_B Versuch {i+1}: Newton-Konvergenzproblem, setze V_CE auf -1")
            V_CE = -1
            # Starte bei nächster Iteration wieder mit ursprünglichen Startwerten
            initial_guess = [0.9, 8.0]

        # Prüfe, ob Lösung im gewünschten Toleranzbereich liegt
        if abs(V_CE - V_CE_ziel) <= tol_abs and V_CE > 0:
            print(f"\nErfolgreich: R_B={R_B:.2f} Ohm, V_CE={V_CE:.4f} V im Sollbereich!")
            print(f"V_BE={V_BE:.5f} V")
            print(f"Fehlervektor bei Lösung: {F([V_BE, V_CE])}")
            return R_B, V_BE, V_CE

        # Steuerung der Bisektion je nach Lage der Lösung:
        # Ist V_CE zu klein → Basisstrom zu gering → R_B muss kleiner sein
        # Ist V_CE zu groß → Basisstrom zu groß → R_B muss größer sein
        if V_CE < 0 or V_CE < V_CE_ziel:
            R_B_max = R_B_try
        else:
            R_B_min = R_B_try

    # Falls kein Wert gefunden wurde
    raise RuntimeError("Kein geeigneter R_B gefunden!")

# -------------------------------------------------------------------------
# Hauptprogramm-Ausführung
# -------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # Finde optimalen Basiswiderstand R_B
        result = finde_R_B_fuer_ap(V_CC=V_CC)

        R_B_opt, V_BE_opt, V_CE_opt = result

        # Berechnung Basisstrom in Ampere und in mA
        I_B_opt = (V_BB - V_BE_opt) / R_B_opt
        I_B_opt_mA = I_B_opt * 1e3

        # Ausgabe mit Basisstrom, Widerständen und Versorgungsspannung
        print("\nEndergebnis:")
        print(f"Optimaler R_B: {R_B_opt:.2f} Ohm")
        print(f"Kollektorwiderstand R_C: {R_C:.2f} Ohm")
        print(f"Versorgungsspannung V_CC: {V_CC:.2f} V")
        print(f"Arbeitspunkt: V_BE = {V_BE_opt:.5f} V, V_CE = {V_CE_opt:.5f} V")
        print(f"Basisstrom I_B = {I_B_opt_mA:.5f} mA")

        # -------------------------------------------------------------------------
        # Plot-Funktion zur Darstellung des Arbeitspunkts, der Arbeitsgeraden
        # und der Transistorkennlinie zum berechneten Basisstrom
        #
        # Außerdem Einblendung der Werte als Text im Plot
        # -------------------------------------------------------------------------
        def plot_kennlinie_mit_arbeitsgerade_und_arbeitspunkt(R_B, V_BE, V_CE,
                                                              q, k_B, T, I_S, V_A, R_C, V_CC, V_BB,
                                                              I_B_mA):
            """
            Zeichnet im 1. Quadranten:
            - Die Transistorkennlinie (Ic gegen Vce) beim Basisstrom, der sich am Arbeitspunkt ergibt,
            - Die Arbeitsgerade des Kollektorwiderstands,
            - Und markiert den Arbeitspunkt.
            Zusätzlich werden die Werte von R_C, R_B, V_CC und I_B als Text im Diagramm angezeigt.
            """

            # Spannung Vce von 0 bis Versorgungsspannung
            V_CE_vals = np.linspace(0, V_CC, 200)

            # Berechne Basisstrom I_B am Arbeitspunkt (aus Maschengleichung)
            I_B = (V_BB - V_BE) / R_B

            # Für diese Basisstromklasse: Kollektorstrom nach Ebers-Moll mit Early-Effekt
            # Ic(Vce) = Ib * (1 + Vce / VA)
            I_C_vals = I_B * (1 + V_CE_vals / V_A)

            # Arbeitsgerade (Lastlinie): Ic = (Vcc - Vce) / Rc
            I_C_loadline = (V_CC - V_CE_vals) / R_C

            plt.figure(figsize=(8,6))

            # Plot der Transistorkennlinie für den berechneten Basisstrom
            plt.plot(V_CE_vals, I_C_vals*1e3, label=f'Transistorkennlinie (I_B={I_B*1e6:.2f} µA)')

            # Plot der Arbeitsgeraden
            plt.plot(V_CE_vals, I_C_loadline*1e3, 'k--', label='Arbeitsgerade (Lastlinie)')

            # Arbeitspunkt (Vce, Ic) als roter Punkt einzeichnen
            I_C_ap = (V_CC - V_CE) / R_C
            plt.plot(V_CE, I_C_ap*1e3, 'ro', markersize=10, label='Arbeitspunkt')

            # Text mit relevanten Werten im Plot anzeigen
            textstr = '\n'.join((
                f'$R_C = {R_C:.1f} \\ \\Omega$',
                f'$R_B = {R_B:.1f} \\ \\Omega$',
                f'$V_{{CC}} = {V_CC:.2f} \\ V$',
                f'$I_B = {I_B_mA:.5f} \\mathrm{{mA}}$'
            ))

            # Position für den Text (relativ im Diagramm):
            plt.gca().text(0.05 * V_CC, 0.8 * max(np.max(I_C_vals), np.max(I_C_loadline))*1e3,
                           textstr, fontsize=12,
                           bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

            plt.xlabel('Kollektor-Emitter-Spannung $V_{CE}$ [V]')
            plt.ylabel('Kollektorstrom $I_C$ [mA]')
            plt.title('Transistorkennlinie, Arbeitsgerade und Arbeitspunkt')
            plt.grid(True)
            plt.legend()
            plt.xlim(0, V_CC * 1.05)
            max_current = max(np.max(I_C_vals), np.max(I_C_loadline))
            plt.ylim(0, max_current*1.2*1e3)
            plt.show()

        # Plot mit den berechneten Werten erzeugen
        plot_kennlinie_mit_arbeitsgerade_und_arbeitspunkt(
            R_B_opt, V_BE_opt, V_CE_opt, q, k_B, T, I_S, V_A, R_C, V_CC, V_BB,
            I_B_opt_mA)

    except Exception as e:
        # Falls keine Lösung gefunden wird oder andere Fehler auftreten
        print("Fehler:", e)
