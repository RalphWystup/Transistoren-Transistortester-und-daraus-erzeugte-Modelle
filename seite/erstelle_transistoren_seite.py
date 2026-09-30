#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt die eigenstaendige Browser-Seite zu

    "Transistoren, der Transistortester und die daraus erzeugten Modelle".

Die Seite ist nach REITERN gegliedert, und die Reiter folgen den
Teilmanuskripten des Verfassers.  Je Reiter steht sein Text vollstaendig und
unveraendert, darunter der rechnende Teil zu genau diesem Thema.

  "ich habe das Kapitel ueber die Transistoren und den Transistortester alles
   exakt ausgearbeitet. Also so lassen. An den Manuskripten nichts aendern, sie
   nur auf Reiter verteilen, und unter den Reitern auch meine Python-Programme
   als Grundlage fuer das HTML-Programm verwenden."

Daraus zwei Regeln, die ueber der ganzen Datei stehen:

 1. **An den Manuskripten wird nichts geaendert.**  Die einzige Ausnahme sind
    die zwoelf Berichtigungen aus der Befundliste, die der Verfasser
    ausdruecklich angenommen hat ("das kannst du anpassen"); sie stehen
    einzeln in `berichtigungen_transistoren.py` und sind in `BERICHTIGUNGEN.md`
    protokolliert.
 2. **Jede Rechnung dieser Seite ist Zeile fuer Zeile aus einem seiner
    Programme uebertragen** - dieselben Formeln, dieselben Konstanten,
    dieselbe Reihenfolge der Schritte, dieselben Startwerte, dieselben
    Abbruchbedingungen.  Ueber jeder Funktion steht, aus welchem Programm und
    aus welchen Zeilen sie stammt.  Nichts ist selbst erfunden; wo sein
    Programm etwas nicht kann, kann es die Seite auch nicht, und das steht
    dann dort.

Eine Regel: die Fassungsnummer steht nur in der Datei VERSION; alles andere
wird daraus gebaut.  Die Seite ist offline lauffaehig - kein Nachladen, keine
Fremdbibliothek, alle Bilder als Daten-Adresse eingebettet.

Zugangsdaten kommen in dieser Arbeit nicht vor: der Tester spricht Modbus
ueber die serielle Schnittstelle, es gibt weder Netznamen noch Kennwort.  Die
Ersetzungsliste `neutral()` bleibt trotzdem bestehen - sie ist die Stelle, an
der ein spaeter hinzukommendes Kennwort durch eine gleich lange Folge "x"
ersetzt wuerde.  Die Werte selbst stehen in `neutral_privat.json` neben dem
Erzeuger und werden nicht mitgeliefert.

  python3 erstelle_transistoren_seite.py
"""
from __future__ import annotations

import base64
import io
import json
import re
import sys
from pathlib import Path

# Keine festen Rechnerpfade: die Berichtigungsliste liegt neben dem Bauskript,
# der Ort wird aus dem dieser Datei erschlossen.
for _k in ("", "../../AUSFUHR", "../rechnung"):
    _p = (Path(__file__).resolve().parent / _k).resolve()
    if (_p / "berichtigungen_transistoren.py").is_file():
        sys.path.insert(0, str(_p))
        break
import berichtigungen_transistoren as BT

H = Path(__file__).resolve().parent
Q = H.parent
R = Q / "rechnung"
B = Q / "Bilder"
# Die Messreihen liegen im Arbeitsbereich neben den Programmen (Q.parent), in der Ausfuhr
# dagegen in einem eigenen Ordner "messungen". Beide Orte werden der Reihe nach gesucht.
KS = next((p for p in (Q.parent, Q.parent / "messungen", H.parent / "messungen", Q.parent.parent)
          if (p / "Ic_Vce.txt").is_file()), Q.parent)

# SEINE Netzliste der B4-Bruecke, woertlich aus der Datei gelesen — nicht
# abgeschrieben.  Im Arbeitsbereich liegt sie beim Grundlagenprojekt, in der
# Ausfuhr daneben in rechnung/.  Keine festen Rechnerpfade.
def _netzliste(name: str) -> str:
    for k in ("../rechnung", "../../DGL_Nichtlinear/Programme",
              "../../../DGL_Nichtlinear/Programme", "."):
        p = (H / k / name).resolve()
        if p.is_file():
            return p.read_text(encoding="utf-8")
    raise SystemExit(f"Netzliste nicht gefunden: {name}")


BRUECKE_NETZ = _netzliste("bruecke.netz")

VERSION = (H / "VERSION").read_text(encoding="utf-8").strip()
DATUM = "30.09.2026"
NAMENSNENNUNG = ("Prof. Dr.-Ing. Ralph Wystup M.Sc. — erstellt mit KI und Agent "
                 "(Claude Code, Anthropic)")
TITEL = "Transistoren, der Transistortester und die daraus erzeugten Modelle"
GRUNDLAGEN = ("https://ralphwystup.github.io/"
              "Schaltungssimulation-von-nichtlinearen-Differentialgleichungssystemen/")


# --------------------------------------------------------------- Neutralisierung
def _liste() -> list[tuple[str, str]]:
    p = H / "neutral_privat.json"
    return [tuple(x) for x in json.loads(p.read_text(encoding="utf-8"))] if p.is_file() else []


def neutral(t: str) -> str:
    """Text fuer die Veroeffentlichung saeubern: Netzname -> Platzhalter,
    Kennwort -> genauso viele "x" wie der Wert Zeichen hat."""
    for alt, neu in _liste():
        t = t.replace(alt, neu)
    t = re.sub(r'((?:WIFI|WLAN)_(?:PASSWORT|WORT|PASSWORD)\s*=\s*")([^"]*)(")',
               lambda m: m.group(1) + "x" * len(m.group(2)) + m.group(3), t)
    t = re.sub(r'((?:passwor[dt]|kennwort)\s*[:=]\s*")([^"]*)(")',
               lambda m: m.group(1) + "x" * len(m.group(2)) + m.group(3), t, flags=re.I)
    return t


# --------------------------------------------------------------- Messdaten lesen
def lade_tracer(name: str) -> list[dict]:
    """Eine Ausgabedatei des Kurvenschreibers: Spurname, x-Spalte, y-Spalte."""
    zeilen = (KS / f"{name}.txt").read_text(encoding="utf-8-sig").splitlines()
    kopf, spuren = 0, []
    for i, z in enumerate(zeilen):
        c = z.split("\t")
        if c[0] == "Trace:":
            spuren = [x.strip() for x in c[1:] if x.strip()]
        if c[0] == "Point":
            kopf = i
            break
    werte = []
    for z in zeilen[kopf + 1:]:
        if not z.strip():
            continue
        werte.append([float(x.strip().replace(",", ".")) if x.strip() else None
                      for x in z.split("\t")])
    aus = []
    for i, s in enumerate(spuren):
        x = [w[1 + 2 * i] if len(w) > 1 + 2 * i else None for w in werte]
        y = [w[2 + 2 * i] if len(w) > 2 + 2 * i else None for w in werte]
        # Runden erst bei 12 Stellen: eine Rundung auf 1e-6 in V_BE wuerde im
        # Gummel-Plot einen Fehler von 1e-6/(n*V_T) = 4e-5 im Logarithmus machen.
        paare = [(round(a, 12), round(b, 12)) for a, b in zip(x, y)
                 if a is not None and b is not None]
        aus.append(dict(name=s,
                        wert=float(re.sub(r"[^0-9.,-]", "", s.split("=")[1]).replace(",", ".")),
                        x=[p[0] for p in paare], y=[p[1] for p in paare]))
    return aus


def lade_csv() -> dict:
    """Die neun Reihen des Testers: {Datei: {IB: [[UCE, IC], ...]}} in A und V."""
    aus = {}
    ordner = Q / "Quellen" / "Messungen"
    for p in sorted(ordner.glob("*.csv")):
        stufen: dict[str, list] = {}
        for zeile in p.read_text(encoding="utf-8-sig").splitlines()[1:]:
            t = zeile.split(";")
            if len(t) < 3:
                continue
            stufen.setdefault(t[0], []).append([round(float(t[1]), 4),
                                                round(float(t[2]) * 1e-3, 8)])
        for v in stufen.values():
            v.sort()
        aus[p.stem] = {k: v for k, v in sorted(stufen.items(), key=lambda kv: float(kv[0]))}
    return aus


# --------------------------------------------------------------- Bilder einbetten
def bild(name: str, breite: int = 1150, qualitaet: int = 80) -> str:
    from PIL import Image
    im = Image.open(B / name)
    if im.width > breite:
        im = im.resize((breite, max(1, round(im.height * breite / im.width))), Image.LANCZOS)
    puffer = io.BytesIO()
    if name.lower().endswith((".jpg", ".jpeg")):
        im.convert("RGB").save(puffer, "JPEG", quality=qualitaet, optimize=True)
        art = "image/jpeg"
    else:
        im.convert("RGB").quantize(colors=128, method=Image.MEDIANCUT).save(
            puffer, "PNG", optimize=True)
        art = "image/png"
    return f"data:{art};base64," + base64.b64encode(puffer.getvalue()).decode("ascii")


# --------------------------------------------------------------- Formelsatz
TEX = [
    (r"\\begin\{aligned\}", ""), (r"\\end\{aligned\}", ""),
    (r"\\begin\{pmatrix\}", "⎡ "), (r"\\end\{pmatrix\}", " ⎤"),
    (r"\\begin\{bmatrix\}", "⎡ "), (r"\\end\{bmatrix\}", " ⎤"),
    (r"\\\\\[[0-9a-z]*\]", " ;  "), (r"\\\\", " ;  "), (r"&", "  "),
    (r"\\underbrace\{([^{}]*)\}_\{[^{}]*\}", r"\1"),
    (r"\\boxed\{", "▸ "), (r"\\left[.]", ""), (r"\\right\|", "|"),
    (r"\\left", ""), (r"\\right", ""),
    (r"\\mathrm\{([^{}]*)\}", r"\1"), (r"\\text\{([^{}]*)\}", r"\1"),
    (r"\\mathbf\{([^{}]*)\}", r"\1"), (r"\\operatorname\{([^{}]*)\}", r"\1"),
    (r"\{,\}", ","), (r"\\quad", "   "), (r"\\qquad", "      "),
    (r"\\,", " "), (r"\\;", " "), (r"\\:", " "), (r"\\!", ""),
    (r"\\sum_\{([^{}]*)\}\^\{([^{}]*)\}", r"Σ[\1..\2] "),
    (r"\\lfloor", "⌊"), (r"\\rfloor", "⌋"),
    (r"\\partial", "∂"), (r"\\cdot", "·"), (r"\\times", "×"),
    (r"\\approx", "≈"), (r"\\le\b", "≤"), (r"\\ge\b", "≥"), (r"\\neq", "≠"),
    (r"\\lesssim", "≲"), (r"\\gg", "≫"), (r"\\ll", "≪"),
    (r"\\parallel", "∥"), (r"\\Longrightarrow", "⟹"), (r"\\Rightarrow", "⟹"),
    (r"\\rightarrow", "→"), (r"\\to\b", "→"), (r"\\pm", "±"), (r"\\infty", "∞"),
    (r"\\Omega", "Ω"), (r"\\mu", "µ"), (r"\\pi", "π"), (r"\\beta", "β"),
    (r"\\alpha", "α"), (r"\\delta", "δ"), (r"\\Delta", "Δ"), (r"\\sigma", "σ"),
    (r"\\lambda", "λ"), (r"\\omega", "ω"), (r"\\varphi", "φ"), (r"\\theta", "θ"),
    (r"\\overline\{([^{}]*)\}", "\\1\u0304"),
    (r"\\exp", "exp"), (r"\\ln\b", "ln"), (r"\\log(?![a-z])", "log"),
    (r"\\max(?![a-z])", "max"), (r"\\min(?![a-z])", "min"),
    (r"\\ldots", "…"), (r"\\dots", "…"), (r"\\cdots", "⋯"),
    (r"\\lVert", "‖"), (r"\\rVert", "‖"),
    (r"\\\|", "∥"), (r"\\%", "%"), (r"\\&", "&"),
]
KLAMMER = r"(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*"
FRAC = re.compile(r"\\[dt]?frac\{(" + KLAMMER + r")\}\{(" + KLAMMER + r")\}")
WURZEL = re.compile(r"\\sqrt\{(" + KLAMMER + r")\}")
SUB = re.compile(r"_\{((?:[^{}]|\{[^{}]*\})*)\}")
SUP = re.compile(r"\^\{((?:[^{}]|\{[^{}]*\})*)\}")


def formel(t: str) -> str:
    t = t.replace(r"\_", "\u0001")
    for a, b in TEX:
        t = re.sub(a, b, t)
    for _ in range(5):
        neu2 = FRAC.sub(r"(\1)/(\2)", WURZEL.sub(r"√(\1)", t))
        if neu2 == t:
            break
        t = neu2
    t = t.replace("\\sqrt", "√")
    for _ in range(3):
        t2 = SUP.sub(r"<sup>\1</sup>", SUB.sub(r"<sub>\1</sub>", t))
        if t2 == t:
            break
        t = t2
    t = re.sub(r"_([A-Za-z0-9πβµαδΔ])", r"<sub>\1</sub>", t)
    t = re.sub(r"\^([A-Za-z0-9])", r"<sup>\1</sup>", t)
    t = t.replace("{", "").replace("}", "").replace("\\", "").replace("\u0001", "_")
    return re.sub(r"[ \t]{2,}", "  ", t).strip()


def zeile(t: str) -> str:
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", t)
    t = re.sub(r"\$([^$]+)\$", lambda m: '<span class="f">' + formel(m.group(1)) + "</span>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<i>\1</i>", t)
    # Was pandoc maskiert hat, wieder entmaskieren - sonst stehen die
    # Schraegstriche im Satz (\[, \], \_, \|, \{, \}, \$, \#).
    t = re.sub(r"\\([\[\]_|{}$#*~^.<>()+-])", r"\1", t)
    return t


def markdown(t: str, bilder: dict) -> str:
    """Genug Markdown fuer diese Dokumente: Ueberschriften, Absaetze, Listen,
    Tabellen (Pipe und Gitter), Bilder, Formeln, Quelltext, Zitatblock."""
    t = re.sub(r"^---\n.*?\n---\n", "", t, flags=re.S)
    t = t.replace("\\newpage", "")
    aus, zeilen, i = [], t.split("\n"), 0
    while i < len(zeilen):
        z = zeilen[i]
        if z.startswith("$$"):
            block = [z]
            if not (z.rstrip().endswith("$$") and len(z.strip()) > 4):
                # Das Ende einer abgesetzten Formel kann auch eine Zeile sein, die
                # MIT $$ anfaengt (pandoc setzt die Gleichungsnummer so: "$$ (4.2)").
                # Ohne diesen Fall frisst der Block den Rest des Dokuments.
                while i + 1 < len(zeilen):
                    i += 1
                    block.append(zeilen[i])
                    if "$$" in zeilen[i]:
                        break
            roh = " ".join(block).replace("$$", " ").strip()
            aus.append('<div class="fb">' + formel(roh) + "</div>")
        elif z.startswith("```"):
            i += 1
            block = []
            while i < len(zeilen) and not zeilen[i].startswith("```"):
                block.append(zeilen[i])
                i += 1
            aus.append("<pre>" + "\n".join(block).replace("&", "&amp;").replace("<", "&lt;") + "</pre>")
        elif z.startswith("!["):
            block = [z]
            while not block[-1].rstrip().endswith(")") and "){" not in block[-1] and i + 1 < len(zeilen):
                i += 1
                block.append(zeilen[i])
            roh = " ".join(block)
            m = re.match(r"!\[(.*?)\]\((.*?)\)", roh, flags=re.S)
            if m:
                n = Path(m.group(2)).name
                if n in bilder:
                    aus.append(f'<figure><img src="{bilder[n]}" alt="Abbildung">'
                               f'<figcaption>{zeile(m.group(1))}</figcaption></figure>')
                else:
                    aus.append(f'<p class="fehlt">[Bild {n} nicht eingebettet]</p>')
        elif z.startswith("#"):
            n = len(z) - len(z.lstrip("#"))
            aus.append(f"<h{min(n+1,6)}>{zeile(z.lstrip('# ').strip())}</h{min(n+1,6)}>")
        elif z.startswith(">"):
            block = []
            while i < len(zeilen) and zeilen[i].startswith(">"):
                block.append(zeilen[i].lstrip("> ").rstrip())
                i += 1
            i -= 1
            aus.append("<blockquote>" + zeile(" ".join(x for x in block if x)) + "</blockquote>")
        elif z.startswith("+--") or z.startswith("+=="):
            # Gittertabelle von pandoc: Zellen koennen mehrzeilig sein
            block = []
            while i < len(zeilen) and (zeilen[i].startswith("|") or zeilen[i].startswith("+")):
                block.append(zeilen[i])
                i += 1
            i -= 1
            reihen, puffer = [], None
            for b in block:
                if b.startswith("+"):
                    if puffer:
                        reihen.append(puffer)
                    puffer = None
                else:
                    # Ein maskierter Strich \| gehoert in die Zelle und ist kein
                    # Zellenende - sonst faellt der Zelleninhalt auseinander.
                    zellen = [c.replace("\u0002", "|").strip()
                              for c in b.replace("\\|", "\u0002").strip("|").split("|")]
                    if puffer is None:
                        puffer = zellen
                    else:
                        for k in range(min(len(puffer), len(zellen))):
                            if zellen[k]:
                                puffer[k] = (puffer[k] + " " + zellen[k]).strip()
            if puffer:
                reihen.append(puffer)
            if reihen:
                leib = "".join("<tr>" + "".join(f"<td>{zeile(c)}</td>" for c in r) + "</tr>"
                               for r in reihen)
                aus.append(f"<table class='gitter'><tbody>{leib}</tbody></table>")
        elif re.fullmatch(r"\s*-{3,}\s*", z) or re.fullmatch(r"\s*\*{3,}\s*", z):
            aus.append("<hr>")
        elif z.startswith("|"):
            block = []
            while i < len(zeilen) and zeilen[i].startswith("|"):
                block.append(zeilen[i])
                i += 1
            i -= 1
            # ein maskierter Strich \| ist Text, kein Zellenende
            teile = lambda r: [c.replace("\u0002", "|").strip()
                               for c in r.replace("\\|", "\u0002").strip("|").split("|")]
            reihen = [teile(r) for r in block]
            reihen = [r for r in reihen if not all(set(c) <= set(":- ") for c in r)]
            if reihen:
                kopf = "".join(f"<th>{zeile(c)}</th>" for c in reihen[0])
                leib = "".join("<tr>" + "".join(f"<td>{zeile(c)}</td>" for c in r) + "</tr>"
                               for r in reihen[1:])
                aus.append(f"<table><thead><tr>{kopf}</tr></thead><tbody>{leib}</tbody></table>")
        elif re.match(r"^\s*[*-]\s+", z) or re.match(r"^\s*\d+\.\s+", z):
            art = "ol" if re.match(r"^\s*\d+\.\s+", z) else "ul"
            block = []
            while i < len(zeilen) and (re.match(r"^\s*[*-]\s+", zeilen[i])
                                       or re.match(r"^\s*\d+\.\s+", zeilen[i])
                                       or (block and zeilen[i].startswith("  ") and zeilen[i].strip())):
                s = re.sub(r"^\s*(?:[*-]|\d+\.)\s+", "", zeilen[i])
                if re.match(r"^\s*(?:[*-]|\d+\.)\s+", zeilen[i]) or not block:
                    block.append(s)
                else:
                    block[-1] += " " + s.strip()
                i += 1
            i -= 1
            aus.append(f"<{art}>" + "".join(f"<li>{zeile(x)}</li>" for x in block) + f"</{art}>")
        elif z.strip():
            block = []
            while i < len(zeilen) and zeilen[i].strip() and not zeilen[i].startswith(
                    ("#", "|", "$$", "```", "![", ">", "+--", "+==")) \
                    and not re.match(r"^\s*(?:[*-]|\d+\.)\s+", zeilen[i]):
                block.append(zeilen[i])
                i += 1
            i -= 1
            aus.append("<p>" + zeile(" ".join(block)) + "</p>")
        i += 1
    return "\n".join(aus)




# ------------------------------------------------- der rechnende Teil je Reiter
def _kopf(titel: str, herkunft: str) -> str:
    return f'<h2>{titel}</h2>\n  <p class="herkunft">{herkunft}</p>\n'


RECHNER = {

# =============================================================== Diodenkennlinie
"diode": _kopf(
    "Arbeitspunkt der Diode: Newton-Raphson, und die Bisektion auf R",
    "Übertragen aus <code>BUCH/kap08_led_quellen.py</code>, Zeilen 30–49 — das ist die "
    "quellentreue Wiedergabe von <code>Optimierung_AP_1.py</code>, dem Programm, das dieses "
    "Manuskript beschreibt. Newton-Raphson im <b>Strom</b> (Abschnitt 5.2), Startwert "
    "<span class='f'>U<sub>ges</sub>/(R+R<sub>S</sub>+1)</span>, Abbruch bei "
    "|ΔI| &lt; 10<sup>−7</sup>, höchstens 1000 Schritte. Die Bisektion auf R (Abschnitt 6.2) "
    "läuft im Intervall 1 Ω … 1 000 000 Ω. <b>Den Ausgleich selbst rechnet die Seite nicht</b> "
    "— dafür benutzt sein Programm <code>scipy.optimize.curve_fit</code> "
    "(Levenberg-Marquardt); die Seite arbeitet mit dem Ergebnis dieses Ausgleichs weiter."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="di_n">Idealitätsfaktor n</label>
      <input id="di_n" type="number" value="1.8976885" step="0.01"></div>
    <div class="feld"><label for="di_ls">log<sub>10</sub>(I<sub>S</sub>/A)</label>
      <input id="di_ls" type="number" value="-25.825582" step="0.1"></div>
    <div class="feld"><label for="di_rs">R<sub>S</sub> / Ω</label>
      <input id="di_rs" type="number" value="16.042814" step="0.5"></div>
    <div class="feld"><label for="di_u">U<sub>ges</sub> / V</label>
      <input id="di_u" type="number" value="5" step="0.5"></div>
    <div class="feld"><label for="di_r">R / Ω</label>
      <input id="di_r" type="number" value="100" step="10"></div>
    <div class="feld"><label for="di_soll">Wunschstrom für die Bisektion / mA</label>
      <input id="di_soll" type="number" value="20" step="1"></div>
    <button class="tat" id="di_start">Newton-Raphson rechnen</button>
    <button class="tat" id="di_bi">R für den Wunschstrom suchen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>Die Newton-Schritte im Strom</h3>
      <div class="iter"><table class="zahl" id="di_tab"></table></div>
      <div class="zu" id="di_zu"></div></div>
    <div class="karte"><h3>Kennlinie und Lastgerade</h3>
      <canvas id="di_bild" width="720" height="470"></canvas></div>
    <div class="karte"><h3>Ergebnis, und was sein Programm ausgibt</h3>
      <table class="zahl" id="di_erg"></table></div>
    <div class="karte"><h3>Bisektion auf R</h3>
      <div class="iter"><table class="zahl" id="di_bitab"></table></div></div>
  </div>""",

