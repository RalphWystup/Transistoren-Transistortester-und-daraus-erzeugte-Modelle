import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Physikalische Konstanten
# ----------------------------

q = 1.602e-19
k_B = 1.381e-23
T = 300

# ----------------------------
# Transistorparameter
# ----------------------------

I_S = 1e-13
beta_F = 200.0
n = 1.0
V_A = 100.0

# ----------------------------
# Schaltung
# ----------------------------

R_C = 1e2
V_CC = 25.0
V_BB = V_CC

R_B = 2e3

# -------------------------------------------------------------------------
# Fehlerfunktion
# -------------------------------------------------------------------------

def F(vars):

    V_BE, V_CE = vars

    I_B = (V_BB - V_BE) / R_B
    I_C = (V_CC - V_CE) / R_C

    exp_term = np.exp(
        q * V_BE / (n * k_B * T)
    )

    eq1 = (
        I_B
        - (I_S / beta_F)
        * exp_term
    )

    eq2 = (
        I_C
        - I_S
        * exp_term
        * (1.0 + V_CE / V_A)
    )

    return np.array([eq1, eq2])


# -------------------------------------------------------------------------
# Jacobi-Matrix
# -------------------------------------------------------------------------

def J(vars):

    V_BE, V_CE = vars

    exp_term = np.exp(
        q * V_BE / (n * k_B * T)
    )

    factor = (
        I_S
        * q
        / (n * k_B * T)
        * exp_term
    )

    d_eq1_dV_BE = (
        -1.0 / R_B
        - factor / beta_F
    )

    d_eq1_dV_CE = 0.0

    d_eq2_dV_BE = (
        -factor
        * (1.0 + V_CE / V_A)
    )

    d_eq2_dV_CE = (
        -1.0 / R_C
        - (I_S / V_A)
        * exp_term
    )

    return np.array([
        [d_eq1_dV_BE, d_eq1_dV_CE],
        [d_eq2_dV_BE, d_eq2_dV_CE]
    ])


# -------------------------------------------------------------------------
# Newton-Raphson
# -------------------------------------------------------------------------

def newton_method(
        initial_guess,
        tol=1e-10,
        max_iter=100):

    xy = np.array(
        initial_guess,
        dtype=float
    )

    for i in range(max_iter):

        f_val = F(xy)

        if np.all(np.abs(f_val) < tol):
            return xy, i + 1

        J_val = J(xy)

        delta = np.linalg.solve(
            J_val,
            -f_val
        )

        xy += delta

    raise ValueError(
        "Keine Konvergenz!"
    )


# -------------------------------------------------------------------------
# Bisektion für R_B
# -------------------------------------------------------------------------

def finde_R_B_fuer_ap(
        V_CC,
        toleranz_rel=0.05,
        R_B_min=10e3,
        R_B_max=500e3,
        max_iter=30):

    global R_B

    V_CE_ziel = V_CC / 2.0
    tol_abs = toleranz_rel * V_CE_ziel

    initial_guess = [0.65, V_CC/2]

    beste_loesung = None

    for i in range(max_iter):

        R_B_try = (
            R_B_min + R_B_max
        ) / 2.0

        R_B = R_B_try

        try:

            solution, iters = (
                newton_method(
                    initial_guess
                )
            )

            V_BE, V_CE = solution

            beste_loesung = (
                R_B,
                V_BE,
                V_CE
            )

            initial_guess = solution

            print(
                f"Versuch {i+1}: "
                f"R_B={R_B:.2f} Ω, "
                f"V_CE={V_CE:.4f} V "
                f"(Newton={iters})"
            )

        except Exception:

            print(
                f"Versuch {i+1}: "
                f"Newton-Fehler"
            )

            continue

        if abs(V_CE - V_CE_ziel) <= tol_abs:

            print()
            print("Arbeitspunkt gefunden")

            return (
                R_B,
                V_BE,
                V_CE
            )

        #
        # KORRIGIERTE Bisektionsrichtung
        #
        # R_B ↑ -> I_B ↓ -> I_C ↓ -> V_CE ↑
        #

        if V_CE < V_CE_ziel:
            R_B_min = R_B_try
        else:
            R_B_max = R_B_try

    if beste_loesung is not None:
        return beste_loesung

    raise RuntimeError(
        "Kein geeigneter R_B gefunden."
    )


# -------------------------------------------------------------------------
# Plot
# -------------------------------------------------------------------------

def plot_kennlinie(
        R_B,
        V_BE,
        V_CE,
        I_B_mA):

    V_CE_vals = np.linspace(
        0,
        V_CC,
        300
    )

    I_C_vals = (
        I_S
        * np.exp(
            q * V_BE
            / (n * k_B * T)
        )
        * (1.0 + V_CE_vals / V_A)
    )

    I_C_loadline = (
        V_CC - V_CE_vals
    ) / R_C

    plt.figure(figsize=(8, 6))

    plt.plot(
        V_CE_vals,
        I_C_vals * 1e3,
        label=f"Kennlinie bei V_BE={V_BE:.3f} V"
    )

    plt.plot(
        V_CE_vals,
        I_C_loadline * 1e3,
        'k--',
        label="Arbeitsgerade"
    )

    I_C_ap = (
        V_CC - V_CE
    ) / R_C

    plt.plot(
        V_CE,
        I_C_ap * 1e3,
        'ro',
        markersize=10,
        label="Arbeitspunkt"
    )

    plt.xlabel(
        "V_CE [V]"
    )

    plt.ylabel(
        "I_C [mA]"
    )

    plt.title(
        "Transistorkennlinie und Lastlinie"
    )

    plt.grid(True)
    plt.legend()

    plt.show()


# -------------------------------------------------------------------------
# Hauptprogramm
# -------------------------------------------------------------------------

if __name__ == "__main__":

    try:

        R_B_opt, V_BE_opt, V_CE_opt = (
            finde_R_B_fuer_ap(V_CC)
        )

        I_B_opt = (
            V_BB - V_BE_opt
        ) / R_B_opt

        I_C_opt = (
            I_S
            * np.exp(
                q * V_BE_opt
                / (n * k_B * T)
            )
            * (1.0 + V_CE_opt / V_A)
        )

        print()
        print("Endergebnis")
        print("---------------------")

        print(
            f"R_B  = {R_B_opt:.2f} Ω"
        )

        print(
            f"R_C  = {R_C:.2f} Ω"
        )

        print(
            f"V_BE = {V_BE_opt:.5f} V"
        )

        print(
            f"V_CE = {V_CE_opt:.5f} V"
        )

        print(
            f"I_B  = {I_B_opt*1e3:.6f} mA"
        )

        print(
            f"I_C  = {I_C_opt*1e3:.6f} mA"
        )

        print(
            f"β_F  = {beta_F:.1f}"
        )

        plot_kennlinie(
            R_B_opt,
            V_BE_opt,
            V_CE_opt,
            I_B_opt * 1e3
        )

    except Exception as e:

        print(
            "Fehler:",
            e
        )