# ===================================================================== Leuchtdiode
"led": _kopf(
    "Die blaue Leuchtdiode: reines Shockley-Modell gegen das erweiterte",
    "Übertragen aus <code>BUCH/kap08_led_quellen.py</code>: die Modellfunktionen "
    "(Zeilen 25–33), der Newton-Löser im Strom (Zeilen 35–49) und die Fitwerte, die sein "
    "Programm an 46 Messpunkten einer blauen LED bestimmt. Die Seite <b>fittet nicht selbst</b> "
    "— sie rechnet mit genau den Werten weiter, die sein Lauf ausgibt, und stellt beide "
    "Modelle nebeneinander."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="le_u">U<sub>ges</sub> / V</label>
      <input id="le_u" type="number" value="5" step="0.5"></div>
    <div class="feld"><label for="le_r">R / Ω</label>
      <input id="le_r" type="number" value="100" step="10"></div>
    <button class="tat" id="le_start">Arbeitspunkt rechnen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>Die beiden Anpassungen aus seinem Lauf</h3>
      <table class="zahl" id="le_fit"></table>
      <div class="zu">46 Messpunkte, davon 35 im erweiterten Fitfenster (I &gt; 0,05 mA) —
        so meldet es <code>kap08_led_quellen.py</code>.</div></div>
    <div class="karte"><h3>Die Newton-Schritte</h3>
      <div class="iter"><table class="zahl" id="le_tab"></table></div></div>
    <div class="karte"><h3>Arbeitspunkt, und was sein Programm ausgibt</h3>
      <table class="zahl" id="le_erg"></table></div>
    <div class="karte"><h3>Beide Kennlinien und die Lastgerade</h3>
      <canvas id="le_bild" width="720" height="470"></canvas></div>
  </div>""",

# ==================================================================== BJT und SPICE
"bjtspice": _kopf(
    "Der Arbeitspunkt der Fixed-Bias-Stufe: Newton innen, Bisektion außen",
    "Übertragen aus <code>Transistor_21b.py</code>: die Residuen (Zeilen 34–57), die "
    "analytische Jacobi-Matrix (Zeilen 63–98), Newton-Raphson mit tol = 10<sup>−10</sup> und "
    "höchstens 100 Schritten (Zeilen 104–140) und die Bisektion auf R<sub>B</sub> im Intervall "
    "10 kΩ … 500 kΩ mit 5 % Toleranzband und mitgeführtem Startwert (Zeilen 143–228). "
    "Parameter dieses Programms: I<sub>S</sub> = 10<sup>−13</sup> A, β<sub>F</sub> = 200, "
    "n = 1, V<sub>A</sub> = 100 V, V<sub>CC</sub> = 25 V, R<sub>C</sub> = 100 Ω."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="bs_vcc">V<sub>CC</sub> = V<sub>BB</sub> / V</label>
      <input id="bs_vcc" type="number" value="25" step="1"></div>
    <div class="feld"><label for="bs_rc">R<sub>C</sub> / Ω</label>
      <input id="bs_rc" type="number" value="100" step="10"></div>
    <button class="tat" id="bs_start">R<sub>B</sub> suchen und Arbeitspunkt rechnen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>Die Bisektionsversuche — wie in seiner Konsolenausgabe</h3>
      <div class="iter"><table class="zahl" id="bs_bitab"></table></div></div>
    <div class="karte"><h3>Die Newton-Schritte im letzten Versuch</h3>
      <div class="iter"><table class="zahl" id="bs_tab"></table></div></div>
    <div class="karte breit"><h3>Ergebnis, und was sein Programm ausgibt</h3>
      <table class="zahl" id="bs_erg"></table>
      <div class="hinweis">Zwei unabhängige Wege, gleiche Zahl: der hier gefundene
        Basiswiderstand steht auf die Ziffer genau auch im Schriftfeld seiner
        LTspice-Schaltung <code>Eigen_RW_1d.asc</code> (R2 = 44453).</div></div>
    <div class="karte breit"><h3>Ausgangskennlinie, Lastgerade und Arbeitspunkt</h3>
      <canvas id="bs_bild" width="1100" height="440"></canvas></div>
  </div>""",

# ================================================================= Extraktion BC547
"bc547": _kopf(
    "Die ideale Abschätzung von R<sub>B</sub> — und wie weit sie neben dem Modell liegt",
    "Übertragen aus <code>BUCH/kap08_rechnung.py</code>, Zeilen 104–107: "
    "<span class='f'>I<sub>C</sub> = V<sub>CC</sub>/(2R<sub>C</sub>)</span>, "
    "<span class='f'>V<sub>BE</sub> = n·V<sub>T</sub>·ln(I<sub>C</sub>/I<sub>S</sub>)</span>, "
    "<span class='f'>R<sub>B</sub> = (V<sub>BB</sub> − V<sub>BE</sub>)/(I<sub>C</sub>/β<sub>F</sub>)</span> "
    "— ohne Early, ohne inneren Basiswiderstand, ohne Webster. Daneben der Wert, den dasselbe "
    "Programm mit dem vollständigen Modell findet (Reiter „Arbeitspunkt Newton“)."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="bc_vcc">V<sub>CC</sub> = V<sub>BB</sub> / V</label>
      <input id="bc_vcc" type="number" value="25" step="1"></div>
    <div class="feld"><label for="bc_rc">R<sub>C</sub> / Ω</label>
      <input id="bc_rc" type="number" value="100" step="10"></div>
    <button class="tat" id="bc_start">Abschätzung und Modellwert rechnen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>Die Abschätzung Schritt für Schritt</h3>
      <table class="zahl" id="bc_tab"></table></div>
    <div class="karte"><h3>Warum der Unterschied so groß ist</h3>
      <table class="zahl" id="bc_warum"></table>
      <div class="zu">Der Kniestrom I<sub>KF</sub> = 80 mA des gemessenen BC547-Satzes liegt
        <i>unter</i> dem Zielstrom von 125 mA — β<sub>eff</sub> bricht ein, und der Basisstrom
        muss entsprechend größer sein.</div></div>
  </div>""",

# ============================================================ Arbeitspunkt von Hand
"t20": _kopf(
    "Newton-Raphson und die äußere Bisektion — genau wie in seinem Programm",
    "Übertragen aus <code>Transistor_20.py</code>: die Fehlerfunktion (Zeilen 36–54), die "
    "analytische Jacobi-Matrix (Zeilen 64–80), Newton-Raphson mit tol = 10<sup>−10</sup>, "
    "höchstens 100 Schritten und Abbruch bei V<sub>CE</sub> &lt; 0 (Zeilen 100–117) und die "
    "äußere Bisektion auf R<sub>B</sub> im Intervall 500 Ω … 100 kΩ mit 5 % Toleranzband, "
    "Startwert [0,9 V; 8,0 V] und adaptiver Mitführung (Zeilen 139–182). "
    "<b>Was dieses Programm nicht kann:</b> es kennt keine Stromverstärkung — Zeile 51 setzt "
    "I<sub>C</sub> = I<sub>B,Shockley</sub>·(1 + V<sub>CE</sub>/V<sub>A</sub>), also "
    "β = 1. Der Basisstrom fällt deshalb mit rund 7 mA viel zu groß aus. Das steht hier so, "
    "weil sein Programm es so rechnet."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="t2_vcc">V<sub>CC</sub> = V<sub>BB</sub> / V</label>
      <input id="t2_vcc" type="number" value="15" step="1"></div>
    <div class="feld"><label for="t2_rc">R<sub>C</sub> / Ω</label>
      <input id="t2_rc" type="number" value="1000" step="100"></div>
    <button class="tat" id="t2_start">R<sub>B</sub> suchen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>Die Versuche der äußeren Bisektion</h3>
      <div class="iter"><table class="zahl" id="t2_bitab"></table></div>
      <div class="zu" id="t2_zu"></div></div>
    <div class="karte"><h3>Ergebnis, und was sein Programm ausgibt</h3>
      <table class="zahl" id="t2_erg"></table></div>
  </div>""",

# ============================================================== Minimaler Datensatz
"mindat": _kopf(
    "Der minimale Datensatz, gerechnet",
    "Dieses Teilmanuskript beschreibt, mit wie wenigen Parametern ein BJT statisch noch "
    "brauchbar beschrieben ist. Gerechnet wird derselbe Satz im Reiter "
    "<b>BJT und SPICE</b> (<code>Transistor_21b.py</code>: I<sub>S</sub>, β<sub>F</sub>, n, "
    "V<sub>A</sub>) und im Reiter <b>Gummel-Poon</b> (die vier Erweiterungen darüber). Hier "
    "steht nur, was sein eigener Bestand hergibt: die Gegenüberstellung der beiden Sätze."
) + r"""
  <div class="karte"><h3>Was die beiden Sätze enthalten</h3>
    <table id="md_tab"></table></div>""",

# ============================================================== Der Transistortester
"tester": _kopf(
    "Das Gerät: aus dem Registerwert in Volt, aus Volt in Ampere",
    "Übertragen aus <code>Kennlinienschreiber_1.py</code>, Zeilen 30–52 und 119–140: "
    "<code>volt_to_dac</code>, <code>adc_to_volt</code> und die beiden Umrechnungen, mit "
    "denen aus den vier gemittelten Wandlerwerten Kollektor- und Basisstrom werden. "
    "Darunter die neun Ausgangskennfelder, die der Tester aufgenommen hat, unmittelbar aus "
    "seinen CSV-Dateien gezeichnet."
) + r"""
  <h3 class="nzh">Das Gerät</h3>
  <div class="gitter2">
    <div class="karte breit"><h3>Die Platine mit dem Prüfling</h3>
      <figure style="margin:0">
        <img data-bild="platine" alt="Platine des Transistortesters mit ESP32-Modul,
          Klemmenleiste, steckbaren Messwiderständen und angeklemmtem Prüfling">
        <figcaption>Links das ESP32-Modul mit seiner USB-Buchse. Daneben die grünen
          Schraubklemmen: zuerst die Versorgung (GND, +24&nbsp;V), dann die acht Messklemmen,
          deren Belegung im Siebdruck für beide Bauteilarten dasteht —
          <span class="f">NPN: Rc C E Rb GND</span> und
          <span class="f">PNP: E C Rc B Rb GND</span>. In den Klemmen stecken die beiden
          <b>Messwiderstände</b>: ein kleiner Schichtwiderstand als R<sub>b</sub> im
          Basiszweig, der große blaue Drahtwiderstand als R<sub>c</sub> im Kollektorzweig.
          Beide sind <b>steckbar</b> — sie bestimmen, welcher Strombereich gemessen wird, und
          sie sind es, aus deren Spannungsabfall die Ströme gerechnet werden. Rechts hängt der
          Prüfling in einem Leistungsgehäuse mit Metallfahne an drei Prüfklemmen: blau an der
          Basis, violett am Kollektor, rot am Emitter. Unten rechts auf der Leiterplatte steht
          die Fertigungsnummer des Platinenherstellers.</figcaption>
      </figure></div>
    <div class="karte breit"><h3>Die Funktionsübersicht — seine Handskizze</h3>
      <figure style="margin:0">
        <img data-bild="skizze" alt="Handskizze des Übersichtsplans: ESP32, zwei
          Digital-Analog-Umsetzer mit Verstärkern, steckbare Widerstände, Prüfling und vier
          Analog-Digital-Umsetzer">
        <figcaption>Von links nach rechts gelesen: Am <b>USB</b> hängt der <b>ESP32</b>
          (in seiner Schrift „ESP23“). Von ihm gehen zwei gleichartige Zweige ab, jeder aus
          einem <b>Digital-Analog-Umsetzer</b> („DA“) und einem nachgeschalteten
          <b>Verstärker</b> („OP“). Der obere Zweig stellt den Kollektorkreis:
          <b>0…12&nbsp;V bei höchstens 500&nbsp;mA</b>. Er speist den Knoten
          <b>Rc1</b>; von dort geht es über den <b>steckbaren Kollektorwiderstand
          R<sub>c</sub></b> zum Knoten <b>Rc2</b>, und der liegt am Kollektor des Prüflings.
          Der untere Zweig stellt den Basiskreis: <b>0…12&nbsp;V bei höchstens 50&nbsp;mA</b>,
          Knoten <b>Rb1</b>, <b>steckbarer Basiswiderstand R<sub>B</sub></b>, Knoten
          <b>Rb2</b> an der Basis. Von Rb2 führt zusätzlich ein <b>Ableitwiderstand
          („RB-GND“)</b> nach Masse. Der <b>Prüfling</b> sitzt in der Mitte, sein Emitter
          liegt an Masse. Rechts vier Messzweige, jeder wieder <b>OP</b> und dahinter
          <b>AD</b>: sie greifen die Potentiale der vier Knoten Rc1, Rc2, Rb2 und Rb1 ab.
          Drei der vier Beschriftungen am rechten Rand sind eindeutig zu lesen —
          U<sub>CE</sub> (an Rc2, dem Kollektor), U<sub>BE</sub> (an Rb2, der Basis) und
          U<sub>BB</sub> (an Rb1, der Basiseinspeisung); die oberste ist es nicht: sie kann
          U<sub>Rc</sub> oder U<sub>BC</sub> heißen. <b>Welche Größe gemeint ist, lässt die
          Schaltung dennoch nicht offen</b> — es ist das Potential des Knotens Rc1, und der
          Schaltplan bestätigt es: der Analog-Digital-Umsetzer AD7682 hat genau vier
          Eingänge, und sie heißen dort UC1_S, UC2_S, UB1_S und UB2_S, also die vier Knoten
          und nichts anderes. Aus den Differenzen werden die Ströme:
          <span class="f">I<sub>C</sub> = (U<sub>Rc1</sub> − U<sub>Rc2</sub>)/R<sub>c</sub></span>
          und
          <span class="f">I<sub>B</sub> = (U<sub>Rb1</sub> − U<sub>Rb2</sub>)/R<sub>b</sub></span>.
          <b>Das Fragezeichen</b> steht an zwei Stellen: an dem Verstärker des
          U<sub>BE</sub>-Zweiges und an der unteren Rückleitung zum ESP32. Es ist seine eigene
          Notiz; worauf sie sich bezieht, lässt sich aus dem vorliegenden Material nicht
          belegen, und sie wird deshalb hier nur benannt und nicht gedeutet.</figcaption>
      </figure></div>
    <div class="karte breit"><h3>Vom Übersichtsbild zur Ausführung: die beiden
      Schaltplanblätter</h3>
      <figure style="margin:0">
        <img data-bild="ops" alt="Schaltplanblatt „OPs“: vier Messverstärker mit
          Schutzdioden und die beiden Leistungsstufen">
        <figcaption><b>Blatt 1 — „OPs“.</b> Oben die vier Messzweige der Skizze in ihrer
          Ausführung: je ein Spannungsteiler 43&nbsp;kΩ / 22&nbsp;kΩ mit einer 4,7-V-Zenerdiode
          (BZT52C4V7) als Schutz, dahinter ein Verstärker vom Typ LTA8092 (U2, U3) als
          Impedanzwandler zu den Wandlereingängen UB1_S, UB2_S, UC1_S und UC2_S. Unten die
          beiden <b>Leistungsstufen</b>, die in der Skizze nur „OP“ heißen: ein
          Doppelverstärker TCA0372 mit einem Längstransistor 2SC3519 an +24&nbsp;V; die
          Gegenkopplung aus 5,6&nbsp;kΩ und 22&nbsp;kΩ setzt die Spannung der
          Digital-Analog-Umsetzer (UB_I, UC_I) auf den Ausgangsbereich um. Links die
          Klemmenleisten CN1/CN2 mit der Belegung RC1, RC2 = C, GND = E, RB2 = B, RB1 — das
          ist genau die Leiste, die auf dem Foto zu sehen ist.</figcaption>
      </figure>
      <figure>
        <img data-bild="cpu" alt="Schaltplanblatt „CPU und AD/DA“: ESP32-DEVKITC, AD7682,
          DAC8565 und die Spannungsversorgung">
        <figcaption><b>Blatt 2 — „CPU und AD/DA“.</b> Links das ESP32-DEVKITC. Unten links
          der <b>Analog-Digital-Umsetzer AD7682</b>, vier Eingänge IN0…IN3 für genau die vier
          Messzweige, mit dem handschriftlichen Vermerk „Uref 4.095 = 0..4.095&nbsp;V“. Unten
          rechts der <b>Digital-Analog-Umsetzer DAC8565</b> mit zwei benutzten Ausgängen
          (UB_I, UC_I) im Bereich 0…2,5&nbsp;V und dem Vermerk „Achtung: SPI_Mode 3!“. Oben
          rechts die Versorgung: aus +24&nbsp;V werden +5&nbsp;V (K7805M), +15&nbsp;V (K7815)
          und −3&nbsp;V (IB0503LS).
          <b>Ein Unterschied zur Skizze, der benannt gehört:</b> die Handskizze beschriftet die
          Verbindung zu den Umsetzern mit „i2c“; ausgeführt sind beide Wandler am
          <b>SPI</b>-Bus (SPI_MOSI, SPI_SCK, SPI_CS1/CS2). Die Skizze ist die ältere
          Darstellung; maßgebend ist das Blatt.</figcaption>
      </figure>
      <div class="zu">Beide Blätter zusammen liegen als <code>Schaltplan_Kennlinienschreiber.pdf</code>
        bei. Im Schriftfeld steht der Name eines Dritten; er ist in der ausgelieferten Fassung
        buchstabengleich durch „x“ ersetzt (Vorgabe vom 29.09.2026).</div></div>
    <div class="karte breit"><h3>Wo das Gerät ausführlich beschrieben ist</h3>
      <p class="merk">Diese Seite zeigt das Gerät so weit, wie es zum Verständnis der Zahlen
        nötig ist: Platine, Übersicht, Schaltplan. Die <b>ausführliche</b> Darstellung —
        Kaskadenregelung der beiden Quellen, Registerplan der Modbus-Schnittstelle und die
        Herleitung der Gerätekonstanten — steht in der eigenen Arbeit zum
        Kennlinienschreiber. <span class="fehlt">Die Veröffentlichungsadresse wird hier
        nachgetragen, sobald sie steht.</span></p></div>
  </div>

  <h3 class="nzh">Von der Klemme zur Zahl</h3>
  <div class="werkbank">
    <div class="feld"><label for="ts_raw">Wandlerwert (0…65535)</label>
      <input id="ts_raw" type="number" value="32768" step="1" min="0" max="65535"></div>
    <div class="feld"><label for="ts_volt">Sollspannung am DAC / V</label>
      <input id="ts_volt" type="number" value="1.25" step="0.05" min="0" max="2.5"></div>
    <div class="feld"><label for="ts_rc">R<sub>c</sub> / Ω</label>
      <input id="ts_rc" type="number" value="100" step="10"></div>
    <div class="feld"><label for="ts_rb">R<sub>b</sub> / Ω</label>
      <input id="ts_rb" type="number" value="10000" step="1000"></div>
    <div class="feld"><label for="ts_reihe">Messreihe</label>
      <select id="ts_reihe"></select></div>
    <button class="tat" id="ts_start">Umrechnen und zeichnen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>Die Gerätekonstanten, wie sie in seinem Programm stehen</h3>
      <table class="zahl" id="ts_konst"></table>
      <div class="hinweis"><b>Zur Referenzspannung.</b> Der Nennwert der internen Referenz des
        AD7682 ist 4,096 V, und mit diesem Wert rechnet sein Programm (Zeile 35). Der Vermerk
        „Uref 4.095 = 0..4.095V“ im Schaltplan nennt den Vollbereich
        (2<sup>16</sup>−1)/2<sup>16</sup>·4,096 V = 4,0999 V, gerundet notiert. Der
        Unterschied beträgt 2,95 mV von 12,1 V an der Klemme, also 0,024 %.</div></div>
    <div class="karte"><h3>Umrechnung, Schritt für Schritt</h3>
      <table class="zahl" id="ts_um"></table></div>
    <div class="karte breit"><h3>Das gewählte Ausgangskennfeld des Testers</h3>
      <canvas id="ts_bild" width="1100" height="470"></canvas>
      <div class="zu" id="ts_zu"></div></div>
  </div>""",

# ===================================================================== Gummel-Poon
"gp": _kopf(
    "Das Gummel-Poon-Modell, rechnend",
    "Übertragen aus <code>BUCH/kapitel_06_gummel_poon.md</code>, Abschnitt 6.9 — der "
    "Python-Implementierung, die im Manuskript darüber steht, Funktion für Funktion: "
    "<code>beta_eff</code> (Webster), <code>v_be_eff</code> (innerer Basiswiderstand), "
    "<code>i_c_modell</code> (Early) und <code>i_b_modell</code> (Basis-Early und "
    "β<sub>eff</sub>), mit genau den Parametern aus Abschnitt 6.9. Die implizite Kopplung "
    "wird wie dort durch Fixpunktiteration gelöst."
) + r"""
  <div class="fb" id="gp_formel"></div>
  <div class="werkbank">
    <div class="feld"><label for="gp_vbe">V<sub>BE</sub> / mV</label>
      <input id="gp_vbe" type="number" value="660" step="5"></div>
    <div class="feld"><label for="gp_vce">V<sub>CE</sub> / V</label>
      <input id="gp_vce" type="number" value="5" step="0.5"></div>
    <div class="feld"><label for="gp_is">I<sub>S</sub> / 10<sup>−14</sup> A</label>
      <input id="gp_is" type="number" value="4.1" step="0.1"></div>
    <div class="feld"><label for="gp_bf">β<sub>F</sub> (BF)</label>
      <input id="gp_bf" type="number" value="292" step="1"></div>
    <div class="feld"><label for="gp_va">V<sub>A</sub> (VAF) / V</label>
      <input id="gp_va" type="number" value="146" step="1"></div>
    <div class="feld"><label for="gp_vab">V<sub>AB</sub> (VAR) / V</label>
      <input id="gp_vab" type="number" value="200" step="10"></div>
    <div class="feld"><label for="gp_ikf">I<sub>KF</sub> / A</label>
      <input id="gp_ikf" type="number" value="0.9" step="0.1"></div>
    <div class="feld"><label for="gp_rbi">R<sub>B,int</sub> (RBM) / Ω</label>
      <input id="gp_rbi" type="number" value="60" step="5"></div>
    <button class="tat" id="gp_start">Modell rechnen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>Der Testlauf aus Abschnitt 6.9</h3>
      <table class="zahl" id="gp_tab"></table>
      <div class="zu">Die rechte Spalte ist die Zahl, die im Manuskript daneben steht.</div></div>
    <div class="karte"><h3>Die Fixpunktiteration auf I<sub>B</sub></h3>
      <div class="iter"><table class="zahl" id="gp_fix"></table></div>
      <div class="zu">V<sub>BE,eff</sub> hängt von I<sub>B</sub> ab und I<sub>B</sub> von
        V<sub>BE,eff</sub> — die algebraische Schleife aus Abschnitt 6.7.</div></div>
    <div class="karte breit"><h3>Das Kennlinienfeld aus diesem Modell, mit den Messpunkten des
      Kurventracers darüber</h3>
      <canvas id="gp_bild" width="1100" height="470"></canvas>
      <div class="zu">Die Linien liegen mit den Voreinstellungen <b>über</b> den Messpunkten,
        und das ist kein Rechenfehler: Abschnitt 6.9 setzt den
        <b>Datenblattsatz</b> des BC337-25 an (β<sub>F</sub> = 292,
        I<sub>S</sub> = 4,1·10<sup>−14</sup> A), während der Prüfling dieser Messung
        β<sub>F</sub> ≈ 250 hat. Wer oben β<sub>F</sub> = 249,9 und
        I<sub>S</sub> = 4,726·10<sup>−14</sup> A einträgt — den Satz, den
        <code>bjt_fit.py</code> an genau diese Kurven angepasst hat —, legt die Linien auf die
        Punkte. Das ist der Unterschied zwischen einem Datenblattwert und einem gemessenen
        Bauteil, und er steht hier absichtlich sichtbar.</div></div>
    <div class="karte breit"><h3>Was die vier Erweiterungen einzeln bewirken</h3>
      <table class="zahl" id="gp_erw"></table>
      <div class="hinweis">Wie aus diesen Bauteilgleichungen ein lösbares Gleichungssystem
        einer ganzen Schaltung wird — Knotenpotentialverfahren, Newton-Raphson und der
        Zeitschritt —, ist in der Arbeit
        <a href="{{GRUNDLAGEN}}">Schaltungssimulation von nichtlinearen
        Differentialgleichungssystemen</a> hergeleitet. Diese Seite setzt den Transistor in
        einer vorgegebenen Schaltung ein; dort steht, warum das Verfahren überhaupt
        funktioniert — und seit Teil XII („Der Transistor als Stempel“, Abschnitte 47 bis 52)
        ist genau dieses Gummel-Poon-Modell dort als Netzlisten-Bauteil eingebaut, mit den
        vier Tangenten von Hand hergeleitet und gegen dieselben Messreihen
        abgenommen.</div></div>
  </div>""",

# ============================================================== Parameterextraktion
"extrakt": _kopf(
    "Die Ablesungen aus den Messdateien — und der vollständige SPICE-Parametersatz",
    "Übertragen aus <code>bjt_extract.py</code>: n und I<sub>S</sub> aus der Steigung im "
    "Gummel-Plot (Zeilen 55–66, Fenster 20 µA … 2 mA, die V<sub>CE</sub>=0-Kurve verworfen), "
    "V<sub>A</sub> aus dem x-Achsenabschnitt des flachen Astes (Zeilen 79–83, ab "
    "V<sub>CE</sub> ≥ 1,5 V), I<sub>S</sub> um den Early-Faktor bereinigt (Zeile 89), "
    "β<sub>F</sub> aus der I<sub>C</sub>-I<sub>B</sub>-Steigung und aus dem h<sub>FE</sub>-"
    "Maximum (Zeilen 103 und 112), I<sub>KF</sub> nur als untere Schranke (Zeilen 114–115). "
    "Gerechnet wird auf denselben fünf Dateien, die auch sein Programm einliest."
) + r"""
  <div class="werkbank">
    <button class="tat" id="ex_start">Aus den Messdaten ablesen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>n und I<sub>S</sub> je aktiver Kurve (Gummel-Plot)</h3>
      <table class="zahl" id="ex_gummel"></table></div>
    <div class="karte"><h3>V<sub>A</sub> je I<sub>B</sub>-Kurve (Early)</h3>
      <table class="zahl" id="ex_early"></table></div>
    <div class="karte"><h3>β<sub>F</sub> auf zwei Wegen</h3>
      <table class="zahl" id="ex_beta"></table></div>
    <div class="karte"><h3>Ergebnis, und was sein Programm ausgibt</h3>
      <table class="zahl" id="ex_erg"></table></div>
    <div class="karte breit"><h3>Der vollständige SPICE-Parametersatz</h3>
      {{SPICETAFEL}}
      <div class="zu">Die letzte Spalte sagt ausdrücklich, welcher Parameter aus <i>diesen</i>
        Daten nicht bestimmbar ist — genau so, wie seine Programme es selbst melden
        (<code>bjt_extract.py</code> Z. 183–186, <code>bjt_analyse.py</code> Z. 218–220,
        <code>bjt_gesamt.py</code> Z. 180–182).</div></div>
    <div class="karte breit"><h3>Welcher Parametersatz aus welchem seiner Programme kommt</h3>
      <table id="ex_saetze"></table></div>
    <div class="karte breit"><h3>Der Gummel-Plot mit der abgelesenen Geraden</h3>
      <canvas id="ex_bild" width="1100" height="440"></canvas></div>
  </div>""",

# ============================================================== Arbeitspunkt Newton
"newton": _kopf(
    "Der Arbeitspunkt: jede Newton-Iteration, die Bisektion, und die h-Parameter daraus",
    "Übertragen aus <code>BUCH/kap08_rechnung.py</code>, Zeile für Zeile: die gemessenen "
    "BC547-Parameter (Z. 19–22), die Schaltung (Z. 24–27), <code>beta_eff</code> (Z. 29–30), "
    "der Residuenvektor F (Z. 32–42), die <b>analytische</b> Jacobi-Matrix (Z. 44–57), "
    "Newton-Raphson mit Startwert (0,65 V; V<sub>CC</sub>/2), tol = 10<sup>−10</sup> und "
    "höchstens 100 Schritten (Z. 59–69) und die Bisektion auf R<sub>B</sub> im Intervall "
    "10 kΩ … 500 kΩ mit dem Toleranzband 0,1 % (Z. 71–84). Die h-Parameter darunter entstehen "
    "nach seinem Rezept aus <code>MANUSKRIPT_Vierpol_Verstaerker.md</code>, Abschnitt 9, "
    "Schritte 2 und 3."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="nw_vcc">V<sub>CC</sub> = V<sub>BB</sub> / V</label>
      <input id="nw_vcc" type="number" value="25" step="1"></div>
    <div class="feld"><label for="nw_rc">R<sub>C</sub> / Ω</label>
      <input id="nw_rc" type="number" value="100" step="10"></div>
    <div class="feld"><label for="nw_rb">R<sub>B</sub> / kΩ</label>
      <input id="nw_rb" type="number" value="37.275390625" step="0.5"></div>
    <div class="feld"><label for="nw_vbe0">Startwert V<sub>BE</sub> / V</label>
      <input id="nw_vbe0" type="number" value="0.65" step="0.05"></div>
    <button class="tat" id="nw_start">Newton-Raphson rechnen</button>
    <button class="tat" id="nw_bi">R<sub>B</sub> für V<sub>CE</sub> = V<sub>CC</sub>/2 suchen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>Die Newton-Iterationen</h3>
      <div class="iter"><table class="zahl" id="nw_tab"></table></div>
      <div class="zu" id="nw_zu"></div></div>
    <div class="karte"><h3>Der Abstieg von ‖F‖ über den Schritten</h3>
      <canvas id="nw_konv" width="720" height="470"></canvas></div>
    <div class="karte"><h3>Der Arbeitspunkt vollständig</h3>
      <table class="zahl" id="nw_erg"></table></div>
    <div class="karte"><h3>Die h-Parameter in genau diesem Arbeitspunkt</h3>
      <table class="zahl" id="nw_h"></table>
      <div class="zu">Vier Grundsteigungen als zentrale Differenzen (ΔV<sub>BE</sub> = 0,1 mV,
        ΔV<sub>CE</sub> = 10 mV), daraus h<sub>11e</sub> = 1/S<sub>3</sub>,
        h<sub>21e</sub> = S<sub>1</sub>/S<sub>3</sub>,
        h<sub>12e</sub> = −S<sub>4</sub>/S<sub>3</sub>,
        h<sub>22e</sub> = S<sub>2</sub> − S<sub>1</sub>S<sub>4</sub>/S<sub>3</sub>.
        Dass h<sub>11e</sub> hier nur einige zehn Ohm beträgt, liegt am Arbeitspunkt:
        bei I<sub>C</sub>/I<sub>KF</sub> = 1,56 fällt β<sub>eff</sub> mit steigendem
        I<sub>C</sub>, der Basisstrom wächst deshalb steiler als die reine e-Funktion, und
        S<sub>3</sub> wird entsprechend groß. Aus demselben Grund ist
        h<sub>21e</sub> deutlich kleiner als h<sub>FE</sub>.</div></div>
    <div class="karte"><h3>Die Bisektion auf R<sub>B</sub></h3>
      <div class="iter"><table class="zahl" id="nw_bitab"></table></div></div>
    <div class="karte"><h3>Kennlinie, Lastgerade und Arbeitspunkt</h3>
      <canvas id="nw_bild" width="720" height="470"></canvas></div>
  </div>""",

# ============================================================== Simulation und SPICE
"sim": _kopf(
    "Buchgleichungen gegen die SPICE-Konvention — derselbe Arbeitspunkt, zwei Rechenwege",
    "Übertragen aus <code>BUCH/kap09_spice_abgleich.py</code>, Zeile für Zeile: die beiden "
    "Thermospannungen (Z. 17–18: Python mit 300 K, LTspice mit 27 °C und den exakten "
    "SI-Konstanten), der gedämpfte Newton mit numerischer Jacobi-Matrix "
    "(Z. 22–38, h = 10<sup>−9</sup>, Schrittweiten auf 0,02 V und 2 V begrenzt, "
    "tol = 10<sup>−12</sup>), die Buchgleichungen (Z. 47–64) und die "
    "Gummel-Poon-Auswertung, wie LTspice sie aus der .MODEL-Karte macht (Z. 67–91: Early über "
    "V<sub>BC</sub>, q<sub>b</sub>-Formulierung). Die beiden Basiswiderstände sind die aus "
    "seinen Schaltplänen."
) + r"""
  <div class="werkbank">
    <button class="tat" id="sp_start">Beide Schaltungen auf beide Weisen rechnen</button>
  </div>
  <div class="gitter2">
    <div class="karte breit"><h3>Einfaches Modell — Eigen_RW_1d, R2 = 44453 Ω</h3>
      <table class="zahl" id="sp_einfach"></table></div>
    <div class="karte breit"><h3>Erweitertes Modell — Eigen_RW_1e, R2 = 36796 Ω</h3>
      <table class="zahl" id="sp_erweitert"></table></div>
    <div class="karte breit"><h3>Die vier .MODEL-Karten, wörtlich aus seinen .asc-Dateien</h3>
      {{LTSPICE}}
      <div class="zu" id="sp_vt"></div></div>
  </div>""",

# =========================================================== Kleinsignal, h-Parameter
"klein": _kopf(
    "Das Kleinsignal-Ersatzschaltbild und die h-Parameter",
    "Übertragen aus <code>bjt_hparam.py</code>: der Parametersatz (Z. 26–28), die "
    "Modellgleichungen <code>ic_model</code> und <code>ib_model</code> mit der "
    "40-schrittigen Fixpunktiteration (Z. 45–55), <code>vbe_from_ic</code> (Z. 56–57), der "
    "Arbeitspunkt (Z. 64–65) und die vier h-Parameter als zentrale Differenzen mit "
    "ΔV<sub>BE</sub> = 0,1 mV und ΔV<sub>CE</sub> = 10 mV (Z. 68–77). Das Ersatzschaltbild "
    "daneben ist das, das er lehrt: der Transistor als <b>Vierpol in Hybriddarstellung</b> "
    "(<code>MANUSKRIPT_Vierpol_Verstaerker.md</code>, Abschnitt 5.1), mit seinen "
    "Formelzeichen. Kein π-Modell."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="kl_ic">I<sub>C</sub> / mA</label>
      <input id="kl_ic" type="number" value="5" step="0.5" min="0.01"></div>
    <div class="feld"><label for="kl_vce">V<sub>CE</sub> / V</label>
      <input id="kl_vce" type="number" value="5" step="0.5" min="0.1"></div>
    <button class="tat" id="kl_start">h-Parameter rechnen</button>
  </div>
  <div class="gitter2">
    <div class="karte breit"><h3>Das Kleinsignal-Ersatzschaltbild — der h-Vierpol</h3>
      <svg class="esb" id="kl_esb" viewBox="0 0 900 330" xmlns="http://www.w3.org/2000/svg">
        <!-- Emitterschiene -->
        <line x1="60" y1="270" x2="840" y2="270"/>
        <!-- Eingangstor -->
        <circle cx="60" cy="80" r="5" class="kasten"/>
        <circle cx="60" cy="270" r="5" class="kasten"/>
        <line x1="60" y1="80" x2="150" y2="80"/>
        <rect class="kasten" x="150" y="60" width="96" height="40"/>
        <line x1="246" y1="80" x2="330" y2="80"/>
        <line x1="330" y1="80" x2="330" y2="146"/>
        <circle cx="330" cy="176" r="30" class="kasten"/>
        <line x1="318" y1="164" x2="342" y2="188"/>
        <line x1="330" y1="206" x2="330" y2="270"/>
        <!-- Ausgangstor: gesteuerte Stromquelle -->
        <circle cx="520" cy="176" r="30" class="kasten"/>
        <path d="M520 194 L520 158 M513 167 L520 158 L527 167"/>
        <line x1="520" y1="146" x2="520" y2="80"/>
        <line x1="520" y1="206" x2="520" y2="270"/>
        <!-- Ausgangsleitwert -->
        <line x1="660" y1="80" x2="660" y2="130"/>
        <rect class="kasten" x="640" y="130" width="40" height="92"/>
        <line x1="660" y1="222" x2="660" y2="270"/>
        <!-- Ausgangsklemme -->
        <line x1="520" y1="80" x2="840" y2="80"/>
        <circle cx="840" cy="80" r="5" class="kasten"/>
        <circle cx="840" cy="270" r="5" class="kasten"/>
        <!-- Beschriftung -->
        <text x="40" y="74" text-anchor="end">B</text>
        <text x="40" y="276" text-anchor="end">E</text>
        <text x="860" y="74">C</text>
        <text x="860" y="276">E</text>
        <text x="198" y="52" text-anchor="middle">h<tspan baseline-shift="sub" font-size="10">11e</tspan></text>
        <text class="wert" id="kl_s11" x="198" y="120" text-anchor="middle">—</text>
        <text x="372" y="172">h<tspan baseline-shift="sub" font-size="10">12e</tspan>·v<tspan baseline-shift="sub" font-size="10">ce</tspan></text>
        <text class="wert" id="kl_s12" x="372" y="192">—</text>
        <text x="562" y="172">h<tspan baseline-shift="sub" font-size="10">21e</tspan>·i<tspan baseline-shift="sub" font-size="10">b</tspan></text>
        <text class="wert" id="kl_s21" x="562" y="192">—</text>
        <text x="700" y="172">1/h<tspan baseline-shift="sub" font-size="10">22e</tspan></text>
        <text class="wert" id="kl_s22" x="700" y="192">—</text>
        <text class="kl" x="100" y="64">i<tspan baseline-shift="sub" font-size="9">b</tspan> →</text>
        <text class="kl" x="86" y="180">v<tspan baseline-shift="sub" font-size="9">be</tspan></text>
        <text class="kl" x="770" y="64">← i<tspan baseline-shift="sub" font-size="9">c</tspan></text>
        <text class="kl" x="790" y="180">v<tspan baseline-shift="sub" font-size="9">ce</tspan></text>
        <line x1="76" y1="110" x2="76" y2="244" stroke-dasharray="4 3"/>
        <line x1="824" y1="110" x2="824" y2="244" stroke-dasharray="4 3"/>
        <text class="kl" x="60" y="310">Tor 1 · Basis–Emitter</text>
        <text class="kl" x="700" y="310">Tor 2 · Kollektor–Emitter</text>
      </svg>
      <div class="fb">⎡ v<sub>be</sub> ⎤ = ⎡ h<sub>11e</sub>  h<sub>12e</sub> ⎤ · ⎡ i<sub>b</sub> ⎤   ;
        ⎡ i<sub>c</sub> ⎤ = ⎡ h<sub>21e</sub>  h<sub>22e</sub> ⎤ · ⎡ v<sub>ce</sub> ⎤</div>
      <div class="zu">Vier Zahlen beschreiben das Kleinsignalverhalten vollständig.
        h<sub>11e</sub> ist der Eingangswiderstand (dV<sub>BE</sub>/dI<sub>B</sub> bei festem
        V<sub>CE</sub>), h<sub>12e</sub> die Spannungsrückwirkung, h<sub>21e</sub> die
        Stromverstärkung, h<sub>22e</sub> der Ausgangsleitwert — die Definitionen aus
        Abschnitt 5.1 seines Vierpol-Manuskripts. Im Kleinsignalbild liegt die Versorgung an
        Masse und die idealen Koppelkondensatoren sind Kurzschlüsse; R<sub>b</sub> und
        R<sub>c</sub> kommen als Querwiderstände dazu (Reiter „Vierpol-Verstärker“).</div>
    </div>
    <div class="karte"><h3>Der Arbeitspunkt und die vier Grundsteigungen</h3>
      <table class="zahl" id="kl_ap"></table></div>
    <div class="karte"><h3>Die h-Parameter, und was sein Programm ausgibt</h3>
      <table class="zahl" id="kl_h"></table></div>
    <div class="karte breit"><h3>Die vier Kennfelder mit der Tangente im Arbeitspunkt</h3>
      <canvas id="kl_bild" width="1100" height="560"></canvas></div>
  </div>""",

# =============================================================== Vierpol-Verstärker
"vierpol": _kopf(
    "Die Emitterschaltung als Vierpol-Kette",
    "Übertragen aus <code>bjt_verstaerker.py</code>, Zeile für Zeile: die Vorgaben "
    "(Z. 51–56), der Parametersatz (Z. 61–62), die Modellgleichungen (Z. 67–77), das "
    "Residuensystem (Z. 95–97), die <b>numerische</b> Jacobi-Matrix als zentrale Differenzen "
    "mit h<sub>b</sub> = 10<sup>−6</sup> und h<sub>c</sub> = 10<sup>−4</sup> (Z. 99–105), "
    "Newton-Raphson mit Dämpfung auf 0,05 V und 2 V und Begrenzung auf physikalisch sinnvolle "
    "Werte (Z. 107–122), die automatische Bestimmung von R<sub>B</sub> mit dem nächsten "
    "E24-Normwert (Z. 140–160), die vier Grundsteigungen und h-Parameter (Z. 174–184), die "
    "Umrechnung h → A und die Querwiderstände (Z. 187–199), das Matrixprodukt in "
    "Signalrichtung (Z. 202) und die fünf Kenngrößen (Z. 205–209)."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="vp_vcc">V<sub>cc</sub> / V</label>
      <input id="vp_vcc" type="number" value="15" step="1"></div>
    <div class="feld"><label for="vp_rc">R<sub>c</sub> / kΩ</label>
      <input id="vp_rc" type="number" value="1" step="0.1"></div>
    <div class="feld"><label for="vp_rb">R<sub>b</sub> / kΩ (leer = automatisch)</label>
      <input id="vp_rb" type="number" value="" step="10" placeholder="automatisch"></div>
    <div class="feld"><label for="vp_rl">R<sub>L</sub> / kΩ</label>
      <input id="vp_rl" type="number" value="10" step="1"></div>
    <div class="feld"><label for="vp_ri">R<sub>i</sub> / kΩ</label>
      <input id="vp_ri" type="number" value="1" step="0.1"></div>
    <button class="tat" id="vp_start">Kette rechnen</button>
  </div>
  <div class="gitter2">
    <div class="karte"><h3>1) Arbeitspunkt der Schaltung</h3>
      <table class="zahl" id="vp_ap"></table>
      <div class="zu" id="vp_rbinfo"></div></div>
    <div class="karte"><h3>2) Der h-Vierpol des Transistors</h3>
      <table class="zahl" id="vp_h"></table></div>
    <div class="karte"><h3>3)–4) Die Kettenmatrizen und ihr Produkt</h3>
      <table class="zahl" id="vp_a"></table>
      <div class="fb">A<sub>ges</sub> = A<sub>Rb</sub> · A<sub>T</sub> · A<sub>Rc</sub>   ;
        A<sub>T</sub> = (1/h<sub>21</sub>)·⎡ −D<sub>h</sub>  −h<sub>11</sub> ⎤ ⎡ −h<sub>22</sub>  −1 ⎤   ;
        Querwiderstand: ⎡ 1  0 ⎤ ⎡ 1/R  1 ⎤</div></div>
    <div class="karte"><h3>5) Die Kenngrößen des belasteten Vierpols</h3>
      <table class="zahl" id="vp_erg"></table></div>
    <div class="karte breit"><h3>|A<sub>v</sub>| über der Last R<sub>L</sub></h3>
      <canvas id="vp_bild" width="1100" height="420"></canvas></div>
  </div>""",

# ==================================================================== Messvorschrift
"messvor": _kopf(
    "Zur Messvorschrift wird hier nichts gerechnet",
    "Dieses Teilmanuskript ist eine Arbeitsanweisung für den Messplatz: welche Kennlinie in "
    "welcher Reihenfolge aufzunehmen ist, damit hinterher jeder SPICE-Parameter bestimmbar "
    "wird. Es beschreibt kein Rechenverfahren, und in seinem Bestand gibt es dazu kein "
    "Programm. Was aus den so gewonnenen Daten abgelesen wird, steht im Reiter "
    "<b>Parameterextraktion</b>; welcher Parameter aus diesen Daten <i>nicht</i> bestimmbar "
    "ist, steht dort in derselben Tafel."
) + "",
}


# --------------------------------------------------------------- Werte aus SEINEN Programmläufen
# Jede Zahl hier ist die Ausgabe eines seiner Programme, nicht nachgerechnet.
# Die Seite rechnet dieselbe Größe im Browser noch einmal und stellt beide
# nebeneinander — zwei unabhängige Wege, gleiche Zahl.
LAUF = {
    # BUCH/kap08_rechnung.py  (Aufruf: python3 kap08_rechnung.py)
    "kap08": dict(RB=37275.390625, VBE=0.752165524358524, VCE=12.491100560416658,
                  IB=6.505051743006777e-4, IC=0.12508899439583343,
                  beta_eff=181.12225375042289, newton=49, bisekt=10,
                  VBEeff=0.7424079467440139,
                  vbe_ideal=0.7456158192280198, rb_ideal=56270.17129939099),
    # bjt_hparam.py
    "hparam": dict(VBE=0.6579987028671513, IB=1.8583526031613462e-05,
                   h11=1452.6733403540968, h21=279.8408975530343,
                   h12=-4.994093043950427e-07, h22=3.30163772931849e-05,
                   gm=0.19263855801526697),
    # bjt_verstaerker.py
    "verst": dict(rb_exakt=532107.5405802932, RB=510000.0,
                  VBE=0.6692610568516003, VCE=7.172564851587398,
                  IB=2.8099488123821077e-05, IC=0.007827435148412817, iter=6,
                  S1=0.3015731639896503, S2=5.1102070112822584e-05,
                  S3=0.0010209576648425756, S4=7.69014173798981e-10,
                  h11=979.4725427270217, h21=295.3826337511759,
                  h12=-7.532282682040078e-07, h22=5.087491668077386e-05,
                  Dh=0.050053074552020876,
                  A=[[-0.0034853965658194156, -3.31594491622046],
                     [-3.5645074356288956e-06, -0.0033919412311879536]],
                  r_ein=977.787620287744, r_aus=951.4861686102911,
                  A_v=-261.9864665520863, A_i=-25.616712367755913,
                  A_vs=-129.52205841003794),
    # Transistor_20.py
    "t20": dict(RB=2054.6875, VBE=0.6457538661970369, VCE=7.490602296732822,
                IB=0.006986096977668363, versuche=6, fehlversuche=5),
    # Transistor_21b.py
    "t21": dict(RB=44453.125, VBE=0.7168661105514321, VCE=12.688472860889675,
                IB=0.0005462638203601787, IC=0.12311527139110325, versuche=7),
    # BUCH/kap09_spice_abgleich.py
    "spice": dict(VT_PY=0.025861423220973783, VT_LT=0.02586487117042268,
                  einfach=dict(RB=44453.0, buch=[0.71687, 12.68844, 0.54627e-3, 123.11558e-3],
                               spice=[0.71696, 12.75910, 0.54626e-3, 122.40899e-3]),
                  erweitert=dict(RB=36796.0, buch=[0.72389, 12.50332, 0.65975e-3, 124.96678e-3],
                                 spice=[0.72844, 12.87938, 0.65963e-3, 121.20617e-3])),
    # BUCH/kap08_led_quellen.py (Ausgleich mit scipy curve_fit — die Seite fittet nicht selbst)
    "led": dict(n=1.8976885072758756, Is=1.4943312915754406e-26, Rs=16.04281407515143,
                VT=0.02585, Uges=5.0, R=100.0,
                Vd=3.0388522003861267, Id=0.019611477996138712,
                Id0=0.042719, iter=3, punkte=46, fitpunkte=35,
                shockley=dict(Is=5.359e-11, n=5.7923)),
    # bjt_extract.py
    "extract": dict(n=1.004, Is=5.260e-14, VA=146.0, beta_steigung=272.0,
                    beta_hfe=271.0, hfe_max=275.0, ic_max=9.3e-3),
    # BUCH/kapitel_06_gummel_poon.md, Abschnitt 6.9 (Testlauf im Text)
    "gp": dict(vbe=0.660, vce=5.0, ic=5.206e-3, ib=1.699e-5, beta=306.0),
    # netz_lauf.py — der Lauf SEINES Netzlisten-Loesers simulator.py ueber die
    # beiden Netzlisten des Reiters "Netzliste und Loeser".  Jede Zahl ist die
    # Ausgabe dieses Laufs; das Pruefprogramm startet ihn selbst und vergleicht.
    "netz": dict(
        f1=dict(u_be=0.664176940665, u_be_eff=0.66372352023, u_ce=5.65148878644,
                i_b=2.41181082897e-05, i_c=0.00634850556207, i_e=0.00637262367036,
                beta=263.225684444, beta_eff=253.001783421, p=0.0358945266861,
                newton=46),
        emp=dict(ikf=[5.69349822589, 0.00630649608061, 54],
                 rbi=[5.65124604831, 0.00634874830044, 46],
                 var=[5.68384698287, 0.00631614733328, 52],
                 var200=[-98.0, 457568.551931, 200]),
        f2=dict(g11=0.244592786292, g12=4.80032823851e-05,
                g21=0.000929940367774, g22=1.74236042398e-08,
                rac=909.090909091, av_klein=-209.412785836,
                schritte=60000, newton_mittel=2.95037, newton_groesste=25,
                abbrueche=0, ua_max=0.984891815079, ua_min=-1.11024055733,
                hub=2.09513237241, av_gross=209.513237241,
                av_oben=200.608737219, av_unten=218.408569407,
                hub_oben=1.00304368609, hub_unten=1.09204284703,
                unsym=-8.49598902312, unterschied=0.0479681334338,
                uc_mittel=5.63096459246, uc_verschiebung=-0.020524193982,
                periodendrift=0.00111741236257),
        fb=dict(u_be=0.752165490095, u_be_eff=0.742407923749, u_ce=12.4911093065,
                i_b=0.000650504423054, i_c=0.125088894444,
                beta_eff=181.122297886, newton=155),
        # Fall 3 — seine B4-Bruecke (bruecke.netz) durch simulator.py
        br=dict(uc_mittel=20.766126381, uc_max=21.359706666, uc_min=20.16957023,
                brumm=1.1901364365, brumm_proz=5.731143183,
                il_mittel=0.20766126381, id1_spitze=0.67692015332,
                iq_spitze=0.67692018425, verlust=8.6402933337,
                uc_ende=20.737734528, schritte=20000, newton_mittel=3.7081,
                newton_groesste=200, abbrueche=11),
        # ... und, als ZWEITER unabhaengiger Weg, die Kennzahlen aus seinem
        # hinterlegten Bericht bericht_bruecke_rc.txt.  Der stammt NICHT vom
        # Netzlisten-Loeser, sondern aus seinem eigenen, fest verdrahteten
        # Programm Bruecke_RC_Last_Knotenpotential.py (Handaufloesung statt
        # Gauss).  Er druckt auf vier Nachkommastellen.
        bericht=dict(uc_mittel=20.7661, uc_max=21.3597, uc_min=20.1696,
                     brumm=1.1901, brumm_proz=5.73, il_mittel=0.2076613,
                     id1_spitze=0.6769201, iq_spitze=0.6769201,
                     verlust=8.6403, newton_mittel=3.94, newton_groesste=6),
    ),
}

# Der volle SPICE-Parametersatz, wie ihn SEINE Anpassung liefert.  Jede Zeile
# nennt die Quelle; wo ein Parameter aus den Daten nicht bestimmbar ist, steht
# das ausdrücklich dort — so, wie seine Programme es selbst ausgeben.
SPICE_SATZ = [
    # SPICE, Symbol, Bedeutung, BC337-25, Quelle, Urteil
    ("IS", "I_S", "Transport-Sättigungsstrom", "5,260·10⁻¹⁴ A",
     "bjt_extract.py Z. 89 (Gummel-Fit, um den Early-Faktor bereinigt)", "gemessen"),
    ("NF", "n", "Vorwärts-Emissionskoeffizient", "1,004",
     "bjt_extract.py Z. 63–64 (Steigung im Gummel-Plot)", "gemessen"),
    ("BF", "β_F", "ideale Vorwärts-Stromverstärkung", "272 (Steigung) · 271 (h_FE-Maximum)",
     "bjt_extract.py Z. 103 und Z. 112", "gemessen"),
    ("VAF", "V_A", "Vorwärts-Early-Spannung", "146,0 V",
     "bjt_extract.py Z. 79–83 (x-Achsenabschnitt des flachen Astes)", "gemessen"),
    ("VAR", "V_AB", "Basis-(Rückwärts-)Early-Spannung", "— (Vorgabe 10⁶ V bzw. 200 V)",
     "bjt_extract.py Z. 186, bjt_analyse.py Z. 219",
     "nicht bestimmbar: aus Konstant-I_B-Daten nicht robust ablesbar"),
    ("IKF", "I_KF", "Vorwärts-Kniestrom (Hochinjektion)", "nur untere Schranke ≫ 9 mA",
     "bjt_extract.py Z. 114–115 und Z. 183–184",
     "nicht bestimmbar: bis 9,3 mA kein Hochstromabfall sichtbar"),
    ("RB / RBM", "R_B,int", "innerer Basisbahnwiderstand", "— (Vorgabe 60 Ω bzw. 10 Ω)",
     "bjt_extract.py Z. 186, bjt_gesamt.py Z. 182 (Datenblattwert)",
     "nicht bestimmbar aus diesen Daten"),
    ("ISE", "I_SE", "Leckterm der BE-Sperrschicht", "3,534·10⁻¹⁵ A (Datenblatt)",
     "bjt_gesamt.py Z. 29 und Z. 182", "nicht gefittet — Datenblatt"),
    ("NE", "n_E", "Emissionskoeffizient des Lecktermes", "1,35 (Datenblatt)",
     "bjt_gesamt.py Z. 29 und Z. 182", "nicht gefittet — Datenblatt"),
    ("BR, NR, IKR, ISC, NC", "—", "Invers- und Sperrbetrieb", "—",
     "in keinem seiner Programme gesetzt",
     "nicht bestimmbar: der Tester misst nur den Vorwärts-Aktivbetrieb"),
    ("RE, RC", "—", "Emitter- und Kollektorbahnwiderstand", "—",
     "in keinem seiner Programme gesetzt",
     "nicht bestimmbar: aus Gleichstrommessungen im Aktivbetrieb nicht trennbar"),
    ("CJE, CJC, TF, TR", "—", "Sperrschichtkapazitäten und Laufzeiten", "—",
     "in keinem seiner Programme gesetzt",
     "nicht bestimmbar: der Tester misst statisch, nicht dynamisch"),
]

# --------------------------------------------------------------------------
# Der SELBST ERMITTELTE Parametersatz, wie ihn der Lauf von bjt_fit.py ausgibt
# (Nelder-Mead über alle fünf gemessenen Kennlinienfelder gleichzeitig), und
# daneben SEIN eigener Identifizierbarkeitstest aus demselben Lauf: um welchen
# Faktor steigt die Gesamtabweichung, wenn der Parameter um 20 % verstellt wird.
# Drei Klassen, getrennt in der Spalte „Herkunft“:
#   gemessen         — aus seinen Messreihen bestimmt
#   gesetzt          — aus diesen Daten nicht bestimmbar, deshalb festgelegt
#   nicht messbar    — mit diesem Gerät überhaupt nicht aufnehmbar
# Die Zahlen sind die des Laufs vom 29.09.2026 (Datei Kennlinienschreiber/
# rechnung/log/bjt_fit.log), nachgerechnet am 30.09.2026 mit demselben Ergebnis.
MODELLKARTE_ZEILE = (".MODEL BC337_eigen NPN(IS=4.765E-14 NF=1.004 BF=253.2 "
                     "VAF=126.6 VAR=1.39E3 IKF=4.05 RB=18.8)")
MODELLKARTE = [
    # SPICE, Zeichen, Wert, Messreihe/Quelle, Empfindlichkeit, Klasse, Urteil
    ("IS", "I_S", "4,765·10⁻¹⁴ A", "Ic_Vbe.txt (Gummel-Plot) im Gesamtausgleich "
     "<code>bjt_fit.py</code>", "×8,87", "gemessen", "gemessen und daraus bestimmt"),
    ("NF", "n", "1,004", "Ic_Vbe.txt — Steigung im Gummel-Plot, "
     "<code>bjt_fit.py</code>", "×3211,81", "gemessen", "gemessen und daraus bestimmt"),
    ("BF", "β_F", "253,2", "Ic_Ib.txt und hFE_Ic.txt, <code>bjt_fit.py</code>",
     "×38,50", "gemessen", "gemessen und daraus bestimmt"),
    ("VAF", "V_A", "126,6 V", "Ic_Vce.txt — flacher Ast, <code>bjt_fit.py</code>",
     "×1,06", "schwach", "gemessen, aber nur schwach bestimmt: 20 % Verstellung "
     "kostet nur 6 % Gesamtabweichung"),
    ("VAR", "V_AB", "1,39·10³ V <b>(gesetzt)</b>",
     "Ergebnis des Ausgleichs, aber ohne Aussagekraft — die Messreihen legen den "
     "Wert nicht fest; er wirkt nur über 1 + V_CE/V_AB im Basisstrom",
     "×1,00", "gesetzt", "aus diesen Daten nicht bestimmbar, deshalb gesetzt"),
    ("RB / RBM", "R_B,int", "18,8 Ω <b>(gesetzt)</b>",
     "Ergebnis des Ausgleichs; der Messplatz misst die Klemmenspannung, der "
     "Spannungsabfall am inneren Bahnwiderstand ist darin nicht trennbar",
     "×1,01", "gesetzt", "aus diesen Daten nicht bestimmbar, deshalb gesetzt"),
    ("IKF", "I_KF", "4,05 A <b>(gesetzt)</b>",
     "Ergebnis des Ausgleichs; gemessen wurde nur bis 9,3 mA, ein Hochstromabfall "
     "wird dort gar nicht erreicht",
     "×1,00", "gesetzt", "aus diesen Daten nicht bestimmbar, deshalb gesetzt"),
    ("—", "V_T", "25,852 mV <b>(Annahme)</b>",
     "T = 300 K; in seinen Programmen steht wörtlich „Annahme Raumtemperatur“ "
     "(<code>bjt_extract.py</code> Z. 13). Die Messdateien tragen keine Temperatur; "
     "seine eigene Messvorschrift verlangt sie („Raumtemperatur notieren“)",
     "—", "gesetzt", "nicht protokolliert, deshalb angenommen"),
    ("BR, NR, IKR, ISC, NC", "—", "—",
     "Rückwärts- und Sättigungsbetrieb", "—", "unmessbar",
     "mit diesem Gerät nicht messbar: es misst nur den Vorwärts-Aktivbetrieb"),
    ("ISE, NE", "I_SE, n_E", "—", "Leckterm der Basis-Emitter-Sperrschicht",
     "—", "unmessbar",
     "mit diesem Gerät nicht messbar: der Kleinststrombereich wird nicht erfasst"),
    ("RE, RC", "—", "—", "Emitter- und Kollektorbahnwiderstand", "—", "unmessbar",
     "mit diesem Gerät nicht messbar: aus Gleichstrommessungen im Aktivbetrieb "
     "nicht von R_B,int trennbar"),
    ("CJE, CJC, VJE, VJC, MJE, MJC", "—", "—", "Sperrschichtkapazitäten",
     "—", "unmessbar",
     "mit diesem Gerät nicht messbar: es misst statisch, Punkt für Punkt"),
    ("TF, TR, ITF, VTF, XTF", "—", "—", "Laufzeiten und Ladungsspeicherung",
     "—", "unmessbar",
     "mit diesem Gerät nicht messbar: es misst statisch, Punkt für Punkt"),
    ("XTI, EG, XTB, TRE1, TRB1", "—", "—", "Temperaturgang",
     "—", "unmessbar",
     "mit diesem Gerät nicht messbar: aufgenommen wurde bei einer einzigen, "
     "nicht protokollierten Temperatur"),
    ("KF, AF", "—", "—", "Rauschen", "—", "unmessbar",
     "mit diesem Gerät nicht messbar: der Messplatz mittelt und misst statisch"),
]

# Die vier LTspice-Karten, wörtlich aus den .asc-Dateien
LTSPICE = [
    ("Eigen_RW_1c.asc", ".MODEL simple_npn NPN(IS=1e-13 BF=200 NF=1 VAF=100)", "R2 = 44453 Ω"),
    ("Eigen_RW_1d.asc", ".MODEL simple_npn NPN(IS=1e-13 BF=200 NF=1 VAF=100)", "R2 = 44453 Ω"),
    ("Eigen_RW_1e.asc", ".MODEL simple_npn NPN(IS=1e-13 BF=200 NF=1 VAF=100 VAR=200 IKF=0.5 RB=10)",
     "R2 = 36796 Ω"),
    ("Eigen_RW_1f.asc", ".MODEL simple_npn NPN(IS=1e-13 BF=200 NF=1 VAF=100 VAR=200 IKF=0.5 RB=10)",
     "R2 = 44453 Ω"),
]


# --------------------------------------------------------------- Seite bauen
def main() -> int:
    tracer = {n: lade_tracer(n) for n in
              ["Ic_Vce", "Ic_Ib", "Ic_Vbe", "hFE_Vce", "hFE_Ic"]}
    reihen = lade_csv()

    # Die Teilmanuskripte: jedes bleibt ein eigenes Dokument, nichts wird
    # verschmolzen, nichts umgeschrieben, nichts gekuerzt.
    texte, berichtigt = {}, 0
    for m in BT.MANUSKRIPTE:
        t, g = BT.lade(m)
        texte[m["kurz"]] = t
        berichtigt += len(g)

    gebraucht = sorted({Path(x).name for t in texte.values()
                        for x in re.findall(r"!\[(?:[^\]]|\n)*?\]\(([^)]+)\)", t, flags=re.S)})
    fehlt = [n for n in gebraucht if not (B / n).exists()]
    if fehlt:
        raise SystemExit("Bilder fehlen: " + ", ".join(fehlt))
    bilder = {n: bild(n) for n in gebraucht}

    # Die Bilder des Geraetes stehen an zwei Stellen auf der Seite (Startreiter
    # und Reiter "Der Transistortester"), sollen aber nur EINMAL in der Datei
    # liegen: sie gehen als Daten-Adresse in STAND, und das Skript setzt sie in
    # jedes <img data-bild="..."> ein.
    geraet = {"platine": "platine_foto.jpg",
              "skizze": "uebersichtsplan_skizze.png",
              "ops": "schaltplan_ops.png",
              "cpu": "schaltplan_cpu_adda.png"}
    fehlt_g = [n for n in geraet.values() if not (B / n).exists()]
    if fehlt_g:
        raise SystemExit("Geraetebilder fehlen: " + ", ".join(fehlt_g))

    stand = dict(
        VERSION=VERSION, DATUM=DATUM, TITEL=TITEL, AUTOR=NAMENSNENNUNG,
        tracer=tracer, reihen=reihen, lauf=LAUF,
        geraet={k: bild(v, breite=1400, qualitaet=72) for k, v in geraet.items()},
        bruecke=BRUECKE_NETZ,
    )

    # ---- Reiterschiene und Abschnitte
    # Ein Reiter, der KEIN Teilmanuskript traegt, steht NEBEN dem Kapitel, zu dem
    # er gehoert, nicht darin.  Er wird hinter dem genannten Reiter eingehaengt.
    ZUSATZ = [dict(kurz="netz", reiter="Netzliste und Löser", nach="sim",
                   herkunft="eigener Teil dieser Seite · neben Kapitel 9, "
                            "nicht darin · Grundlage: Teil XII des "
                            "Grundlagenprojekts",
                   doku=NETZ_DOKU, rechner=NETZ_RECHNER)]

    knoepfe = ['<button class="an" data-ziel="start">Start</button>']
    abschnitte = [START_ABSCHNITT]

    def _zusatz(nach: str) -> None:
        for zu in ZUSATZ:
            if zu["nach"] != nach:
                continue
            k = zu["kurz"]
            knoepfe.append(f'<button data-ziel="{k}">{zu["reiter"]}</button>')
            abschnitte.append(
                f'<section id="{k}">\n'
                f'  <div class="reiterkopf">\n'
                f'    <div><b>{zu["reiter"]}</b> · {zu["herkunft"]}</div>\n'
                f'    <a class="sprung" href="#r_{k}">↓ zum rechnenden Teil</a>\n'
                f'  </div>\n'
                f'  <div class="doku">\n{zu["doku"]}\n  </div>\n'
                f'  <hr class="trenn">\n'
                f'  <div class="rechner" id="r_{k}">\n{zu["rechner"]}\n  </div>\n'
                f'</section>')

    for m in BT.MANUSKRIPTE:
        k = m["kurz"]
        knoepfe.append(f'<button data-ziel="{k}">{m["reiter"]}</button>')
        rechnen = RECHNER.get(k, KEIN_RECHNER)
        abschnitte.append(
            f'<section id="{k}">\n'
            f'  <div class="reiterkopf">\n'
            f'    <div><b>{m["reiter"]}</b> · Teilmanuskript '
            f'<code>{m["ziel"].split("/")[-1]}</code> · Quelle: {m["ursprung"]}</div>\n'
            f'    <a class="sprung" href="#r_{k}">↓ zum rechnenden Teil</a>\n'
            f'  </div>\n'
            f'  <div class="doku">\n{markdown(texte[k], bilder)}\n  </div>\n'
            f'  <hr class="trenn">\n'
            f'  <div class="rechner" id="r_{k}">\n{rechnen}\n  </div>\n'
            f'</section>')
        _zusatz(k)

    seite = VORLAGE
    seite = seite.replace("{{TITEL}}", TITEL)
    seite = seite.replace("{{VERSION}}", VERSION)
    seite = seite.replace("{{DATUM}}", DATUM)
    seite = seite.replace("{{AUTOR}}", NAMENSNENNUNG)
    seite = seite.replace("{{STIL}}", STIL)
    seite = seite.replace("{{REITER}}", "\n  ".join(knoepfe))
    seite = seite.replace("{{ABSCHNITTE}}", "\n".join(abschnitte))
    seite = seite.replace("{{GRUNDLAGEN}}", GRUNDLAGEN)
    seite = seite.replace("{{SPICETAFEL}}", spicetafel())
    seite = seite.replace("{{LTSPICE}}", ltspicetafel())
    seite = seite.replace("{{MODELLKARTE_ZEILE}}", MODELLKARTE_ZEILE)
    seite = seite.replace("{{MODELLKARTE}}", modellkarte())
    seite = seite.replace("{{DATEN}}", json.dumps(stand, ensure_ascii=False,
                                                  separators=(",", ":")))
    seite = seite.replace("{{SKRIPT}}", SKRIPT)
    seite = neutral(seite)

    ziel = H / f"Transistortechnik_{VERSION}.html"
    ziel.write_text(seite, encoding="utf-8")

    # Fuer die Pruefung: wie viele Woerter traegt jedes Teilmanuskript in der
    # Quelle?  Die Seite muss sie vollstaendig zeigen.
    zaehl = {}
    for m in BT.MANUSKRIPTE:
        roh = re.sub(r"^---\n.*?\n---\n", "", texte[m["kurz"]], flags=re.S)
        # Bildunterschriften, Quelltextbloecke und Formeln zaehlen nicht mit:
        # sie stehen auf der Seite in eigenen Elementen und werden dort ebenso
        # herausgenommen.  Verglichen wird Fliesstext gegen Fliesstext.
        roh = re.sub(r"!\[(?:[^\]]|\n)*?\]\([^)]+\)(\{[^}]*\})?", " ", roh, flags=re.S)
        roh = re.sub(r"```.*?```", " ", roh, flags=re.S)
        roh = re.sub(r"\$\$.*?\$\$", " ", roh, flags=re.S)
        roh = re.sub(r"\$[^$\n]*\$", " ", roh)
        roh = re.sub(r"\\[A-Za-z]+", " ", roh)      # LaTeX-Makros sind keine Woerter
        roh = re.sub(r"[|#>*`\\_{}]", " ", roh)
        # Vollstaendigkeitsprobe: jedes laengere Wort des Manuskripts muss in
        # der Seite wiederzufinden sein.  Das ist unempfindlich dagegen, dass
        # der Formelsatz Zeichenketten anders zerlegt als die Quelle.
        lang = sorted({w.lower() for w in re.findall(r"[A-Za-zÄÖÜäöüß]{7,}", roh)})
        zaehl[m["kurz"]] = dict(reiter=m["reiter"], woerter=len(roh.split()),
                                pruefwoerter=lang)
    (H / "manuskript_woerter.json").write_text(
        json.dumps(zaehl, ensure_ascii=False, indent=1), encoding="utf-8")
    print("=" * 74)
    print(f"  geschrieben: {ziel.name}   {len(seite.encode('utf-8')):,} Byte")
    print(f"  Reiter: {len(BT.MANUSKRIPTE) + 1 + len(ZUSATZ)}  "
          f"(Start + {len(BT.MANUSKRIPTE)} Teilmanuskripte + {len(ZUSATZ)} eigener)")
    print(f"  Bilder eingebettet: {len(bilder)}")
    print(f"  Berichtigungen eingesetzt: {berichtigt}")
    print("  Messspuren: " + ", ".join(f"{k} ({len(v)})" for k, v in tracer.items()))
    print(f"  Messreihen (CSV): {len(reihen)}")
    print("=" * 74)
    return 0


def spicetafel() -> str:
    r = ["<table><thead><tr><th>SPICE</th><th>Zeichen</th><th>Bedeutung</th>"
         "<th>BC337-25 aus seiner Anpassung</th><th>woher</th><th>Urteil</th></tr>"
         "</thead><tbody>"]
    for sp, sym, bed, wert, quelle, urteil in SPICE_SATZ:
        kl = "schlecht" if urteil.startswith("nicht bestimmbar") else (
            "warn" if urteil.startswith("nicht gefittet") else "gut")
        r.append(f"<tr><td><code>{sp}</code></td><td>{sym}</td><td>{bed}</td>"
                 f"<td>{wert}</td><td><code>{quelle}</code></td>"
                 f"<td class='{kl}'>{urteil}</td></tr>")
    return "".join(r) + "</tbody></table>"


def modellkarte() -> str:
    """Die SPICE-artige Modellkarte des selbst ermittelten Satzes, mit der
    Spalte „Herkunft“ in drei sichtbar getrennten Klassen."""
    kl = {"gemessen": "gut", "schwach": "warn", "gesetzt": "warn",
          "unmessbar": "schlecht"}
    wort = {"gemessen": "gemessen", "schwach": "gemessen (schwach)",
            "gesetzt": "gesetzt", "unmessbar": "nicht messbar"}
    r = ["<table><thead><tr><th>SPICE</th><th>Zeichen</th><th>Wert im Satz</th>"
         "<th>woher die Zahl kommt</th><th>Empfindlichkeits&shy;probe</th>"
         "<th>Herkunft</th><th>was das heißt</th></tr></thead><tbody>"]
    for sp, sym, wert, quelle, emp, klasse, urteil in MODELLKARTE:
        r.append(f"<tr><td><code>{sp}</code></td><td>{sym}</td><td>{wert}</td>"
                 f"<td>{quelle}</td><td>{emp}</td>"
                 f"<td class='{kl[klasse]}'>{wort[klasse]}</td><td>{urteil}</td></tr>")
    return "".join(r) + "</tbody></table>"


def ltspicetafel() -> str:
    r = ["<table><thead><tr><th>Datei</th><th>.MODEL-Karte, wörtlich</th>"
         "<th>Basiswiderstand im Schaltplan</th></tr></thead><tbody>"]
    for n, karte, r2 in LTSPICE:
        r.append(f"<tr><td><code>{n}</code></td><td><code>{karte}</code></td>"
                 f"<td>{r2}</td></tr>")
    return "".join(r) + "</tbody></table>"


# --------------------------------------------------------------------------- Stil
STIL = r"""
:root{
  --grund:#fbfaf7; --karte:#ffffff; --linie:#d9d3c7; --text:#22201c;
  --matt:#6b655c; --ton:#155e75; --ton2:#0e7490; --warn:#b45309;
  --gut:#15803d; --schlecht:#b91c1c; --schiene:#f2efe8;
}
*{box-sizing:border-box}
body{margin:0;background:var(--grund);color:var(--text);
     font:16px/1.55 "Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{background:var(--karte);border-bottom:2px solid var(--ton);padding:14px 20px}
header h1{margin:0;font-size:21px;letter-spacing:.1px}
header .kopf{margin-top:3px;font-size:13px;color:var(--matt)}
nav{display:flex;flex-wrap:wrap;gap:4px;background:var(--schiene);
    padding:6px 14px;border-bottom:1px solid var(--linie);position:sticky;top:0;z-index:20}
nav button{border:1px solid var(--linie);background:#fff;color:var(--text);
  padding:6px 11px;border-radius:6px;cursor:pointer;font-size:13.5px}
nav button.an{background:var(--ton);color:#fff;border-color:var(--ton)}
nav button:hover{border-color:var(--ton)}
main{padding:14px 20px 60px;max-width:1500px}
section{display:none} section.an{display:block}
.reiterkopf{display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;
  align-items:center;background:var(--karte);border:1px solid var(--linie);
  border-left:4px solid var(--ton);border-radius:6px;padding:8px 12px;
  margin:0 0 14px;font-size:13px;color:var(--matt)}
.reiterkopf b{color:var(--text);font-size:15px}
a.sprung{color:var(--ton);text-decoration:none;font-weight:600;white-space:nowrap}
a.sprung:hover{text-decoration:underline}
hr.trenn{border:none;border-top:2px dashed var(--linie);margin:26px 0}
.rechner{scroll-margin-top:90px}
.rechner>h2{font-size:19px;color:var(--ton);margin:0 0 4px}
.rechner>.herkunft{font-size:13px;color:var(--matt);margin:0 0 12px}
.werkbank{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;
  background:var(--karte);border:1px solid var(--linie);border-radius:8px;
  padding:12px 14px;margin:0 0 14px}
.feld{display:flex;flex-direction:column;gap:3px}
.feld label{font-size:12px;color:var(--matt)}
.feld input,.feld select{border:1px solid var(--linie);border-radius:5px;
  padding:6px 8px;font:inherit;font-size:14px;min-width:120px;background:#fff}
button.tat{background:var(--ton);color:#fff;border:none;border-radius:6px;
  padding:9px 16px;font-size:14px;cursor:pointer}
button.tat:hover{background:var(--ton2)}
button.tat[disabled]{background:#9aa0a6;cursor:not-allowed}
.gitter2{display:grid;grid-template-columns:repeat(auto-fit,minmax(560px,1fr));gap:14px}
.karte{background:var(--karte);border:1px solid var(--linie);border-radius:8px;padding:12px 14px}
.karte h3{margin:0 0 8px;font-size:15px;color:var(--ton)}
.karte.breit{grid-column:1/-1}
canvas{width:100%;height:auto;display:block;background:#fff;border-radius:4px}
svg.esb{width:100%;height:auto;display:block;background:#fff;border-radius:4px}
table{border-collapse:collapse;width:100%;font-size:13px;margin:6px 0 10px}
th,td{border:1px solid var(--linie);padding:4px 7px;text-align:left;vertical-align:top}
th{background:var(--schiene);font-weight:600}
table.zahl td:not(:first-child){text-align:right;font-variant-numeric:tabular-nums}
table.gitter th,table.gitter td{font-size:12.5px}
code,pre{font-family:"Cascadia Mono",Consolas,monospace;font-size:13px}
pre{background:#f6f4ef;border:1px solid var(--linie);border-radius:6px;
    padding:9px 11px;overflow-x:auto}
.f,.fb{font-family:"Cambria Math","Latin Modern Math",Georgia,serif}
.fb{margin:9px 0;padding:7px 12px;background:#f6f4ef;border-left:3px solid var(--ton);
    border-radius:0 5px 5px 0;overflow-x:auto}
figure{margin:12px 0}
figure img{max-width:100%;border:1px solid var(--linie);border-radius:5px}
figcaption{font-size:12.5px;color:var(--matt);margin-top:4px}
blockquote{margin:9px 0;padding:7px 12px;border-left:3px solid var(--warn);
  background:#fdf8ef;border-radius:0 5px 5px 0;font-size:14px}
.doku{max-width:980px}
.doku h2{font-size:20px;border-bottom:1px solid var(--linie);padding-bottom:3px;margin-top:26px}
.doku h3{font-size:17px;margin-top:20px}
.doku h4,.doku h5,.doku h6{font-size:15px;margin-top:15px}
.merk{font-size:13px;color:var(--matt);margin:4px 0 10px}
.gut{color:var(--gut);font-weight:600}
.schlecht{color:var(--schlecht);font-weight:600}
.warn{color:var(--warn);font-weight:600}
.fehlt{color:var(--warn);font-size:13px}
.feld input[type=range]{padding:0;min-width:170px;accent-color:var(--ton)}
textarea.netz{width:100%;min-height:120px;border:1px solid var(--linie);border-radius:6px;
  padding:9px 11px;background:#f6f4ef;font-family:"Cascadia Mono",Consolas,monospace;
  font-size:13px;line-height:1.45;resize:vertical;margin-bottom:8px}
h3.nzh{font-size:17px;color:var(--ton);margin:22px 0 10px;
  border-bottom:2px solid var(--linie);padding-bottom:4px}
.weg{display:flex;flex-wrap:wrap;gap:8px;align-items:stretch;margin:12px 0 6px}
.weg .st{flex:1 1 168px;background:var(--karte);border:1px solid var(--linie);
  border-left:4px solid var(--ton);border-radius:6px;padding:8px 11px;font-size:13px}
.weg .st b{display:block;font-size:13.5px;color:var(--text);margin-bottom:2px}
.weg .st a{color:var(--ton);text-decoration:none;font-weight:600;font-size:12.5px}
.weg .st a:hover{text-decoration:underline}
.weg .pf{align-self:center;color:var(--matt);font-size:17px;flex:0 0 auto}
.iter{max-height:290px;overflow:auto;border:1px solid var(--linie);border-radius:6px}
.iter table{margin:0;border:none}
.iter th{position:sticky;top:0}
.zu{font-size:12px;color:var(--matt);margin-top:6px}
.hinweis{background:#f0f7f9;border:1px solid #bfdde4;border-left:4px solid var(--ton);
  border-radius:0 6px 6px 0;padding:9px 13px;margin:10px 0;font-size:14px}
.esb text{font:13px "Segoe UI",sans-serif;fill:#22201c}
.esb text.kl{font-size:11.5px;fill:#6b655c}
.esb text.wert{font-size:12px;fill:#155e75;font-weight:600}
.esb line,.esb path,.esb rect,.esb circle{stroke:#22201c;stroke-width:1.8;fill:none}
.esb rect.kasten{fill:#fff}
.esb .quer line,.esb .quer rect{stroke:#b45309;stroke-dasharray:5 3}
.esb .quer text{fill:#b45309}
@media (max-width:760px){
  .gitter2{grid-template-columns:1fr}
  main{padding:12px 16px 50px}
  /* Nur Tabellen duerfen breiter sein als der Bildschirm - und dann in einem
     eigenen Waagerechtlauf. Der Seitenkoerper laeuft nie waagerecht. */
  table{display:block;overflow-x:auto;white-space:nowrap;max-width:100%}
  .karte,.doku,.rechner,section{overflow-x:hidden;max-width:100%}
  .werkbank .feld input,.werkbank .feld select{min-width:0;width:100%}
  .feld{flex:1 1 130px}
  pre{white-space:pre;max-width:100%}
  svg.esb{min-width:0}
}
"""


# --------------------------------------------------------------------------- Vorlage
VORLAGE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TITEL}} · Fassung {{VERSION}}</title>
<style>{{STIL}}</style>
</head>
<body>
<header>
  <h1>{{TITEL}}</h1>
  <div class="kopf">Fassung {{VERSION}} · {{DATUM}} · {{AUTOR}}</div>
</header>
<nav id="schiene">
  {{REITER}}
</nav>
<main>
{{ABSCHNITTE}}
</main>
<script>const STAND = {{DATEN}};</script>
<script>{{SKRIPT}}</script>
</body>
</html>
"""

# --------------------------------------------------------------------------- Start
# ------------------------------------------------- Reiter „Netzliste und Löser“
# Dieser Reiter ist KEIN Teilmanuskript des Verfassers.  Er steht neben dem
# Kapitel 9 („Simulation und SPICE“), nicht darin, und der Text darüber ist
# ausdrücklich als unserer gekennzeichnet.  Gerechnet wird mit seinem Löser:
# die Übertragung nach JavaScript ist Zeile für Zeile aus
# DGL_Nichtlinear/Programme/simulator.py, und daneben steht die Zahl, die
# genau dieses Programm für dieselbe Netzliste ausgibt.
NETZ_DOKU = r"""
  <h2>Die Schaltung als Netzliste — gerechnet vom eigenen Löser</h2>

  <div class="hinweis">
    <b>Dieser Reiter trägt kein Teilmanuskript.</b> Alle anderen Reiter zeigen oben einen
    Text des Verfassers, vollständig und unverändert. Hier steht statt dessen unsere eigene
    Beschreibung — sie <i>tritt neben</i> das Kapitel 9 „Simulation und SPICE“ und nicht
    hinein. Die Herleitung, auf der alles beruht, ist seine und steht an ihrer Stelle:
    <a href="{{GRUNDLAGEN}}">Schaltungssimulation von nichtlinearen
    Differentialgleichungssystemen</a>, <b>Teil XII, Abschnitte 47 bis 52</b> („Der Transistor
    als Stempel: Gummel-Poon im Knotenpotentialverfahren“) — dort stehen die vier Tangenten
    von Hand hergeleitet (48), der Stempel mit seinen zwölf Kreuzungen (49), die Abnahmen mit
    Zahlen (50) und ein eigener Abschnitt darüber, was das Bauteil von SPICE nachbildet und
    was nicht (51).
  </div>

  <h3>Was hier anders ist als in allen Reitern davor</h3>
  <p>In den Reitern „Arbeitspunkt von Hand“, „Arbeitspunkt Newton“ und „Simulation und SPICE“
     wird jedesmal <b>dieselbe Schaltung von Hand in Gleichungen gebracht</b>: zwei Maschen
     aufschreiben, den Residuenvektor <span class="f">F(V<sub>BE</sub>, V<sub>CE</sub>)</span>
     hinschreiben, die Jacobi-Matrix dazu ableiten, Newton laufen lassen. Das geht, solange
     die Schaltung zwei Unbekannte hat. Bei drei Widerständen, zwei Kondensatoren und einer
     Signalquelle geht es nicht mehr — und vor allem: für jede neue Schaltung müsste man von
     vorn anfangen.</p>
  <p>Hier wird statt dessen <b>nichts von Hand aufgestellt</b>. Die Schaltung wird als
     <b>Netzliste</b> hingeschrieben, eine Zeile je Bauteil, und ein Löser baut daraus selbst
     die Knotenleitwertmatrix: jedes Bauteil trägt nur seinen festen <b>Stempel</b> ein, der
     Transistor eben vier Leitwerte und zwei Ersatzstromquellen statt eines Leitwerts und
     einer Ersatzquelle. Newton-Raphson erneuert diese Tangenten in jedem Durchgang, Euler
     schreibt danach die Kondensatorspannungen fort. Das ist genau das, was ein
     SPICE-Programm tut — nur ist hier jeder Schritt sichtbar und von Hand nachrechenbar.</p>
  <p><b>Alle sechs Bauteilklassen seines Lösers sind übertragen</b>, nicht eine Auswahl:
     Widerstand, Spannungsquelle (Gleich- und Sinusquelle), Diode mit ihren Modellkarten,
     Kondensator, Induktivität und Transistor. Eine Netzlistenzeile, die bei ihm läuft,
     läuft deshalb auch hier.</p>
  <p>Als Probe darauf, dass hier wirklich sein <i>allgemeines</i> Verfahren steht und kein
     Transistor-Sonderfall, rechnet der dritte Fall unten <b>seine B4-Brücke</b> — vier
     Dioden, ein RC-Glied mit Last, eine Sinusquelle —, und zwar mit demselben Quelltext:
     geändert wird die Netzliste, nicht das Programm.</p>

  <h3>Die Parameter sind die selbst ermittelten</h3>
  <p>Gerechnet wird mit dem Satz, den <b>sein</b> Gesamtausgleich aus <b>seinen</b> Messungen
     gewonnen hat — <code>bjt_fit.py</code>, Nelder-Mead über alle fünf gemessenen
     Kennlinienfelder gleichzeitig, Prüfling BC337 —, nicht mit einem Datenblattsatz. So sieht
     die Karte aus, wenn man sie als <code>.MODEL</code>-Zeile schreibt:</p>
  <pre>{{MODELLKARTE_ZEILE}}</pre>
  <p>Diese sieben Zahlen sind nicht gleichwertig. Der Lauf von <code>bjt_fit.py</code> prüft
     selbst nach, welcher Parameter durch die Messdaten überhaupt festgelegt ist: er verstellt
     jeden um 20 % und sieht nach, um welchen Faktor die Gesamtabweichung steigt. Steigt sie
     kaum, dann sagen die Daten über diesen Parameter nichts. Die Spalte
     <b>Empfindlichkeitsprobe</b> unten trägt genau diese Faktoren, die Spalte
     <b>Herkunft</b> die Einordnung in drei Klassen.</p>
  {{MODELLKARTE}}

  <div class="hinweis">
    <b>Was daraus für die Zahlen dieses Reiters folgt — an der Stelle, an der es weh tut.</b>
    <ul>
      <li>Das Modell hat <b>keine Sperrschichtkapazitäten und keine Laufzeiten</b>, weil der
        Messplatz sie nicht messen kann. Die Verstärkung, die hier herauskommt, ist deshalb
        die <b>quasistatische</b>: Bei 1 kHz und bei 100 MHz käme dieselbe Zahl heraus. Das
        ist falsch — nur eben nicht mit diesem Gerät als falsch nachweisbar. <b>Eine obere
        Grenzfrequenz hat dieses Modell nicht.</b></li>
      <li>Der Zeitverlauf zeigt die Verzerrung, die aus der <b>Kennlinie</b> kommt (die
        e-Funktion), <b>nicht</b> die aus der Ladungsspeicherung. Die Unsymmetrie unten ist
        also die der Exponentialfunktion und sonst nichts.</li>
      <li>Das Bauteil kennt <b>keine Sättigung und keinen Inversbetrieb</b> (Teil XII,
        Abschnitt 51.2). Wer den Kollektorwiderstand so groß schiebt, dass
        <span class="f">V<sub>CE</sub></span> unter etwa 0,3 V geriete, bekommt keine
        Sättigungskennlinie, sondern eine Zahl außerhalb des Gültigkeitsbereichs. Die Seite
        sagt es dann an.</li>
      <li>Die Thermospannung ist eine <b>Annahme</b>: <span class="f">T</span> = 300 K. Die
        Messdateien tragen keine Temperatur, obwohl seine eigene Messvorschrift sie verlangt.
        Alle Ströme hängen über <span class="f">exp(V/nV<sub>T</sub>)</span> unmittelbar
        daran.</li>
    </ul>
  </div>"""

NETZ_RECHNER = _kopf(
    "Drei Netzlisten, ein Löser: Arbeitspunkt, Signalverstärkung — und ein Brückengleichrichter mit vier Dioden",
    "Übertragen aus <code>DGL_Nichtlinear/Programme/simulator.py</code>, Zeile für Zeile — "
    "über jeder Funktion im Quelltext der Seite steht, aus welcher Klasse und welchen Zeilen "
    "sie stammt: <code>wert</code> (Z. 96–102), <code>Widerstand</code> (Z. 109–131), "
    "<code>Spannungsquelle</code> (Z. 134–167), "
    "<code>Diode</code> (Z. 170–199) samt ihren Modellkarten aus "
    "<code>bruecke_kern.py</code> (Z. 51, 53–84), <code>Kondensator</code> (Z. 202–252), "
    "<code>Induktivitaet</code> (Z. 255–292), <code>GummelPoon</code> (Z. 338–424) mit den "
    "vier analytischen Tangenten, <code>MODELLE_BJT</code> (Z. 432–463), "
    "<code>Transistor</code> (Z. 466–568) mit den zwölf Kreuzungen und den zwei "
    "Ersatzstromquellen, und <code>Simulator</code> (Z. 577–740) mit dem Einlesen der "
    "Netzliste, der Vergabe der Zusatzunbekannten, <code>_newton</code> (Z. 662–696: "
    "<span class='f'>GMIN</span> = 10<sup>−9</sup> S an jedem Knoten, Dämpfung "
    "<span class='f'>d<sub>max</sub></span> = 0,5 V, Abbruch bei "
    "max|F| &lt; 10<sup>−12</sup> <i>und</i> max|Δ| &lt; 10<sup>−9</sup>, höchstens 200 "
    "Durchgänge) und <code>schritt</code> (Z. 699–711: Newton, dann Euler). "
    "<b>Alle sechs Bauteilklassen seines Lösers sind übertragen, nicht eine Auswahl</b> — "
    "R, Q/V, D, C, L und T; eine Netzlistenzeile, die bei ihm läuft, läuft hier auch. "
    "<b>Zwei Zutaten sind ausdrücklich unsere:</b> die Auflösung des Gleichungssystems "
    "(sein Löser ruft <code>numpy.linalg.solve</code>, hier steht das Gauß-Verfahren mit "
    "Teilpivotierung ausgeschrieben — dasselbe Verfahren, das LAPACK darunter ausführt) und "
    "das Mitschreiben des Newton-Protokolls, das an der Rechnung nichts ändert."
) + r"""
  <div class="werkbank">
    <div class="feld"><label for="nz_vcc">V<sub>CC</sub> / V · <span id="nz_vcc_w"></span></label>
      <input id="nz_vcc" type="range" min="4" max="24" step="0.5" value="12"></div>
    <div class="feld"><label for="nz_rb">R<sub>B</sub> / kΩ · <span id="nz_rb_w"></span></label>
      <input id="nz_rb" type="range" min="100" max="2000" step="10" value="470"></div>
    <div class="feld"><label for="nz_rc">R<sub>C</sub> / Ω · <span id="nz_rc_w"></span></label>
      <input id="nz_rc" type="range" min="100" max="4700" step="50" value="1000"></div>
    <div class="feld"><label for="nz_rl">R<sub>L</sub> / kΩ · <span id="nz_rl_w"></span></label>
      <input id="nz_rl" type="range" min="1" max="100" step="1" value="10"></div>
    <div class="feld"><label for="nz_us">û<sub>s</sub> / mV · <span id="nz_us_w"></span></label>
      <input id="nz_us" type="range" min="0.5" max="40" step="0.5" value="5"></div>
    <button class="tat" id="nz_start">Alle Netzlisten rechnen</button>
    <button class="tat" id="nz_zurueck">Voreinstellung</button>
  </div>
  <div class="zu" id="nz_stand"></div>

  <h3 class="nzh">Fall 1 — nur der Arbeitspunkt</h3>
  <div class="gitter2">
    <div class="karte"><h3>Die Netzliste — fünf Zeilen, änderbar</h3>
      <textarea class="netz" id="nz_n1" rows="6" spellcheck="false"></textarea>
      <button class="tat" id="nz_n1_start">Diese Netzliste so rechnen</button>
      <div class="zu">Die Schieber schreiben hier hinein. Wer den Text ändert und diesen Knopf
        drückt, rechnet genau das, was dasteht — Bauteilbuchstaben R, Q/V, C, L, T, Knoten
        „0“ ist Masse, Kommentar mit <code>*</code> oder <code>#</code>, Vorsätze
        p n u m k meg.</div>
      <div class="zu" id="nz_n1_fehler"></div></div>
    <div class="karte"><h3>Die Knotenmatrix Y und der Vektor i im letzten Durchgang</h3>
      <div class="iter"><table class="zahl" id="nz_mat"></table></div>
      <div class="zu" id="nz_mat_zu"></div></div>
    <div class="karte"><h3>Die Newton-Durchgänge</h3>
      <div class="iter"><table class="zahl" id="nz_it"></table></div>
      <div class="zu" id="nz_it_zu"></div></div>
    <div class="karte"><h3>Der Arbeitspunkt vollständig — und was sein Löser ausgibt</h3>
      <table class="zahl" id="nz_ap"></table>
      <div class="zu" id="nz_ap_zu"></div></div>
    <div class="karte breit"><h3>Wie weit trägt die Zahl? Empfindlichkeit gegen die drei
      <i>gesetzten</i> Parameter</h3>
      <table class="zahl" id="nz_emp"></table>
      <div class="zu">Jeder der drei Parameter, die aus den Messdaten <b>nicht</b> bestimmbar
        sind, wird einzeln deutlich verstellt und der Arbeitspunkt neu gerechnet. Die letzte
        Spalte sagt, wieviel die Zahl dadurch wandert — so weit und nicht weiter darf man ihr
        trauen.</div></div>
    <div class="karte breit"><h3>Gegenprobe: dieselbe Netzliste für <i>seine</i>
      Fixed-Bias-Schaltung mit dem BC547</h3>
      <table class="zahl" id="nz_gegen"></table>
      <div class="zu" id="nz_gegen_zu"></div></div>
  </div>

  <h3 class="nzh">Fall 2 — die vollständige Verstärkerstufe</h3>
  <div class="gitter2">
    <div class="karte"><h3>Die Netzliste der Verstärkerstufe</h3>
      <textarea class="netz" id="nz_n2" rows="10" spellcheck="false"></textarea>
      <div class="zu" id="nz_n2_zu"></div></div>
    <div class="karte"><h3>Die Schaltung</h3>
      <svg class="esb" id="nz_bild_sch" viewBox="0 0 740 380"></svg></div>
    <div class="karte"><h3>Der Arbeitspunkt der Stufe</h3>
      <table class="zahl" id="nz_ap2"></table></div>
    <div class="karte"><h3>Die vier Tangenten im Arbeitspunkt — und die
      Kleinsignalverstärkung daraus</h3>
      <table class="zahl" id="nz_klein"></table>
      <div class="zu" id="nz_klein_zu"></div></div>
    <div class="karte breit"><h3>Die zwei Verstärkungen nebeneinander</h3>
      <table class="zahl" id="nz_av"></table>
      <div class="zu" id="nz_av_zu"></div></div>
    <div class="karte breit"><h3>Der Zeitverlauf: Eingang und Ausgang, letzte Periode</h3>
      <canvas id="nz_zeit" width="1100" height="440"></canvas>
      <div class="zu" id="nz_zeit_zu"></div></div>
    <div class="karte breit"><h3>Der Ausgangshub über dem Eingangshub — die Kennlinie der
      Stufe im Großsignal</h3>
      <canvas id="nz_kenn" width="1100" height="440"></canvas>
      <div class="zu">Die gestrichelte Gerade ist die Kleinsignaltangente aus den vier
        Stempeltangenten, durch den Mittelwert des Ausgangs gelegt. Die durchgezogene Kurve
        ist der gerechnete Großsignallauf. Sie ist keine Gerade: zu negativen Eingangswerten
        hin (rechts unten im Bild) wird sie steiler, zu positiven flacher — das ist die
        e-Funktion des Basisstroms. Wo beide auseinandergehen, steht die Verzerrung. Die
        Kurve ist minimal aufgefächert, weil die Koppelkondensatoren eine kleine
        Phasendrehung beisteuern.</div></div>
  </div>

  <h3 class="nzh">Fall 3 — dieselben fünf Klassen lösen auch einen Brückengleichrichter</h3>
  <p class="merk">Bis hierher stand ein Transistor in der Netzliste. Jetzt steht dort
    <b>seine B4-Brücke</b> — vier Dioden, ein Innenwiderstand, ein RC-Glied mit Last, eine
    Sinusquelle —, und es ist <b>derselbe Löser, Zeile für Zeile derselbe Quelltext</b>, der
    sie rechnet. Das ist der Beleg dafür, dass hier sein allgemeines Verfahren steht und kein
    Transistor-Sonderfall: geändert wird die Netzliste, nicht das Programm.</p>
  <div class="gitter2">
    <div class="karte"><h3>Seine Netzliste <code>bruecke.netz</code>, wörtlich</h3>
      <textarea class="netz" id="nz_n3" rows="15" spellcheck="false"></textarea>
      <button class="tat" id="nz_n3_start">Diese Netzliste so rechnen</button>
      <div class="zu" id="nz_n3_zu"></div>
      <div class="zu" id="nz_n3_fehler"></div></div>
    <div class="karte breit"><h3>Die Kennzahlen im eingeschwungenen Zustand — und was sein
      Löser ausgibt</h3>
      <table class="zahl" id="nz_br"></table>
      <div class="zu" id="nz_br_zu"></div></div>
    <div class="karte breit"><h3>Der Zeitverlauf: Quellspannung, Brückenausgang und die
      Spannung am Kondensator</h3>
      <canvas id="nz_br_zeit" width="1100" height="440"></canvas>
      <div class="zu" id="nz_br_zeit_zu"></div></div>
    <div class="karte"><h3>Die letzte Periode: die Restwelligkeit</h3>
      <canvas id="nz_br_welle" width="720" height="430"></canvas>
      <div class="zu" id="nz_br_welle_zu"></div></div>
    <div class="karte"><h3>Die letzte Periode: die Stromspitzen in den Dioden</h3>
      <canvas id="nz_br_strom" width="720" height="430"></canvas>
      <div class="zu" id="nz_br_strom_zu"></div></div>
  </div>

  <div class="karte breit" style="margin-top:14px"><h3>Was offen ist</h3>
    <ul id="nz_offen"></ul></div>"""

START_ABSCHNITT = r"""<section id="start" class="an">
  <div class="doku">
    <h2>Von der Messung zum eigenen Berechnungsverfahren</h2>
    <p>Aus <b>selbst gemessenen</b> Kennlinien werden <b>selbst ermittelte</b> Parameter, und
       mit diesen Parametern rechnet ein <b>selbst geschriebener</b> L&ouml;ser eine ganze
       Schaltung durch — Arbeitspunkt, Kleinsignalverhalten, Verst&auml;rkung, Zeitverlauf.
       Das ist dasselbe, was ein SPICE-Programm tut, nur ist hier jeder Schritt sichtbar und
       von Hand nachrechenbar.</p>

    <figure>
      <img data-bild="platine" alt="Der Transistortester: Platine mit ESP32-Modul,
        Klemmenleiste, steckbaren Messwiderst&auml;nden und angeklemmtem Pr&uuml;fling">
      <figcaption><b>Der Messplatz, mit dem alles anf&auml;ngt.</b> Links auf der Platine das
        ESP32-Modul mit seiner USB-Buchse, rechts daneben die gr&uuml;nen Schraubklemmen: erst
        die Versorgung (GND, +24&nbsp;V), dann die Messklemmen, deren Belegung im Siebdruck
        darunter f&uuml;r beide Bauteilarten steht — <span class="f">NPN: Rc C E Rb GND</span>
        und <span class="f">PNP: E C Rc B Rb GND</span>. In den Klemmen stecken die beiden
        <b>Messwiderst&auml;nde</b>, die den Strom in eine messbare Spannung umsetzen: ein
        kleiner Schichtwiderstand im Basiszweig und der gro&szlig;e blaue Drahtwiderstand im
        Kollektorzweig. Rechts, an drei Pr&uuml;fklemmen (blau an der Basis, violett am
        Kollektor, rot am Emitter), h&auml;ngt der Pr&uuml;fling in einem Leistungsgeh&auml;use
        mit Metallfahne. Unten rechts auf der Leiterplatte steht die Fertigungsnummer des
        Platinenherstellers. Mehr ist es nicht — und alle Zahlen dieser Arbeit kommen von
        diesem Aufbau.</figcaption>
    </figure>

    <h3>Der Weg, Station f&uuml;r Station</h3>
    <div class="weg">
      <div class="st"><b>1 · Ger&auml;t und Pr&uuml;fling</b>
        Zwei Digital-Analog-Umsetzer stellen Basis- und Kollektorzweig, vier
        Analog-Digital-Umsetzer messen zur&uuml;ck.
        <a href="#" data-spring="tester">&rarr; Der Transistortester</a></div>
      <div class="pf">&rarr;</div>
      <div class="st"><b>2 · Gemessene Kennlinienfelder</b>
        Ausgangskennlinienfeld, Eingangskennlinie, Stromsteuerkennlinie,
        h<sub>FE</sub>-Verl&auml;ufe — die f&uuml;nf Messreihen des Kurvenschreibers.
        <a href="#" data-spring="extrakt">&rarr; Parameterextraktion</a></div>
      <div class="pf">&rarr;</div>
      <div class="st"><b>3 · Parameter bestimmen</b>
        Einmal von Hand aus zwei abgelesenen Punkten, einmal als Ausgleich &uuml;ber alle
        Kurven zugleich — mit der Frage, welcher Parameter aus diesen Daten &uuml;berhaupt
        bestimmbar ist.
        <a href="#" data-spring="bc547">&rarr; Extraktion BC547</a></div>
      <div class="pf">&rarr;</div>
      <div class="st"><b>4 · Der eigene Parametersatz</b>
        Als SPICE-artige <code>.MODEL</code>-Karte geschrieben, mit der Herkunft jeder
        einzelnen Zahl.
        <a href="#" data-spring="mindat">&rarr; Minimaler Datensatz</a></div>
      <div class="pf">&rarr;</div>
      <div class="st"><b>5 · Der eigene L&ouml;ser</b>
        Knotenpotentialverfahren, Newton-Raphson, Euler — die Schaltung als Netzliste, jedes
        Bauteil nur ein Stempel.
        <a href="#" data-spring="netz">&rarr; Netzliste und L&ouml;ser</a></div>
      <div class="pf">&rarr;</div>
      <div class="st"><b>6 · Arbeitspunkt und Verst&auml;rkung</b>
        Newton-Raphson auf die ganze Schaltung, daraus das Kleinsignalverhalten und der
        Vierpol.
        <a href="#" data-spring="newton">&rarr; Arbeitspunkt Newton</a></div>
      <div class="pf">&rarr;</div>
      <div class="st"><b>7 · Gegenprobe</b>
        Dieselbe Schaltung mit LTspice und mit der SPICE-Konvention gerechnet — zwei Wege,
        die nichts voneinander wissen.
        <a href="#" data-spring="sim">&rarr; Simulation und SPICE</a></div>
    </div>

    <h3>Der Zielpunkt dieses Bogens</h3>
    <p>Am Ende steht der Reiter <a href="#" data-spring="netz"><b>Netzliste und
       L&ouml;ser</b></a>. Dort wird die Schaltung nicht mehr als von Hand aufgestelltes
       Gleichungssystem gel&ouml;st, sondern <b>als Netzliste durch das eigene Verfahren</b> —
       mit den selbst ermittelten Parametern, einmal nur der Arbeitspunkt und einmal die
       komplette Verst&auml;rkerstufe mit Kollektor-, Last- und Basiswiderstand,
       Koppelkondensatoren und Signalquelle. Die Signalverst&auml;rkung wird dort auf zwei
       Wegen gerechnet, und der Unterschied zwischen beiden ist die Aussage.</p>

    <h3>Die Manuskripte sind der Hintergrund und der Lernapparat</h3>
    <p>Unter jedem Reiter steht <b>das zugeh&ouml;rige Teilmanuskript des Verfassers,
       vollst&auml;ndig und unver&auml;ndert</b>. Dort stehen die Herleitungen, die Zahlen und
       die Begr&uuml;ndungen; sie sind nicht Anhang und nicht Beiwerk, sondern der Lehrtext, zu
       dem alles &Uuml;brige die Probe ist. Der rechnende Teil dar&uuml;ber ist Zeile f&uuml;r
       Zeile aus einem seiner Python-Programme &uuml;bertragen — dieselben Formeln, dieselben
       Konstanten, dieselbe Reihenfolge der Schritte, dieselben Startwerte, dieselben
       Abbruchbedingungen. &Uuml;ber jeder Rechnung steht, aus welchem Programm und aus welchen
       Zeilen sie stammt, und daneben die Zahl, die dieses Programm ausgibt. <b>Wer lernen
       will, liest den Text; wer pr&uuml;fen will, dreht an den Schiebern.</b></p>
    <p>Eine Ausnahme gibt es: der Reiter „Netzliste und L&ouml;ser“ tr&auml;gt kein
       Teilmanuskript. Er ist unser Teil und steht <i>neben</i> dem Kapitel 9, nicht darin —
       das ist dort ausdr&uuml;cklich gesagt.</p>

    <div class="hinweis">
      <b>Drei verschiedene Transistoren.</b> In diesen Manuskripten kommen drei Pr&uuml;flinge vor:
      der <b>BC547</b> (Extraktion und Arbeitspunkt, &beta;<sub>F</sub> = 290), der
      <b>BC337-25</b> (Kurventracer, Kleinsignal und Verst&auml;rker, &beta;<sub>F</sub> &asymp; 250…275) und
      der nicht benannte Pr&uuml;fling der neun CSV-Reihen des Testers (&beta;<sub>F</sub> &asymp; 53). Dass
      ihre Parameter auseinanderliegen, ist deshalb kein Widerspruch — es sind
      <b>verschiedene Bauteile</b>. Wer Zahlen aus einem Reiter in die Rechnung eines anderen
      einsetzt, muss zuerst den Pr&uuml;fling vergleichen.
    </div>

    <h3>Worauf das aufbaut</h3>
    <p>Das Verfahren, mit dem eine Schaltung aus nichtlinearen Bauteilen &uuml;berhaupt gerechnet
       wird — Knotenpotentialverfahren, Newton-Raphson und Euler —, ist in einer eigenen
       Arbeit hergeleitet:
       <a href="{{GRUNDLAGEN}}">Schaltungssimulation von nichtlinearen
       Differentialgleichungssystemen</a>. Dort steht, warum aus den Bauteilgleichungen ein
       Gleichungssystem <span class="f">Y·u = i</span> wird, wie die Ableitung eines
       nichtlinearen Bauteils als Leitwert in diese Matrix gestempelt wird und wie der
       Zeitschritt dazukommt. Diese Arbeit hier setzt dort an, wo das Verfahren steht, und
       f&uuml;llt es mit einem gemessenen Transistor. <strong>Der Transistor ist dort seit
       Teil XII auch als Bauteil eingebaut</strong> — „Der Transistor als Stempel:
       Gummel-Poon im Knotenpotentialverfahren“, Abschnitte 47 bis 52: die vier Tangenten
       von Hand, der Stempel, die Abnahmen, und ein eigener Abschnitt dar&uuml;ber, was das
       Bauteil von SPICE nachbildet und was nicht. Der Arbeitspunkt, den es rechnet, stimmt
       mit dem Programm aus dem Reiter „Arbeitspunkt Newton“ auf mindestens sechs
       g&uuml;ltige Stellen &uuml;berein — zwei Wege, die nichts voneinander wissen.</p>

    <h3>Der Weg in einem Satz</h3>
    <p>Messger&auml;t &rarr; Kennlinienfeld &rarr; Parametersatz &rarr; eigener L&ouml;ser &rarr;
       Arbeitspunkt &rarr; Kleinsignal &rarr; Vierpol &rarr; Verst&auml;rker, und an jeder Stelle
       die Frage, wie genau die Zahl eigentlich ist.</p>

    <h3>Die Reiter der Reihe nach</h3>
    <table id="wegweiser"></table>
  </div>
</section>"""

KEIN_RECHNER = r"""<h2>Kein rechnender Teil</h2>
  <p class="herkunft">Zu diesem Teilmanuskript gibt es in seinem Bestand kein Programm, das
  hier etwas rechnen könnte — es beschreibt ein Verfahren beziehungsweise eine Vorschrift.
  Es wird deshalb nichts gerechnet; eine eigene Herleitung an dieser Stelle wäre nicht seine.</p>"""


# --------------------------------------------------------------------------- Skript
SKRIPT = r"""
'use strict';
const $ = s => document.querySelector(s);
const L = STAND.lauf;

/* ==========================================================================
   Werkzeug: Darstellung, Tabellen, 2x2-Gleichungssystem, Ausgleichsgerade
   ========================================================================== */
function fmt(v){
  if(v===0) return '0';
  const a=Math.abs(v);
  if(a>=1000) return v.toFixed(0);
  if(a>=100)  return v.toFixed(0);
  if(a>=10)   return v.toFixed(1);
  if(a>=1)    return v.toFixed(2);
  if(a>=0.01) return v.toFixed(3);
  return v.toExponential(1);
}
function si(v, e, n){
  n = (n===undefined)?4:n;
  if(v===0) return '0 '+e;
  const a=Math.abs(v);
  const st=[[1e9,'G'],[1e6,'M'],[1e3,'k'],[1,''],[1e-3,'m'],[1e-6,'µ'],[1e-9,'n'],[1e-12,'p']];
  for(const s of st) if(a>=s[0]) return (v/s[0]).toPrecision(n)+' '+s[1]+e;
  return v.toExponential(2)+' '+e;
}
function tab(el, kopf, reihen){
  if(!el) return;
  let h = kopf ? '<thead><tr>'+kopf.map(c=>'<th>'+c+'</th>').join('')+'</tr></thead>' : '';
  h += '<tbody>'+reihen.map(r=>'<tr>'+r.map(c=>'<td>'+c+'</td>').join('')+'</tr>').join('')+'</tbody>';
  el.innerHTML=h;
}
/* np.linalg.solve(J, -r) fuer 2x2 — dieselbe Operation wie in seinen Programmen */
function loese2(J, r){
  const d = J[0][0]*J[1][1] - J[0][1]*J[1][0];
  return [(-r[0]*J[1][1] + r[1]*J[0][1])/d,
          (-r[1]*J[0][0] + r[0]*J[1][0])/d];
}
/* np.polyfit(x, y, 1) -> Steigung b, Achsenabschnitt a */
function gerade(xs, ys){
  const n=xs.length;
  let sx=0, sy=0, sxx=0, sxy=0;
  for(let k=0;k<n;k++){ sx+=xs[k]; sy+=ys[k]; sxx+=xs[k]*xs[k]; sxy+=xs[k]*ys[k]; }
  const b=(n*sxy-sx*sy)/(n*sxx-sx*sx);
  const a=(sy-b*sx)/n;
  let s=0; for(let k=0;k<n;k++){ const e=ys[k]-(a+b*xs[k]); s+=e*e; }
  return {a:a, b:b, rms:Math.sqrt(s/n), n:n};
}
function mul(A,B){ return [[A[0][0]*B[0][0]+A[0][1]*B[1][0], A[0][0]*B[0][1]+A[0][1]*B[1][1]],
                           [A[1][0]*B[0][0]+A[1][1]*B[1][0], A[1][0]*B[0][1]+A[1][1]*B[1][1]]]; }
function abw(browser, python){
  if(python===0) return browser===0 ? '0' : '—';
  const r = Math.abs((browser-python)/python);
  const k = r < 1e-9 ? 'gut' : (r < 1e-6 ? 'gut' : 'warn');
  return '<span class="'+k+'">'+(r===0 ? '0' : r.toExponential(1))+'</span>';
}
function vgl(name, browser, python, einheit, stellen){
  stellen = stellen===undefined ? 6 : stellen;
  const f = x => (einheit==='' ? x.toPrecision(stellen) : si(x, einheit, stellen));
  return [name, f(browser), f(python), abw(browser, python)];
}

/* ------------------------------------------------------------ Zeichenflaeche */
function Bild(cv){
  const g=cv.getContext('2d');
  const W=cv.width, He=cv.height;
  const m={l:82, r:20, o:18, u:48};
  return {
    g:g, W:W, H:He, m:m,
    rahmen(xa,xe,ya,ye,xt,yt,logx,logy){
      this.xa=xa; this.xe=xe; this.ya=ya; this.ye=ye; this.logx=!!logx; this.logy=!!logy;
      g.clearRect(0,0,W,He);
      g.fillStyle='#fff'; g.fillRect(0,0,W,He);
      g.strokeStyle='#d9d3c7'; g.lineWidth=1;
      g.strokeRect(m.l, m.o, W-m.l-m.r, He-m.o-m.u);
      g.font='13px Segoe UI';
      const nx=6, ny=6;
      // Bei kleiner Spanne braucht die Achse mehr Stellen, sonst stehen
      // sechs gleiche Zahlen untereinander (gefunden beim Ruckwirkungsfeld).
      const stellig = (a,e) => {
        const sp=Math.abs(e-a), gr=Math.max(Math.abs(a),Math.abs(e));
        if(sp<=0 || gr===0) return fmt;
        const n=Math.max(0, Math.ceil(Math.log10(gr/sp))+1);
        return n<=2 ? fmt : (v=>v.toFixed(Math.min(n,4)));
      };
      // Bei wenigen Dekaden ist "1e2" zweimal dieselbe Marke - dann den Wert
      // selbst schreiben (gefunden am |A_v|-Bild ueber R_L).
      const dek = (a,e) => Math.abs(Math.log10(e)-Math.log10(a));
      const logbes = (a,e) => dek(a,e) >= 4
        ? (v => '1e'+Math.round(Math.log10(v))) : (v => fmt(v));
      const fx = this.logx ? logbes(xa,xe) : stellig(xa,xe);
      const fy = this.logy ? logbes(ya,ye) : stellig(ya,ye);
      for(let i=0;i<=nx;i++){
        const v = this.logx ? Math.pow(10, Math.log10(xa)+(Math.log10(xe)-Math.log10(xa))*i/nx)
                            : xa+(xe-xa)*i/nx;
        const px=this.px(v);
        g.strokeStyle='#eee9df'; g.beginPath(); g.moveTo(px,m.o); g.lineTo(px,He-m.u); g.stroke();
        g.fillStyle='#6b655c'; g.textAlign='center';
        g.fillText(fx(v), px, He-m.u+16);
      }
      for(let i=0;i<=ny;i++){
        const v = this.logy ? Math.pow(10, Math.log10(ya)+(Math.log10(ye)-Math.log10(ya))*i/ny)
                            : ya+(ye-ya)*i/ny;
        const py=this.py(v);
        g.strokeStyle='#eee9df'; g.beginPath(); g.moveTo(m.l,py); g.lineTo(W-m.r,py); g.stroke();
        g.fillStyle='#6b655c'; g.textAlign='right';
        g.fillText(fy(v), m.l-7, py+4);
      }
      g.fillStyle='#22201c'; g.textAlign='center';
      g.fillText(xt, m.l+(W-m.l-m.r)/2, He-9);
      g.save(); g.translate(16, m.o+(He-m.o-m.u)/2); g.rotate(-Math.PI/2);
      g.textAlign='center'; g.fillText(yt,0,0); g.restore();
    },
    px(v){ return this.logx
      ? this.m.l + (this.W-this.m.l-this.m.r)*(Math.log10(v)-Math.log10(this.xa))/(Math.log10(this.xe)-Math.log10(this.xa))
      : this.m.l + (this.W-this.m.l-this.m.r)*(v-this.xa)/(this.xe-this.xa); },
    py(v){ return this.logy
      ? this.H-this.m.u - (this.H-this.m.o-this.m.u)*(Math.log10(v)-Math.log10(this.ya))/(Math.log10(this.ye)-Math.log10(this.ya))
      : this.H-this.m.u - (this.H-this.m.o-this.m.u)*(v-this.ya)/(this.ye-this.ya); },
    linie(pk, farbe, breit, strich){
      g.save(); g.beginPath(); g.rect(m.l,m.o,this.W-m.l-m.r,this.H-m.o-m.u); g.clip();
      g.strokeStyle=farbe; g.lineWidth=breit||1.8;
      if(strich) g.setLineDash(strich);
      g.beginPath();
      let auf=false;
      for(const p of pk){
        if(!isFinite(p[0])||!isFinite(p[1])){ auf=false; continue; }
        const X=this.px(p[0]), Y=this.py(p[1]);
        if(!auf){ g.moveTo(X,Y); auf=true; } else g.lineTo(X,Y);
      }
      g.stroke(); g.setLineDash([]); g.restore();
    },
    punkte(pk, farbe, gr){
      g.save(); g.beginPath(); g.rect(m.l,m.o,this.W-m.l-m.r,this.H-m.o-m.u); g.clip();
      g.fillStyle=farbe;
      for(const p of pk){
        if(!isFinite(p[0])||!isFinite(p[1])) continue;
        g.beginPath(); g.arc(this.px(p[0]), this.py(p[1]), gr||2.5, 0, 7); g.fill();
      }
      g.restore();
    },
    marke(x,y,farbe,text,dx,dy){
      g.fillStyle=farbe; g.beginPath(); g.arc(this.px(x),this.py(y),5.5,0,7); g.fill();
      if(text){ g.font='13px Segoe UI';
        g.textAlign=(dx!==undefined && dx<0) ? 'right' : 'left';
        g.fillText(text, this.px(x)+(dx===undefined?9:dx),
                         this.py(y)+(dy===undefined?-9:dy)); }
    },
    legende(eintraege){
      g.font='13px Segoe UI'; g.textAlign='left';
      let y=this.m.o+16;
      for(const e of eintraege){
        g.fillStyle=e[1]; g.fillRect(this.W-this.m.r-214, y-8, 18, 3.5);
        g.fillStyle='#22201c'; g.fillText(e[0], this.W-this.m.r-190, y-4);
        y+=17;
      }
    }
  };
}
const FARB = ['#0E7C86','#C77400','#3B7A57','#B3261E','#6A4C93','#155e75','#8a5a00'];

/* ==========================================================================
   1) BUCH/kap08_rechnung.py — Fixed-Bias mit den gemessenen BC547-Parametern
   ========================================================================== */
/* Zeilen 19-22 */
const K08 = {IS:5.0e-14, NF:1.01, BF:290.0, VAF:95.0, VAR:190.0, IKF:0.08,
             RBI:15.0, VT:0.02586};
/* Zeilen 24-27 (Voreinstellung; die Werkbank darf sie aendern) */
let K08S = {VCC:25.0, VBB:25.0, RC:100.0};
/* Zeilen 29-30 */
function k08_beta_eff(ic){ return K08.BF/Math.sqrt(1.0 + Math.max(ic,0.0)/K08.IKF); }
/* Zeilen 32-42: Residuenvektor [f1, f2] */
function k08_F(x, RB){
  const vbe=x[0], vce=x[1];
  const ib=(K08S.VBB-vbe)/RB;                 // Basiskreis-Masche
  const ic=(K08S.VCC-vce)/K08S.RC;            // Lastgerade
  const veff=vbe-ib*K08.RBI;                  // innerer Basiswiderstand
  const ex=Math.exp(veff/(K08.NF*K08.VT));
  const b=k08_beta_eff(ic);
  return [ib-(K08.IS/b)*ex*(1.0+vce/K08.VAR),
          ic-K08.IS*ex*(1.0+vce/K08.VAF)];
}
/* Zeilen 44-57: analytische Jacobi-Matrix */
function k08_J(x, RB){
  const vbe=x[0], vce=x[1];
  const ib=(K08S.VBB-vbe)/RB;
  const ic=(K08S.VCC-vce)/K08S.RC;
  const veff=vbe-ib*K08.RBI;
  const ex=Math.exp(veff/(K08.NF*K08.VT));
  const b=k08_beta_eff(ic);
  const dveff=1.0+K08.RBI/RB;
  return [[-1.0/RB - (K08.IS/b)*ex*dveff/(K08.NF*K08.VT)*(1+vce/K08.VAR),
           -(K08.IS/b)*ex/K08.VAR],
          [-K08.IS*ex*dveff/(K08.NF*K08.VT)*(1+vce/K08.VAF),
           -1.0/K08S.RC - K08.IS*ex/K08.VAF]];
}
/* Zeilen 59-69: Newton-Raphson, tol 1e-10, hoechstens 100 Schritte */
function k08_newton(RB, vbe0){
  let x=[vbe0===undefined?0.65:vbe0, K08S.VCC/2];
  const prot=[];
  for(let k=0;k<100;k++){
    const r=k08_F(x,RB);
    const norm=Math.hypot(r[0],r[1]);
    prot.push({k:k, VBE:x[0], VCE:x[1], f1:r[0], f2:r[1], norm:norm});
    if(norm<1e-10) return {x:x, k:k, prot:prot, fertig:true};
    const d=loese2(k08_J(x,RB), r);
    x=[x[0]+d[0], x[1]+d[1]];
  }
  return {x:x, k:99, prot:prot, fertig:false};
}
/* Zeilen 71-84: Bisektion auf R_B fuer V_CE = V_CC/2 */
function k08_bisektion(){
  const ziel=K08S.VCC/2;
  let lo=10e3, hi=500e3, RB=0;
  const prot=[];
  for(let i=0;i<60;i++){
    RB=0.5*(lo+hi);
    const r=k08_newton(RB);
    const vce=r.x[1];
    prot.push({k:i+1, RB:RB, VCE:vce, fehler:Math.abs(vce-ziel)});
    if(Math.abs(vce-ziel) <= 0.001*ziel) break;
    if(vce<ziel) lo=RB; else hi=RB;
  }
  return {RB:RB, prot:prot};
}
/* Zeilen 104-107: ideale Abschaetzung */
function k08_ideal(){
  const ic=K08S.VCC/(2*K08S.RC);
  const vbe=K08.NF*K08.VT*Math.log(ic/K08.IS);
  return {ic:ic, vbe:vbe, rb:(K08S.VBB-vbe)/(ic/K08.BF)};
}
/* Die h-Parameter in diesem Arbeitspunkt — Rezept aus
   MANUSKRIPT_Vierpol_Verstaerker.md, Abschnitt 9, Schritte 2 und 3.
   Die Modellgleichungen sind die von kap08_rechnung.py (innere Spannung). */
function k08_hparam(VBE, VCE, RB){
  const ic_v = (vbe,vce) => {
    const ib=(K08S.VBB-vbe)/RB;
    return K08.IS*Math.exp((vbe-ib*K08.RBI)/(K08.NF*K08.VT))*(1+vce/K08.VAF);
  };
  const ib_v = (vbe,vce) => {
    const ib=(K08S.VBB-vbe)/RB, ic=ic_v(vbe,vce);
    return (K08.IS/k08_beta_eff(ic))*Math.exp((vbe-ib*K08.RBI)/(K08.NF*K08.VT))*(1+vce/K08.VAR);
  };
  const dVb=1e-4, dVc=1e-2;
  const S1=(ic_v(VBE+dVb,VCE)-ic_v(VBE-dVb,VCE))/(2*dVb);
  const S2=(ic_v(VBE,VCE+dVc)-ic_v(VBE,VCE-dVc))/(2*dVc);
  const S3=(ib_v(VBE+dVb,VCE)-ib_v(VBE-dVb,VCE))/(2*dVb);
  const S4=(ib_v(VBE,VCE+dVc)-ib_v(VBE,VCE-dVc))/(2*dVc);
  const h11=1/S3, h21=S1/S3, h12=-S4/S3, h22=S2-S1*S4/S3;
  return {S1:S1,S2:S2,S3:S3,S4:S4,h11:h11,h21:h21,h12:h12,h22:h22,
          Dh:h11*h22-h12*h21};
}

/* ==========================================================================
   2) bjt_hparam.py / bjt_verstaerker.py — BC337-25 aus dem Kurventracer-Fit
   ========================================================================== */
const HVT = 0.025852;                                   /* bjt_hparam.py Z. 25 */
const HP  = {n:1.004, Is:4.726e-14, Beta_F:249.9, VA:146.0,
             IKF:0.9, RB:60.0, Vab:1e6};                /* Z. 26-28 */
/* Z. 45-46 */
function hp_vt(P){ return (P && P.VT) ? P.VT : HVT; }
function hp_ic(vbe, vce, P){ P=P||HP; return P.Is*Math.exp(vbe/(P.n*hp_vt(P)))*(1+vce/P.VA); }
/* Z. 47-55: mit der 40-schrittigen Fixpunktiteration auf I_B */
function hp_ib(vbe, vce, P, prot){
  P=P||HP;
  const ic=hp_ic(vbe,vce,P);
  const be=P.Beta_F/Math.sqrt(1+ic/P.IKF);
  let ib=ic/be;
  if(prot) prot.push({k:0, ib:ib, veff:vbe-ib*P.RB});
  for(let k=0;k<40;k++){
    const ibn=(P.Is/be)*Math.exp((vbe-ib*P.RB)/(P.n*hp_vt(P)))*(1+vce/P.Vab);
    if(prot) prot.push({k:k+1, ib:ibn, veff:vbe-ibn*P.RB});
    if(Math.abs(ibn-ib) <= 1e-20+1e-10*Math.abs(ibn)){ ib=ibn; break; }
    ib=ibn;
  }
  return ib;
}
/* Z. 56-57 */
function hp_vbe_from_ic(ic, vce, P){ P=P||HP; return Math.log(ic/(P.Is*(1+vce/P.VA)))*(P.n*hp_vt(P)); }
/* Z. 58-61: Bisektion, 50 Schritte in [0,2 V; 1,0 V] */
function hp_vbe_for_ib(ib, vce, P){
  P=P||HP;
  let lo=0.2, hi=1.0;
  for(let k=0;k<50;k++){
    const mid=0.5*(lo+hi);
    if(hp_ib(mid,vce,P)-ib > 0) hi=mid; else lo=mid;
  }
  return 0.5*(lo+hi);
}
/* Z. 64-77: Arbeitspunkt und h-Parameter als zentrale Differenzen */
function hp_rechnen(IC_Q, VCE_Q){
  const VBE_Q = hp_vbe_from_ic(IC_Q, VCE_Q);
  const IB_Q  = hp_ib(VBE_Q, VCE_Q);
  const dVb=1e-4, dVc=1e-2;
  const gm  = (hp_ic(VBE_Q+dVb,VCE_Q)-hp_ic(VBE_Q-dVb,VCE_Q))/(2*dVb);
  const go  = (hp_ic(VBE_Q,VCE_Q+dVc)-hp_ic(VBE_Q,VCE_Q-dVc))/(2*dVc);
  const gpi = (hp_ib(VBE_Q+dVb,VCE_Q)-hp_ib(VBE_Q-dVb,VCE_Q))/(2*dVb);
  const gmu = (hp_ib(VBE_Q,VCE_Q+dVc)-hp_ib(VBE_Q,VCE_Q-dVc))/(2*dVc);
  const h11=1/gpi, h21=gm/gpi, h12=-gmu/gpi, h22=go-gm*gmu/gpi;
  return {IC:IC_Q, VCE:VCE_Q, VBE:VBE_Q, IB:IB_Q, gm:gm, go:go, gpi:gpi, gmu:gmu,
          h11:h11, h12:h12, h21:h21, h22:h22, Dh:h11*h22-h12*h21};
}

/* --- bjt_verstaerker.py, Z. 95-209 ------------------------------------- */
function vp_F(vbe, vce, rb, S){
  return [(S.VBB-vbe)/rb - hp_ib(vbe,vce), (S.VCC-vce)/S.RC - hp_ic(vbe,vce)];
}
/* Z. 99-105: numerische Jacobi-Matrix, zentrale Differenzen */
function vp_J(vbe, vce, rb, S){
  const hb=1e-6, hc=1e-4;
  const a=vp_F(vbe+hb,vce,rb,S), b=vp_F(vbe-hb,vce,rb,S);
  const c=vp_F(vbe,vce+hc,rb,S), d=vp_F(vbe,vce-hc,rb,S);
  return [[(a[0]-b[0])/(2*hb), (c[0]-d[0])/(2*hc)],
          [(a[1]-b[1])/(2*hb), (c[1]-d[1])/(2*hc)]];
}
/* Z. 107-122: Newton-Raphson mit Daempfung und Begrenzung */
function vp_arbeitspunkt(rb, S){
  let x=[0.65, S.VCC/2];
  for(let i=0;i<60;i++){
    const f=vp_F(x[0],x[1],rb,S);
    if(Math.abs(f[0])<1e-12 && Math.abs(f[1])<1e-12) return {VBE:x[0], VCE:x[1], iter:i+1};
    const d=loese2(vp_J(x[0],x[1],rb,S), f);
    let d0=Math.max(-0.05, Math.min(0.05, d[0]));
    let d1=Math.max(-2.0,  Math.min(2.0,  d[1]));
    x=[x[0]+d0, x[1]+d1];
    x[0]=Math.min(Math.max(x[0],0.2),1.0);
    x[1]=Math.min(Math.max(x[1],1e-3),S.VCC);
  }
  return {VBE:x[0], VCE:x[1], iter:60, warnung:'Newton-Raphson konvergiert nicht'};
}
/* Z. 140-145 */
const E24=[1.0,1.1,1.2,1.3,1.5,1.6,1.8,2.0,2.2,2.4,2.7,3.0,
           3.3,3.6,3.9,4.3,4.7,5.1,5.6,6.2,6.8,7.5,8.2,9.1];
function e24_naechster(r){
  const dek=Math.pow(10, Math.floor(Math.log10(r)));
  const kand=E24.map(m=>m*dek).concat([E24[0]*dek*10]);
  let best=kand[0];
  for(const x of kand) if(Math.abs(Math.log(x/r)) < Math.abs(Math.log(best/r))) best=x;
  return best;
}
/* Z. 147-160: R_B automatisch fuer Vce = Vcc/2 */
function vp_rb_auto(S){
  const vce_z=S.VCC/2;
  const ic_z=(S.VCC-vce_z)/S.RC;
  let vbe_k=hp_vbe_from_ic(ic_z, vce_z);
  for(let k=0;k<30;k++){
    const f=hp_ic(vbe_k,vce_z)-ic_z;
    vbe_k -= f/(hp_ic(vbe_k,vce_z)/(HP.n*HVT));
  }
  const ib_z=hp_ib(vbe_k, vce_z);
  const rb_exakt=(S.VBB-vbe_k)/ib_z;
  return {exakt:rb_exakt, e24:e24_naechster(rb_exakt)};
}
/* Z. 187-199 */
function h_zu_a(h11,h12,h21,h22){
  const Dh=h11*h22-h12*h21;
  return [[-Dh/h21, -h11/h21],[-h22/h21, -1.0/h21]];
}
function a_quer(R){ return [[1.0,0.0],[1.0/R,1.0]]; }
/* Z. 163-209 zusammen */
function vp_kette(S){
  let RB=S.RB, info='';
  if(!RB){ const a=vp_rb_auto(S); RB=a.e24;
    info='R_B automatisch für V_ce = V_cc/2: exakt '+(a.exakt/1e3).toFixed(1)
        +' kΩ → E24-Wert '+(a.e24/1e3).toFixed(0)+' kΩ'; }
  const ap=vp_arbeitspunkt(RB, S);
  const VBE=ap.VBE, VCE=ap.VCE;
  const IB=hp_ib(VBE,VCE), IC=hp_ic(VBE,VCE);
  const dVb=1e-4, dVc=1e-2;
  const S1=(hp_ic(VBE+dVb,VCE)-hp_ic(VBE-dVb,VCE))/(2*dVb);
  const S2=(hp_ic(VBE,VCE+dVc)-hp_ic(VBE,VCE-dVc))/(2*dVc);
  const S3=(hp_ib(VBE+dVb,VCE)-hp_ib(VBE-dVb,VCE))/(2*dVb);
  const S4=(hp_ib(VBE,VCE+dVc)-hp_ib(VBE,VCE-dVc))/(2*dVc);
  const h11=1/S3, h21=S1/S3, h12=-S4/S3, h22=S2-S1*S4/S3;
  const Dh=h11*h22-h12*h21;
  const A_T=h_zu_a(h11,h12,h21,h22);
  const A=mul(mul(a_quer(RB), A_T), a_quer(S.RC));
  const r_ein=(A[0][0]*S.RL+A[0][1])/(A[1][0]*S.RL+A[1][1]);
  const r_aus=(A[1][1]*S.RI+A[0][1])/(A[1][0]*S.RI+A[0][0]);
  const A_v=S.RL/(A[0][0]*S.RL+A[0][1]);
  const A_i=1/(A[1][0]*S.RL+A[1][1]);
  const A_vs=A_v*r_ein/(r_ein+S.RI);
  return {RB:RB, info:info, iter:ap.iter, VBE:VBE, VCE:VCE, IB:IB, IC:IC,
          S1:S1,S2:S2,S3:S3,S4:S4, h11:h11,h12:h12,h21:h21,h22:h22, Dh:Dh,
          A_T:A_T, A:A, r_ein:r_ein, r_aus:r_aus, A_v:A_v, A_i:A_i, A_vs:A_vs};
}

/* ==========================================================================
   3) Transistor_20.py — das einfachste Modell, ohne Stromverstaerkung
   ========================================================================== */
const T20 = {q:1.602e-19, k_B:1.381e-23, T:300, I_S:1e-13, V_A:100};  /* Z. 8-12 */
function t20_F(x, rb, S){                                            /* Z. 36-54 */
  const V_BE=x[0], V_CE=x[1];
  const I_B=(S.VBB-V_BE)/rb;
  const I_C=(S.VCC-V_CE)/S.RC;
  const I_B_shockley=T20.I_S*Math.exp(T20.q*V_BE/(T20.k_B*T20.T));
  return [I_B-I_B_shockley, I_C-I_B_shockley*(1+V_CE/T20.V_A)];
}
function t20_J(x, rb, S){                                            /* Z. 64-80 */
  const V_BE=x[0], V_CE=x[1];
  const ex=Math.exp(T20.q*V_BE/(T20.k_B*T20.T));
  const fa=T20.I_S*T20.q/(T20.k_B*T20.T)*ex;
  return [[-1/rb-fa, 0.0],
          [-fa*(1+V_CE/T20.V_A), -1/S.RC+(T20.I_S/T20.V_A)*ex]];
}
function t20_newton(start, rb, S){                                   /* Z. 100-117 */
  let xy=[start[0], start[1]];
  for(let i=0;i<100;i++){
    const f=t20_F(xy,rb,S);
    if(Math.abs(f[0])<1e-10 && Math.abs(f[1])<1e-10) return {x:xy, iter:i+1};
    const d=loese2(t20_J(xy,rb,S), f);
    xy=[xy[0]+d[0], xy[1]+d[1]];
    if(xy[1]<0) throw new Error('Unphysikalische Lösung in Iteration '+(i+1)
                                +': V_CE = '+xy[1].toFixed(5));
  }
  throw new Error('Keine Konvergenz!');
}
function t20_suche(S){                                               /* Z. 139-182 */
  const V_CE_ziel=S.VCC/2, tol_abs=0.05*V_CE_ziel;
  let R_B_min=500, R_B_max=100e3;
  let start=[0.9, 8.0];
  const versuche=[];
  for(let i=0;i<30;i++){
    const R_B_try=(R_B_min+R_B_max)/2;
    let V_BE=null, V_CE=-1, iters=null, fehler=null;
    try{
      const r=t20_newton(start, R_B_try, S);
      V_BE=r.x[0]; V_CE=r.x[1]; iters=r.iter; start=[r.x[0], r.x[1]];
    }catch(e){
      V_CE=-1; start=[0.9, 8.0]; fehler=e.message;
    }
    versuche.push({k:i+1, RB:R_B_try, VCE:V_CE, iter:iters, fehler:fehler});
    if(Math.abs(V_CE-V_CE_ziel)<=tol_abs && V_CE>0)
      return {RB:R_B_try, VBE:V_BE, VCE:V_CE, versuche:versuche,
              IB:(S.VBB-V_BE)/R_B_try};
    if(V_CE<0 || V_CE<V_CE_ziel) R_B_max=R_B_try; else R_B_min=R_B_try;
  }
  return {versuche:versuche, fehlschlag:true};
}

/* ==========================================================================
   4) Transistor_21b.py — dasselbe, aber mit beta_F
   ========================================================================== */
const T21 = {q:1.602e-19, k_B:1.381e-23, T:300, I_S:1e-13, beta_F:200.0,
             n:1.0, V_A:100.0};                                      /* Z. 8-19 */
function t21_F(x, rb, S){                                            /* Z. 34-57 */
  const V_BE=x[0], V_CE=x[1];
  const I_B=(S.VBB-V_BE)/rb, I_C=(S.VCC-V_CE)/S.RC;
  const ex=Math.exp(T21.q*V_BE/(T21.n*T21.k_B*T21.T));
  return [I_B-(T21.I_S/T21.beta_F)*ex, I_C-T21.I_S*ex*(1.0+V_CE/T21.V_A)];
}
function t21_J(x, rb, S){                                            /* Z. 63-98 */
  const V_BE=x[0], V_CE=x[1];
  const ex=Math.exp(T21.q*V_BE/(T21.n*T21.k_B*T21.T));
  const fa=T21.I_S*T21.q/(T21.n*T21.k_B*T21.T)*ex;
  return [[-1.0/rb-fa/T21.beta_F, 0.0],
          [-fa*(1.0+V_CE/T21.V_A), -1.0/S.RC-(T21.I_S/T21.V_A)*ex]];
}
function t21_newton(start, rb, S){                                   /* Z. 104-140 */
  let xy=[start[0], start[1]];
  const prot=[];
  for(let i=0;i<100;i++){
    const f=t21_F(xy,rb,S);
    prot.push({k:i, VBE:xy[0], VCE:xy[1], f1:f[0], f2:f[1],
               norm:Math.hypot(f[0],f[1])});
    if(Math.abs(f[0])<1e-10 && Math.abs(f[1])<1e-10)
      return {x:xy, iter:i+1, prot:prot};
    const d=loese2(t21_J(xy,rb,S), f);
    xy=[xy[0]+d[0], xy[1]+d[1]];
  }
  throw new Error('Keine Konvergenz!');
}
function t21_suche(S){                                               /* Z. 143-228 */
  const V_CE_ziel=S.VCC/2.0, tol_abs=0.05*V_CE_ziel;
  let R_B_min=10e3, R_B_max=500e3;
  let start=[0.65, S.VCC/2];
  const versuche=[];
  let letzte=null;
  for(let i=0;i<30;i++){
    const R_B_try=(R_B_min+R_B_max)/2.0;
    const r=t21_newton(start, R_B_try, S);
    const V_BE=r.x[0], V_CE=r.x[1];
    start=[V_BE, V_CE];
    letzte={RB:R_B_try, VBE:V_BE, VCE:V_CE, iter:r.iter, prot:r.prot};
    versuche.push({k:i+1, RB:R_B_try, VCE:V_CE, iter:r.iter});
    if(Math.abs(V_CE-V_CE_ziel)<=tol_abs) break;
    if(V_CE<V_CE_ziel) R_B_min=R_B_try; else R_B_max=R_B_try;
  }
  letzte.versuche=versuche;
  letzte.IB=(S.VBB-letzte.VBE)/letzte.RB;
  letzte.IC=(S.VCC-letzte.VCE)/S.RC;
  return letzte;
}

/* ==========================================================================
   5) BUCH/kap09_spice_abgleich.py — Buchgleichungen gegen SPICE-Konvention
   ========================================================================== */
const SP = {V_CC:25.0, R_C:100.0, V_BB:25.0, IS:1e-13, BF:200.0, NF:1.0,
            VAF:100.0, VAR:200.0, IKF:0.5, RBint:10.0};              /* Z. 12-15 */
const VT_PY = 1.381e-23*300.0/1.602e-19;                             /* Z. 17 */
const VT_LT = 1.380649e-23*300.15/1.602176634e-19;                   /* Z. 18 */
/* Z. 22-38: gedaempfter Newton mit numerischer Jacobi-Matrix */
function sp_newton2(F, start){
  let x=[start[0], start[1]];
  for(let n=0;n<400;n++){
    const f=F(x);
    if(Math.abs(f[0])<1e-12 && Math.abs(f[1])<1e-12) return x;
    const h=1e-9;
    const J=[[0,0],[0,0]];
    for(let j=0;j<2;j++){
      const d=[x[0],x[1]]; d[j]+=h;
      const fd=F(d);
      J[0][j]=(fd[0]-f[0])/h; J[1][j]=(fd[1]-f[1])/h;
    }
    const dd=loese2(J,f);
    x=[x[0]+Math.max(-0.02,Math.min(0.02,dd[0])),
       x[1]+Math.max(-2.0, Math.min(2.0, dd[1]))];
  }
  throw new Error('keine Konvergenz');
}
function sp_ap(F, R_B){                                              /* Z. 40-44 */
  const x=sp_newton2(F, [0.65, SP.V_CC/2]);
  return [x[0], x[1], (SP.V_BB-x[0])/R_B, (SP.V_CC-x[1])/SP.R_C];
}
function sp_buch_einfach(R_B){                                       /* Z. 47-53 */
  return v => { const V_BE=v[0], V_CE=v[1];
    const e=Math.exp(V_BE/(SP.NF*VT_PY));
    return [(SP.V_BB-V_BE)/R_B - SP.IS/SP.BF*e,
            (SP.V_CC-V_CE)/SP.R_C - SP.IS*e*(1+V_CE/SP.VAF)]; };
}
function sp_buch_erweitert(R_B){                                     /* Z. 55-64 */
  return v => { const V_BE=v[0], V_CE=v[1];
    const I_B=(SP.V_BB-V_BE)/R_B, I_C=(SP.V_CC-V_CE)/SP.R_C;
    const beta=SP.BF/Math.sqrt(1+Math.max(I_C,0)/SP.IKF);
    const e=Math.exp((V_BE-I_B*SP.RBint)/(SP.NF*VT_PY));
    return [I_B - SP.IS/beta*e*(1+V_CE/SP.VAR),
            I_C - SP.IS*e*(1+V_CE/SP.VAF)]; };
}
function sp_spice_einfach(R_B){                                      /* Z. 67-76 */
  return v => { const V_BE=v[0], V_CE=v[1];
    const V_BC=V_BE-V_CE;
    const e_be=Math.exp(V_BE/(SP.NF*VT_LT));
    const e_bc=Math.exp(V_BC/(SP.NF*VT_LT));
    const qb=1.0/(1.0-V_BC/SP.VAF);
    return [(SP.V_BB-V_BE)/R_B - SP.IS/SP.BF*(e_be-1),
            (SP.V_CC-V_CE)/SP.R_C - SP.IS*(e_be-e_bc)/qb]; };
}
function sp_spice_erweitert(R_B){                                    /* Z. 78-91 */
  const kl = x => Math.max(-80, Math.min(80, x));
  return v => { const V_BE=v[0], V_CE=v[1];
    const I_B=(SP.V_BB-V_BE)/R_B;
    const Vbe_i=V_BE-I_B*SP.RBint;
    const V_BC=Vbe_i-V_CE;
    const e_be=Math.exp(kl(Vbe_i/(SP.NF*VT_LT)));
    const e_bc=Math.exp(kl(V_BC/(SP.NF*VT_LT)));
    const q1=1.0/(1.0-V_BC/SP.VAF-Vbe_i/SP.VAR);
    const q2=SP.IS/SP.IKF*(e_be-1);
    const qb=q1/2.0*(1.0+Math.sqrt(1.0+4.0*q2));
    return [I_B - SP.IS/SP.BF*(e_be-1),
            (SP.V_CC-V_CE)/SP.R_C - SP.IS*(e_be-e_bc)/qb]; };
}

/* ==========================================================================
   6) BUCH/kap08_led_quellen.py — Diode und Leuchtdiode
   ========================================================================== */
const DVT = 0.02585;                                                 /* Z. 22 */
/* Z. 30-33: erweiterte Shockley-Gleichung V(I) */
function d_spannung(Id, log10_Is, n, Rs){
  const Is=Math.pow(10, log10_Is);
  return n*DVT*Math.log(Id/Is+1) + Id*Rs;
}
/* Z. 35-49: Newton-Raphson im Strom I_d — wortgetreu */
function d_solve_for_Id(Uges, R, log10_Is, n, Rs, prot){
  const Is=Math.pow(10, log10_Is);
  let Id=Uges/(R+Rs+1.0);                    // gedaempfter Kurzschlussstrom
  const tolerance=1e-7;
  if(prot) prot.push({k:0, I:Id, rest:n*DVT*Math.log(Id/Is+1)+Id*Rs+Id*R-Uges});
  for(let k=0;k<1000;k++){
    if(Id<=0) Id=1e-12;
    const f = n*DVT*Math.log(Id/Is+1) + Id*Rs + Id*R - Uges;
    const df = (n*DVT)/(Id+Is) + Rs + R;
    const Id_new = Id - f/df;
    if(prot) prot.push({k:k+1, I:Id_new,
      rest:n*DVT*Math.log(Math.max(Id_new,1e-30)/Is+1)+Id_new*Rs+Id_new*R-Uges});
    if(Math.abs(Id_new-Id) < tolerance) return (Id_new>0) ? Id_new : null;
    Id=Id_new;
  }
  return null;
}
/* Die Bisektion auf R — Abschnitt 6.2 des Diodenmanuskripts,
   Suchintervall 1 Ohm ... 1 000 000 Ohm */
function d_bisektion(Uges, Isoll, log10_Is, n, Rs){
  let Rmin=1.0, Rmax=1e6;
  const prot=[];
  let R=0;
  for(let k=0;k<60;k++){
    R=0.5*(Rmin+Rmax);
    const I=d_solve_for_Id(Uges, R, log10_Is, n, Rs);
    prot.push({k:k+1, R:R, I:I, fehler:Math.abs(I-Isoll)});
    if(Math.abs(I-Isoll) <= 1e-9*Isoll) break;
    if(I > Isoll) Rmin=R; else Rmax=R;
  }
  return {R:R, prot:prot};
}
/* Z. 25-27: reine Shockley-Gleichung I(V) */
function d_shockley(Vd, Is, n){ return Is*(Math.exp(Vd/(n*DVT))-1); }

/* ==========================================================================
   7) BUCH/kapitel_06_gummel_poon.md, Abschnitt 6.9 — die Python-Implementierung
   ========================================================================== */
const GP0 = {IS:4.1e-14, NF:1.0, BETA:292.0, VA:146.0, VAB:200.0,
             IKF:0.9, RBI:60.0, VT:0.02585};
function gp_beta_eff(ic, P){ return P.BETA/Math.sqrt(1.0+ic/P.IKF); }
function gp_v_be_eff(v_be, i_b, P){ return v_be - i_b*P.RBI; }
function gp_i_c_modell(v_be, v_ce, P){
  return P.IS*Math.exp(v_be/(P.NF*P.VT))*(1.0+v_ce/P.VA);
}
function gp_i_b_modell(v_be_wirksam, v_ce, ic, P){
  return (P.IS/gp_beta_eff(ic,P))*Math.exp(v_be_wirksam/(P.NF*P.VT))*(1.0+v_ce/P.VAB);
}
/* Die Fixpunktiteration aus Abschnitt 6.9: I_B^(0) = I_C/beta_eff,
   dann wiederholt I_B aus V_BE - I_B*R_B,int */
function gp_rechnen(vbe, vce, P, prot){
  const ic=gp_i_c_modell(vbe,vce,P);
  let ib=ic/gp_beta_eff(ic,P);
  if(prot) prot.push({k:0, veff:vbe, ib:ib, quelle:'Startwert I_C/β_eff'});
  for(let k=0;k<40;k++){
    const veff=gp_v_be_eff(vbe, ib, P);
    const ibn=gp_i_b_modell(veff, vce, ic, P);
    if(prot) prot.push({k:k+1, veff:veff, ib:ibn, quelle:'Fixpunkt'});
    if(Math.abs(ibn-ib) <= 1e-20+1e-12*Math.abs(ibn)){ ib=ibn; break; }
    ib=ibn;
  }
  return {ic:ic, ib:ib, beta:ic/ib, beta_eff:gp_beta_eff(ic,P),
          veff:gp_v_be_eff(vbe, ib, P)};
}

/* ==========================================================================
   8) bjt_extract.py — die Ablesungen aus den Messdateien
   ========================================================================== */
const EVT = 0.025852;                                                /* Z. 13 */
function ex_ablesen(){
  /* Z. 50-66: n und I_S,eff aus dem Gummel-Plot */
  const gummel=[];
  for(const s of STAND.tracer.Ic_Vbe){
    const vce=s.wert;
    if(vce < 1) continue;                       // Z. 55: Vce=0 ist nicht aktiv
    const xs=[], ys=[];
    for(let i=0;i<s.x.length;i++){
      const ic=s.y[i]*1e-3;                     // Datei in mA
      if(ic > 2e-5 && ic < 2e-3){ xs.push(s.x[i]); ys.push(Math.log(ic)); }
    }
    if(xs.length < 2) continue;
    const g=gerade(xs, ys);                     // Z. 63
    gummel.push({vce:vce, n:1.0/(g.b*EVT), is_eff:Math.exp(g.a),
                 punkte:xs.length, a:g.a, b:g.b});
  }
  const n = gummel.reduce((s,x)=>s+x.n,0)/gummel.length;             // Z. 68
  /* Z. 74-86: V_A je Ib-Kurve */
  const early=[];
  for(const s of STAND.tracer.Ic_Vce){
    const xs=[], ys=[];
    for(let i=0;i<s.x.length;i++)
      if(s.x[i] >= 1.5){ xs.push(s.x[i]); ys.push(s.y[i]*1e-3); }
    if(xs.length < 2) continue;
    const g=gerade(xs, ys);                     // ic = a + b*vce
    early.push({ib:s.wert, VA:g.a/g.b, punkte:xs.length});
  }
  const VA = early.reduce((s,x)=>s+x.VA,0)/early.length;
  /* Z. 89: I_S um den Early-Faktor bereinigt */
  const is_vals = gummel.map(x => x.is_eff/(1+x.vce/VA));
  const Is = is_vals.reduce((s,x)=>s+x,0)/is_vals.length;
  /* Z. 98-112: beta auf zwei Wegen */
  const betas=[];
  for(const s of STAND.tracer.Ic_Ib){
    const xs=[], ys=[];
    for(let i=0;i<s.x.length;i++){
      const ib=s.x[i]*1e-6, ic=s.y[i]*1e-3;
      if(ib > 0){ xs.push(ib); ys.push(ic); }
    }
    if(xs.length < 2) continue;
    const g=gerade(xs, ys);
    betas.push({vce:s.wert, beta:g.b, punkte:xs.length});
  }
  const beta_steig = betas.reduce((s,x)=>s+x.beta,0)/betas.length;
  let hfe_max=0, ic_max=0;
  for(const s of STAND.tracer.hFE_Ic){
    for(let i=0;i<s.y.length;i++){
      if(s.y[i] > hfe_max) hfe_max=s.y[i];
      if(s.x[i]*1e-3 > ic_max) ic_max=s.x[i]*1e-3;
    }
  }
  return {gummel:gummel, n:n, early:early, VA:VA, Is:Is, is_vals:is_vals,
          betas:betas, beta_steig:beta_steig, hfe_max:hfe_max, ic_max:ic_max};
}

/* ==========================================================================
   9) Kennlinienschreiber_1.py — die Gerätekonstanten
   ========================================================================== */
const GER = {MODBUS_ADR:1, BAUD:115200, REG_DA0:0, REG_ADMIW:8,
             DAC_MAX_V:2.5, ADC_MAX_V:4.096, DAC_BITS:65535, ADC_BITS:65535};
function volt_to_dac(v){                                             /* Z. 44-47 */
  const raw=Math.round(v/GER.DAC_MAX_V*GER.DAC_BITS);
  return Math.max(0, Math.min(GER.DAC_BITS, raw));
}
function adc_to_volt(raw){ return raw/GER.ADC_BITS*GER.ADC_MAX_V; }  /* Z. 49-51 */

/* ==========================================================================
   10) DGL_Nichtlinear/Programme/simulator.py — der Netzlisten-Loeser

   Uebertragung Zeile fuer Zeile.  Ueber jeder Funktion steht, aus welcher
   Klasse und welchen Zeilen von simulator.py sie stammt.  Nichts ist hier
   neu erfunden und nichts "besser" gemacht; wo sein Loeser etwas nicht kann,
   kann es die Seite auch nicht.

   ALLE Bauteilklassen seines Loesers sind uebertragen, nicht eine Auswahl:
   Widerstand, Spannungsquelle, Diode (samt den Modellkarten aus
   bruecke_kern.py), Kondensator, Induktivitaet und Transistor.

   Zwei Zutaten sind ausdruecklich UNSERE und als solche gekennzeichnet:
     * sim_loese  — sein Loeser ruft numpy.linalg.solve (Z. 689); hier steht
                    das Gauss-Verfahren mit Teilpivotierung ausgeschrieben,
                    dasselbe Verfahren, das LAPACK darunter ausfuehrt.
     * das Newton-Protokoll — Mitschreiben, das an der Rechnung nichts aendert.
   ========================================================================== */
const SIM_GMIN = 1e-9;                                        /* Z. 90 */
const SIM_VORSATZ = {meg:1e6, k:1e3, m:1e-3, u:1e-6, n:1e-9, p:1e-12, f:1e-15};
const SIM_VORSATZ_LANG = Object.keys(SIM_VORSATZ).sort((a,b)=>b.length-a.length);

/* Z. 96-102: Zahl mit Vorsatz — '1000u' -> 1e-3, '2.2k' -> 2200, '10' -> 10 */
function sim_wert(text){
  const t = String(text).trim().toLowerCase();
  for(const vs of SIM_VORSATZ_LANG)
    if(t.endsWith(vs) && t.length>vs.length)
      return parseFloat(t.slice(0, t.length-vs.length))*SIM_VORSATZ[vs];
  return parseFloat(t);
}

/* UNSER Ersatz fuer numpy.linalg.solve (Z. 689): Gauss mit Teilpivotierung. */
function sim_loese(A, b, n){
  const x = b;
  for(let k=0;k<n;k++){
    let p=k, gr=Math.abs(A[k][k]);
    for(let r=k+1;r<n;r++){ const a=Math.abs(A[r][k]); if(a>gr){ gr=a; p=r; } }
    if(!(gr>0)) throw new Error('Knotenmatrix singulär in Spalte '+k);
    if(p!==k){ const z=A[p]; A[p]=A[k]; A[k]=z; const s=x[p]; x[p]=x[k]; x[k]=s; }
    const Ak=A[k], pv=Ak[k];
    for(let r=k+1;r<n;r++){
      const Ar=A[r], f=Ar[k]/pv;
      if(f===0) continue;
      for(let c=k;c<n;c++) Ar[c]-=f*Ak[c];
      x[r]-=f*x[k];
    }
  }
  for(let r=n-1;r>=0;r--){
    let s=x[r]; const Ar=A[r];
    for(let c=r+1;c<n;c++) s-=Ar[c]*x[c];
    x[r]=s/Ar[r];
  }
  return x;
}

/* ---- Z. 109-131: Widerstand — vier Eintraege mit G = 1/R -------------- */
class SimWiderstand{
  constructor(name,p,n,rest){
    this.name=name; this.p=p; this.n=n; this.R=sim_wert(rest[0]);
    if(!(this.R>0)) throw new Error(name+': Widerstand muss positiv sein');
  }
  stempeln(Y,i,u,t,dt){
    const G=1.0/this.R, p=this.p, n=this.n;
    Y[p][p]+=G; Y[n][n]+=G; Y[p][n]-=G; Y[n][p]-=G;
  }
  residuum(F,u,t){
    const I=(u[this.p]-u[this.n])/this.R;
    F[this.p]+=I; F[this.n]-=I;
  }
  messwerte(u){ const uR=u[this.p]-u[this.n]; return {u:uR, i:uR/this.R}; }
}

/* ---- Z. 134-167: Spannungsquelle (dc oder sinus), Zweigstrom als
        Zusatzunbekannte j, Zwangszeile u_p - u_n = u_q(t) --------------- */
class SimSpannungsquelle{
  constructor(name,p,n,rest){
    this.name=name; this.p=p; this.n=n; this.braucht_j=true; this.j=null;
    const art=String(rest[0]).toLowerCase();
    if(art==='dc'){ this.U=sim_wert(rest[1]); this.f=0.0; }
    else if(art==='sinus'){ this.U=sim_wert(rest[1]); this.f=sim_wert(rest[2]); }
    else { this.U=sim_wert(rest[0]); this.f=0.0; }
  }
  u_quelle(t){
    if(this.f===0.0) return this.U;
    return this.U*Math.sin(2.0*Math.PI*this.f*t);
  }
  stempeln(Y,i,u,t,dt){
    const p=this.p, n=this.n, j=this.j;
    Y[p][j]+=1.0; Y[n][j]-=1.0;
    Y[j][p]+=1.0; Y[j][n]-=1.0;
    i[j]+=this.u_quelle(t);
  }
  residuum(F,u,t){
    const I=u[this.j];
    F[this.p]+=I; F[this.n]-=I;
    F[this.j]+=u[this.p]-u[this.n]-this.u_quelle(t);
  }
  messwerte(u){ return {u:u[this.p]-u[this.n], i:u[this.j]}; }
}

/* ---- Z. 202-252: Kondensator.  Zustandsgroesse u_C, Zweigstrom I_C als
        Zusatzunbekannte j.  EXPLIZIT: u_C waehrend des Zeitschritts fest,
        Zwangszeile u_p - u_n = u_C, danach u_C <- u_C + dt*I_C/C.  Der
        implizite Zweig ist mit uebertragen, wird hier aber nicht benutzt. */
class SimKondensator{
  constructor(name,p,n,rest){
    this.name=name; this.p=p; this.n=n; this.braucht_j=true; this.j=null;
    this.C=sim_wert(rest[0]);
    if(!(this.C>0)) throw new Error(name+': Kapazität muss positiv sein');
    this.uC = rest.length>1 ? sim_wert(rest[1]) : 0.0;
    this.uC0 = this.uC;
  }
  stempeln(Y,i,u,t,dt){
    const p=this.p, n=this.n, j=this.j;
    Y[p][j]+=1.0; Y[n][j]-=1.0;
    if(this.implizit){
      const gC=this.C/dt;
      Y[j][p]-=gC; Y[j][n]+=gC; Y[j][j]+=1.0;
      i[j]-=gC*this.uC;
    }else{
      Y[j][p]+=1.0; Y[j][n]-=1.0;
      i[j]+=this.uC;
    }
  }
  residuum(F,u,t){
    const I=u[this.j];
    F[this.p]+=I; F[this.n]-=I;
    if(this.implizit){
      const gC=this.C/this._dt;
      F[this.j]+=I-gC*(u[this.p]-u[this.n])+gC*this.uC;
    }else{
      F[this.j]+=u[this.p]-u[this.n]-this.uC;
    }
  }
  euler(u,dt){
    if(this.implizit) this.uC=u[this.p]-u[this.n];
    else this.uC += dt*u[this.j]/this.C;
  }
  messwerte(u){ return {u:this.uC, i:u[this.j]}; }
}

/* ---- bruecke_kern.py Z. 51, 53-83: das Shockley-Modell ohne Naeherung und
        die Modellkarten, die simulator.py von dort holt (Z. 88). --------- */
const SIM_EXP_MAX_D = 200.0;                        /* bruecke_kern.py Z. 51 */
class SimDiodenModell{
  constructor(IS, n, VT, name){ this.IS=IS; this.n=n; this.VT=VT; this.name=name; }
  get nVT(){ return this.n*this.VT; }
  strom(v){                        /* I_D = IS*(exp(v/(n VT)) - 1)  Z. 66-69 */
    const e=v/this.nVT;
    return this.IS*(Math.exp(e<SIM_EXP_MAX_D ? e : SIM_EXP_MAX_D)-1.0);
  }
  leitwert(v){                     /* dI/dv im Arbeitspunkt        Z. 71-74 */
    const e=v/this.nVT;
    return this.IS/this.nVT*Math.exp(e<SIM_EXP_MAX_D ? e : SIM_EXP_MAX_D);
  }
}
const SIM_MODELLE = {                                /* bruecke_kern.py Z. 79-84 */
  '1N4148': new SimDiodenModell(2.52e-9, 1.752, 0.025852, '1N4148'),
  '1N4007': new SimDiodenModell(14.11e-9, 1.984, 0.025852, '1N4007'),
  '1N5408': new SimDiodenModell(14.11e-9, 1.984, 0.025852, '1N5408'),
  'Schottky 1N5819': new SimDiodenModell(31.7e-6, 1.373, 0.025852, '1N5819'),
};

/* ---- Z. 170-199: Diode — Shockley ohne Naeherung; je Newton-Durchgang die
        Tangente g_d = dI/du und I_eq = I(v) - g_d*v am Arbeitspunkt
        (Manuskript, Abschnitt 13).  p = Anode, n = Kathode.  Dasselbe
        Muster wie beim Transistor, nur mit EINER Tangente und EINER
        Ersatzquelle statt vier und zwei. */
class SimDiode{
  constructor(name,p,n,rest){
    this.name=name; this.p=p; this.n=n;
    const modell = rest.length ? rest.join(' ') : '1N4148';
    if(!(modell in SIM_MODELLE))
      throw new Error(name+": unbekanntes Diodenmodell '"+modell+"' (bekannt: "
                      +Object.keys(SIM_MODELLE).join(', ')+')');
    this.modell=SIM_MODELLE[modell];
  }
  stempeln(Y,i,u,t,dt){
    const p=this.p, n=this.n;
    const v=u[p]-u[n];
    const gd=this.modell.leitwert(v);
    const Ieq=this.modell.strom(v)-gd*v;
    Y[p][p]+=gd; Y[n][n]+=gd;
    Y[p][n]-=gd; Y[n][p]-=gd;
    i[p]-=Ieq; i[n]+=Ieq;
  }
  residuum(F,u,t){
    const I=this.modell.strom(u[this.p]-u[this.n]);
    F[this.p]+=I; F[this.n]-=I;
  }
  messwerte(u){
    const v=u[this.p]-u[this.n];
    return {u:v, i:this.modell.strom(v)};
  }
}

/* ---- Z. 255-292: Induktivitaet ---------------------------------------- */
class SimInduktivitaet{
  constructor(name,p,n,rest){
    this.name=name; this.p=p; this.n=n;
    this.L=sim_wert(rest[0]);
    if(!(this.L>0)) throw new Error(name+': Induktivität muss positiv sein');
    this.iL = rest.length>1 ? sim_wert(rest[1]) : 0.0;
  }
  stempeln(Y,i,u,t,dt){
    const p=this.p, n=this.n;
    if(this.implizit){
      const gL=dt/this.L;
      Y[p][p]+=gL; Y[n][n]+=gL; Y[p][n]-=gL; Y[n][p]-=gL;
    }
    i[p]-=this.iL; i[n]+=this.iL;
  }
  residuum(F,u,t){
    let I=this.iL;
    if(this.implizit) I=I+this._dt/this.L*(u[this.p]-u[this.n]);
    F[this.p]+=I; F[this.n]-=I;
  }
  euler(u,dt){ this.iL += dt*(u[this.p]-u[this.n])/this.L; }
  messwerte(u){ return {u:u[this.p]-u[this.n], i:this.iL}; }
}

/* ---- Z. 335, 338-424: GummelPoon — ein Parametersatz (eine .model-Karte)
        und die Auswertung des Modells samt seiner VIER TANGENTEN.
        v1 = V_BE,eff = u(B') - u(E) ,  v2 = V_CE = u(C) - u(E)          */
const SIM_EXP_MAX_BJT = 200.0;                                /* Z. 335 */
class SimGummelPoon{
  constructor(o){ Object.assign(this, o); }
  get nVT(){ return this.NF*this.VT; }
  _kern(v1,v2){                                               /* Z. 365-377 */
    const e=v1/this.nVT;
    const E=Math.exp(e<SIM_EXP_MAX_BJT ? e : SIM_EXP_MAX_BJT);
    const fA=1.0+v2/this.VAF;
    const fB=1.0+v2/this.VAR;
    const IC=this.IS*E*fA;
    const q=Math.sqrt(1.0+Math.max(IC,0.0)/this.IKF);
    const A=this.IS/this.BF*E;
    return {E:E, fA:fA, fB:fB, IC:IC, q:q, A:A, IB:A*q*fB};
  }
  stroeme(v1,v2){ const k=this._kern(v1,v2); return [k.IC, k.IB]; }
  tangenten(v1,v2){                                           /* Z. 384-405 */
    const k=this._kern(v1,v2);
    const g11=this.IS*k.E*k.fA/this.nVT;
    const g12=this.IS*k.E/this.VAF;
    let dq1=0.0, dq2=0.0;
    if(k.IC>0.0){
      dq1=g11/(2.0*k.q*this.IKF);
      dq2=g12/(2.0*k.q*this.IKF);
    }
    const g21=k.A*k.fB*(k.q/this.nVT+dq1);
    const g22=k.A*(k.q/this.VAR+k.fB*dq2);
    return [g11,g12,g21,g22];
  }
  alles(v1,v2){                                               /* Z. 407-420 */
    const k=this._kern(v1,v2);
    const g11=this.IS*k.E*k.fA/this.nVT;
    const g12=this.IS*k.E/this.VAF;
    let dq1=0.0, dq2=0.0;
    if(k.IC>0.0){
      dq1=g11/(2.0*k.q*this.IKF);
      dq2=g12/(2.0*k.q*this.IKF);
    }
    const g21=k.A*k.fB*(k.q/this.nVT+dq1);
    const g22=k.A*(k.q/this.VAR+k.fB*dq2);
    return [k.IC, k.IB, g11, g12, g21, g22];
  }
  beta_eff(v1,v2){ return this.BF/this._kern(v1,v2).q; }      /* Z. 422-424 */
}

const SIM_UNENDLICH = 1e12;                                   /* Z. 427 */
/* Z. 432-463: die Parameterkarten, jede Zahl aus seinen Unterlagen oder aus
   der Ausgabe seiner Programme. Hier wird NICHTS neu gefittet. */
const SIM_MODELLE_BJT = {
  'BC547': new SimGummelPoon({IS:5.0e-14, NF:1.01, BF:290.0, VAF:95.0,
      VAR:190.0, IKF:0.08, RBI:15.0, VT:0.02586, name:'BC547',
      quelle:'Buch Kap. 7.8 (gemessen) / kap08_rechnung.py'}),
  'BC337': new SimGummelPoon({IS:4.765e-14, NF:1.004, BF:253.2, VAF:126.6,
      VAR:1.39e3, IKF:4.05, RBI:18.8, VT:0.025852, name:'BC337',
      quelle:'bjt_fit.py, globaler Fit (V_AB, R_BI, I_KF nicht bestimmbar)'}),
  'Demo_einfach': new SimGummelPoon({IS:1e-13, NF:1.0, BF:200.0, VAF:100.0,
      VAR:SIM_UNENDLICH, IKF:SIM_UNENDLICH, RBI:0.0, VT:0.025852,
      name:'Demo_einfach', quelle:'LTspice Eigen_RW_1c.asc / _1d.asc'}),
  'Demo_erweitert': new SimGummelPoon({IS:1e-13, NF:1.0, BF:200.0, VAF:100.0,
      VAR:200.0, IKF:0.5, RBI:10.0, VT:0.025852, name:'Demo_erweitert',
      quelle:'LTspice Eigen_RW_1e.asc / _1f.asc'}),
};

/* ---- Z. 466-568: Transistor — der Stempel.
        Netzliste:  T1  <K> <B> <E>  <Modellname>
        Zwoelf Kreuzungen (zwei Stroeme mal zwei Spannungen) und zwei
        Ersatzstromquellen; dazu der Basisbahnwiderstand zwischen der
        Klemme b und dem INNEREN Basisknoten B'.                          */
class SimTransistor{
  constructor(name,c,b,e,rest){
    this.name=name; this.c=c; this.b=b; this.e=e;
    const modell = rest.length ? rest.join(' ') : 'BC547';
    if(!(modell in SIM_MODELLE_BJT))
      throw new Error(name+": unbekanntes Transistormodell '"+modell+"' (bekannt: "
                      +Object.keys(SIM_MODELLE_BJT).join(', ')+')');
    this.M=SIM_MODELLE_BJT[modell];
    this.modell=modell;
    if(this.M.RBI>0.0){ this.braucht_j=true; this.j=null; }
  }
  get bi(){ return (this.j!==null && this.j!==undefined) ? this.j : this.b; }
  _spannungen(u){ const bi=this.bi; return [u[bi]-u[this.e], u[this.c]-u[this.e]]; }
  stempeln(Y,i,u,t,dt){
    const c=this.c, e=this.e, bi=this.bi;
    const v=this._spannungen(u);
    const a=this.M.alles(v[0], v[1]);
    const IC=a[0], IB=a[1], g11=a[2], g12=a[3], g21=a[4], g22=a[5];
    /* I_C (c -> e) nach v1 = u(bi) - u(e) */
    Y[c][bi]+=g11; Y[c][e]-=g11;
    Y[e][bi]-=g11; Y[e][e]+=g11;
    /* I_C (c -> e) nach v2 = u(c) - u(e) */
    Y[c][c]+=g12; Y[c][e]-=g12;
    Y[e][c]-=g12; Y[e][e]+=g12;
    /* I_B (bi -> e) nach v1 */
    Y[bi][bi]+=g21; Y[bi][e]-=g21;
    Y[e][bi]-=g21; Y[e][e]+=g21;
    /* I_B (bi -> e) nach v2 */
    Y[bi][c]+=g22; Y[bi][e]-=g22;
    Y[e][c]-=g22; Y[e][e]+=g22;
    /* die beiden Ersatzstromquellen */
    const ICeq=IC-g11*v[0]-g12*v[1];
    const IBeq=IB-g21*v[0]-g22*v[1];
    i[c]-=ICeq; i[e]+=ICeq;
    i[bi]-=IBeq; i[e]+=IBeq;
    /* der Basisbahnwiderstand zwischen Klemme b und innerem Knoten B' */
    if(bi!==this.b){
      const G=1.0/this.M.RBI, b=this.b;
      Y[b][b]+=G; Y[bi][bi]+=G;
      Y[b][bi]-=G; Y[bi][b]-=G;
    }
  }
  residuum(F,u,t){
    const c=this.c, e=this.e, bi=this.bi;
    const v=this._spannungen(u);
    const s=this.M.stroeme(v[0], v[1]);
    F[c]+=s[0]; F[e]-=s[0];
    F[bi]+=s[1]; F[e]-=s[1];
    if(bi!==this.b){
      const IR=(u[this.b]-u[bi])/this.M.RBI;
      F[this.b]+=IR; F[bi]-=IR;
    }
  }
  messwerte(u){
    const v=this._spannungen(u);
    const s=this.M.stroeme(v[0], v[1]);
    return {u_be:u[this.b]-u[this.e], u_be_eff:v[0], u_ce:v[1],
            u_bc:u[this.b]-u[this.c], i_c:s[0], i_b:s[1], i_e:s[0]+s[1],
            beta:(s[1]!==0.0 ? s[0]/s[1] : NaN),
            beta_eff:this.M.beta_eff(v[0], v[1]), u:v[1], i:s[0]};
  }
}
SimTransistor.KNOTEN = 3;                                     /* Z. 490 */

const SIM_TYPEN = {R:SimWiderstand, Q:SimSpannungsquelle, V:SimSpannungsquelle,
                   D:SimDiode, C:SimKondensator, L:SimInduktivitaet,
                   T:SimTransistor};                             /* Z. 571-573 */

/* ---- Z. 577-740: der Simulator ---------------------------------------- */
class SimSimulator{
  constructor(netzliste, o){                                  /* Z. 592-650 */
    o = o || {};
    this.verfahren = o.verfahren || 'explizit';
    this.dt = o.dt===undefined ? 10e-6 : o.dt;
    this.tol_F = o.tol_F===undefined ? 1e-12 : o.tol_F;
    this.tol_u = o.tol_u===undefined ? 1e-9 : o.tol_u;
    this.max_it = o.max_it===undefined ? 200 : o.max_it;
    this.d_max = o.d_max===undefined ? 0.5 : o.d_max;
    if(this.verfahren!=='explizit' && this.verfahren!=='implizit')
      throw new Error("verfahren: 'explizit' oder 'implizit'");

    this.bauteile=[];
    this.knoten=new Map([['0',0], ['K0',0]]);
    let naechster=1;
    for(let zeile of String(netzliste).split('\n')){
      zeile = zeile.split('*')[0].split('#')[0].trim();
      if(!zeile) continue;
      const teile = zeile.split(/\s+/);
      const typ = SIM_TYPEN[teile[0][0].toUpperCase()];
      if(!typ) throw new Error("unbekannter Bauteiltyp: '"+teile[0]
        +"' (Anfangsbuchstabe R, Q/V, D, C, L oder T)");
      const anz = typ.KNOTEN || 2;
      if(teile.length < anz+2)
        throw new Error("Netzlistenzeile unvollständig: '"+zeile+"'");
      const name=teile[0];
      const anschluesse=teile.slice(1, 1+anz);
      const rest=teile.slice(1+anz);
      for(const k of anschluesse)
        if(!this.knoten.has(k)) this.knoten.set(k, naechster++);
      const idx=anschluesse.map(k=>this.knoten.get(k));
      const b = new typ(name, ...idx, rest);
      b.implizit = (this.verfahren==='implizit');
      this.bauteile.push(b);
    }
    if(!this.bauteile.length) throw new Error('leere Netzliste');

    this.n_knoten = naechster;
    let j = this.n_knoten;
    for(const b of this.bauteile) if(b.braucht_j) b.j = j++;
    this.n_unbekannte = j;

    this.speicher = this.bauteile.filter(b=>typeof b.euler==='function');
    for(const b of this.speicher) b._dt = this.dt;

    /* Arbeitsspeicher, einmal angelegt und in jedem Durchgang geleert —
       an der Rechnung aendert das nichts. */
    const N=this.n_unbekannte;
    this._Y=[]; this._A=[];
    for(let r=0;r<N;r++) this._Y.push(new Float64Array(N));
    for(let r=0;r<N-1;r++) this._A.push(new Float64Array(N-1));
    this._i=new Float64Array(N);
    this._F=new Float64Array(N);
    this._rhs=new Float64Array(N-1);
    this.ruecksetzen();
  }

  ruecksetzen(){                                              /* Z. 653-659 */
    this.t=0.0;
    this.u=new Float64Array(this.n_unbekannte);
    this.schritte=0; this.it_summe=0; this.it_groesste=0; this.abbrueche=0;
  }

  /* Z. 662-696: VERFAHREN 2 um VERFAHREN 1 — stempeln, aufloesen,
     wiederholen.  Geloest wird die POTENTIALFORM Y*u_neu = i; der Abbruch
     prueft das wahre Residuum F, DIREKT aus den Zweigstroemen gebildet,
     und die gedaempfte Aenderung delta. */
  _newton(prot){
    const u=this.u, N=this.n_unbekannte, M=N-1;
    const Y=this._Y, i=this._i, F=this._F, A=this._A, rhs=this._rhs;
    let it=0;
    for(it=1; it<=this.max_it; it++){
      for(let r=0;r<N;r++) Y[r].fill(0.0);
      i.fill(0.0); F.fill(0.0);
      for(let k=1;k<this.n_knoten;k++){          /* GMIN an jedem Knoten */
        Y[k][k]+=SIM_GMIN;
        F[k]+=SIM_GMIN*u[k];
      }
      for(const b of this.bauteile){
        b.stempeln(Y, i, u, this.t, this.dt);
        b.residuum(F, u, this.t);
      }
      if(prot) prot.Y_letzte = Y.slice(1).map(r=>Array.from(r.slice(1)));
      if(prot) prot.i_letzte = Array.from(i.slice(1));
      for(let r=0;r<M;r++){
        const Ar=A[r], Yr=Y[r+1];
        for(let c=0;c<M;c++) Ar[c]=Yr[c+1];
        rhs[r]=i[r+1];
      }
      const u_neu=sim_loese(A, rhs, M);
      let dmax=0.0, fmax=0.0;
      for(let r=0;r<M;r++){
        let d=u_neu[r]-u[r+1];
        if(d> this.d_max) d= this.d_max;
        if(d<-this.d_max) d=-this.d_max;
        u[r+1]+=d;
        const ad=Math.abs(d); if(ad>dmax) dmax=ad;
        const af=Math.abs(F[r+1]); if(af>fmax) fmax=af;
      }
      if(prot) prot.schritte.push({k:it, u:Array.from(u), fmax:fmax, dmax:dmax});
      if(fmax<this.tol_F && dmax<this.tol_u) break;
    }
    if(it>this.max_it) it=this.max_it;
    return it;
  }

  schritt(){                                                  /* Z. 699-711 */
    const it=this._newton();
    this.it_summe+=it;
    if(it>this.it_groesste) this.it_groesste=it;
    if(it>=this.max_it) this.abbrueche++;
    for(const b of this.speicher) b.euler(this.u, this.dt);   /* VERFAHREN 3 */
    this.t+=this.dt;
    this.schritte++;
    return it;
  }

  /* Z. 713-726: bis t_ende rechnen.  Die Seite zeichnet nur ausgewaehlte
     Knoten mit, sonst ist das Feld so gross wie der Bildschirmspeicher. */
  lauf(t_ende, namen){
    const n=Math.round(t_ende/this.dt);
    const idx=namen.map(x=>this.knoten.get(x));
    const tt=new Float64Array(n);
    const uu={}; for(const x of namen) uu[x]=new Float64Array(n);
    for(let k=0;k<n;k++){
      tt[k]=this.t;
      this.schritt();
      for(let m=0;m<namen.length;m++) uu[namen[m]][k]=this.u[idx[m]];
    }
    return {t:tt, u:uu};
  }

  potential(name){ return this.u[this.knoten.get(name)]; }    /* Z. 729-730 */
  bauteil(name){                                              /* Z. 732-736 */
    for(const b of this.bauteile) if(b.name===name) return b;
    throw new Error(name);
  }
  messwerte(name){ return this.bauteil(name).messwerte(this.u); } /* Z. 738-740 */
}

/* ==========================================================================
   Reiter
   ========================================================================== */
const ZEICHNER = {};
document.querySelectorAll('#schiene button').forEach(b=>{
  b.addEventListener('click', ()=>{
    document.querySelectorAll('#schiene button').forEach(x=>x.classList.remove('an'));
    document.querySelectorAll('main section').forEach(x=>x.classList.remove('an'));
    b.classList.add('an');
    const z=document.getElementById(b.dataset.ziel);
    z.classList.add('an');
    window.scrollTo(0,0);
    if(ZEICHNER[b.dataset.ziel]) ZEICHNER[b.dataset.ziel]();
  });
});

/* Die Bilder des Geraetes stehen nur EINMAL in der Datei (als Daten-Adresse in
   STAND) und werden hier in jedes <img data-bild="..."> eingesetzt — auf dem
   Startreiter und im Reiter "Der Transistortester" dasselbe Bild, eine Datei. */
document.querySelectorAll('img[data-bild]').forEach(x=>{
  const q = STAND.geraet[x.dataset.bild];
  if(q) x.src=q;
});

/* Sprungmarken der ersten Seite: sie druecken denselben Knopf wie die Schiene. */
document.querySelectorAll('[data-spring]').forEach(a=>{
  a.addEventListener('click', ev=>{
    ev.preventDefault();
    const k=document.querySelector('#schiene button[data-ziel="'+a.dataset.spring+'"]');
    if(k) k.click();
  });
});

/* ---------------------------------------------------------------- Wegweiser */
(function(){
  const reihen=[];
  document.querySelectorAll('main section').forEach(s=>{
    if(s.id==='start') return;
    const kopf=s.querySelector('.reiterkopf div');
    const rech=s.querySelector('.rechner h2');
    reihen.push(['<b>'+(kopf?kopf.querySelector('b').textContent:s.id)+'</b>',
                 kopf?kopf.innerHTML.replace(/^.*?·\s*/,''):'',
                 rech?rech.textContent:'—']);
  });
  tab($('#wegweiser'), ['Reiter','Teilmanuskript','Was darunter gerechnet wird'], reihen);
})();

/* ---------------------------------------------------- Reiter: Diodenkennlinie */
function di_rechnen(){
  const n=+$('#di_n').value, ls=+$('#di_ls').value, rs=+$('#di_rs').value;
  const U=+$('#di_u').value, R=+$('#di_r').value;
  const prot=[];
  const I=d_solve_for_Id(U, R, ls, n, rs, prot);
  const V=d_spannung(I, ls, n, rs);
  tab($('#di_tab'), ['k','I<sub>d</sub> / mA','U über R / V','Rest g(I) / V'],
    prot.slice(0,40).map(p=>[p.k, (p.I*1e3).toPrecision(8),
      (U-p.I*R).toPrecision(6), p.rest.toExponential(3)]));
  $('#di_zu').innerHTML='Startwert U<sub>ges</sub>/(R+R<sub>S</sub>+1) = '
    +(U/(R+rs+1)*1e3).toFixed(3)+' mA · '+(prot.length-1)+' Schritte bis |ΔI| &lt; 10<sup>−7</sup> A';
  const istLed = Math.abs(n-L.led.n)<1e-6 && Math.abs(ls-Math.log10(L.led.Is))<1e-4
              && Math.abs(rs-L.led.Rs)<1e-4 && U===L.led.Uges && R===L.led.R;
  const zeilen=[['V<sub>d</sub>', V.toPrecision(8)+' V',
                 istLed? L.led.Vd.toPrecision(8)+' V':'—',
                 istLed? abw(V,L.led.Vd):'—'],
                ['I<sub>d</sub>', (I*1e3).toPrecision(8)+' mA',
                 istLed? (L.led.Id*1e3).toPrecision(8)+' mA':'—',
                 istLed? abw(I,L.led.Id):'—'],
                ['U über R', (I*R).toPrecision(6)+' V','—','—'],
                ['P im Widerstand', si(I*I*R,'W'),'—','—']];
  tab($('#di_erg'), ['Größe','Browser','kap08_led_quellen.py','Abweichung'], zeilen);
  di_zeichnen(n, ls, rs, U, R, V, I);
}
function di_zeichnen(n, ls, rs, U, R, V, I){
  const b=Bild($('#di_bild'));
  const Is=Math.pow(10,ls);
  const imax=Math.max(U/R*1e3, I*1e3*1.4);
  b.rahmen(0, Math.max(V*1.35, 1), 0, imax, 'V_d / V', 'I_d / mA');
  const kur=[];
  for(let k=0;k<=400;k++){
    const id=1e-9 + (imax*1e-3)*k/400;
    kur.push([d_spannung(id, ls, n, rs), id*1e3]);
  }
  b.linie(kur, FARB[0], 2.2);
  b.linie([[0, U/R*1e3],[U, 0]], FARB[1], 2.0);
  b.marke(V, I*1e3, '#B3261E', 'AP: '+V.toFixed(4)+' V · '+(I*1e3).toFixed(3)+' mA');
  b.legende([['Diodenkennlinie (erweitertes Shockley)', FARB[0]],
             ['Lastgerade (U_ges − I·R)', FARB[1]]]);
}
function di_bisektion(){
  const n=+$('#di_n').value, ls=+$('#di_ls').value, rs=+$('#di_rs').value;
  const U=+$('#di_u').value, soll=+$('#di_soll').value*1e-3;
  const r=d_bisektion(U, soll, ls, n, rs);
  tab($('#di_bitab'), ['k','R / Ω','I<sub>d</sub> / mA','|I − I<sub>soll</sub>| / mA'],
    r.prot.map(p=>[p.k, p.R.toFixed(3), (p.I*1e3).toFixed(6),
      (p.fehler*1e3).toExponential(2)]));
  $('#di_r').value=r.R.toFixed(2);
}
$('#di_start').addEventListener('click', di_rechnen);
$('#di_bi').addEventListener('click', di_bisektion);
ZEICHNER['diode']=()=>{ if(!$('#di_erg').innerHTML) di_rechnen(); };

/* ------------------------------------------------------- Reiter: Leuchtdiode */
function le_rechnen(){
  const U=+$('#le_u').value, R=+$('#le_r').value;
  tab($('#le_fit'), ['Modell','Parameter','Ergebnis seines Ausgleichs'], [
    ['reines Shockley I(V)','I<sub>S</sub>, n',
     'I<sub>S</sub> = '+L.led.shockley.Is.toExponential(3)+' A · n = '
      +L.led.shockley.n.toFixed(4)],
    ['erweitert V(I), mit R<sub>S</sub>','log<sub>10</sub>I<sub>S</sub>, n, R<sub>S</sub>',
     'I<sub>S</sub> = '+L.led.Is.toExponential(3)+' A · n = '+L.led.n.toFixed(4)
      +' · R<sub>S</sub> = '+L.led.Rs.toFixed(3)+' Ω']]);
  const prot=[];
  const ls=Math.log10(L.led.Is);
  const I=d_solve_for_Id(U, R, ls, L.led.n, L.led.Rs, prot);
  const V=d_spannung(I, ls, L.led.n, L.led.Rs);
  tab($('#le_tab'), ['k','I<sub>d</sub> / mA','Rest g(I) / V'],
    prot.map(p=>[p.k, (p.I*1e3).toPrecision(8), p.rest.toExponential(3)]));
  const ist = (U===L.led.Uges && R===L.led.R);
  tab($('#le_erg'), ['Größe','Browser','kap08_led_quellen.py','Abweichung'], [
    ['V<sub>d</sub>', V.toPrecision(8)+' V', ist?L.led.Vd.toPrecision(8)+' V':'—',
     ist?abw(V,L.led.Vd):'—'],
    ['I<sub>d</sub>', (I*1e3).toPrecision(8)+' mA', ist?(L.led.Id*1e3).toPrecision(8)+' mA':'—',
     ist?abw(I,L.led.Id):'—'],
    ['U<sub>R</sub>', (I*R).toPrecision(6)+' V', ist?(L.led.Id*L.led.R).toPrecision(6)+' V':'—',
     ist?abw(I*R, L.led.Id*L.led.R):'—'],
    ['P<sub>R</sub>', si(I*I*R,'W'), ist?si(L.led.Id*L.led.Id*L.led.R,'W'):'—',
     ist?abw(I*I*R, L.led.Id*L.led.Id*L.led.R):'—'],
    ['Newton-Schritte', String(prot.length-1), ist?String(L.led.iter):'—','—']]);
  const b=Bild($('#le_bild'));
  const imax=Math.max(U/R*1e3, I*1e3*1.4);
  b.rahmen(0, Math.max(V*1.35,1), 0, imax, 'V_d / V', 'I_d / mA');
  const k1=[], k2=[];
  for(let k=0;k<=400;k++){
    const id=1e-9+(imax*1e-3)*k/400;
    k1.push([d_spannung(id, ls, L.led.n, L.led.Rs), id*1e3]);
  }
  for(let k=0;k<=400;k++){
    const vd=(Math.max(V*1.35,1))*k/400;
    k2.push([vd, d_shockley(vd, L.led.shockley.Is, L.led.shockley.n)*1e3]);
  }
  b.linie(k1, FARB[0], 2.2);
  b.linie(k2, FARB[4], 1.8, [6,4]);
  b.linie([[0,U/R*1e3],[U,0]], FARB[1], 2.0);
  b.marke(V, I*1e3, '#B3261E', 'AP');
  b.legende([['erweitert (mit R_S)', FARB[0]], ['reines Shockley', FARB[4]],
             ['Lastgerade', FARB[1]]]);
}
$('#le_start').addEventListener('click', le_rechnen);
ZEICHNER['led']=()=>{ if(!$('#le_erg').innerHTML) le_rechnen(); };

/* ------------------------------------------------------ Reiter: BJT und SPICE */
function bs_rechnen(){
  const S={VCC:+$('#bs_vcc').value, VBB:+$('#bs_vcc').value, RC:+$('#bs_rc').value};
  const r=t21_suche(S);
  tab($('#bs_bitab'), ['Versuch','R<sub>B</sub> / Ω','V<sub>CE</sub> / V','Newton-Schritte'],
    r.versuche.map(v=>[v.k, v.RB.toFixed(2), v.VCE.toFixed(4), v.iter]));
  tab($('#bs_tab'), ['k','V<sub>BE</sub> / V','V<sub>CE</sub> / V','f₁ / A','f₂ / A','‖F‖'],
    r.prot.map(p=>[p.k, p.VBE.toFixed(7), p.VCE.toFixed(6), p.f1.toExponential(3),
      p.f2.toExponential(3), p.norm.toExponential(3)]));
  const ist = (S.VCC===25 && S.RC===100);
  tab($('#bs_erg'), ['Größe','Browser','Transistor_21b.py','Abweichung'], [
    ['R<sub>B</sub>', r.RB.toFixed(4)+' Ω', ist?L.t21.RB.toFixed(4)+' Ω':'—',
     ist?abw(r.RB,L.t21.RB):'—'],
    ['V<sub>BE</sub>', r.VBE.toPrecision(8)+' V', ist?L.t21.VBE.toPrecision(8)+' V':'—',
     ist?abw(r.VBE,L.t21.VBE):'—'],
    ['V<sub>CE</sub>', r.VCE.toPrecision(8)+' V', ist?L.t21.VCE.toPrecision(8)+' V':'—',
     ist?abw(r.VCE,L.t21.VCE):'—'],
    ['I<sub>B</sub>', (r.IB*1e3).toPrecision(8)+' mA', ist?(L.t21.IB*1e3).toPrecision(8)+' mA':'—',
     ist?abw(r.IB,L.t21.IB):'—'],
    ['I<sub>C</sub>', (r.IC*1e3).toPrecision(8)+' mA', ist?(L.t21.IC*1e3).toPrecision(8)+' mA':'—',
     ist?abw(r.IC,L.t21.IC):'—'],
    ['Versuche der Bisektion', String(r.versuche.length), ist?String(L.t21.versuche):'—','—']]);
  const b=Bild($('#bs_bild'));
  const icmax=S.VCC/S.RC*1e3*1.15;
  b.rahmen(0, S.VCC, 0, icmax, 'V_CE / V', 'I_C / mA');
  const kur=[];
  for(let k=0;k<=400;k++){
    const v=0.02+(S.VCC-0.02)*k/400;
    const ex=Math.exp(T21.q*r.VBE/(T21.n*T21.k_B*T21.T));
    kur.push([v, T21.I_S*ex*(1+v/T21.V_A)*1e3]);
  }
  b.linie(kur, FARB[0], 2.2);
  b.linie([[0,S.VCC/S.RC*1e3],[S.VCC,0]], FARB[1], 2.0, [7,4]);
  b.marke(r.VCE, r.IC*1e3, '#B3261E',
    'AP: '+r.VCE.toFixed(3)+' V · '+(r.IC*1e3).toFixed(2)+' mA');
  b.legende([['Transistorkennlinie bei gefundenem V_BE', FARB[0]],
             ['Lastgerade I_C = (V_CC − V_CE)/R_C', FARB[1]]]);
}
$('#bs_start').addEventListener('click', bs_rechnen);
ZEICHNER['bjtspice']=()=>{ if(!$('#bs_erg').innerHTML) bs_rechnen(); };

/* --------------------------------------------------- Reiter: Extraktion BC547 */
function bc_rechnen(){
  K08S={VCC:+$('#bc_vcc').value, VBB:+$('#bc_vcc').value, RC:+$('#bc_rc').value};
  const id=k08_ideal();
  const bi=k08_bisektion();
  const nw=k08_newton(bi.RB);
  const ic=(K08S.VCC-nw.x[1])/K08S.RC;
  tab($('#bc_tab'), ['Schritt','Formel','Wert','kap08_rechnung.py'], [
    ['Zielstrom','I_C = V_CC/(2·R_C)', (id.ic*1e3).toPrecision(6)+' mA',
     (K08S.VCC===25&&K08S.RC===100)?'125,0 mA':'—'],
    ['idealer Basisstrom','I_B = I_C/β_F', si(id.ic/K08.BF,'A'),
     (K08S.VCC===25&&K08S.RC===100)?'431,0 µA':'—'],
    ['BE-Spannung','V_BE = n·V_T·ln(I_C/I_S)', id.vbe.toPrecision(6)+' V',
     (K08S.VCC===25&&K08S.RC===100)?L.kap08.vbe_ideal.toPrecision(6)+' V':'—'],
    ['<b>ideale Abschätzung</b>','R_B = (V_BB − V_BE)/(I_C/β_F)',
     '<b>'+(id.rb/1e3).toPrecision(6)+' kΩ</b>',
     (K08S.VCC===25&&K08S.RC===100)?(L.kap08.rb_ideal/1e3).toPrecision(6)+' kΩ':'—'],
    ['<b>vollständiges Modell</b>','Newton + Bisektion',
     '<b>'+(bi.RB/1e3).toPrecision(6)+' kΩ</b>',
     (K08S.VCC===25&&K08S.RC===100)?(L.kap08.RB/1e3).toPrecision(6)+' kΩ':'—'],
    ['Abstand','(Abschätzung − Modell)/Modell',
     '<span class="schlecht">'+(100*(id.rb-bi.RB)/bi.RB).toFixed(1)+' %</span>','—']]);
  tab($('#bc_warum'), ['Größe','Wert'], [
    ['I<sub>C</sub> im Arbeitspunkt', si(ic,'A')],
    ['Kniestrom I<sub>KF</sub>', si(K08.IKF,'A')],
    ['I<sub>C</sub>/I<sub>KF</sub>', (ic/K08.IKF).toFixed(3)],
    ['β<sub>eff</sub> = β_F/√(1+I_C/I_KF)', k08_beta_eff(ic).toFixed(2)],
    ['β<sub>F</sub> (ideal)', K08.BF.toFixed(0)],
    ['Faktor im Basisstrom', (K08.BF/k08_beta_eff(ic)).toFixed(3)]]);
  K08S={VCC:25.0, VBB:25.0, RC:100.0};
}
$('#bc_start').addEventListener('click', bc_rechnen);
ZEICHNER['bc547']=()=>{ if(!$('#bc_tab').innerHTML) bc_rechnen(); };

/* ------------------------------------------------ Reiter: Arbeitspunkt von Hand */
function t2_rechnen(){
  const S={VCC:+$('#t2_vcc').value, VBB:+$('#t2_vcc').value, RC:+$('#t2_rc').value};
  const r=t20_suche(S);
  tab($('#t2_bitab'), ['Versuch','R<sub>B</sub> / Ω','V<sub>CE</sub> / V','Newton-Schritte','Bemerkung'],
    r.versuche.map(v=>[v.k, v.RB.toFixed(2),
      v.VCE<0 ? '<span class="schlecht">—</span>' : v.VCE.toFixed(4),
      v.iter===null?'—':v.iter,
      v.fehler ? '<span class="warn">'+v.fehler+'</span>' : '']));
  const misslungen=r.versuche.filter(v=>v.fehler).length;
  $('#t2_zu').innerHTML=misslungen+' von '+r.versuche.length
    +' Versuchen brechen ab — der Startwert [0,9 V; 8,0 V] liegt weit außerhalb des '
    +'Einzugsbereichs der e-Funktion. Genau so meldet es seine Konsolenausgabe.';
  const ist=(S.VCC===15 && S.RC===1000);
  if(r.fehlschlag){ tab($('#t2_erg'), ['Größe','Wert'],
      [['Ergebnis','<span class="schlecht">Kein geeigneter R_B gefunden</span>']]); return; }
  tab($('#t2_erg'), ['Größe','Browser','Transistor_20.py','Abweichung'], [
    ['R<sub>B</sub>', r.RB.toFixed(4)+' Ω', ist?L.t20.RB.toFixed(4)+' Ω':'—',
     ist?abw(r.RB,L.t20.RB):'—'],
    ['V<sub>BE</sub>', r.VBE.toPrecision(8)+' V', ist?L.t20.VBE.toPrecision(8)+' V':'—',
     ist?abw(r.VBE,L.t20.VBE):'—'],
    ['V<sub>CE</sub>', r.VCE.toPrecision(8)+' V', ist?L.t20.VCE.toPrecision(8)+' V':'—',
     ist?abw(r.VCE,L.t20.VCE):'—'],
    ['I<sub>B</sub>', (r.IB*1e3).toPrecision(8)+' mA', ist?(L.t20.IB*1e3).toPrecision(8)+' mA':'—',
     ist?abw(r.IB,L.t20.IB):'—'],
    ['Versuche bis zum Treffer', String(r.versuche.length), ist?String(L.t20.versuche):'—','—'],
    ['davon abgebrochen', String(misslungen), ist?String(L.t20.fehlversuche):'—','—']]);
}
$('#t2_start').addEventListener('click', t2_rechnen);
ZEICHNER['t20']=()=>{ if(!$('#t2_erg').innerHTML) t2_rechnen(); };

/* ------------------------------------------------ Reiter: Minimaler Datensatz */
(function(){
  tab($('#md_tab'), ['SPICE','Transistor_21b.py (vier Parameter)',
                     'Gummel-Poon, Abschnitt 6.8 (sieben Parameter)'], [
    ['<code>IS</code>', '10<sup>−13</sup> A', '4,1·10<sup>−14</sup> A'],
    ['<code>NF</code>', '1,0', '1,0'],
    ['<code>BF</code>', '200', '292'],
    ['<code>VAF</code>', '100 V', '146 V'],
    ['<code>VAR</code>', '— (kein Basis-Early)', '200 V'],
    ['<code>IKF</code>', '— (kein Hochstromknie)', '0,9 A'],
    ['<code>RBM</code>', '— (kein Basisbahnwiderstand)', '60 Ω'],
    ['Arbeitspunkt', 'analytisch erreichbar, Newton konvergiert in 4–6 Schritten',
     'implizit — Fixpunkt oder Newton nötig'],
    ['gerechnet im Reiter', 'BJT und SPICE', 'Gummel-Poon']]);
})();

/* -------------------------------------------------- Reiter: Der Transistortester */
(function(){
  const s=$('#ts_reihe');
  for(const n of Object.keys(STAND.reihen)){
    const o=document.createElement('option'); o.value=n; o.textContent=n; s.appendChild(o);
  }
})();
function ts_rechnen(){
  tab($('#ts_konst'), ['Konstante','Wert','Zeile in seinem Programm'], [
    ['MODBUS_ADR', String(GER.MODBUS_ADR), 'Z. 30'],
    ['BAUD', String(GER.BAUD), 'Z. 31'],
    ['REG_DA0 (UC=0, UB=1)', String(GER.REG_DA0), 'Z. 33'],
    ['REG_ADMIW (Urc1…Urb2)', String(GER.REG_ADMIW), 'Z. 34'],
    ['DAC_MAX_V', GER.DAC_MAX_V.toFixed(3)+' V', 'Z. 36'],
    ['ADC_MAX_V', GER.ADC_MAX_V.toFixed(3)+' V', 'Z. 37'],
    ['DAC_BITS / ADC_BITS', String(GER.DAC_BITS), 'Z. 38–39']]);
  const raw=+$('#ts_raw').value, volt=+$('#ts_volt').value;
  const rc=+$('#ts_rc').value, rb=+$('#ts_rb').value;
  const u=adc_to_volt(raw);
  tab($('#ts_um'), ['Schritt','Rechnung','Ergebnis'], [
    ['Wandlerwert → Spannung', raw+' / 65535 · 4,096 V', u.toPrecision(7)+' V'],
    ['Kollektorstrom', 'I_c = U_rc1 / R_c = '+u.toPrecision(6)+' V / '+rc+' Ω',
     (u/rc*1e3).toPrecision(7)+' mA'],
    ['Basisstrom', 'I_b = U_rb1 / R_b = '+u.toPrecision(6)+' V / '+rb+' Ω',
     (u/rb*1e6).toPrecision(7)+' µA'],
    ['Sollspannung → DAC-Wert', volt.toFixed(4)+' V / 2,5 V · 65535',
     String(volt_to_dac(volt))],
    ['und zurück', String(volt_to_dac(volt))+' / 65535 · 2,5 V',
     (volt_to_dac(volt)/GER.DAC_BITS*GER.DAC_MAX_V).toPrecision(7)+' V'],
    ['Auflösung am DAC', '2,5 V / 65535', si(GER.DAC_MAX_V/GER.DAC_BITS,'V')],
    ['Auflösung im Kollektorstrom', '(4,096 V / 65535) / R_c',
     si(GER.ADC_MAX_V/GER.ADC_BITS/rc,'A')]]);
  ts_zeichnen();
}
function ts_zeichnen(){
  const name=$('#ts_reihe').value;
  const reihe=STAND.reihen[name];
  if(!reihe) return;
  const b=Bild($('#ts_bild'));
  let xmax=0, ymax=0, punkte=0;
  for(const k of Object.keys(reihe))
    for(const p of reihe[k]){ if(p[0]>xmax) xmax=p[0]; if(p[1]>ymax) ymax=p[1]; punkte++; }
  b.rahmen(0, xmax*1.02||1, 0, ymax*1.1e3||1, 'U_CE / V', 'I_C / mA');
  const leg=[];
  Object.keys(reihe).forEach((k,i)=>{
    const f=FARB[i%FARB.length];
    b.linie(reihe[k].map(p=>[p[0], p[1]*1e3]), f, 1.8);
    b.punkte(reihe[k].map(p=>[p[0], p[1]*1e3]), f, 2.0);
    leg.push(['I_B = '+k+' mA', f]);
  });
  b.legende(leg);
  $('#ts_zu').innerHTML=name+' · '+Object.keys(reihe).length+' Basisstromstufen · '
    +punkte+' Messpunkte, unmittelbar aus der CSV-Datei des Testers gezeichnet '
    +'(Spalte IB_soll_mA — der Sollwert des Basisstroms in mA).';
}
$('#ts_start').addEventListener('click', ts_rechnen);
$('#ts_reihe').addEventListener('change', ts_zeichnen);
ZEICHNER['tester']=()=>{ if(!$('#ts_konst').innerHTML) ts_rechnen(); };

/* ---------------------------------------------------------- Reiter: Gummel-Poon */
$('#gp_formel').innerHTML =
  'I<sub>C</sub> = I<sub>S</sub>·e<sup>V<sub>BE</sub>/(n·V<sub>T</sub>)</sup>·(1 + V<sub>CE</sub>/V<sub>A</sub>)'
  + ' &nbsp;;&nbsp; β<sub>eff</sub> = β<sub>F</sub>/√(1 + I<sub>C</sub>/I<sub>KF</sub>)'
  + ' &nbsp;;&nbsp; V<sub>BE,eff</sub> = V<sub>BE</sub> − I<sub>B</sub>·R<sub>B,int</sub>'
  + ' &nbsp;;&nbsp; I<sub>B</sub> = (I<sub>S</sub>/β<sub>eff</sub>)·e<sup>V<sub>BE,eff</sub>/(n·V<sub>T</sub>)</sup>·(1 + V<sub>CE</sub>/V<sub>AB</sub>)';
function gp_lesen(){
  return {IS:+$('#gp_is').value*1e-14, NF:GP0.NF, BETA:+$('#gp_bf').value,
          VA:+$('#gp_va').value, VAB:+$('#gp_vab').value, IKF:+$('#gp_ikf').value,
          RBI:+$('#gp_rbi').value, VT:GP0.VT};
}
function gp_rechnen_ui(){
  const P=gp_lesen();
  const vbe=+$('#gp_vbe').value*1e-3, vce=+$('#gp_vce').value;
  const prot=[];
  const r=gp_rechnen(vbe, vce, P, prot);
  // Die Eingabefelder liefern Gleitkommazahlen (4.1*1e-14 ist nicht bitgleich
  // 4.1e-14); verglichen wird deshalb relativ.
  const gl = (a,b) => Math.abs(a-b) <= 1e-9*Math.max(1e-30, Math.abs(b));
  const ist = (gl(vbe,L.gp.vbe) && gl(vce,L.gp.vce)
               && gl(P.IS,GP0.IS) && gl(P.BETA,GP0.BETA) && gl(P.VA,GP0.VA)
               && gl(P.VAB,GP0.VAB) && gl(P.IKF,GP0.IKF) && gl(P.RBI,GP0.RBI));
  tab($('#gp_tab'), ['Größe','Browser','Abschnitt 6.9'], [
    ['I<sub>C</sub>', (r.ic*1e3).toPrecision(6)+' mA', ist?'5,20 mA':'—'],
    ['Startwert I<sub>B</sub> = I_C/β_eff', (prot[0].ib*1e6).toPrecision(6)+' µA',
     ist?'17,9 µA':'—'],
    ['I<sub>B</sub> nach der Iteration', (r.ib*1e6).toPrecision(6)+' µA',
     ist?'17,0 µA':'—'],
    ['β = I_C/I_B', r.beta.toPrecision(5), ist?'≈ 305':'—'],
    ['β<sub>eff</sub> (Webster)', r.beta_eff.toPrecision(6),'—'],
    ['V<sub>BE,eff</sub>', (r.veff*1e3).toPrecision(7)+' mV',
     ist?'≈ 659 mV (0,660 V − 1,03 mV)':'—'],
    ['Abfall I<sub>B</sub>·R<sub>B,int</sub>', ((vbe-r.veff)*1e3).toPrecision(4)+' mV',
     ist?'1,03 mV (Rechenbeispiel 6.3)':'—']]);
  tab($('#gp_fix'), ['k','V<sub>BE,eff</sub> / mV','I<sub>B</sub> / µA','Herkunft'],
    prot.map(p=>[p.k, (p.veff*1e3).toPrecision(9), (p.ib*1e6).toPrecision(9), p.quelle]));
  const ideal=P.IS*Math.exp(vbe/(P.NF*P.VT));
  tab($('#gp_erw'), ['Erweiterung','SPICE','was sie hier bewirkt'], [
    ['ideale Kennlinie (6.3)','IS, NF, BF', si(ideal,'A')+' — der Ausgangswert'],
    ['Early-Effekt (6.4)','VAF','Faktor 1 + V_CE/V_A = '+(1+vce/P.VA).toFixed(5)
      +' → '+(100*vce/P.VA).toFixed(2)+' % mehr I_C'],
    ['Basis-Early (6.5)','VAR','Faktor 1 + V_CE/V_AB = '+(1+vce/P.VAB).toFixed(5)
      +' → '+(100*vce/P.VAB).toFixed(2)+' % mehr I_B'],
    ['Hochinjektion (6.6)','IKF','β_eff/β_F = '+(r.beta_eff/P.BETA).toFixed(5)
      +' bei I_C/I_KF = '+(r.ic/P.IKF).toExponential(3)],
    ['innerer Basiswiderstand (6.7)','RBM','ΔV = '+((vbe-r.veff)*1e3).toFixed(4)
      +' mV → I_B um '+(100*(1-Math.exp(-(vbe-r.veff)/(P.NF*P.VT)))).toFixed(2)+' % kleiner']]);
  gp_zeichnen(P);
}
function gp_zeichnen(P){
  const b=Bild($('#gp_bild'));
  const spuren=STAND.tracer.Ic_Vce;
  let ymax=0;
  for(const s of spuren) for(const y of s.y) if(y>ymax) ymax=y;
  b.rahmen(0, 12, 0, ymax*1.25||1, 'V_CE / V', 'I_C / mA');
  const leg=[];
  spuren.forEach((s,i)=>{
    const f=FARB[i%FARB.length];
    b.punkte(s.x.map((x,k)=>[x, s.y[k]]), f, 2.2);
    // Zum gemessenen I_B die passende V_BE suchen.  Geloest wird mit SEINEM
    // Loeser aus bjt_hparam.py (Z. 47-61): ib_model mit der 40-schrittigen
    // Fixpunktiteration und solve_vbe_for_ib mit 50 Bisektionsschritten in
    // [0,2 V; 1,0 V] - nur mit den Parametern des Abschnitts 6.9.  Eine
    // kuerzere Fixpunktschleife laeuft bei grossem V_BE weg (die algebraische
    // Schleife aus Abschnitt 6.7), seine 40 Schritte tun das nicht.
    const PG={n:P.NF, Is:P.IS, Beta_F:P.BETA, VA:P.VA, IKF:P.IKF,
              RB:P.RBI, Vab:P.VAB, VT:P.VT};
    const ibz=s.wert*1e-6;
    const kur=[];
    for(let k=0;k<=200;k++){
      const vce=0.05+(12-0.05)*k/200;
      const vbe=hp_vbe_for_ib(ibz, vce, PG);
      kur.push([vce, hp_ic(vbe,vce,PG)*1e3]);
    }
    b.linie(kur, f, 1.8);
    leg.push(['I_B = '+s.wert+' µA', f]);
  });
  b.legende(leg);
}
$('#gp_start').addEventListener('click', gp_rechnen_ui);
ZEICHNER['gp']=()=>{ if(!$('#gp_tab').innerHTML) gp_rechnen_ui(); };

/* --------------------------------------------------- Reiter: Parameterextraktion */
function ex_zeigen(){
  const e=ex_ablesen();
  tab($('#ex_gummel'), ['V<sub>CE</sub> / V','Punkte im Fenster','n','I<sub>S,eff</sub> / A'],
    e.gummel.map(g=>[g.vce.toFixed(2), g.punkte, g.n.toFixed(4),
      g.is_eff.toExponential(3)]));
  tab($('#ex_early'), ['I<sub>B</sub> / µA','Punkte ab 1,5 V','V<sub>A</sub> / V'],
    e.early.map(g=>[g.ib.toFixed(0), g.punkte, g.VA.toFixed(1)]));
  tab($('#ex_beta'), ['V<sub>CE</sub> / V','Punkte','β aus der I_C-I_B-Steigung'],
    e.betas.map(g=>[g.vce.toFixed(1), g.punkte, g.beta.toFixed(0)]));
  tab($('#ex_erg'), ['Größe','Browser','bjt_extract.py','Abweichung'], [
    ['n', e.n.toFixed(4), L.extract.n.toFixed(4), abw(e.n, L.extract.n)],
    ['I<sub>S</sub>', e.Is.toExponential(4)+' A', L.extract.Is.toExponential(4)+' A',
     abw(e.Is, L.extract.Is)],
    ['V<sub>A</sub>', e.VA.toFixed(2)+' V', L.extract.VA.toFixed(2)+' V',
     abw(e.VA, L.extract.VA)],
    ['β<sub>F</sub> (Steigung)', e.beta_steig.toFixed(1), L.extract.beta_steigung.toFixed(1),
     abw(e.beta_steig, L.extract.beta_steigung)],
    ['h<sub>FE</sub>-Maximum über alle Daten', e.hfe_max.toFixed(1),
     L.extract.hfe_max.toFixed(1), abw(e.hfe_max, L.extract.hfe_max)],
    ['größter gemessener I<sub>C</sub>', (e.ic_max*1e3).toFixed(2)+' mA',
     (L.extract.ic_max*1e3).toFixed(2)+' mA', abw(e.ic_max, L.extract.ic_max)],
    ['I<sub>KF</sub>', '<span class="schlecht">nicht bestimmbar — nur untere Schranke ≫ '
      +(e.ic_max*1e3).toFixed(0)+' mA</span>',
     'nur untere Schranke', '—']]);
  tab($('#ex_saetze'), ['Programm','Verfahren','Parametersatz','wo er benutzt wird'], [
    ['<code>bjt_extract.py</code>','merkmalsweise Ablesung aus fünf Kennfeldern',
     'n, I<sub>S</sub>, V<sub>A</sub>, β<sub>F</sub> — I<sub>KF</sub>, V<sub>AB</sub>, R<sub>B</sub> nicht bestimmbar',
     'dieser Reiter'],
    ['<code>bjt_analyse.py</code>','dieselben Ablesungen, Vorgaben für das Unbestimmbare',
     'IKF = 1,0 A · V<sub>ab</sub> = 10<sup>6</sup> V · R<sub>B</sub> = 10 Ω',
     'Kontrollrechnung'],
    ['<code>bjt_fit.py</code>','globaler Ausgleich (eigener Nelder-Mead, sieben Parameter)',
     'Startsatz n = 1,004 · I<sub>S</sub> = 4,85·10<sup>−14</sup> A · β<sub>F</sub> = 272 · V<sub>A</sub> = 146 V',
     'mit Identifizierbarkeitstest (+20 % je Parameter)'],
    ['<code>bjt_gesamt.py</code>','Ausgleich über vier Parameter, Rest aus dem Datenblatt',
     'ISE = 3,534·10<sup>−15</sup> A · NE = 1,35 · IKF = 0,9 A · R<sub>B</sub> = 60 Ω (Datenblatt)',
     'Vergleich Modell ↔ Messung'],
    ['<code>bjt_hparam.py</code>, <code>bjt_verstaerker.py</code>','kein Fit — fester Satz',
     'n = 1,004 · I<sub>S</sub> = 4,726·10<sup>−14</sup> A · β<sub>F</sub> = 249,9 · V<sub>A</sub> = 146 V · IKF = 0,9 A · R<sub>B</sub> = 60 Ω',
     'Reiter „Kleinsignal“ und „Vierpol-Verstärker“'],
    ['<code>BUCH/kap08_rechnung.py</code>','gemessener BC547-Satz aus Kapitel 7',
     'n = 1,01 · I<sub>S</sub> = 5·10<sup>−14</sup> A · β<sub>F</sub> = 290 · VAF = 95 V · VAR = 190 V · IKF = 0,08 A · R<sub>B</sub> = 15 Ω',
     'Reiter „Arbeitspunkt Newton“ und „Extraktion BC547“'],
    ['<code>Transistor_21b.py</code>, die .asc-Karten','Demo-Satz',
     'I<sub>S</sub> = 10<sup>−13</sup> A · β<sub>F</sub> = 200 · n = 1 · VAF = 100 V',
     'Reiter „BJT und SPICE“ und „Simulation und SPICE“']]);
  // Gummel-Plot
  const b=Bild($('#ex_bild'));
  b.rahmen(0.35, 0.75, 1e-7, 1e-1, 'V_BE / V', 'I_C / A', false, true);
  const leg=[];
  STAND.tracer.Ic_Vbe.forEach((s,i)=>{
    const f=FARB[i%FARB.length];
    b.punkte(s.x.map((x,k)=>[x, Math.max(s.y[k]*1e-3,1e-12)]), f, 2.2);
    leg.push(['V_CE = '+s.wert+' V', f]);
  });
  for(const g of e.gummel){
    const pts=[];
    for(let k=0;k<=60;k++){ const v=0.4+0.3*k/60; pts.push([v, Math.exp(g.a+g.b*v)]); }
    b.linie(pts, '#22201c', 1.2, [5,4]);
  }
  leg.push(['abgelesene Gerade je Kurve','#22201c']);
  b.legende(leg);
}
$('#ex_start').addEventListener('click', ex_zeigen);
ZEICHNER['extrakt']=()=>{ if(!$('#ex_erg').innerHTML) ex_zeigen(); };

/* ---------------------------------------------------- Reiter: Arbeitspunkt Newton */
let NW=null;
function nw_rechnen(){
  K08S={VCC:+$('#nw_vcc').value, VBB:+$('#nw_vcc').value, RC:+$('#nw_rc').value};
  const RB=+$('#nw_rb').value*1e3;
  const r=k08_newton(RB, +$('#nw_vbe0').value);
  NW={RB:RB, r:r};
  tab($('#nw_tab'), ['k','V<sub>BE</sub> / V','V<sub>CE</sub> / V','f₁ / A','f₂ / A','‖F‖'],
    r.prot.map(p=>[p.k, p.VBE.toFixed(7), p.VCE.toFixed(6), p.f1.toExponential(3),
      p.f2.toExponential(3), p.norm.toExponential(3)]));
  const VBE=r.x[0], VCE=r.x[1];
  const IB=(K08S.VBB-VBE)/RB, IC=(K08S.VCC-VCE)/K08S.RC;
  const veff=VBE-IB*K08.RBI, be=k08_beta_eff(IC);
  $('#nw_zu').innerHTML = r.fertig
    ? ('‖F‖ &lt; 10<sup>−10</sup> nach <b>'+r.k+'</b> Schritten. Der erste Schritt schießt über '
       +'die e-Funktion hinaus (‖F‖ steigt von '+r.prot[0].norm.toExponential(3)+' auf '
       +r.prot[1].norm.toExponential(3)+'); danach fällt der Rest je Schritt um den Faktor '
       +(r.prot[10].norm/r.prot[9].norm).toFixed(4)+' ≈ 1/e — lineare Konvergenz —, '
       +'und erst die letzten vier Schritte sind quadratisch.')
    : '<span class="schlecht">Newton-Raphson hat in 100 Schritten nicht konvergiert.</span>';
  const ist = (K08S.VCC===25 && K08S.RC===100 && Math.abs(RB-L.kap08.RB)<1e-6);
  tab($('#nw_erg'), ['Größe','Browser','kap08_rechnung.py','Abweichung'], [
    ['R<sub>B</sub>', (RB/1e3).toPrecision(8)+' kΩ', ist?(L.kap08.RB/1e3).toPrecision(8)+' kΩ':'—',
     ist?abw(RB,L.kap08.RB):'—'],
    ['V<sub>BE</sub>', (VBE*1e3).toPrecision(8)+' mV', ist?(L.kap08.VBE*1e3).toPrecision(8)+' mV':'—',
     ist?abw(VBE,L.kap08.VBE):'—'],
    ['V<sub>BE,eff</sub>', (veff*1e3).toPrecision(8)+' mV',
     ist?(L.kap08.VBEeff*1e3).toPrecision(8)+' mV':'—', ist?abw(veff,L.kap08.VBEeff):'—'],
    ['V<sub>CE</sub>', VCE.toPrecision(8)+' V', ist?L.kap08.VCE.toPrecision(8)+' V':'—',
     ist?abw(VCE,L.kap08.VCE):'—'],
    ['V über R<sub>C</sub>', (K08S.VCC-VCE).toPrecision(8)+' V','—','—'],
    ['I<sub>B</sub>', (IB*1e6).toPrecision(8)+' µA', ist?(L.kap08.IB*1e6).toPrecision(8)+' µA':'—',
     ist?abw(IB,L.kap08.IB):'—'],
    ['I<sub>C</sub>', (IC*1e3).toPrecision(8)+' mA', ist?(L.kap08.IC*1e3).toPrecision(8)+' mA':'—',
     ist?abw(IC,L.kap08.IC):'—'],
    ['I<sub>E</sub> = I_B + I_C', ((IB+IC)*1e3).toPrecision(8)+' mA','—','—'],
    ['h<sub>FE</sub> = I_C/I_B', (IC/IB).toPrecision(7), ist?(L.kap08.IC/L.kap08.IB).toPrecision(7):'—',
     ist?abw(IC/IB, L.kap08.IC/L.kap08.IB):'—'],
    ['β<sub>eff</sub> (Webster)', be.toPrecision(7), ist?L.kap08.beta_eff.toPrecision(7):'—',
     ist?abw(be,L.kap08.beta_eff):'—'],
    ['I<sub>C</sub>/I<sub>KF</sub>', (IC/K08.IKF).toPrecision(4),
     ist?(L.kap08.IC/K08.IKF).toPrecision(4):'—','—'],
    ['P<sub>V</sub> = V_CE·I_C', si(VCE*IC,'W'),'—','—'],
    ['Newton-Schritte', String(r.k), ist?String(L.kap08.newton):'—','—']]);
  const h=k08_hparam(VBE, VCE, RB);
  tab($('#nw_h'), ['Größe','Wert','Bedeutung'], [
    ['S<sub>1</sub> = ∂I_C/∂V_BE', si(h.S1,'S'), 'Steilheit'],
    ['S<sub>2</sub> = ∂I_C/∂V_CE', si(h.S2,'S'), 'Early-Steigung'],
    ['S<sub>3</sub> = ∂I_B/∂V_BE', si(h.S3,'S'), 'Eingangsleitwert'],
    ['S<sub>4</sub> = ∂I_B/∂V_CE', si(h.S4,'S'), 'Rückwirkung'],
    ['<b>h<sub>11e</sub></b> = 1/S₃', '<b>'+si(h.h11,'Ω')+'</b>', 'Eingangswiderstand'],
    ['<b>h<sub>21e</sub></b> = S₁/S₃', '<b>'+h.h21.toPrecision(6)+'</b>', 'Stromverstärkung'],
    ['<b>h<sub>12e</sub></b> = −S₄/S₃', '<b>'+h.h12.toExponential(4)+'</b>', 'Spannungsrückwirkung'],
    ['<b>h<sub>22e</sub></b> = S₂ − S₁S₄/S₃', '<b>'+si(h.h22,'S')+'</b>',
     'Ausgangsleitwert (1/h₂₂ = '+si(1/h.h22,'Ω')+')'],
    ['D<sub>h</sub> = h₁₁h₂₂ − h₁₂h₂₁', h.Dh.toPrecision(6), 'Determinante der Hybridmatrix']]);
  nw_zeichnen(VBE, VCE, IC, RB, r.prot);
}
function nw_zeichnen(VBE, VCE, IC, RB, prot){
  const b=Bild($('#nw_bild'));
  const icmax=K08S.VCC/K08S.RC*1e3*1.1;
  b.rahmen(0, K08S.VCC, 0, icmax, 'V_CE / V', 'I_C / mA');
  const kur=[];
  for(let k=0;k<=400;k++){
    const v=0.05+(K08S.VCC-0.05)*k/400;
    const ibg=(K08S.VBB-VBE)/RB;
    const veffg=VBE-ibg*K08.RBI;
    kur.push([v, K08.IS*Math.exp(veffg/(K08.NF*K08.VT))*(1+v/K08.VAF)*1e3]);
  }
  b.linie(kur, FARB[0], 2.4);
  b.linie([[0,K08S.VCC/K08S.RC*1e3],[K08S.VCC,0]], FARB[1], 2.2);
  b.marke(VCE, IC*1e3, '#B3261E',
    'Arbeitspunkt: '+VCE.toFixed(3)+' V · '+(IC*1e3).toFixed(2)+' mA');
  b.legende([['Transistorkennlinie bei gefundenem V_BE', FARB[0]],
             ['Lastgerade I_C = (V_CC − V_CE)/R_C', FARB[1]]]);
  const k=Bild($('#nw_konv'));
  const gut=prot.map(p=>Math.max(p.norm,1e-13));
  let mx=0; for(const v of gut) if(v>mx) mx=v;
  k.rahmen(0, prot.length-1, 1e-12, mx*10, 'Newton-Iteration k', '‖F(x_k)‖', false, true);
  k.linie(prot.map((p,i)=>[i, gut[i]]), FARB[0], 2.2);
  k.punkte(prot.map((p,i)=>[i, gut[i]]), FARB[0], 3);
  k.linie([[0,1e-10],[prot.length-1,1e-10]], '#B3261E', 1.4, [6,4]);
  k.legende([['‖F‖ je Schritt', FARB[0]], ['Schranke 10⁻¹⁰','#B3261E']]);
}
function nw_bisektion(){
  K08S={VCC:+$('#nw_vcc').value, VBB:+$('#nw_vcc').value, RC:+$('#nw_rc').value};
  const bi=k08_bisektion();
  tab($('#nw_bitab'), ['Schritt','R<sub>B</sub> / kΩ','V<sub>CE</sub> / V',
                       '|V_CE − V_CC/2| / V'],
    bi.prot.map(p=>[p.k, (p.RB/1e3).toFixed(4), p.VCE.toFixed(5),
      p.fehler.toExponential(3)]));
  $('#nw_rb').value=(bi.RB/1e3);
  nw_rechnen();
}
$('#nw_start').addEventListener('click', nw_rechnen);
$('#nw_bi').addEventListener('click', nw_bisektion);
ZEICHNER['newton']=()=>{ if(!$('#nw_erg').innerHTML){ nw_rechnen(); nw_bisektion(); } };

/* ------------------------------------------------ Reiter: Simulation und SPICE */
function sp_zeigen(){
  const namen=['V<sub>BE</sub> / V','V<sub>CE</sub> / V','I<sub>B</sub> / mA','I<sub>C</sub> / mA'];
  const fakt=[1,1,1e3,1e3];
  for(const [id, RB, Fb, Fs, ref] of [
        ['#sp_einfach', 44453.0, sp_buch_einfach, sp_spice_einfach, L.spice.einfach],
        ['#sp_erweitert', 36796.0, sp_buch_erweitert, sp_spice_erweitert, L.spice.erweitert]]){
    const vb=sp_ap(Fb(RB), RB), vs=sp_ap(Fs(RB), RB);
    const reihen=[];
    for(let i=0;i<4;i++){
      const d=vs[i]-vb[i];
      reihen.push([namen[i], (fakt[i]*vb[i]).toPrecision(8),
        (fakt[i]*vs[i]).toPrecision(8),
        (d>=0?'+':'')+(fakt[i]*d).toPrecision(4),
        (100*d/vb[i]>=0?'+':'')+(100*d/vb[i]).toFixed(2)+' %',
        abw(vb[i], ref.buch[i])]);
    }
    tab($(id), ['Größe','Buchgleichungen','SPICE-Konvention','Differenz','relativ',
                'Abstand zu kap09_spice_abgleich.py'], reihen);
  }
  $('#sp_vt').innerHTML='Thermospannung: V<sub>T</sub> (Python, 300 K) = '
    +(1e3*VT_PY).toFixed(4)+' mV · V<sub>T</sub> (LTspice, 27 °C, exakte SI-Konstanten) = '
    +(1e3*VT_LT).toFixed(4)+' mV — ein Unterschied von '
    +(1e6*(VT_LT-VT_PY)).toFixed(2)+' µV. Er allein erklärt den Rest nicht; der Hauptteil '
    +'kommt aus der q<sub>b</sub>-Formulierung und daraus, dass LTspice den Early-Effekt '
    +'über V<sub>BC</sub> statt über V<sub>CE</sub> ansetzt.';
}
$('#sp_start').addEventListener('click', sp_zeigen);
ZEICHNER['sim']=()=>{ if(!$('#sp_einfach').innerHTML) sp_zeigen(); };

/* ---------------------------------------------------------- Reiter: Kleinsignal */
function kl_rechnen(){
  const IC=+$('#kl_ic').value*1e-3, VCE=+$('#kl_vce').value;
  const h=hp_rechnen(IC, VCE);
  const ist = (Math.abs(IC-5e-3)<1e-12 && VCE===5);
  tab($('#kl_ap'), ['Größe','Browser','bjt_hparam.py','Abweichung'], [
    ['V<sub>BE</sub>', (h.VBE*1e3).toPrecision(7)+' mV',
     ist?(L.hparam.VBE*1e3).toPrecision(7)+' mV':'—', ist?abw(h.VBE,L.hparam.VBE):'—'],
    ['I<sub>B</sub>', (h.IB*1e6).toPrecision(7)+' µA',
     ist?(L.hparam.IB*1e6).toPrecision(7)+' µA':'—', ist?abw(h.IB,L.hparam.IB):'—'],
    ['I<sub>C</sub>', (IC*1e3).toPrecision(7)+' mA','—','—'],
    ['h<sub>FE</sub> = I_C/I_B', (IC/h.IB).toPrecision(6),'—','—'],
    ['S₁ = ∂I_C/∂V_BE (g<sub>m</sub>)', si(h.gm,'S'),
     ist?si(L.hparam.gm,'S'):'—', ist?abw(h.gm,L.hparam.gm):'—'],
    ['S₂ = ∂I_C/∂V_CE', si(h.go,'S'),'—','—'],
    ['S₃ = ∂I_B/∂V_BE', si(h.gpi,'S'),'—','—'],
    ['S₄ = ∂I_B/∂V_CE', si(h.gmu,'S'),'—','—']]);
  tab($('#kl_h'), ['h-Parameter','Definition','Browser','bjt_hparam.py','Abweichung'], [
    ['h<sub>11e</sub>','dV_BE/dI_B bei V_CE = konst.', si(h.h11,'Ω'),
     ist?si(L.hparam.h11,'Ω'):'—', ist?abw(h.h11,L.hparam.h11):'—'],
    ['h<sub>12e</sub>','dV_BE/dV_CE bei I_B = konst.', h.h12.toExponential(4),
     ist?L.hparam.h12.toExponential(4):'—', ist?abw(h.h12,L.hparam.h12):'—'],
    ['h<sub>21e</sub>','dI_C/dI_B bei V_CE = konst.', h.h21.toPrecision(6),
     ist?L.hparam.h21.toPrecision(6):'—', ist?abw(h.h21,L.hparam.h21):'—'],
    ['h<sub>22e</sub>','dI_C/dV_CE bei I_B = konst.', si(h.h22,'S'),
     ist?si(L.hparam.h22,'S'):'—', ist?abw(h.h22,L.hparam.h22):'—'],
    ['1/h<sub>22e</sub>','Ausgangswiderstand', si(1/h.h22,'Ω'),
     ist?si(1/L.hparam.h22,'Ω'):'—','—'],
    ['D<sub>h</sub>','h₁₁h₂₂ − h₁₂h₂₁', h.Dh.toPrecision(6),'—','—']]);
  $('#kl_s11').textContent = si(h.h11,'Ω',4);
  $('#kl_s12').textContent = h.h12.toExponential(3);
  $('#kl_s21').textContent = h.h21.toPrecision(5);
  $('#kl_s22').textContent = si(1/h.h22,'Ω',4);
  kl_zeichnen(h);
}
function kl_zeichnen(h){
  const cv=$('#kl_bild'), g=cv.getContext('2d');
  g.clearRect(0,0,cv.width,cv.height);
  g.fillStyle='#fff'; g.fillRect(0,0,cv.width,cv.height);
  // vier kleine Kennfelder nebeneinander in zwei Reihen
  const teil=(x,y,w,hh)=>{
    const c=document.createElement('canvas'); c.width=w; c.height=hh;
    return {c:c, x:x, y:y};
  };
  const felder=[
    ['Eingangskennlinie I_B(V_BE)', 0, 0],
    ['Übertragungskennlinie I_C(I_B)', 1, 0],
    ['Ausgangskennlinie I_C(V_CE)', 0, 1],
    ['Rückwirkung V_BE(V_CE)', 1, 1]];
  const W=cv.width/2, He=cv.height/2;
  felder.forEach((f,i)=>{
    const t=teil(f[1]*W, f[2]*He, W, He);
    const b=Bild(t.c);
    if(i===0){
      const x=[], y=[];
      for(let k=0;k<=200;k++){ const v=h.VBE-0.06+0.12*k/200; x.push(v); y.push(hp_ib(v,h.VCE)*1e6); }
      b.rahmen(x[0], x[x.length-1], 0, Math.max.apply(null,y), 'V_BE / V','I_B / µA');
      b.linie(x.map((v,k)=>[v,y[k]]), FARB[0], 2.2);
      const s=h.gpi*1e6;
      b.linie([[h.VBE-0.02, (h.IB-0.02*h.gpi)*1e6],[h.VBE+0.02,(h.IB+0.02*h.gpi)*1e6]],
              '#B3261E', 1.8, [6,4]);
      b.marke(h.VBE, h.IB*1e6, '#B3261E', 'h₁₁e = '+si(h.h11,'Ω',4), -10, 18);
    } else if(i===1){
      const x=[], y=[];
      for(let k=0;k<=200;k++){
        const ib=Math.max(h.IB*0.2 + h.IB*1.6*k/200, 1e-12);
        const v=hp_vbe_for_ib(ib, h.VCE);
        x.push(ib*1e6); y.push(hp_ic(v,h.VCE)*1e3);
      }
      b.rahmen(x[0], x[x.length-1], 0, Math.max.apply(null,y), 'I_B / µA','I_C / mA');
      b.linie(x.map((v,k)=>[v,y[k]]), FARB[1], 2.2);
      b.marke(h.IB*1e6, h.IC*1e3, '#B3261E', 'h₂₁e = '+h.h21.toPrecision(5));
    } else if(i===2){
      const x=[], y=[];
      for(let k=0;k<=200;k++){ const v=0.2+11.8*k/200; x.push(v);
        y.push(hp_ic(hp_vbe_for_ib(h.IB, v), v)*1e3); }
      b.rahmen(0, 12, 0, Math.max.apply(null,y)*1.15, 'V_CE / V','I_C / mA');
      b.linie(x.map((v,k)=>[v,y[k]]), FARB[2], 2.2);
      b.linie([[h.VCE-3, (h.IC-3*h.h22)*1e3],[h.VCE+3, (h.IC+3*h.h22)*1e3]],
              '#B3261E', 1.8, [6,4]);
      b.marke(h.VCE, h.IC*1e3, '#B3261E', 'h₂₂e = '+si(h.h22,'S',4));
    } else {
      const x=[], y=[];
      for(let k=0;k<=200;k++){ const v=0.5+11.5*k/200; x.push(v);
        y.push(hp_vbe_for_ib(h.IB, v)*1e3); }
      const mn=Math.min.apply(null,y), mx=Math.max.apply(null,y);
      b.rahmen(0, 12, mn-0.02, mx+0.02, 'V_CE / V','V_BE / mV');
      b.linie(x.map((v,k)=>[v,y[k]]), FARB[4], 2.2);
      b.marke(h.VCE, hp_vbe_for_ib(h.IB,h.VCE)*1e3, '#B3261E',
              'h₁₂e = '+h.h12.toExponential(3));
    }
    g.drawImage(t.c, t.x, t.y);
  });
}
$('#kl_start').addEventListener('click', kl_rechnen);
ZEICHNER['klein']=()=>{ if(!$('#kl_h').innerHTML) kl_rechnen(); };

/* ------------------------------------------------- Reiter: Vierpol-Verstärker */
function vp_rechnen(){
  const rbv=$('#vp_rb').value.trim();
  const S={VCC:+$('#vp_vcc').value, VBB:+$('#vp_vcc').value,
           RC:+$('#vp_rc').value*1e3, RB: rbv==='' ? null : +rbv*1e3,
           RL:+$('#vp_rl').value*1e3, RI:+$('#vp_ri').value*1e3};
  const r=vp_kette(S);
  const ist = (S.VCC===15 && S.RC===1000 && rbv==='' && S.RL===10000 && S.RI===1000);
  $('#vp_rbinfo').textContent=r.info;
  tab($('#vp_ap'), ['Größe','Browser','bjt_verstaerker.py','Abweichung'], [
    ['R<sub>B</sub>', (r.RB/1e3).toPrecision(6)+' kΩ', ist?(L.verst.RB/1e3).toPrecision(6)+' kΩ':'—',
     ist?abw(r.RB,L.verst.RB):'—'],
    ['V<sub>BE</sub>', (r.VBE*1e3).toPrecision(7)+' mV', ist?(L.verst.VBE*1e3).toPrecision(7)+' mV':'—',
     ist?abw(r.VBE,L.verst.VBE):'—'],
    ['V<sub>CE</sub>', r.VCE.toPrecision(7)+' V', ist?L.verst.VCE.toPrecision(7)+' V':'—',
     ist?abw(r.VCE,L.verst.VCE):'—'],
    ['I<sub>B</sub>', (r.IB*1e6).toPrecision(7)+' µA', ist?(L.verst.IB*1e6).toPrecision(7)+' µA':'—',
     ist?abw(r.IB,L.verst.IB):'—'],
    ['I<sub>C</sub>', (r.IC*1e3).toPrecision(7)+' mA', ist?(L.verst.IC*1e3).toPrecision(7)+' mA':'—',
     ist?abw(r.IC,L.verst.IC):'—'],
    ['h<sub>FE</sub>', (r.IC/r.IB).toPrecision(5), ist?(L.verst.IC/L.verst.IB).toPrecision(5):'—','—'],
    ['Newton-Schritte', String(r.iter), ist?String(L.verst.iter):'—','—']]);
  tab($('#vp_h'), ['Größe','Browser','bjt_verstaerker.py','Abweichung'], [
    ['S₁ = ∂I_C/∂V_BE', si(r.S1,'S'), ist?si(L.verst.S1,'S'):'—', ist?abw(r.S1,L.verst.S1):'—'],
    ['S₂ = ∂I_C/∂V_CE', si(r.S2,'S'), ist?si(L.verst.S2,'S'):'—', ist?abw(r.S2,L.verst.S2):'—'],
    ['S₃ = ∂I_B/∂V_BE', si(r.S3,'S'), ist?si(L.verst.S3,'S'):'—', ist?abw(r.S3,L.verst.S3):'—'],
    ['S₄ = ∂I_B/∂V_CE', si(r.S4,'S'), ist?si(L.verst.S4,'S'):'—', ist?abw(r.S4,L.verst.S4):'—'],
    ['h<sub>11e</sub>', si(r.h11,'Ω'), ist?si(L.verst.h11,'Ω'):'—', ist?abw(r.h11,L.verst.h11):'—'],
    ['h<sub>12e</sub>', r.h12.toExponential(4), ist?L.verst.h12.toExponential(4):'—',
     ist?abw(r.h12,L.verst.h12):'—'],
    ['h<sub>21e</sub>', r.h21.toPrecision(6), ist?L.verst.h21.toPrecision(6):'—',
     ist?abw(r.h21,L.verst.h21):'—'],
    ['h<sub>22e</sub>', si(r.h22,'S'), ist?si(L.verst.h22,'S'):'—', ist?abw(r.h22,L.verst.h22):'—'],
    ['D<sub>h</sub>', r.Dh.toPrecision(6), ist?L.verst.Dh.toPrecision(6):'—',
     ist?abw(r.Dh,L.verst.Dh):'—']]);
  tab($('#vp_a'), ['Matrix','A₁₁','A₁₂','A₂₁','A₂₂'], [
    ['A<sub>T</sub> (Transistor, h → A)', r.A_T[0][0].toExponential(4),
     r.A_T[0][1].toExponential(4), r.A_T[1][0].toExponential(4), r.A_T[1][1].toExponential(4)],
    ['A<sub>Rb</sub> (Querwiderstand)','1','0',(1/r.RB).toExponential(4),'1'],
    ['A<sub>Rc</sub> (Querwiderstand)','1','0',(1/S.RC).toExponential(4),'1'],
    ['<b>A<sub>ges</sub></b>', '<b>'+r.A[0][0].toExponential(4)+'</b>',
     '<b>'+r.A[0][1].toExponential(4)+'</b>', '<b>'+r.A[1][0].toExponential(4)+'</b>',
     '<b>'+r.A[1][1].toExponential(4)+'</b>'],
    ['bjt_verstaerker.py', ist?L.verst.A[0][0].toExponential(4):'—',
     ist?L.verst.A[0][1].toExponential(4):'—', ist?L.verst.A[1][0].toExponential(4):'—',
     ist?L.verst.A[1][1].toExponential(4):'—']]);
  tab($('#vp_erg'), ['Kenngröße','Formel','Browser','bjt_verstaerker.py','Abweichung'], [
    ['r<sub>ein</sub>','(A₁₁R_L+A₁₂)/(A₂₁R_L+A₂₂)', si(r.r_ein,'Ω'),
     ist?si(L.verst.r_ein,'Ω'):'—', ist?abw(r.r_ein,L.verst.r_ein):'—'],
    ['r<sub>aus</sub>','(A₂₂R_i+A₁₂)/(A₂₁R_i+A₁₁)', si(r.r_aus,'Ω'),
     ist?si(L.verst.r_aus,'Ω'):'—', ist?abw(r.r_aus,L.verst.r_aus):'—'],
    ['A<sub>v</sub>','R_L/(A₁₁R_L+A₁₂)', r.A_v.toPrecision(6)+'  ('
      +(20*Math.log10(Math.abs(r.A_v))).toFixed(1)+' dB, invertierend)',
     ist?L.verst.A_v.toPrecision(6):'—', ist?abw(r.A_v,L.verst.A_v):'—'],
    ['A<sub>i</sub>','1/(A₂₁R_L+A₂₂)', r.A_i.toPrecision(6),
     ist?L.verst.A_i.toPrecision(6):'—', ist?abw(r.A_i,L.verst.A_i):'—'],
    ['A<sub>vs</sub>','A_v·r_ein/(r_ein+R_i)', r.A_vs.toPrecision(6)+'  ('
      +(20*Math.log10(Math.abs(r.A_vs))).toFixed(1)+' dB)',
     ist?L.verst.A_vs.toPrecision(6):'—', ist?abw(r.A_vs,L.verst.A_vs):'—']]);
  const b=Bild($('#vp_bild'));
  b.rahmen(30, 1e6, 1, 400, 'R_L / Ω','|A_v|', true, true);
  const kur=[];
  for(let e=0;e<=300;e++){
    const rl=Math.pow(10, Math.log10(30)+e*(Math.log10(1e6)-Math.log10(30))/300);
    kur.push([rl, Math.abs(rl/(r.A[0][0]*rl+r.A[0][1]))]);
  }
  b.linie(kur, FARB[0], 2.4);
  b.marke(S.RL, Math.abs(r.A_v), '#B3261E',
    'R_L = '+(S.RL/1e3).toFixed(0)+' k · |A_v| = '+Math.abs(r.A_v).toFixed(1));
  b.legende([['|A_v| aus der Gesamt-Kettenmatrix', FARB[0]]]);
}
$('#vp_start').addEventListener('click', vp_rechnen);
ZEICHNER['vierpol']=()=>{ if(!$('#vp_erg').innerHTML) vp_rechnen(); };

/* ------------------------------------------------ Reiter: Netzliste und Löser */
/* Die Voreinstellung ist dieselbe wie in netz_lauf.py — nur dann steht in der
   Spalte "sein Löser" eine Zahl, sonst ein Strich. */
const NZ0 = {vcc:12, rb:470e3, rc:1000, rl:10000, us:0.005};
const NZ  = {f:2000, ck:10e-6, ca:10e-6, dt:100e-9, perioden:12, modell:'BC337'};
const NZL = L.netz;

/* Zahl schreiben wie "%g" in netz_lauf.py, damit der Netzlistentext auf der
   Seite Zeichen fuer Zeichen derselbe ist wie der des Python-Laufs. */
function nz_g(x){
  const v=Number(x);
  if(v===0) return '0';
  const ex=Math.floor(Math.log10(Math.abs(v)));
  const kuerzen = t => t.includes('.') ? t.replace(/0+$/,'').replace(/\.$/,'') : t;
  if(ex < -4 || ex >= 6){
    const st=v.toExponential(5).split('e');
    let d=st[1].replace(/[+-]/,'');
    if(d.length<2) d='0'+d;
    return kuerzen(st[0])+'e'+(st[1][0]==='-'?'-':'+')+d;
  }
  return kuerzen(v.toPrecision(6));
}
function nz_stellwerte(){
  return {vcc:+$('#nz_vcc').value, rb:(+$('#nz_rb').value)*1e3,
          rc:+$('#nz_rc').value, rl:(+$('#nz_rl').value)*1e3,
          us:(+$('#nz_us').value)*1e-3};
}
function nz_ist0(S){
  return Math.abs(S.vcc-NZ0.vcc)<1e-9 && Math.abs(S.rb-NZ0.rb)<1e-6
      && Math.abs(S.rc-NZ0.rc)<1e-9 && Math.abs(S.rl-NZ0.rl)<1e-6
      && Math.abs(S.us-NZ0.us)<1e-12;
}
function nz_netz1(S){
  return '* Fall 1 — nur der Arbeitspunkt\n'
    + 'V1  vcc 0     dc '+nz_g(S.vcc)+'\n'
    + 'RB  vcc b     '+nz_g(S.rb)+'\n'
    + 'RC  vcc c     '+nz_g(S.rc)+'\n'
    + 'T1  c   b  0  '+NZ.modell+'\n';
}
function nz_netz2(S, uck, uca){
  return '* Fall 2 — die vollstaendige Verstaerkerstufe\n'
    + 'V1  vcc 0     dc '+nz_g(S.vcc)+'\n'
    + 'RB  vcc b     '+nz_g(S.rb)+'\n'
    + 'RC  vcc c     '+nz_g(S.rc)+'\n'
    + 'T1  c   b  0  '+NZ.modell+'\n'
    + 'Vs  s   0     sinus '+nz_g(S.us)+' '+nz_g(NZ.f)+'\n'
    + 'Ck  s   b     '+nz_g(NZ.ck*1e6)+'u  '+uck.toFixed(12)+'\n'
    + 'Ca  c   a     '+nz_g(NZ.ca*1e6)+'u  '+uca.toFixed(12)+'\n'
    + 'RL  a   0     '+nz_g(S.rl)+'\n';
}
/* Beschriftung aller Unbekannten: erst die Knotenpotentiale, dahinter die
   Zusatzunbekannten (Zweigstroeme der Quellen und Kondensatoren, innerer
   Basisknoten des Transistors). */
function nz_namen(sim){
  const n=new Array(sim.n_unbekannte).fill('?');
  sim.knoten.forEach((idx,name)=>{ if(idx!==0 && name!=='K0') n[idx]='u('+name+')'; });
  for(const b of sim.bauteile){
    if(b.j===null || b.j===undefined) continue;
    n[b.j] = (b instanceof SimTransistor) ? 'u('+b.name+".B')" : 'i('+b.name+')';
  }
  return n;
}
function nz_ap_zeilen(m, it, p, ist, py){
  const f = x => (x===null||x===undefined||!isFinite(x)) ? '—' : x.toPrecision(11);
  const z = (name, lesbar, wert, pyw) => [name, lesbar, f(wert),
      ist ? f(pyw) : '—', ist ? abw(wert, pyw) : '—'];
  return [
    z('U_BE',      si(m.u_be,'V'),     m.u_be,     py.u_be),
    z('U_BE,eff',  si(m.u_be_eff,'V'), m.u_be_eff, py.u_be_eff),
    z('U_CE',      si(m.u_ce,'V'),     m.u_ce,     py.u_ce),
    z('I_B',       si(m.i_b,'A'),      m.i_b,      py.i_b),
    z('I_C',       si(m.i_c,'A'),      m.i_c,      py.i_c),
    z('I_E',       si(m.i_e,'A'),      m.i_e,      py.i_e),
    z('beta',      m.beta.toFixed(3),  m.beta,     py.beta),
    z('beta_eff',  m.beta_eff.toFixed(3), m.beta_eff, py.beta_eff),
    z('P_V',       si(p,'W'),          p,          py.p),
    ['Newton-Durchgänge', String(it), String(it),
     ist ? String(py.newton) : '—',
     ist ? (it===py.newton ? '<span class="gut">0</span>'
                           : '<span class="schlecht">'+(it-py.newton)+'</span>') : '—'],
  ];
}

let NZ_STAND = null;

function nz_rechnen(volle){
  const S=nz_stellwerte();
  const ist=nz_ist0(S);
  $('#nz_vcc_w').textContent=S.vcc.toFixed(1);
  $('#nz_rb_w').textContent=(S.rb/1e3).toFixed(0);
  $('#nz_rc_w').textContent=S.rc.toFixed(0);
  $('#nz_rl_w').textContent=(S.rl/1e3).toFixed(0);
  $('#nz_us_w').textContent=(S.us*1e3).toFixed(1);
  $('#nz_n1').value=nz_netz1(S);
  $('#nz_stand').innerHTML = ist
    ? 'Die Schieber stehen auf der Voreinstellung — das ist genau die Netzliste, die '
      + '<code>netz_lauf.py</code> durch <code>simulator.py</code> schickt. Deshalb steht '
      + 'in den Tabellen die Spalte „sein Löser“ mit Zahlen.'
    : '<span class="warn">Die Schieber stehen nicht auf der Voreinstellung.</span> Für diese '
      + 'Netzliste liegt kein Python-Lauf vor; die Spalte „sein Löser“ bleibt leer. '
      + 'Der Knopf „Voreinstellung“ stellt sie zurück.';
  nz_fall1(S, ist, $('#nz_n1').value);
  if(volle!==false) nz_fall2(S, ist);
  nz_gegenprobe();
  if(volle!==false && !$('#nz_n3').value){
    $('#nz_n3').value=STAND.bruecke;
    nz_bruecke($('#nz_n3').value);
  }
}

function nz_fall1(S, ist, text){
  $('#nz_n1_fehler').innerHTML='';
  let sim, prot={schritte:[]}, it, m;
  try{
    sim=new SimSimulator(text);
    it=sim._newton(prot);
    m=sim.messwerte('T1');
  }catch(e){
    $('#nz_n1_fehler').innerHTML='<span class="schlecht">Diese Netzliste geht nicht: '
      +e.message+'</span>';
    return;
  }
  NZ_STAND={sim:sim, m:m, it:it};
  const py=NZL.f1;
  const P=m.u_ce*m.i_c + m.u_be*m.i_b;
  tab($('#nz_ap'), ['Größe','Wert','Seite (Grundeinheit)','sein Löser <code>simulator.py</code>',
                    'Abweichung'], nz_ap_zeilen(m, it, P, ist, py));
  const gueltig = m.u_ce>0.3;
  $('#nz_ap_zu').innerHTML =
    (gueltig ? '' : '<span class="schlecht">V<sub>CE</sub> liegt unter 0,3 V. Das Bauteil '
      + 'kennt keine Sättigung (Teil XII, 51.2) — die Zahlen oben liegen damit außerhalb '
      + 'des Gültigkeitsbereichs des Modells und sind keine Aussage über einen echten '
      + 'Transistor.</span><br>')
    + 'P<sub>V</sub> = V<sub>CE</sub>·I<sub>C</sub> + V<sub>BE</sub>·I<sub>B</sub>. '
    + 'Der Newton-Start ist <span class="f">u = 0</span> (kalter Start, wie in seinem '
    + 'Löser); die Dämpfung d<sub>max</sub> = 0,5 V braucht entsprechend viele Durchgänge, '
    + 'um die Betriebsspannung hochzulaufen.';

  /* Knotenmatrix und rechte Seite des LETZTEN Durchgangs */
  const nam=nz_namen(sim);
  const kopf=[''].concat(nam.slice(1).map(x=>'<span class="f">'+x+'</span>'))
                 .concat(['i']);
  const reihen=prot.Y_letzte.map((r,k)=>
    ['<span class="f">'+nam[k+1]+'</span>'].concat(
      r.map(v=>v===0 ? '·' : v.toExponential(3)))
     .concat([prot.i_letzte[k]===0 ? '·' : prot.i_letzte[k].toExponential(3)]));
  tab($('#nz_mat'), kopf, reihen);
  $('#nz_mat_zu').innerHTML='Die Matrix ist '+(sim.n_unbekannte-1)+'×'
    +(sim.n_unbekannte-1)+' groß: '+(sim.n_knoten-1)+' Knotenpotentiale (ohne den '
    +'Bezugsknoten) und '+(sim.n_unbekannte-sim.n_knoten)+' Zusatzunbekannte. Der innere '
    +'Basisknoten B′ steht in keiner Netzlistenzeile — das Bauteil legt ihn selbst an, '
    +'so wenig wie bei SPICE. Jeder Knoten trägt zusätzlich G<sub>min</sub> = 10<sup>−9</sup> S '
    +'gegen Masse. „·“ heißt: genau null.';

  /* Newton-Protokoll */
  const spa=nam.slice(1, Math.min(nam.length, 5));
  tab($('#nz_it'), ['k'].concat(spa.map(x=>'<span class="f">'+x+'</span>/V'))
                        .concat(['max|F| / A','max|Δ| / V']),
    prot.schritte.map(p=>[p.k].concat(
      spa.map((x,q)=>p.u[q+1].toPrecision(9)))
      .concat([p.fmax.toExponential(3), p.dmax.toExponential(3)])));
  $('#nz_it_zu').innerHTML=prot.schritte.length+' Durchgänge bis max|F| &lt; 10<sup>−12</sup> A '
    +'<i>und</i> max|Δ| &lt; 10<sup>−9</sup> V. Beide Bedingungen müssen erfüllt sein — '
    +'sein Löser bildet F <b>direkt aus den Zweigströmen</b>, nicht als Y·u − i, weil sich '
    +'dort große Tangententerme fast auslöschen (simulator.py, Z. 662–675).';

  /* Empfindlichkeit gegen die drei GESETZTEN Parameter */
  const M=SIM_MODELLE_BJT['BC337'];
  const proben=[
    ['I_KF', 'IKF', 4.05, 0.405, 'Faktor 10 kleiner', NZL.emp.ikf],
    ['R_B,int', 'RBI', 18.8, 0.0, 'ganz abgeschaltet', NZL.emp.rbi],
    ['V_AB', 'VAR', 1.39e3, 600.0, 'Faktor 2,3 kleiner', NZL.emp.var],
    ['V_AB', 'VAR', 1.39e3, 200.0, 'auf den Wert seiner LTspice-Karte', NZL.emp.var200],
  ];
  const ez=[];
  for(const [zn, feld, alt, neu, was, pyv] of proben){
    M[feld]=neu;
    let uce=NaN, ic=NaN, iw=0;
    try{
      const s2=new SimSimulator(text);
      iw=s2._newton();
      const m2=s2.messwerte('T1');
      uce=m2.u_ce; ic=m2.i_c;
    }catch(e){ }
    M[feld]=alt;
    const weg = (uce-m.u_ce);
    const abg = iw>=200;
    ez.push([zn, (feld==='RBI'? alt.toFixed(1)+' Ω' : (feld==='IKF'? alt+' A' : alt+' V')),
      (feld==='RBI'? neu.toFixed(1)+' Ω' : (feld==='IKF'? neu+' A' : neu+' V'))+' ('+was+')',
      abg ? '<span class="schlecht">kein Ergebnis</span>' : uce.toPrecision(9),
      ist ? (abg ? '<span class="schlecht">kein Ergebnis</span>' : pyv[0].toPrecision(9)) : '—',
      abg ? '<span class="schlecht">Newton bricht nach 200 Durchgängen ab</span>'
          : (weg*1e3).toFixed(2)+' mV ('+(100*weg/m.u_ce).toFixed(2)+' %)']);
  }
  tab($('#nz_emp'), ['Parameter','gesetzter Wert','verstellt auf','V<sub>CE</sub> / V (Seite)',
                     'V<sub>CE</sub> / V (sein Löser)','wie weit die Zahl wandert'], ez);
}

function nz_gegenprobe(){
  /* Wörtlich seine Netzliste bjt_fixedbias.netz aus DGL_Nichtlinear/Programme. */
  const t='V1  vcc 0     dc 25\nRB  vcc b     37275.390625\nRC  vcc c     100\n'
        + 'T1  c   b  0  BC547\n';
  const s=new SimSimulator(t);
  const it=s._newton();
  const m=s.messwerte('T1');
  const py=NZL.fb, k8=L.kap08;
  const f=x=>x.toPrecision(11);
  tab($('#nz_gegen'), ['Größe','Netzlisten-Löser auf dieser Seite',
                       'sein <code>simulator.py</code>','Abweichung',
                       'Reiter „Arbeitspunkt Newton“ (<code>kap08_rechnung.py</code>)',
                       'Abweichung'], [
    ['U_BE',     f(m.u_be),     f(py.u_be),     abw(m.u_be, py.u_be),
                 f(k8.VBE),     abw(m.u_be, k8.VBE)],
    ['U_BE,eff', f(m.u_be_eff), f(py.u_be_eff), abw(m.u_be_eff, py.u_be_eff),
                 f(k8.VBEeff), abw(m.u_be_eff, k8.VBEeff)],
    ['U_CE',     f(m.u_ce),     f(py.u_ce),     abw(m.u_ce, py.u_ce),
                 f(k8.VCE),     abw(m.u_ce, k8.VCE)],
    ['I_B',      f(m.i_b),      f(py.i_b),      abw(m.i_b, py.i_b),
                 f(k8.IB),      abw(m.i_b, k8.IB)],
    ['I_C',      f(m.i_c),      f(py.i_c),      abw(m.i_c, py.i_c),
                 f(k8.IC),      abw(m.i_c, k8.IC)],
    ['beta_eff', f(m.beta_eff), f(py.beta_eff), abw(m.beta_eff, py.beta_eff),
                 f(k8.beta_eff), abw(m.beta_eff, k8.beta_eff)],
    ['Newton-Durchgänge', String(it), String(py.newton),
     it===py.newton ? '<span class="gut">0</span>' : '<span class="schlecht">≠</span>',
     '49', 'anderes Verfahren'],
  ]);
  $('#nz_gegen_zu').innerHTML =
    '<b>Warum das hier steht.</b> Der Arbeitspunkt aus Fall 1 <b>kann</b> nicht mit dem '
    + 'aus dem Reiter „Arbeitspunkt Newton“ zusammenpassen: dort ist der Prüfling ein '
    + '<b>BC547</b> (β<sub>F</sub> = 290, I<sub>KF</sub> = 80 mA) an V<sub>CC</sub> = 25 V '
    + 'mit R<sub>C</sub> = 100 Ω und R<sub>B</sub> = 37,275 kΩ; hier ist es ein '
    + '<b>BC337</b> mit dem selbst ermittelten Satz an 12 V. Andere Beschaltung, anderer '
    + 'Prüfling, andere Zahlen — das wird nicht passend gemacht. Was sich vergleichen '
    + '<i>lässt</i>, steht in dieser Tabelle: <b>dieselbe Schaltung</b> (seine Netzliste '
    + '<code>bjt_fixedbias.netz</code>, wörtlich) einmal durch den Löser dieser Seite, '
    + 'einmal durch seinen Python-Löser und einmal durch das von Hand aufgestellte '
    + 'Gleichungssystem in <code>kap08_rechnung.py</code>. Der Rest gegen '
    + '<code>kap08_rechnung.py</code> ist <b>G<sub>min</sub></b> und sonst nichts — das ist '
    + 'in Teil XII, Abschnitt 50.1 einzeln nachgewiesen: dieselben Gleichungen von Hand, '
    + 'aber mit G<sub>min</sub> gerechnet, treffen den Netzlisten-Löser auf 1,2·10<sup>−13</sup> V.';
}

function nz_fall2(S, ist){
  if(!NZ_STAND) return;
  const m1=NZ_STAND.m;
  const n2=nz_netz2(S, -m1.u_be, m1.u_ce);
  $('#nz_n2').value=n2;
  $('#nz_n2_zu').innerHTML =
    'Die beiden letzten Zahlen sind die <b>Anfangswerte der Koppelkondensatoren</b>: die '
    + 'Spannungen, die im Arbeitspunkt über ihnen stehen (u<sub>Ck</sub> = −V<sub>BE</sub>, '
    + 'u<sub>Ca</sub> = +V<sub>CE</sub>). Damit startet der Lauf <i>im</i> Arbeitspunkt und '
    + 'nicht daneben — genau so steht es in seiner Netzliste '
    + '<code>bjt_emitter_zeit.netz</code>. Emitterwiderstand gibt es keinen: seine '
    + 'Schaltungen (Kapitel 8, <code>Transistor_20.py</code>, <code>Transistor_21b.py</code>, '
    + 'die LTspice-Dateien) sind alle <b>Fixed-Bias</b> ohne R<sub>E</sub>, und es wird hier '
    + 'nichts hinzuerfunden.';
  nz_schaltbild(S);

  /* Arbeitspunkt der Stufe: gleichstromseitig ist das Fall 1 (die
     Koppelkondensatoren tragen keinen Gleichstrom, R_L liegt hinter Ca). */
  const py=NZL.f1;
  tab($('#nz_ap2'), ['Größe','Wert','Seite (Grundeinheit)',
                     'sein Löser <code>simulator.py</code>','Abweichung'],
      nz_ap_zeilen(m1, NZ_STAND.it, m1.u_ce*m1.i_c+m1.u_be*m1.i_b, ist, py));

  /* --- Weg 1: kleinsignalig aus den vier Tangenten des Stempels ---------- */
  const M=SIM_MODELLE_BJT[NZ.modell];
  const g=M.tangenten(m1.u_be_eff, m1.u_ce);
  const g11=g[0], g12=g[1], g21=g[2], g22=g[3];
  const rac=1.0/(1.0/S.rc+1.0/S.rl);
  /* b' : (u1 − u_s)/R_BI + g21 u1 + g22 u2 = 0
     c  :  u2/(R_C‖R_L)  + g11 u1 + g12 u2 = 0     mit u_s = 1 V   */
  const a11=1.0/M.RBI+g21, a12=g22, a21=g11, a22=1.0/rac+g12;
  const det=a11*a22-a12*a21;
  const av_klein=( a11*0 - (1.0/M.RBI)*a21 )/det;
  const pf=NZL.f2;
  tab($('#nz_klein'), ['Größe','Formel','Seite','sein Löser <code>netz_lauf.py</code>',
                       'Abweichung'], [
    ['g11', 'dI_C/dv1 = I_C/(n·V_T)', g11.toPrecision(11),
     ist?pf.g11.toPrecision(11):'—', ist?abw(g11,pf.g11):'—'],
    ['g12', 'dI_C/dv2 = I_S·E/V_A', g12.toPrecision(11),
     ist?pf.g12.toPrecision(11):'—', ist?abw(g12,pf.g12):'—'],
    ['g21', 'dI_B/dv1 = A·fB·(q/(n·V_T)+dq/dv1)', g21.toPrecision(11),
     ist?pf.g21.toPrecision(11):'—', ist?abw(g21,pf.g21):'—'],
    ['g22', 'dI_B/dv2 = A·(q/V_AB+fB·dq/dv2)', g22.toPrecision(11),
     ist?pf.g22.toPrecision(11):'—', ist?abw(g22,pf.g22):'—'],
    ['R_ac', 'R_C ∥ R_L', rac.toPrecision(11),
     ist?pf.rac.toPrecision(11):'—', ist?abw(rac,pf.rac):'—'],
    ['A_v klein', 'u_c aus dem 2×2-System oben', av_klein.toPrecision(11),
     ist?pf.av_klein.toPrecision(11):'—', ist?abw(av_klein,pf.av_klein):'—'],
  ]);
  $('#nz_klein_zu').innerHTML =
    'Das sind <b>genau die vier Tangenten, die der Stempel in jedem Newton-Durchgang '
    + 'ohnehin bildet</b> (<code>GummelPoon.tangenten</code>, Z. 384–405), ausgewertet im '
    + 'Arbeitspunkt. Bei 2 kHz sind beide Koppelkondensatoren Kurzschlüsse '
    + '(1/(2πfC) = '+(1/(2*Math.PI*NZ.f*NZ.ck)).toFixed(2)+' Ω) und die Betriebsspannung '
    + 'ist Wechselstrommasse; damit bleiben zwei Knotengleichungen, die von Hand auflösbar '
    + 'sind. Zum Vergleich: die einfache Schulformel −g<sub>m</sub>·R<sub>ac</sub> mit '
    + 'g<sub>m</sub> = I<sub>C</sub>/(n·V<sub>T</sub>) gäbe '
    + (-m1.i_c/(M.NF*M.VT)*rac).toFixed(3)+'; der Unterschied von '
    + (100*Math.abs((-m1.i_c/(M.NF*M.VT)*rac-av_klein)/av_klein)).toFixed(2)
    + ' % ist der Spannungsteiler aus R<sub>B,int</sub> und dem Basiseingang plus der '
    + 'Early-Leitwert g12. <b>Diese Verstärkung hat keine obere Grenzfrequenz</b> — im '
    + 'Modell steht keine einzige Kapazität des Transistors, weil der Messplatz keine '
    + 'messen kann.';

  /* --- Weg 2: großsignalig, sein Löser rechnet den Zeitverlauf ---------- */
  let sim2, lauf;
  try{
    sim2=new SimSimulator(n2, {dt:NZ.dt});
    lauf=sim2.lauf(NZ.perioden/NZ.f, ['s','a','c']);
  }catch(e){
    $('#nz_av_zu').innerHTML='<span class="schlecht">Der Zeitverlauf geht nicht: '
      +e.message+'</span>';
    return;
  }
  const per=Math.round((1.0/NZ.f)/NZ.dt);
  const n=lauf.t.length;
  const ua=lauf.u.a.subarray(n-per), uc=lauf.u.c.subarray(n-per);
  let uamax=-Infinity, uamin=Infinity, ucmax=-Infinity, ucmin=Infinity, ucsum=0;
  for(let k=0;k<per;k++){
    if(ua[k]>uamax) uamax=ua[k];
    if(ua[k]<uamin) uamin=ua[k];
    if(uc[k]>ucmax) ucmax=uc[k];
    if(uc[k]<ucmin) ucmin=uc[k];
    ucsum+=uc[k];
  }
  const ucmit=ucsum/per;
  const oben=ucmax-ucmit, unten=ucmit-ucmin;
  const hub=uamax-uamin;
  const av_gross=hub/(2.0*S.us);
  const unsym=100.0*(oben-unten)/(0.5*(oben+unten));
  const unterschied=100.0*(av_gross-Math.abs(av_klein))/Math.abs(av_klein);
  let ucsum2=0; const uc2=lauf.u.c.subarray(n-2*per, n-per);
  for(let k=0;k<per;k++) ucsum2+=uc2[k];
  const drift=ucmit-ucsum2/per;

  const f12=x=>x.toPrecision(11);
  tab($('#nz_av'), ['Weg','wie gerechnet','Seite','sein Löser <code>netz_lauf.py</code>',
                    'Abweichung'], [
    ['A_v klein', 'aus den vier Tangenten des Stempels im Arbeitspunkt (Kleinsignal)',
     f12(av_klein), ist?f12(pf.av_klein):'—', ist?abw(av_klein,pf.av_klein):'—'],
    ['A_v gross', 'Ausgangshub am Eingangshub, letzte Periode des Euler-Laufs',
     f12(-av_gross), ist?f12(-pf.av_gross):'—', ist?abw(av_gross,pf.av_gross):'—'],
    ['Unterschied', '(|A_v gross| − |A_v klein|)/|A_v klein|',
     unterschied.toFixed(6)+' %', ist?pf.unterschied.toFixed(6)+' %':'—',
     ist?abw(unterschied,pf.unterschied):'—'],
    ['Hub oben', 'V_CE,max − Mittelwert der letzten Periode',
     f12(oben), ist?f12(pf.hub_oben):'—', ist?abw(oben,pf.hub_oben):'—'],
    ['Hub unten', 'Mittelwert − V_CE,min',
     f12(unten), ist?f12(pf.hub_unten):'—', ist?abw(unten,pf.hub_unten):'—'],
    ['Unsymmetrie', '(oben − unten) / Mittel beider',
     unsym.toFixed(6)+' %', ist?pf.unsym.toFixed(6)+' %':'—',
     ist?abw(unsym,pf.unsym):'—'],
    ['Verschiebung', 'Mittelwert V_CE mit Signal − Arbeitspunkt ohne Signal',
     (ucmit-m1.u_ce).toPrecision(8), ist?pf.uc_verschiebung.toPrecision(8):'—',
     ist?abw(ucmit-m1.u_ce,pf.uc_verschiebung):'—'],
    ['Drift', 'Mittelwert letzte Periode − vorletzte Periode',
     drift.toPrecision(8), ist?pf.periodendrift.toPrecision(8):'—',
     ist?abw(drift,pf.periodendrift):'—'],
    ['Newton im Mittel', 'Durchgänge je Zeitschritt',
     (sim2.it_summe/sim2.schritte).toFixed(5),
     ist?pf.newton_mittel.toFixed(5):'—',
     ist?abw(+(sim2.it_summe/sim2.schritte).toFixed(5), pf.newton_mittel):'—'],
  ]);
  $('#nz_av_zu').innerHTML =
    '<b>Das ist die Aussage dieses Reiters.</b> Die Kleinsignalverstärkung ist die, die man '
    + 'erwartet: '+av_klein.toFixed(3)+'. Die großsignalig gerechnete ist '
    + (-av_gross).toFixed(3)+' — Spitze zu Spitze also nur '+unterschied.toFixed(3)
    + ' % daneben. Wer daraus schlösse, die Stufe sei linear, läge falsch: der Ausgang '
    + 'schwingt <b>'+oben.toFixed(4)+' V nach oben und '+unten.toFixed(4)+' V nach '
    + 'unten</b>, das sind '+unsym.toFixed(2)+' % Unsymmetrie. <b>Eine lineare Stufe hätte '
    + 'hier exakt 0,00 %.</b> Die Spitze-zu-Spitze-Messung mittelt die Stauchung der einen '
    + 'gegen die Dehnung der anderen Halbwelle fast heraus — deshalb sieht sie harmlos aus. '
    + 'Getrennt gerechnet ist die obere Halbwelle '+(oben/S.us).toFixed(1)+'-fach, die '
    + 'untere '+(unten/S.us).toFixed(1)+'-fach verstärkt. Die Unsymmetrie ist die der '
    + 'e-Funktion und sonst nichts: das Modell hat keine Ladungsspeicherung, die verzerren '
    + 'könnte. Dass der Mittelwert von V<sub>CE</sub> um '
    + ((ucmit-m1.u_ce)*1e3).toFixed(1)+' mV vom Arbeitspunkt abweicht, ist die '
    + '<b>Selbstvorspannung des Koppelkondensators</b> (Teil XII, 50.4) und kein Wegdriften '
    + '— von Periode zu Periode bleiben davon noch '+(drift*1e6).toFixed(1)+' µV übrig. '
    + 'Der Lauf umfasst '+sim2.schritte+' Zeitschritte à '+(NZ.dt*1e9).toFixed(0)
    + ' ns, im Mittel '+(sim2.it_summe/sim2.schritte).toFixed(2)+' Newton-Durchgänge, '
    + 'größte '+sim2.it_groesste+', Abbrüche '+sim2.abbrueche+'.';

  /* --- Bilder ---------------------------------------------------------- */
  const t0=lauf.t[n-per];
  const P1=[], P2=[];
  const schritt=Math.max(1, Math.round(per/900));
  let lmin=Infinity, lmax=-Infinity;
  for(let k=0;k<per;k+=schritt){
    const tm=(lauf.t[n-per+k]-t0)*1e6;
    const lin=lauf.u.s[n-per+k]*av_klein;      /* was eine LINEARE Stufe machte */
    if(lin<lmin) lmin=lin;
    if(lin>lmax) lmax=lin;
    P1.push([tm, lin]);
    P2.push([tm, ua[k]]);
  }
  const b=Bild($('#nz_zeit'));
  const yu=Math.min(uamin, lmin), yo=Math.max(uamax, lmax);
  const rand=0.12*(yo-yu);
  b.rahmen(0, (per*NZ.dt)*1e6, yu-rand, yo+rand, 't / µs', 'u / V');
  b.linie([[0,0],[(per*NZ.dt)*1e6,0]], '#b0aaa0', 1, [4,4]);
  b.linie([[0,uamin],[(per*NZ.dt)*1e6,uamin]], '#B3261E', 1, [3,3]);
  b.linie([[0,uamax],[(per*NZ.dt)*1e6,uamax]], '#B3261E', 1, [3,3]);
  b.linie(P1, FARB[1], 2.2, [7,4]);
  b.linie(P2, FARB[0], 2.4);
  b.legende([['u_s · A_v (lineare Stufe)', FARB[1]],
             ['u_a großsignalig', FARB[0]],
             ['Umkehrpunkte', '#B3261E']]);
  $('#nz_zeit_zu').innerHTML='Letzte der '+NZ.perioden+' gerechneten Perioden. Damit beide '
    + 'Kurven vergleichbar sind, ist der Eingang mit der <b>Kleinsignalverstärkung</b> '
    + av_klein.toFixed(3)+' gestreckt: <b>eine lineare Stufe läge deckungsgleich darunter.</b> '
    + 'Der gerechnete Ausgang liegt oben '+Math.abs(lmax-uamax).toFixed(4)+' V darunter und '
    + 'unten '+Math.abs(lmin-uamin).toFixed(4)+' V darüber hinaus — die obere Halbwelle wird '
    + 'gestaucht, die untere gedehnt. Die beiden roten Linien sind die Umkehrpunkte des '
    + 'gerechneten Ausgangs; ihr Abstand zur Nulllinie ist oben und unten verschieden, und '
    + 'genau das ist die Verzerrung.';

  const b2=Bild($('#nz_kenn'));
  const uin=[], uout=[];
  let uasum=0;
  for(let k=0;k<per;k+=schritt){ uin.push(lauf.u.s[n-per+k]*1e3); uout.push(ua[k]); }
  for(let k=0;k<per;k++) uasum+=ua[k];
  const uamit=uasum/per;                 /* Mittelwert des Ausgangs = Anker */
  const xl=Math.min.apply(null,uin), xh=Math.max.apply(null,uin);
  const rd=0.06*(uamax-uamin);
  b2.rahmen(xl, xh, uamin-rd, uamax+rd, 'u_s / mV', 'u_a / V');
  b2.linie([[xl, uamit+av_klein*xl*1e-3],
            [xh, uamit+av_klein*xh*1e-3]], FARB[3], 1.8, [6,4]);
  b2.linie(uin.map((x,k)=>[x, uout[k]]), FARB[0], 2.6);
  b2.legende([['großsignalig gerechnet', FARB[0]],
              ['Kleinsignaltangente', FARB[3]]]);

  /* --- Was offen ist ---------------------------------------------------- */
  $('#nz_offen').innerHTML = [
    '<b>Die Temperatur ist nicht protokolliert.</b> Die Messdateien tragen keine, seine '
    + 'eigene Messvorschrift verlangt sie („Raumtemperatur notieren“). V<sub>T</sub> = '
    + '25,852 mV ist deshalb eine <b>Annahme</b> (T = 300 K), keine Messung — so steht es '
    + 'auch in seinem <code>bjt_extract.py</code>, Zeile 13.',
    '<b>Drei Parameter sind gesetzt, nicht gemessen</b> — I<sub>KF</sub>, R<sub>B,int</sub> '
    + 'und V<sub>AB</sub>. Wie weit die Zahlen dadurch wandern, steht in der Tabelle in '
    + 'Fall 1 und ist damit benannt, nicht verschwiegen.',
    '<b>Das Modell hat keine obere Grenzfrequenz.</b> Es enthält keine einzige '
    + 'Sperrschichtkapazität und keine Laufzeit, weil der Messplatz statisch misst. Die '
    + 'Verstärkung oben gilt quasistatisch; bei welcher Frequenz sie in Wirklichkeit '
    + 'abfällt, sagen diese Daten nicht.',
    '<b>Keine Sättigung, kein Inversbetrieb.</b> Wird der Arbeitspunkt so gewählt, dass '
    + 'V<sub>CE</sub> klein wird, rechnet das Bauteil weiter, aber außerhalb seines '
    + 'Gültigkeitsbereichs (Teil XII, 51.2).',
    '<b>Der Klirrfaktor ist nicht gerechnet.</b> Die Seite misst die Unsymmetrie der '
    + 'Halbwellen. Eine Zerlegung in Oberschwingungen wäre eine zusätzliche Rechnung, die '
    + 'in keinem seiner Programme steht, und wird deshalb hier nicht behauptet.',
    '<b>Der Lauf ist nicht bis zum Ende eingeschwungen.</b> Nach '+NZ.perioden
    + ' Perioden wandert der Mittelwert von V<sub>CE</sub> von Periode zu Periode noch um '
    + (drift*1e6).toFixed(1)+' µV. Die Zeitkonstante des Koppelkondensators am Ausgang '
    + '(C<sub>a</sub>·R<sub>L</sub> = '+(NZ.ca*S.rl*1e3).toFixed(0)+' ms) ist viel länger '
    + 'als der gerechnete Ausschnitt; der Endzustand ist also gerechnet, aber nicht '
    + 'abgewartet.',
    '<b>Elf von 20 000 Zeitschritten der Brücke erreichen die Newton-Grenze</b> '
    + 'max_it = 200. Sein Löser zählt sie mit, die Seite zählt dieselbe Zahl, und die '
    + 'Kennzahlen stimmen trotzdem. <b>Woran es liegt, ist nicht geklärt</b> — die Abbrüche '
    + 'liegen verstreut über den Lauf, nicht nur am kalten Start.',
    '<b>Die mittlere Zahl der Newton-Durchgänge der Brücke weicht um rund 10<sup>−4</sup> '
    + 'ab</b> (Seite gegen seinen Python-Lauf, sechs Durchgänge von 74 000). Die Kennzahlen '
    + 'hängen nicht daran, die Ursache ist aber nicht belegt.',
  ].map(x=>'<li>'+x+'</li>').join('');
}

/* --- Fall 3: SEINE B4-Bruecke, woertlich aus bruecke.netz ----------------
   Dieselbe Klasse SimSimulator, derselbe Quelltext — nur eine andere
   Netzliste.  Vier Dioden statt eines Transistors, sonst nichts geaendert. */
const NZB = {dt:10e-6, ende:0.2, f:50, ri:1.0, rl:100.0, modell:'1N4148'};

function nz_bruecke(text){
  $('#nz_n3_fehler').innerHTML='';
  let sim, lauf;
  try{
    sim=new SimSimulator(text, {dt:NZB.dt});
    lauf=sim.lauf(NZB.ende, ['K1','K3','K4','K5','K2']);
  }catch(e){
    $('#nz_n3_fehler').innerHTML='<span class="schlecht">Diese Netzliste geht nicht: '
      +e.message+'</span>';
    return;
  }
  const ist = text.trim()===String(STAND.bruecke).trim();
  const n=lauf.t.length, per=Math.round((1/NZB.f)/NZB.dt);
  const K1=lauf.u.K1, K3=lauf.u.K3, K4=lauf.u.K4, K5=lauf.u.K5;
  const D=SIM_MODELLE[NZB.modell];
  let ucmax=-Infinity, ucmin=Infinity, ucsum=0, id1=-Infinity, iq=0;
  for(let k=n-per;k<n;k++){
    const u=K4[k];
    if(u>ucmax) ucmax=u;
    if(u<ucmin) ucmin=u;
    ucsum+=u;
    const i1=D.strom(K1[k]-K3[k]);
    if(i1>id1) id1=i1;
    const a=Math.abs((K5[k]-K1[k])/NZB.ri);
    if(a>iq) iq=a;
  }
  const ucmit=ucsum/per;
  const brumm=ucmax-ucmin;
  const pb=L.netz.br, pr=L.netz.bericht;
  const f11=x=>x.toPrecision(11);
  const sp=(name, wert, py, ber, einheit, stellen)=>[
    name, si(wert, einheit, 7), f11(wert),
    ist?f11(py):'—', ist?abw(wert,py):'—',
    ber===null?'—':ber.toFixed(stellen), ber===null?'—':abw(+wert.toFixed(stellen), ber)];
  tab($('#nz_br'),
    ['Größe','Wert','Seite (Grundeinheit)','sein <code>simulator.py</code>','Abweichung',
     'sein Bericht <code>bericht_bruecke_rc.txt</code>','Abweichung'], [
    sp('u_C Mittelwert', ucmit, pb.uc_mittel, pr.uc_mittel, 'V', 4),
    sp('u_C größte',     ucmax, pb.uc_max,    pr.uc_max,    'V', 4),
    sp('u_C kleinste',   ucmin, pb.uc_min,    pr.uc_min,    'V', 4),
    sp('Brummspannung',  brumm, pb.brumm,     pr.brumm,     'V', 4),
    ['Brummspannung / u_C', (100*brumm/ucmit).toFixed(4)+' %',
     (100*brumm/ucmit).toPrecision(11), ist?pb.brumm_proz.toPrecision(11):'—',
     ist?abw(100*brumm/ucmit, pb.brumm_proz):'—', pr.brumm_proz.toFixed(2)+' %',
     abw(+(100*brumm/ucmit).toFixed(2), pr.brumm_proz)],
    sp('Laststrom Mittelwert', ucmit/NZB.rl, pb.il_mittel, pr.il_mittel, 'A', 7),
    sp('Diodenstrom D1 Spitze', id1, pb.id1_spitze, pr.id1_spitze, 'A', 7),
    sp('Quellstrom Spitze', iq, pb.iq_spitze, pr.iq_spitze, 'A', 7),
    sp('Verlust bis zum Kondensator', 30.0-ucmax, pb.verlust, pr.verlust, 'V', 4),
    ['Zeitschritte', String(sim.schritte), String(sim.schritte),
     ist?String(pb.schritte):'—', ist?(sim.schritte===pb.schritte?'<span class="gut">0</span>':'<span class="schlecht">≠</span>'):'—',
     '—','—'],
    ['Newton im Mittel', (sim.it_summe/sim.schritte).toFixed(4),
     (sim.it_summe/sim.schritte).toFixed(4), ist?pb.newton_mittel.toFixed(4):'—',
     ist?abw(+(sim.it_summe/sim.schritte).toFixed(4), pb.newton_mittel):'—',
     pr.newton_mittel.toFixed(2), '<span class="warn">anderes Programm</span>'],
    ['Newton größte / Abbrüche', sim.it_groesste+' / '+sim.abbrueche,
     String(sim.it_groesste), ist?String(pb.newton_groesste):'—',
     ist?(sim.it_groesste===pb.newton_groesste?'<span class="gut">0</span>':'<span class="schlecht">≠</span>'):'—',
     pr.newton_groesste.toFixed(0), '<span class="warn">anderes Programm</span>'],
  ]);
  $('#nz_br_zu').innerHTML =
    'Ausgewertet wird die <b>letzte Periode</b> (20 ms von 200 ms), genau wie in seinem '
    + 'Bericht. Die beiden rechten Spalten sind ein <b>zweiter, unabhängiger Weg</b>: '
    + '<code>bericht_bruecke_rc.txt</code> stammt nicht vom Netzlisten-Löser, sondern aus '
    + 'seinem fest verdrahteten Programm <code>Bruecke_RC_Last_Knotenpotential.py</code>, '
    + 'das dieselbe Methode mit Handauflösung statt Gauß rechnet. Es druckt auf vier '
    + 'Nachkommastellen; verglichen wird deshalb auf dieser Stelle. '
    + '<b>Die Newton-Zahlen der beiden Programme sind nicht dieselben</b> und sollen es auch '
    + 'nicht sein: sein Netzlisten-Löser setzt G<sub>min</sub> auch an die Zusatzknoten und '
    + 'prüft zusätzlich die Schrittweite, die Handauflösung tut beides nicht. '
    + '<b>' + sim.abbrueche + ' der ' + sim.schritte + ' Zeitschritte erreichen die Grenze '
    + 'max_it = 200</b> — sein Löser zählt sie selbst mit (Feld <code>abbrueche</code>), und '
    + 'die Seite zählt dieselbe Zahl. Sie liegen verstreut im Lauf; woran es liegt, ist '
    + 'nicht geklärt und steht unten unter „Was offen ist". Am Ergebnis ändert es nichts: '
    + 'die Kennzahlen treffen seinen Bericht auf allen vier gedruckten Nachkommastellen. '
    + '<b>Die mittlere Zahl der Newton-Durchgänge weicht als einzige Größe ab</b> — Seite '
    + (sim.it_summe/sim.schritte).toFixed(4)+', sein Löser '+pb.newton_mittel.toFixed(4)
    + ', das sind '+Math.abs(sim.it_summe-pb.newton_mittel*pb.schritte).toFixed(0)
    + ' Durchgänge von '+sim.it_summe+'. Die Zustände beider Läufe unterscheiden sich nach '
    + '20 000 Schritten um rund 10<sup>−11</sup> V, und die Abbruchbedingung prüft |Δ| gegen '
    + '10<sup>−9</sup> V; ein Rest dieser Größe kann an der Schranke über einen Durchgang '
    + 'mehr oder weniger entscheiden. <b>Nachgewiesen ist das nicht</b>, deshalb steht es '
    + 'unten unter „Was offen ist". Die Kennzahlen selbst hängen nicht daran: sie stimmen '
    + 'auf elf Stellen.';

  /* ---- Zeitverlauf ueber den ganzen Lauf --------------------------------- */
  {
    const b=Bild($('#nz_br_zeit'));
    const s1=Math.max(1, Math.round(n/1400));
    const Q=[], P=[], C=[];
    for(let k=0;k<n;k+=s1){
      const tm=lauf.t[k]*1e3;
      Q.push([tm, K5[k]-lauf.u.K2[k]]);      /* Quellspannung u_q(t) */
      P.push([tm, K3[k]]);                   /* Brueckenausgang P    */
      C.push([tm, K4[k]]);                   /* Kondensator          */
    }
    b.rahmen(0, NZB.ende*1e3, -32, 34, 't / ms', 'u / V');
    b.linie(Q, '#b0aaa0', 1.4);
    b.linie(P, FARB[1], 1.6);
    b.linie(C, FARB[0], 2.6);
    b.legende([['Quelle u_q', '#b0aaa0'],
               ['Brückenausgang P', FARB[1]],
               ['Kondensator u_C', FARB[0]]]);
    $('#nz_br_zeit_zu').innerHTML =
      'Die Quelle schwingt mit ±30 V, der Brückenausgang zeigt die gleichgerichteten '
      + 'Halbwellen (100 Hz aus 50 Hz), und der Kondensator lädt sich über die ersten '
      + 'Perioden auf seinen Mittelwert von '+ucmit.toFixed(4)+' V. Der Abstand '
      + 'zum Scheitelwert von 30 V ist '+(30-ucmax).toFixed(4)+' V: zwei Diodenflussspannungen, '
      + 'der Innenwiderstand und der Vorwiderstand R1.';
  }

  /* ---- Letzte Periode: Welligkeit und Stromspitzen, GETRENNT ------------
     Beides in ein Bild zu legen geht nicht: 20 V gegen 677 mA sind zwei
     Groessenordnungen, und die Welligkeit von 1,19 V waere dann eine Linie. */
  {
    const b=Bild($('#nz_br_welle'));
    const t0=lauf.t[n-per];
    const C=[];
    for(let k=n-per;k<n;k++) C.push([(lauf.t[k]-t0)*1e3, K4[k]]);
    const rd=0.25*brumm;
    b.rahmen(0, (per*NZB.dt)*1e3, ucmin-rd, ucmax+rd, 't / ms  (letzte Periode)', 'u_C / V');
    b.linie([[0,ucmax],[(per*NZB.dt)*1e3,ucmax]], '#B3261E', 1.2, [4,3]);
    b.linie([[0,ucmin],[(per*NZB.dt)*1e3,ucmin]], '#B3261E', 1.2, [4,3]);
    b.linie([[0,ucmit],[(per*NZB.dt)*1e3,ucmit]], '#b0aaa0', 1.2, [2,3]);
    b.linie(C, FARB[0], 2.8);
    b.legende([['u_C', FARB[0]], ['größte / kleinste', '#B3261E'], ['Mittelwert', '#b0aaa0']]);
    $('#nz_br_welle_zu').innerHTML =
      '<b>Zwei</b> Ladestöße je Netzperiode — daher 100 Hz Brummfrequenz aus 50 Hz Netz. '
      + 'Zwischen den Stößen entlädt der Kondensator sich über die Last, und das ist die '
      + 'fallende Flanke. Brummspannung '+brumm.toFixed(4)+' V von '+ucmit.toFixed(4)
      + ' V Mittelwert, also '+(100*brumm/ucmit).toFixed(2)+' %. Die Achse ist gedehnt: '
      + 'sie umfasst nur '+(ucmax-ucmin+2*rd).toFixed(3)+' V.';
  }
  {
    const b=Bild($('#nz_br_strom'));
    const t0=lauf.t[n-per];
    const I1=[], I2=[], IL=[];
    for(let k=n-per;k<n;k++){
      const tm=(lauf.t[k]-t0)*1e3;
      I1.push([tm, D.strom(K1[k]-K3[k])*1e3]);
      I2.push([tm, D.strom(lauf.u.K2[k]-K3[k])*1e3]);
      IL.push([tm, K4[k]/NZB.rl*1e3]);
    }
    b.rahmen(0, (per*NZB.dt)*1e3, -0.04*id1*1e3, 1.10*id1*1e3,
             't / ms  (letzte Periode)', 'i / mA');
    b.linie(IL, '#b0aaa0', 2.0);
    b.linie(I1, FARB[1], 2.2);
    b.linie(I2, FARB[3], 2.2, [6,4]);
    b.legende([['i_D1', FARB[1]], ['i_D2', FARB[3]], ['Laststrom i_RL', '#b0aaa0']]);
    $('#nz_br_strom_zu').innerHTML =
      'Die Dioden leiten nur in den kurzen Augenblicken, in denen die Quelle über der '
      + 'Kondensatorspannung steht — D1 in der einen Halbwelle, D2 in der anderen. Deshalb '
      + 'ist der Spitzenstrom mit '+(id1*1e3).toFixed(2)+' mA rund '
      + (id1/(ucmit/NZB.rl)).toFixed(1)+'-mal so groß wie der mittlere Laststrom von '
      + (ucmit/NZB.rl*1e3).toFixed(2)+' mA (graue Linie). Genau diese Stromspitzen sind der '
      + 'Grund, warum ein Gleichrichter Dioden und Trafo stärker belastet, als die mittlere '
      + 'Leistung vermuten ließe.';
  }
}

function nz_schaltbild(S){
  const e=$('#nz_bild_sch');
  if(!e) return;
  const T=(x,y,t,k)=>'<text x="'+x+'" y="'+y+'"'+(k?' class="'+k+'"':'')+'>'+t+'</text>';
  const LN=(x1,y1,x2,y2)=>'<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'"/>';
  const RE=(x,y,w,h)=>'<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'"/>';
  const PU=(x,y)=>'<circle cx="'+x+'" cy="'+y+'" r="3.2" style="fill:#22201c"/>';
  const GND=(x,y)=>LN(x,y,x,y+14)+LN(x-13,y+14,x+13,y+14)+LN(x-8,y+19,x+8,y+19)
                  +LN(x-3,y+24,x+3,y+24);
  const KAP=(x,y)=>LN(x-9,y-14,x-9,y+14)+LN(x+9,y-14,x+9,y+14);
  let s='';
  /* Betriebsspannungsschiene */
  s+=LN(140,40,352,40);
  s+=T(60,45,'+V_CC');
  s+=T(60,62,S.vcc.toFixed(1)+' V','wert');
  s+=LN(110,40,140,40);
  s+=PU(140,40)+PU(330,40);
  /* R_B */
  s+=LN(140,40,140,80)+RE(126,80,28,64)+LN(140,144,140,200);
  s+=T(160,105,'R_B')+T(160,122,(S.rb/1e3).toFixed(0)+' kΩ','wert');
  /* R_C */
  s+=LN(330,40,330,80)+RE(316,80,28,64)+LN(330,144,330,196);
  s+=T(350,105,'R_C')+T(350,122,S.rc.toFixed(0)+' Ω','wert');
  /* Basisknoten und Transistor */
  s+=PU(140,200)+LN(140,200,268,200);
  s+='<circle cx="300" cy="200" r="38"/>';
  s+=LN(282,176,282,224);
  s+=LN(268,200,282,200);
  s+=LN(282,186,318,166)+LN(318,166,318,196);
  s+=LN(282,214,318,234)+LN(318,234,318,300);
  s+='<path d="M 305 222 L 318 234 L 302 232 Z" style="fill:#22201c"/>';
  s+=T(250,180,'B','kl')+T(340,160,'C','kl')+T(326,250,'E','kl');
  s+=T(352,222,'T1 · '+NZ.modell,'wert');
  s+=GND(318,300);
  /* Kollektorknoten und Auskopplung */
  s+=PU(330,196)+LN(318,196,330,196);
  s+=LN(330,196,430,196)+KAP(439,196)+LN(448,196,560,196);
  s+=T(424,176,'C_a')+T(424,232,(NZ.ca*1e6).toFixed(0)+' µF','wert');
  /* R_L */
  s+=PU(560,196)+LN(560,196,560,230)+RE(546,230,28,64)+LN(560,294,560,300);
  s+=T(580,258,'R_L')+T(580,275,(S.rl/1e3).toFixed(0)+' kΩ','wert');
  s+=GND(560,300);
  s+=LN(560,196,630,196)+PU(630,196)+T(596,180,'u_aus','wert');
  /* Signalquelle und Ck */
  s+=LN(60,200,90,200)+KAP(99,200)+LN(108,200,140,200);
  s+=T(84,168,'C_k')+T(84,184,(NZ.ck*1e6).toFixed(0)+' µF','wert');
  s+='<circle cx="60" cy="230" r="22"/>';
  s+=LN(60,200,60,208)+LN(60,252,60,300);
  s+='<path d="M 48 230 q 6 -11 12 0 q 6 11 12 0" />';
  s+=T(14,236,'V_s','wert');
  s+=T(10,290,(S.us*1e3).toFixed(1)+' mV','wert');
  s+=T(10,306,(NZ.f/1e3).toFixed(0)+' kHz','wert');
  s+=GND(60,300);
  e.innerHTML=s;
}

(function(){
  const schieber=['#nz_vcc','#nz_rb','#nz_rc','#nz_rl','#nz_us'];
  for(const id of schieber){
    $(id).addEventListener('input', ()=>nz_rechnen(false));
    $(id).addEventListener('change', ()=>nz_rechnen(true));
  }
  $('#nz_start').addEventListener('click', ()=>nz_rechnen(true));
  $('#nz_n3_start').addEventListener('click', ()=>nz_bruecke($('#nz_n3').value));
  $('#nz_n1_start').addEventListener('click', ()=>{
    const S=nz_stellwerte();
    nz_fall1(S, false, $('#nz_n1').value);
  });
  $('#nz_zurueck').addEventListener('click', ()=>{
    $('#nz_vcc').value=NZ0.vcc; $('#nz_rb').value=NZ0.rb/1e3;
    $('#nz_rc').value=NZ0.rc;   $('#nz_rl').value=NZ0.rl/1e3;
    $('#nz_us').value=NZ0.us*1e3;
    nz_rechnen(true);
  });
})();
ZEICHNER['netz']=()=>{ if(!$('#nz_ap').innerHTML) nz_rechnen(true); };

/* ------------------------------------------------------------ erster Aufbau */
window.MESSWERTE_GERECHNET = false;
(function(){
  for(const k of Object.keys(ZEICHNER)){
    try{ ZEICHNER[k](); }catch(e){ console.error('Reiter '+k+':', e); }
  }
  window.MESSWERTE_GERECHNET = true;
})();
"""


if __name__ == "__main__":
    raise SystemExit(main())
