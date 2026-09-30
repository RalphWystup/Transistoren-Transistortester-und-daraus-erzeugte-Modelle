// Prüfung der Seite „Transistoren, der Transistortester und die daraus erzeugten Modelle"
// im echten Browser (Playwright, Chromium).
//
// Der Maßstab ist NICHT eine eigene Nachrechnung, sondern der LAUF SEINER
// PYTHON-PROGRAMME.  Die Prüfung startet sie selbst, liest ihre Konsolenausgabe
// und hält die Zahlen der Seite daneben.
//
//  K1  Seite lädt, baut auf, keine Konsolenfehler
//  K2  fünfzehn Reiter, je Teilmanuskript einer, jeder trägt seinen Text vollständig
//  K3  Arbeitspunkt gegen den Lauf von BUCH/kap08_rechnung.py
//  K4  Newton-Protokoll und Bisektion: Schrittzahlen und Schranke
//  K5  h-Parameter gegen den Lauf von bjt_hparam.py
//  K6  Vierpol-Kette gegen den Lauf von bjt_verstaerker.py
//  K7  Arbeitspunkt von Hand gegen den Lauf von Transistor_20.py
//  K8  Fixed-Bias gegen den Lauf von Transistor_21b.py
//  K9  Buch gegen SPICE gegen den Lauf von BUCH/kap09_spice_abgleich.py
//  K10 Leuchtdiode gegen den Lauf von BUCH/kap08_led_quellen.py
//  K11 Gummel-Poon gegen den Testlauf in Abschnitt 6.9 seines Manuskripts
//  K12 Parameterextraktion gegen den Lauf von bjt_extract.py
//  K13 Kleinsignal-Ersatzschaltbild: h-Vierpol mit seinen Formelzeichen, kein π-Modell
//  K14 SPICE-Parametersatz vollständig, Unbestimmbares ausdrücklich benannt
//  K15 Netzliste und Löser: alle drei Netzlisten gegen den Lauf von netz_lauf.py,
//      das SEINEN Löser DGL_Nichtlinear/Programme/simulator.py aufruft —
//      Arbeitspunkt, Verstärkerstufe und seine B4-Brücke mit vier Dioden
//  K16 das Gerät im Bild: Foto, Übersichtsskizze, beide Schaltplanblätter —
//      jede Bilddatei nur EINMAL in der Seite
//  K17 Veröffentlichungsvorgaben: kein Pfad, kein Netzname, kein Firmenname,
//      keine Befundliste, Kopfzeile mit Fassung, Datum und Namensnennung
//  K18 jeder Reiter als Bildschirmfoto abgelegt (zum Ansehen)
//
// Ergebnis nach pruefe_seite.json, Bildschirmfotos in den Kritzelordner.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
const require = createRequire(import.meta.url);
// Playwright wird dort gesucht, wo es installiert ist; der Ort steht in der
// Umgebungsvariablen PLAYWRIGHT, sonst wird die übliche Auflösung benutzt.
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');

// Keine festen Rechnerpfade: alles wird aus dem Ort dieser Datei erschlossen.
// Sie läuft damit im Arbeitsbereich ebenso wie im ausgelieferten Repositorium,
// wo seine Programme in ../pc und ../rechnung liegen und die Messdaten in
// ../messungen.
const H = path.dirname(new URL(import.meta.url).pathname) + '/';
const imRepo = fs.existsSync(H + '../pc');
const prog = n => {
  for (const k of imRepo ? ['../pc/', '../rechnung/', '../seite/', './']
                         : ['../../', '../../BUCH/',
                            '../../DGL_Nichtlinear/Programme/', './']) {
    if (fs.existsSync(H + k + n)) return H + k + n;
  }
  throw new Error('Programm nicht gefunden: ' + n);
};
const mess = n => (imRepo ? H + '../messungen/' : H + '../../') + n;
const V = fs.readFileSync(H + 'VERSION', 'utf8').trim();
const S = (process.env.KRITZEL || (H + 'pruefung/')).replace(/\/?$/, '/');
fs.mkdirSync(S, { recursive: true });
fs.mkdirSync(S + 'schuss', { recursive: true });

let fehler = 0; const BEF = [];
const sage = (gut, t, zahl) => {
  if (!gut) fehler++;
  BEF.push({ gut, text: t, zahl: zahl === undefined ? null : zahl });
  console.log((gut ? '  ok   ' : '  FEHL ') + t);
};
const rel = (a, b) => (b === 0 ? Math.abs(a) : Math.abs((a - b) / b));
// Nachkommastellen, mit denen eine Zahl dasteht
const stellen = x => {
  const s = String(x);
  const pt = s.indexOf('.');
  return pt < 0 ? 0 : s.length - pt - 1;
};
// einen gelesenen Wert umskalieren (kOhm -> Ohm): Schranke waechst mit
const skal = (p, f) => p === null ? null
  : { v: p.v * f, roh: p.roh, dez: p.dez - Math.round(Math.log10(f)) };
// Seine Programme drucken gerundet.  Die Schranke ist deshalb eine halbe
// Einheit der letzten gedruckten Stelle — mehr kann die Konsolenausgabe nicht
// hergeben, und weniger zu fordern wäre eine Scheingenauigkeit.
const nahe = (name, a, p) => {
  if (p === null || p === undefined || !isFinite(p.v)) {
    sage(false, `${name}: Wert aus der Programmausgabe nicht gelesen`);
    return;
  }
  // Auch die Seite schreibt gerundet.  Massgebend ist die groebere der beiden
  // Darstellungen, sonst prueft man gegen eine Scheingenauigkeit.
  const dezS = stellen(a);
  const s = 0.5 * Math.pow(10, -Math.min(p.dez, dezS));
  const d = Math.abs(a - p.v);
  sage(isFinite(a) && d <= s * (1 + 1e-9),
    `${name}: Seite ${a} · Python ${p.roh} · Abstand ${d.toExponential(2)} ` +
    `(Schranke ${s.toExponential(2)} = halbe letzte gedruckte Stelle)`, d);
};
// Zahl aus einer Tabellenzelle: "752.16552 mV" -> 752.16552
const zahl = t => {
  if (t === null || t === undefined) return NaN;
  const m = String(t).replace(/\s/g, ' ').match(/-?\d+(?:[.,]\d+)?(?:e[+-]?\d+)?/i);
  return m ? parseFloat(m[0].replace(',', '.')) : NaN;
};

/* ------------------------------------------------- seine Programme laufen lassen */
const LAUF = S + 'lauf/';
fs.mkdirSync(LAUF + 'bilder', { recursive: true });
for (const f of ['Ic_Vbe.txt', 'Ic_Vce.txt', 'Ic_Ib.txt', 'hFE_Ic.txt', 'hFE_Vce.txt'])
  fs.copyFileSync(mess(f), LAUF + f);
const PROG = {
  kap08: prog('kap08_rechnung.py'),
  hparam: prog('bjt_hparam.py'),
  verst: prog('bjt_verstaerker.py'),
  t20: prog('Transistor_20.py'),
  t21: prog('Transistor_21b.py'),
  spice: prog('kap09_spice_abgleich.py'),
  led: prog('kap08_led_quellen.py'),
  extract: prog('bjt_extract.py'),
  // SEIN Netzlisten-Loeser, angestossen durch unser netz_lauf.py.  Der Loeser
  // selbst (simulator.py, bruecke_kern.py) geht unveraendert mit.
  netz: prog('netz_lauf.py'),
};
// Der Loeser, sein Unterbau und SEINE Netzliste der Bruecke — netz_lauf.py
// sucht sie im eigenen Ordner.
for (const n of ['simulator.py', 'bruecke_kern.py', 'bruecke.netz'])
  fs.copyFileSync(prog(n), LAUF + n);
const AUSGABE = {};
console.log('\nSeine Programme laufen lassen:');
for (const [k, p] of Object.entries(PROG)) {
  fs.copyFileSync(p, LAUF + path.basename(p));
  try {
    AUSGABE[k] = execFileSync('python3', [path.basename(p)],
      { cwd: LAUF, encoding: 'utf8', env: { ...process.env, MPLBACKEND: 'Agg' },
        timeout: 300000, stdio: ['ignore', 'pipe', 'pipe'] });
    console.log('  gelaufen: ' + path.basename(p));
  } catch (e) {
    AUSGABE[k] = (e.stdout || '') + '';
    console.log('  ABBRUCH:  ' + path.basename(p) + ' — ' + String(e.message).slice(0, 120));
  }
  fs.writeFileSync(S + 'ausgabe_' + k + '.txt', AUSGABE[k]);
}
// Zahl hinter einem Muster in der Konsolenausgabe
const aus = (k, re) => {
  const m = AUSGABE[k].match(re);
  if (!m) return null;
  const roh = m[1];
  const pt = roh.indexOf('.');
  return { v: parseFloat(roh), roh: roh, dez: pt < 0 ? 0 : roh.length - pt - 1 };
};

/* ----------------------------------------------------------------- Browser */
const browser = await chromium.launch();
const seite = await browser.newPage({ viewport: { width: 1500, height: 1100 } });
const konsole = [];
seite.on('console', m => { if (m.type() === 'error') konsole.push(m.text()); });
seite.on('pageerror', e => konsole.push('PAGEERROR: ' + e.message));

// Die Seite liegt im Arbeitsbereich neben dem Prüfer, im ausgelieferten
// Repositorium eine Ebene darüber.
const datei = [H + `Transistortechnik_${V}.html`, H + `../Transistortechnik_${V}.html`]
  .find(x => fs.existsSync(x));
if (!datei) throw new Error(`Transistortechnik_${V}.html nicht gefunden`);
await seite.goto('file://' + datei);
let aufgebaut = true;
try { await seite.waitForFunction('window.MESSWERTE_GERECHNET===true', { timeout: 120000 }); }
catch (e) { aufgebaut = false; }

console.log('\nK1 — Seite lädt und baut auf');
sage(aufgebaut, 'alle Reiter ohne Ausnahme aufgebaut');
sage(konsole.length === 0, `Konsolenfehler: ${konsole.length} (Schranke 0)`, konsole.length);
konsole.slice(0, 6).forEach(t => console.log('        ' + t.slice(0, 160)));

console.log('\nK2 — die Reiter folgen seinen Teilmanuskripten');
const knoepfe = await seite.$$eval('#schiene button', n => n.map(x => x.dataset.ziel));
sage(knoepfe.length === 16,
     `Reiter: ${knoepfe.length} (Soll 16 = Start + 14 Teilmanuskripte + 1 eigener)`,
     knoepfe.length);
sage(knoepfe.includes('netz'), 'der eigene Reiter „Netzliste und Löser“ ist vorhanden');
const abschnitte = await seite.$$eval('main section', n => n.map(x => x.id));
sage(abschnitte.length === 16, `Abschnitte: ${abschnitte.length} (Soll 16)`, abschnitte.length);
// Vollstaendigkeit: die Seite muss je Reiter mindestens 90 % der Woerter
// zeigen, die im Teilmanuskript stehen (Formelzeichen und Bildunterschriften
// zaehlen im Satz anders, deshalb nicht 100 %).
const soll = JSON.parse(fs.readFileSync(H + 'manuskript_woerter.json', 'utf8'));
let schlechteste = 1, gesamt = 0;
for (const [kurz, s] of Object.entries(soll)) {
  const w = await seite.$eval(`#${kurz} .doku`, n => {
    const k = n.cloneNode(true);
    k.querySelectorAll('.fb,.f,pre,figcaption').forEach(x => x.remove());
    return k.innerText.trim().split(/\s+/).filter(Boolean).length;
  });
  gesamt += w;
  if (s.woerter === 0) {
    // Teilmanuskripte, die nur aus Quelltext bestehen (der ESP32-Code), haben
    // keinen Fliesstext; gemessen werden dann die Zeilen des Listings.
    const z = await seite.$eval(`#${kurz} .doku pre`,
      n => n.innerText.split('\n').length);
    sage(z > 250, `${s.reiter}: Quelltext mit ${z} Zeilen vollständig gezeigt (Schranke 250)`, z);
    continue;
  }
  // Vollstaendigkeit wortweise: jedes Wort ab sieben Buchstaben, das im
  // Teilmanuskript steht, muss auf der Seite wiederzufinden sein.  Die reine
  // Wortzahl taugt dafuer nicht, weil der Formelsatz anders zerlegt als die
  // Quelle — dieselbe Aussage, andere Zaehlung.
  const roh = (await seite.$eval(`#${kurz} .doku`, n => n.innerText)).toLowerCase();
  const fehlend = s.pruefwoerter.filter(x => !roh.includes(x));
  const q = 1 - fehlend.length / Math.max(1, s.pruefwoerter.length);
  if (q < schlechteste) schlechteste = q;
  sage(fehlend.length === 0,
    `${s.reiter}: ${s.pruefwoerter.length - fehlend.length} von ${s.pruefwoerter.length} ` +
    `Stichwörtern wiedergefunden (${(100 * q).toFixed(2)} %, Schranke 100 %)` +
    (fehlend.length ? ' — fehlt: ' + fehlend.slice(0, 8).join(', ') : ''),
    fehlend.length);
}
sage(gesamt > 24000, `Fließtext aller Teilmanuskripte auf der Seite, Wortzahl: ${gesamt}`, gesamt);
const kein_gesamt = !(await seite.evaluate(
  () => /Gesamtmanuskript/i.test(document.body.innerText)));
sage(kein_gesamt, 'kein Verweis auf ein Gesamtmanuskript');

/* ---- Hilfsmittel: eine Zelle aus einer Tabelle nach ihrer Zeilenbeschriftung */
// Die Beschriftung steht mit Tiefstellungen in der Zelle ("R<sub>B</sub>" wird
// zu "RB"); verglichen wird deshalb normalisiert: nur Buchstaben und Ziffern.
const norm = s => String(s).replace(/[^\p{L}\p{N}]/gu, '').toLowerCase();
const zelle = (tid, zeile, spalte) => seite.evaluate(([tid, zeile, spalte]) => {
  const nn = s => String(s).replace(/[^\p{L}\p{N}]/gu, '').toLowerCase();
  const t = document.querySelector(tid);
  if (!t) return null;
  for (const tr of t.querySelectorAll('tbody tr')) {
    const td = tr.querySelectorAll('td');
    if (td.length > spalte && nn(td[0].innerText) === nn(zeile))
      return td[spalte].innerText.replace(/\s+/g, ' ').trim();
  }
  return null;
}, [tid, zeile, spalte]);

console.log('\nK3 — Arbeitspunkt gegen den Lauf von BUCH/kap08_rechnung.py');
await seite.click('#schiene button[data-ziel="newton"]');
await seite.waitForTimeout(400);
const p_rb   = aus('kap08', /R_B\s+=\s+([\d.]+)\s+kOhm/);
const p_vbe  = aus('kap08', /V_BE\s+=\s+([\d.]+)\s+mV/);
const p_veff = aus('kap08', /V_BE,eff\s+=\s+([\d.]+)\s+mV/);
const p_vce  = aus('kap08', /V_CE\s+=\s+([\d.]+)\s+V/);
const p_ib   = aus('kap08', /I_B\s+=\s+([\d.]+)\s+uA/);
const p_ic   = aus('kap08', /I_C\s+=\s+([\d.]+)\s+mA/);
const p_be   = aus('kap08', /beta_eff\s+=\s+([\d.]+)/);
// Die Konsolenausgabe rundet auf die gedruckte Stelle; die Schranke folgt ihr.
await nahe('R_B',        zahl(await zelle('#nw_erg', 'R_B', 1)),        p_rb);
await nahe('V_BE',       zahl(await zelle('#nw_erg', 'V_BE', 1)),       p_vbe);
await nahe('V_BE,eff',   zahl(await zelle('#nw_erg', 'V_BE,eff', 1)),   p_veff);
await nahe('V_CE',       zahl(await zelle('#nw_erg', 'V_CE', 1)),       p_vce);
await nahe('I_B',        zahl(await zelle('#nw_erg', 'I_B', 1)),        p_ib);
await nahe('I_C',        zahl(await zelle('#nw_erg', 'I_C', 1)),        p_ic);
await nahe('β_eff',      zahl(await zelle('#nw_erg', 'β_eff (Webster)', 1)), p_be);
// und gegen den vollen Wert, der in der Seite mitgeliefert ist
const abwSp = await seite.$$eval('#nw_erg tbody tr td:nth-child(4)',
  n => n.map(x => x.innerText.trim()).filter(t => t !== '—'));
const schlimmst = Math.max(...abwSp.map(t => t === '0' ? 0 : parseFloat(t)));
sage(schlimmst <= 1e-12,
  `Abweichung Seite ↔ mitgeliefertem Programmwert höchstens ${schlimmst.toExponential(1)} ` +
  `(Schranke 1e-12)`, schlimmst);

console.log('\nK4 — Newton-Protokoll und Bisektion');
const nSchritte = zahl(await zelle('#nw_erg', 'Newton-Schritte', 1));
sage(nSchritte === 49, `Newton-Schritte bis ‖F‖ < 10⁻¹⁰: ${nSchritte} (Soll 49)`, nSchritte);
const letzteNorm = await seite.$eval('#nw_tab tbody tr:last-child td:last-child',
  n => parseFloat(n.innerText));
sage(letzteNorm < 1e-10, `‖F‖ am Ende ${letzteNorm.toExponential(2)} (Schranke 1e-10)`, letzteNorm);
const nBi = await seite.$$eval('#nw_bitab tbody tr', n => n.length);
sage(nBi === 10, `Bisektionsschritte: ${nBi} (Soll 10)`, nBi);

console.log('\nK5 — h-Parameter gegen den Lauf von bjt_hparam.py');
await seite.click('#schiene button[data-ziel="klein"]');
await seite.waitForTimeout(400);
const h_vbe = aus('hparam', /VBE=([\d.]+)\s*mV/);
const h_ib  = aus('hparam', /IB=([\d.]+)\s*uA/);
const h11p  = aus('hparam', /h11e\s*=\s*([\d.]+)\s*Ohm/);
const h21p  = aus('hparam', /h21e\s*=\s*([\d.]+)/);
const h22p  = aus('hparam', /h22e\s*=\s*([\d.]+)\s*uS/);
const h12p  = aus('hparam', /h12e\s*=\s*(-?[\d.e+-]+)/);
await nahe('V_BE',  zahl(await zelle('#kl_ap', 'V_BE', 1)), h_vbe);
await nahe('I_B',   zahl(await zelle('#kl_ap', 'I_B', 1)),  h_ib);
await nahe('h11e',  zahl(await zelle('#kl_h', 'h11e', 2)) * 1000, h11p);
await nahe('h21e',  zahl(await zelle('#kl_h', 'h21e', 2)), h21p);
await nahe('h22e',  zahl(await zelle('#kl_h', 'h22e', 2)), h22p);
await nahe('h12e',  zahl(await zelle('#kl_h', 'h12e', 2)), h12p);

console.log('\nK6 — Vierpol-Kette gegen den Lauf von bjt_verstaerker.py');
await seite.click('#schiene button[data-ziel="vierpol"]');
await seite.waitForTimeout(500);
const v_rb  = aus('verst', /Rb=([\d.]+)\s*k/);
const v_vbe = aus('verst', /VBE=\s*([\d.]+)\s*mV/);
const v_vce = aus('verst', /VCE=\s*([\d.]+)\s*V/);
const v_ib  = aus('verst', /IB=\s*([\d.]+)\s*uA/);
const v_ic  = aus('verst', /IC=\s*([\d.]+)\s*mA/);
const v_h11 = aus('verst', /h11e\s*=\s*([\d.]+)\s*Ohm/);
const v_h21 = aus('verst', /h21e\s*=\s*([\d.]+)/);
const v_h22 = aus('verst', /h22e\s*=\s*([\d.]+)\s*uS/);
const v_re  = aus('verst', /r_ein\s*=.*?=\s*([\d.]+)\s*kOhm/);
const v_ra  = aus('verst', /r_aus\s*=.*?=\s*([\d.]+)\s*kOhm/);
const v_av  = aus('verst', /A_v\s*=.*?=\s*(-?[\d.]+)\s/);
const v_ai  = aus('verst', /A_i\s*=.*?=\s*(-?[\d.]+)\s/);
const v_avs = aus('verst', /A_vs\s*=.*?=\s*(-?[\d.]+)\s/);
await nahe('R_B',   zahl(await zelle('#vp_ap', 'R_B', 1)),   v_rb);
await nahe('V_BE',  zahl(await zelle('#vp_ap', 'V_BE', 1)),  v_vbe);
await nahe('V_CE',  zahl(await zelle('#vp_ap', 'V_CE', 1)),  v_vce);
await nahe('I_B',   zahl(await zelle('#vp_ap', 'I_B', 1)),   v_ib);
await nahe('I_C',   zahl(await zelle('#vp_ap', 'I_C', 1)),   v_ic);
await nahe('h11e',  zahl(await zelle('#vp_h', 'h11e', 1)),   v_h11);
await nahe('h21e',  zahl(await zelle('#vp_h', 'h21e', 1)),   v_h21);
await nahe('h22e',  zahl(await zelle('#vp_h', 'h22e', 1)),   v_h22);
await nahe('r_ein', zahl(await zelle('#vp_erg', 'r_ein', 2)), skal(v_re, 1000));
await nahe('r_aus', zahl(await zelle('#vp_erg', 'r_aus', 2)), skal(v_ra, 1000));
await nahe('A_v',   zahl(await zelle('#vp_erg', 'A_v', 2)),   v_av);
await nahe('A_i',   zahl(await zelle('#vp_erg', 'A_i', 2)),   v_ai);
await nahe('A_vs',  zahl(await zelle('#vp_erg', 'A_vs', 2)),  v_avs);

console.log('\nK7 — Arbeitspunkt von Hand gegen den Lauf von Transistor_20.py');
await seite.click('#schiene button[data-ziel="t20"]');
await seite.waitForTimeout(400);
const t20_rb  = aus('t20', /Optimaler R_B:\s*([\d.]+)\s*Ohm/);
const t20_vbe = aus('t20', /V_BE\s*=\s*([\d.]+)\s*V/);
const t20_vce = aus('t20', /V_CE\s*=\s*([\d.]+)\s*V/);
const t20_ib  = aus('t20', /Basisstrom I_B\s*=\s*([\d.]+)\s*mA/);
await nahe('R_B',  zahl(await zelle('#t2_erg', 'R_B', 1)),  t20_rb);
await nahe('V_BE', zahl(await zelle('#t2_erg', 'V_BE', 1)), t20_vbe);
await nahe('V_CE', zahl(await zelle('#t2_erg', 'V_CE', 1)), t20_vce);
await nahe('I_B',  zahl(await zelle('#t2_erg', 'I_B', 1)),  t20_ib);
const t20_abbr = (AUSGABE.t20.match(/Newton-Konvergenzproblem/g) || []).length;
const s_abbr = zahl(await zelle('#t2_erg', 'davon abgebrochen', 1));
sage(s_abbr === t20_abbr,
  `abgebrochene Newton-Läufe: Seite ${s_abbr} · Python ${t20_abbr}`, s_abbr);

console.log('\nK8 — Fixed-Bias gegen den Lauf von Transistor_21b.py');
await seite.click('#schiene button[data-ziel="bjtspice"]');
await seite.waitForTimeout(400);
// Nur der Endergebnis-Block zaehlt; davor stehen die Bisektionsversuche.
AUSGABE.t21end = AUSGABE.t21.split('Endergebnis')[1] || '';
const t21_rb  = aus('t21end', /R_B\s*=\s*([\d.]+)\s*Ω/);
const t21_vbe = aus('t21end', /V_BE\s*=\s*([\d.]+)\s*V/);
const t21_vce = aus('t21end', /V_CE\s*=\s*([\d.]+)\s*V/);
const t21_ib  = aus('t21end', /I_B\s*=\s*([\d.]+)\s*mA/);
const t21_ic  = aus('t21end', /I_C\s*=\s*([\d.]+)\s*mA/);
await nahe('R_B',  zahl(await zelle('#bs_erg', 'R_B', 1)),  t21_rb);
await nahe('V_BE', zahl(await zelle('#bs_erg', 'V_BE', 1)), t21_vbe);
await nahe('V_CE', zahl(await zelle('#bs_erg', 'V_CE', 1)), t21_vce);
await nahe('I_B',  zahl(await zelle('#bs_erg', 'I_B', 1)),  t21_ib);
await nahe('I_C',  zahl(await zelle('#bs_erg', 'I_C', 1)),  t21_ic);
sage(t21_rb !== null && Math.abs(t21_rb.v - 44453) < 1,
  `zwei unabhängige Wege: R_B = ${t21_rb ? t21_rb.roh : '?'} Ω gegen R2 = 44453 Ω ` +
  `im LTspice-Schaltplan Eigen_RW_1d.asc`, t21_rb ? t21_rb.v : null);

console.log('\nK9 — Buch gegen SPICE, gegen den Lauf von BUCH/kap09_spice_abgleich.py');
await seite.click('#schiene button[data-ziel="sim"]');
await seite.waitForTimeout(400);
{
    const mask = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const dez = s => { const k = s.indexOf('.'); return k < 0 ? 0 : s.length - k - 1; };
  const lies = (block, name) => {
    const m = block.match(new RegExp(mask(name) + '\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)'));
    if (!m) return [null, null];
    return [{ v: parseFloat(m[1]), roh: m[1], dez: dez(m[1]) },
            { v: parseFloat(m[2]), roh: m[2], dez: dez(m[2]) }];
  };
  const teile = [['#sp_einfach', AUSGABE.spice.split('EINFACH')[1].split('ERWEITERT')[0]],
                 ['#sp_erweitert', AUSGABE.spice.split('ERWEITERT')[1]]];
  for (const [tid, block] of teile) {
    for (const [zn, pn] of [['V_BE / V', 'V_BE [V]'], ['V_CE / V', 'V_CE [V]'],
                            ['I_B / mA', 'I_B [mA]'], ['I_C / mA', 'I_C [mA]']]) {
      const [pb, ps] = lies(block, pn);
      await nahe(`${tid.slice(4)} ${zn} Buch`,  zahl(await zelle(tid, zn, 1)), pb);
      await nahe(`${tid.slice(4)} ${zn} SPICE`, zahl(await zelle(tid, zn, 2)), ps);
    }
  }
}

console.log('\nK10 — Leuchtdiode gegen den Lauf von BUCH/kap08_led_quellen.py');
await seite.click('#schiene button[data-ziel="led"]');
await seite.waitForTimeout(400);
const l_vd = aus('led', /Vd\s*=\s*([\d.]+)\s*V/);
const l_id = aus('led', /Id\s*=\s*([\d.]+)\s*mA/);
await nahe('V_d', zahl(await zelle('#le_erg', 'V_d', 1)), l_vd);
await nahe('I_d', zahl(await zelle('#le_erg', 'I_d', 1)), l_id);
const l_it = zahl(await zelle('#le_erg', 'Newton-Schritte', 1));
sage(l_it === 3, `Newton-Schritte der Leuchtdiode: ${l_it} (Soll 3)`, l_it);

console.log('\nK11 — Gummel-Poon gegen den Testlauf in Abschnitt 6.9');
await seite.click('#schiene button[data-ziel="gp"]');
await seite.waitForTimeout(400);
await nahe('I_C',  zahl(await zelle('#gp_tab', 'I_C', 1)),
           {v:5.20, roh:'5,20 mA', dez:2});
await nahe('I_B',  zahl(await zelle('#gp_tab', 'I_B nach der Iteration', 1)),
           {v:17.0, roh:'17,0 µA', dez:1});
const gpb = zahl(await zelle('#gp_tab', 'β = I_C/I_B', 1));
sage(Math.abs(gpb - 305) <= 2, `β = ${gpb} gegen „≈ 305" im Manuskript (Schranke ±2)`, gpb);
const fixzeilen = await seite.$$eval('#gp_fix tbody tr', n => n.length);
sage(fixzeilen >= 2, `Fixpunktiteration sichtbar: ${fixzeilen} Schritte`, fixzeilen);

console.log('\nK12 — Parameterextraktion gegen den Lauf von bjt_extract.py');
await seite.click('#schiene button[data-ziel="extrakt"]');
await seite.waitForTimeout(600);
const e_n  = aus('extract', /->\s*n\s*=\s*([\d.]+)/);
const e_is = aus('extract', /->\s*Is\s*=\s*([\d.e+-]+)\s*A/);
const e_va = aus('extract', /->\s*V_A\s*=\s*([\d.]+)\s*V/);
const e_b  = aus('extract', /beta_F \(Steigung\)\s*=\s*([\d.]+)/);
const e_hf = aus('extract', /hFE-Max ueber alle Daten:\s*([\d.]+)/);
await nahe('n',      zahl(await zelle('#ex_erg', 'n', 1)),  e_n);
{ // I_S steht auf beiden Seiten in Exponentialschreibweise; verglichen wird
  // die Mantisse zur gedruckten Stelle.
  const st = await zelle('#ex_erg', 'I_S', 1);
  const sm = parseFloat(String(st).split(/e/i)[0]);
  const pm = e_is === null ? null
    : { v: parseFloat(e_is.roh.split('e')[0]), roh: e_is.roh,
        dez: (e_is.roh.split('e')[0].split('.')[1] || '').length };
  await nahe('I_S (Mantisse)', sm, pm);
}
await nahe('V_A',    zahl(await zelle('#ex_erg', 'V_A', 1)),  e_va);
await nahe('β_F',    zahl(await zelle('#ex_erg', 'β_F (Steigung)', 1)), e_b);
await nahe('h_FE-Max', zahl(await zelle('#ex_erg', 'h_FE-Maximum über alle Daten', 1)), e_hf);

console.log('\nK13 — das Kleinsignal-Ersatzschaltbild');
await seite.click('#schiene button[data-ziel="klein"]');
await seite.waitForTimeout(300);
const esb = await seite.$eval('#kl_esb', n => n.textContent.replace(/\s+/g, ' '));
for (const z of ['h11e', 'h12e', 'h21e', 'h22e', 'vbe', 'vce', 'ib', 'ic'])
  sage(esb.includes(z), `Ersatzschaltbild beschriftet ${z}`);
// Das Verbot gilt fuer DIE AUSGABE, also fuer den rechnenden Teil und die
// Bilder, die diese Seite selbst erzeugt — nicht fuer seine Manuskripte, in
// denen r_pi und g_pi als Zwischengroessen durchaus vorkommen duerfen.
const ausgabe = await seite.$$eval('main section .rechner',
  n => n.map(x => x.innerText).join('\n'));
const pi = [/r\s*_?\s*π/i, /\bg_?m\s*·\s*v_?be/i, /\bgm\s*\*\s*vbe/i,
            /π-Ersatzschaltbild/i, /Hybrid-π/i, /\bg_?π\b/i, /\bg_?μ\b/i];
const gefunden = pi.filter(r => r.test(ausgabe)).map(r => r.source);
sage(gefunden.length === 0,
  `kein π-Modell im rechnenden Teil (gefunden: ${gefunden.length ? gefunden.join(', ') : 'nichts'})`,
  gefunden.length);
const zeichen = await seite.$$eval('#kl_esb text.wert', n => n.map(x => x.textContent));
sage(zeichen.every(t => t !== '—' && t.length > 1),
  `alle vier Elemente tragen ihren gerechneten Wert: ${zeichen.join(' · ')}`);

console.log('\nK14 — der vollständige SPICE-Parametersatz');
await seite.click('#schiene button[data-ziel="extrakt"]');
await seite.waitForTimeout(300);
const tafel = await seite.evaluate(() => {
  const k = [...document.querySelectorAll('#extrakt .karte')]
    .find(x => /vollständige SPICE-Parametersatz/.test(x.innerText));
  return k ? k.innerText : '';
});
for (const n of ['IS', 'NF', 'BF', 'VAF', 'VAR', 'IKF', 'RB', 'ISE', 'NE',
                 'BR', 'IKR', 'ISC', 'NC', 'RE', 'CJE', 'CJC', 'TF', 'TR'])
  sage(new RegExp('\\b' + n + '\\b').test(tafel), `SPICE-Parameter ${n} benannt`);
const unbest = (tafel.match(/nicht bestimmbar/g) || []).length;
sage(unbest >= 6,
  `Parameter ausdrücklich als nicht bestimmbar ausgewiesen: ${unbest} (Schranke ≥ 6)`, unbest);

console.log('\nK15 — Netzliste und Löser gegen den Lauf von netz_lauf.py (simulator.py)');
await seite.click('#schiene button[data-ziel="netz"]');
await seite.waitForTimeout(1200);

// Der Maßstab ist die Konsolenausgabe von netz_lauf.py.  Dieses Programm rechnet
// nichts selbst: es schickt dieselben zwei Netzlisten durch SEINEN Löser
// DGL_Nichtlinear/Programme/simulator.py (unverändert) und druckt die Ergebnisse.
const nz = n => aus('netz', new RegExp('^' + n + ' = (-?[\\d.e+-]+)$', 'm'));

// 1) Die Netzliste selbst muss Zeichen für Zeichen dieselbe sein.  Fall 1
//    enthält keine gerechnete Zahl, also ist der Vergleich hart.
const n1_py = (AUSGABE.netz.match(/\* Fall 1[^]*?\nT1 [^\n]*\n/) || [''])[0].trim();
const n1_se = (await seite.$eval('#nz_n1', n => n.value)).trim();
sage(n1_py.length > 0 && n1_py === n1_se,
  `Netzliste Fall 1 wörtlich gleich (${n1_se.split('\n').length} Zeilen)` +
  (n1_py === n1_se ? '' : `\n        Seite : ${JSON.stringify(n1_se)}\n        Python: ${JSON.stringify(n1_py)}`));
// Fall 2 trägt zwei GERECHNETE Zahlen (die Anfangswerte der Koppelkondensatoren);
// verglichen werden deshalb die Zeilen ohne diese beiden Zahlen, und die Zahlen
// selbst als Zahlen.
const n2_py = (AUSGABE.netz.match(/\* Fall 2[^]*?\nRL [^\n]*\n/) || [''])[0].trim();
const n2_se = (await seite.$eval('#nz_n2', n => n.value)).trim();
const ohneZahl = t => t.split('\n').map(z =>
  z.replace(/(10u\s+)(-?[\d.]+)/, '$1<Anfangswert>')).join('\n');
sage(n2_py.length > 0 && ohneZahl(n2_py) === ohneZahl(n2_se),
  `Netzliste Fall 2 gleich bis auf die zwei gerechneten Anfangswerte ` +
  `(${n2_se.split('\n').length} Zeilen)`);
{
  const zz = t => (t.match(/10u\s+(-?[\d.]+)/g) || []).map(x => parseFloat(x.split(/\s+/)[1]));
  const a = zz(n2_se), b = zz(n2_py);
  const d = (a.length === 2 && b.length === 2)
    ? Math.max(Math.abs(a[0] - b[0]), Math.abs(a[1] - b[1])) : NaN;
  sage(d < 1e-9, `Anfangswerte der Koppelkondensatoren: Abstand ${d.toExponential(2)} V ` +
    `(Schranke 1e-9 = die Abbruchschranke tol_u seines Newton)`, d);
}

// 2) Fall 1 — der Arbeitspunkt, Zeile für Zeile gegen seinen Löser
for (const [zeile, marke] of [['U_BE', 'F1_UBE'], ['U_BE,eff', 'F1_UBEEFF'],
                              ['U_CE', 'F1_UCE'], ['I_B', 'F1_IB'], ['I_C', 'F1_IC'],
                              ['I_E', 'F1_IE'], ['beta', 'F1_BETA'],
                              ['beta_eff', 'F1_BETAEFF'], ['P_V', 'F1_P']])
  await nahe('Fall 1 ' + zeile, zahl(await zelle('#nz_ap', zeile, 2)), nz(marke));
{
  const it = zahl(await zelle('#nz_ap', 'Newton-Durchgänge', 2));
  const py = nz('F1_NEWTON');
  sage(it === py.v, `Fall 1 Newton-Durchgänge: Seite ${it} · Python ${py.v}`, it);
}

// 3) Fall 1 — Empfindlichkeit gegen die drei GESETZTEN Parameter
for (const [k, marke] of [[0, 'F1_EMP_IKF_UCE'], [1, 'F1_EMP_RBI_UCE'],
                          [2, 'F1_EMP_VAR_UCE']]) {
  const w = await seite.$eval(`#nz_emp tbody tr:nth-child(${k + 1}) td:nth-child(4)`,
    n => n.innerText.trim());
  await nahe(`Empfindlichkeit ${k + 1} (V_CE)`, zahl(w), nz(marke));
}
{
  // Die vierte Probe (V_AB = 200 V) konvergiert NICHT — beide Seiten müssen das
  // melden, statt eine Zahl hinzuschreiben.
  const w = await seite.$eval('#nz_emp tbody tr:nth-child(4) td:nth-child(4)',
    n => n.innerText.trim());
  const pyIt = nz('F1_EMP_VAR200_NEWTON');
  sage(/kein Ergebnis/.test(w) && pyIt.v === 200,
    `V_AB = 200 V: Seite meldet „${w}“, Python bricht nach ${pyIt.v} Durchgängen ab`);
}

// 4) Gegenprobe — seine Netzliste bjt_fixedbias.netz mit dem BC547
for (const [zeile, marke] of [['U_BE', 'FB_UBE'], ['U_BE,eff', 'FB_UBEEFF'],
                              ['U_CE', 'FB_UCE'], ['I_B', 'FB_IB'],
                              ['I_C', 'FB_IC'], ['beta_eff', 'FB_BETAEFF']])
  await nahe('Gegenprobe ' + zeile, zahl(await zelle('#nz_gegen', zeile, 1)), nz(marke));
{
  // ... und gegen das VON HAND aufgestellte Gleichungssystem in
  // kap08_rechnung.py.  Hier ist ein Rest zu erwarten, und er ist benannt:
  // es ist GMIN (Teil XII, Abschnitt 50.1).  Verlangt wird deshalb nicht
  // Gleichheit, sondern die sechs gültigen Stellen, die dort nachgewiesen sind.
  const nzs = await seite.$$eval('#nz_gegen tbody tr', rr => rr.slice(0, 6).map(r => {
    const td = r.querySelectorAll('td');
    return [td[0].innerText.trim(), td[5] ? td[5].innerText.trim() : ''];
  }));
  const schlimm = Math.max(...nzs.map(r => parseFloat(r[1]) || 0));
  sage(schlimm < 1e-5,
    `Gegenprobe gegen kap08_rechnung.py (von Hand aufgestelltes System): ` +
    `größte relative Abweichung ${schlimm.toExponential(1)} (Schranke 1e-5, ` +
    `der Rest ist GMIN — Teil XII, 50.1)`, schlimm);
}

// 5) Fall 2 — die vier Tangenten und die Kleinsignalverstärkung daraus
for (const [zeile, marke] of [['g11', 'F2_G11'], ['g12', 'F2_G12'], ['g21', 'F2_G21'],
                              ['g22', 'F2_G22'], ['R_ac', 'F2_RAC'],
                              ['A_v klein', 'F2_AVKLEIN']])
  await nahe('Tangenten ' + zeile, zahl(await zelle('#nz_klein', zeile, 2)), nz(marke));

// 6) Fall 2 — die zwei Verstärkungen und die Verzerrung
await nahe('A_v klein',   zahl(await zelle('#nz_av', 'A_v klein', 2)),   nz('F2_AVKLEIN'));
{
  // Auf der Seite steht die Großsignalverstärkung mit Vorzeichen (invertierend),
  // der Python-Lauf druckt den Betrag.
  const a = zahl(await zelle('#nz_av', 'A_v gross', 2));
  await nahe('A_v gross', Math.abs(a), nz('F2_AVGROSS'));
  sage(a < 0, `A_v gross steht invertierend da: ${a}`);
}
await nahe('Unterschied',  zahl(await zelle('#nz_av', 'Unterschied', 2)),  nz('F2_UNTERSCHIED'));
await nahe('Hub oben',     zahl(await zelle('#nz_av', 'Hub oben', 2)),     nz('F2_HUBOBEN'));
await nahe('Hub unten',    zahl(await zelle('#nz_av', 'Hub unten', 2)),    nz('F2_HUBUNTEN'));
await nahe('Unsymmetrie',  zahl(await zelle('#nz_av', 'Unsymmetrie', 2)),  nz('F2_UNSYM'));
await nahe('Verschiebung', zahl(await zelle('#nz_av', 'Verschiebung', 2)), nz('F2_UCVERSCHIEBUNG'));
await nahe('Drift',        zahl(await zelle('#nz_av', 'Drift', 2)),        nz('F2_PERIODENDRIFT'));
{
  const unsym = zahl(await zelle('#nz_av', 'Unsymmetrie', 2));
  sage(Math.abs(unsym) > 1,
    `die Verzerrung ist sichtbar: Unsymmetrie ${unsym} % (eine lineare Stufe hätte 0,00 %)`,
    unsym);
}

// 6b) Fall 3 — SEINE B4-Brücke, wörtlich aus bruecke.netz.  Derselbe
//     JavaScript-Löser, nur eine andere Netzliste: vier Dioden statt eines
//     Transistors.  Das ist der Beleg, dass hier sein allgemeines Verfahren
//     steht und kein Transistor-Sonderfall.
{
  // Die Netzliste muss Zeichen für Zeichen seine Datei sein.
  const roh_netz = fs.readFileSync(prog('bruecke.netz'), 'utf8').trim();
  const se_netz = (await seite.$eval('#nz_n3', n => n.value)).trim();
  sage(roh_netz === se_netz,
    `Netzliste der Brücke wörtlich aus bruecke.netz (${se_netz.split('\n').length} Zeilen)`);
  const dz = (se_netz.match(/^D\d/gm) || []).length;
  sage(dz === 4, `vier Diodenzeilen in der Netzliste: ${dz}`, dz);
}
for (const [zeile, marke] of [['u_C Mittelwert', 'B_UC_MITTEL'],
                              ['u_C größte', 'B_UC_MAX'],
                              ['u_C kleinste', 'B_UC_MIN'],
                              ['Brummspannung', 'B_BRUMM'],
                              ['Brummspannung / u_C', 'B_BRUMM_PROZ'],
                              ['Laststrom Mittelwert', 'B_IL_MITTEL'],
                              ['Diodenstrom D1 Spitze', 'B_ID1_SPITZE'],
                              ['Quellstrom Spitze', 'B_IQ_SPITZE'],
                              ['Verlust bis zum Kondensator', 'B_VERLUST']])
  await nahe('Brücke ' + zeile, zahl(await zelle('#nz_br', zeile, 2)), nz(marke));
{
  const sch = zahl(await zelle('#nz_br', 'Zeitschritte', 2));
  sage(sch === nz('B_SCHRITTE').v, `Brücke Zeitschritte: ${sch}`, sch);
  const gr = zahl(await zelle('#nz_br', 'Newton größte / Abbrüche', 2));
  sage(gr === nz('B_NEWTON_GROESSTE').v,
    `Brücke größte Newton-Durchgänge: Seite ${gr} · Python ${nz('B_NEWTON_GROESSTE').v}`, gr);
  // Die MITTLERE Zahl der Durchgänge weicht als einzige Größe ab: die Zustände
  // beider Läufe liegen nach 20 000 Schritten rund 1e-11 V auseinander, und die
  // Abbruchbedingung prüft |Δ| gegen 1e-9 V.  Verlangt wird deshalb hier nicht
  // die gedruckte Stelle, sondern eine ausdrücklich genannte relative Schranke
  // — und die Seite muss diesen Unterschied selbst benennen.
  const mi = zahl(await zelle('#nz_br', 'Newton im Mittel', 2));
  const r = Math.abs((mi - nz('B_NEWTON_MITTEL').v) / nz('B_NEWTON_MITTEL').v);
  sage(r < 1e-3, `Brücke Newton im Mittel: Seite ${mi} · Python ` +
    `${nz('B_NEWTON_MITTEL').v} · relativ ${r.toExponential(1)} (Schranke 1e-3, ` +
    `ausdrücklich gröber als die gedruckte Stelle — Begründung steht auf der Seite)`, r);
  const zu = await seite.$eval('#nz_br_zu', n => n.innerText);
  sage(/weicht als einzige Größe ab/.test(zu),
    'die Seite benennt den Unterschied in der Newton-Zahl selbst');
  sage(/erreichen die Grenze/.test(zu),
    `die Seite weist die ${nz('B_ABBRUECHE').v} Newton-Abbrüche aus, statt sie zu verschweigen`);
}
{
  // ... und gegen SEINEN hinterlegten Bericht bericht_bruecke_rc.txt, der aus
  // einem anderen Programm stammt (Handauflösung statt Gauß) — der zweite,
  // unabhängige Weg.  Er druckt auf vier Nachkommastellen.
  const sp = await seite.$$eval('#nz_br tbody tr', rr => rr.slice(0, 9).map(r => {
    const td = r.querySelectorAll('td');
    return [td[0].innerText.trim(), td[6] ? td[6].innerText.trim() : ''];
  }));
  const schlimm = Math.max(...sp.map(r => parseFloat(r[1]) || 0));
  sage(schlimm < 1e-6,
    `Brücke gegen seinen Bericht bericht_bruecke_rc.txt (anderes Programm, ` +
    `Handauflösung statt Gauß): größte relative Abweichung ${schlimm.toExponential(1)} ` +
    `(Schranke 1e-6 = die vierte gedruckte Nachkommastelle)`, schlimm);
}
{
  // Alle sechs Bauteilklassen müssen wirklich da sein: eine Netzliste mit
  // Diode UND Induktivität muss durchlaufen.
  const ok = await seite.evaluate(() => {
    try {
      const s = new SimSimulator(
        'V1 q 0 sinus 10 50\nR1 q a 100\nD1 a k 1N4148\nR2 k 0 100\n' +
        'C1 k 0 100u\nL1 k 0 10m\nT1 c b 0 BC547\nRB q b 470k\nRC q c 1k\n',
        {dt: 1e-5});
      s.lauf(2e-3, ['k']);
      return { gut: true, klassen: Object.keys(SIM_TYPEN).join(''),
               modelle: Object.keys(SIM_MODELLE).length };
    } catch (e) { return { gut: false, fehler: e.message }; }
  });
  sage(ok.gut, `eine Netzliste mit R, V, D, C, L und T läuft durch` +
    (ok.gut ? ` · Buchstaben ${ok.klassen} · ${ok.modelle} Diodenkarten`
            : ` — FEHLER: ${ok.fehler}`));
  const kl = await seite.evaluate(() => Object.keys(SIM_TYPEN).sort().join(','));
  sage(kl === 'C,D,L,Q,R,T,V',
    `alle Bauteilbuchstaben seines Lösers übertragen: ${kl} (Soll C,D,L,Q,R,T,V)`);
  // Die vier Karten aus bruecke_kern.py, Z. 79-84, Zahl für Zahl.
  const soll = { '1N4148': [2.52e-9, 1.752, 0.025852],
                 '1N4007': [14.11e-9, 1.984, 0.025852],
                 '1N5408': [14.11e-9, 1.984, 0.025852],
                 'Schottky 1N5819': [31.7e-6, 1.373, 0.025852] };
  const mo = await seite.evaluate(() => Object.fromEntries(
    Object.entries(SIM_MODELLE).map(([k, v]) => [k, [v.IS, v.n, v.VT]])));
  for (const [k, w] of Object.entries(soll)) {
    const g = mo[k];
    const gleich = g && w.every((x, i) => g[i] === x);
    sage(gleich, `Diodenkarte ${k} unverändert aus bruecke_kern.py: ` +
      (g ? `IS=${g[0]} n=${g[1]} VT=${g[2]}` : 'FEHLT'));
  }
  sage(Object.keys(mo).length === 4,
    `genau die vier Karten seines Bestandes: ${Object.keys(mo).length}`,
    Object.keys(mo).length);
}

// 7) Die SPICE-artige Modellkarte: die drei Klassen müssen getrennt dastehen
const karte = await seite.$eval('#netz .doku', n => n.innerText);
const reiterNetz = await seite.$eval('#netz', n => n.innerText);
sage(/\.MODEL\s+BC337_eigen\s+NPN\(/.test(karte), 'die Modellkarte steht als .MODEL-Zeile da');
for (const t of ['IS=4.765E-14', 'NF=1.004', 'BF=253.2', 'VAF=126.6',
                 'VAR=1.39E3', 'IKF=4.05', 'RB=18.8'])
  sage(karte.includes(t), `Modellkarte trägt ${t}`);
{
  const gemessen = (karte.match(/gemessen und daraus bestimmt/g) || []).length;
  const gesetzt  = (karte.match(/nicht bestimmbar, deshalb gesetzt/g) || []).length;
  const unmess   = (karte.match(/mit diesem Gerät nicht messbar/g) || []).length;
  sage(gemessen >= 3, `Klasse „gemessen“: ${gemessen} Zeilen (Schranke ≥ 3)`, gemessen);
  sage(gesetzt === 3, `Klasse „gesetzt, weil nicht bestimmbar“: ${gesetzt} Zeilen ` +
    `(Soll 3 — I_KF, R_B,int, V_AB)`, gesetzt);
  sage(unmess >= 6, `Klasse „mit diesem Gerät nicht messbar“: ${unmess} Zeilen ` +
    `(Schranke ≥ 6)`, unmess);
}
sage(/obere Grenzfrequenz/i.test(karte) && /keine obere Grenzfrequenz/i.test(reiterNetz),
     'die fehlende obere Grenzfrequenz steht im Text UND an den gerechneten Zahlen');
sage(/Annahme/.test(karte) && /300 K/.test(karte),
     'die Thermospannung ist ausdrücklich als Annahme benannt');
{
  const offen = await seite.$$eval('#nz_offen li', n => n.length);
  sage(offen >= 5, `Liste „Was offen ist“ im Reiter: ${offen} Einträge (Schranke ≥ 5)`, offen);
}
sage(/Teil XII/.test(karte), 'Verweis auf Teil XII des Grundlagenprojekts im Reiter');

// 8) Die Schieber müssen wirken — und dann darf keine Python-Spalte mehr dastehen
{
  const vorher = await zelle('#nz_ap', 'U_CE', 2);
  await seite.$eval('#nz_rc', n => { n.value = '2000'; n.dispatchEvent(new Event('input')); });
  await seite.waitForTimeout(400);
  const nachher = await zelle('#nz_ap', 'U_CE', 2);
  const leer = await zelle('#nz_ap', 'U_CE', 3);
  sage(vorher !== nachher, `Schieber R_C wirkt: V_CE ${vorher} → ${nachher}`);
  sage(leer === '—',
    'außerhalb der Voreinstellung bleibt die Spalte „sein Löser“ leer statt zu behaupten');
  await seite.click('#nz_zurueck');
  await seite.waitForTimeout(1200);
  const zurueck = await zelle('#nz_ap', 'U_CE', 2);
  sage(zurueck === vorher, `Knopf „Voreinstellung“ stellt zurück: ${zurueck}`);
}

console.log('\nK16 — das Gerät im Bild');
await seite.click('#schiene button[data-ziel="tester"]');
await seite.waitForTimeout(400);
{
  const bilder = await seite.$$eval('img[data-bild]',
    n => n.map(x => ({ k: x.dataset.bild, gesetzt: (x.src || '').startsWith('data:'),
                       breit: x.naturalWidth, hoch: x.naturalHeight })));
  for (const k of ['platine', 'skizze', 'ops', 'cpu'])
    sage(bilder.some(b => b.k === k && b.gesetzt && b.breit > 400),
      `Bild „${k}“ eingebettet und geladen`);
  sage(bilder.filter(b => b.k === 'platine').length === 2,
    `das Foto der Platine steht an zwei Stellen (Start und Gerät): ` +
    `${bilder.filter(b => b.k === 'platine').length}`);
  // ... aber die Datei liegt nur EINMAL in der Seite.
  const roh0 = fs.readFileSync(datei, 'utf8');
  for (const art of ['data:image/jpeg;base64,', 'data:image/png;base64,']) {
    const n = (roh0.split(art).length - 1);
    sage(n > 0, `Daten-Adressen der Art ${art}: ${n}`, n);
  }
  const doppelt = await seite.evaluate(() => {
    const q = [...document.querySelectorAll('img[data-bild]')].map(x => x.src);
    const h = new Set(q);
    return q.length - h.size;   // Zahl der Bilder, die eine Adresse teilen
  });
  sage(doppelt === 1, `dieselbe Bilddatei zweimal angezeigt, einmal gespeichert: ` +
    `${doppelt} geteilte Adresse`, doppelt);
}
{
  const t = await seite.$eval('#r_tester', n => n.innerText);
  for (const w of ['ESP32', 'Prüfling', 'steckbar', 'Rc1', 'Rb2', 'AD7682', 'DAC8565',
                   'Fragezeichen', 'SPI'])
    sage(t.includes(w), `Bildunterschrift benennt „${w}“`);
  const pos = ['Das Gerät', 'Von der Klemme zur Zahl'].map(x => t.indexOf(x));
  sage(pos[0] >= 0 && pos[1] > pos[0],
    'erst das Gerät, dann die Umrechnung und die Messreihen');
}
{
  const st = await seite.$eval('#start', n => n.innerText);
  sage(/Von der Messung zum eigenen Berechnungsverfahren/.test(st),
    'die erste Seite trägt den Bogen in der Überschrift');
  const stationen = await seite.$$eval('#start .weg .st', n => n.length);
  sage(stationen >= 7, `Stationen des Weges auf der ersten Seite: ${stationen}`, stationen);
  const spruenge = await seite.$$eval('#start [data-spring]', n => n.length);
  sage(spruenge >= 8, `Sprungmarken auf die Reiter: ${spruenge}`, spruenge);
  sage(/Lernapparat|Lehrtext/.test(st),
    'die Manuskripte sind als Hintergrund und Lernapparat eingeführt');
}

console.log('\nK17 — Veröffentlichungsvorgaben');
const roh = fs.readFileSync(datei, 'utf8');
// Regel 11 der Veröffentlichungsvorgaben: der Prüfer darf die Geheimnisse nicht
// selbst tragen.  Die verbotenen Firmennamen stehen deshalb als Muster in
// `pruefe_privat.json` neben dem Prüfer und werden nicht mitgeliefert; hier steht
// nur, dass danach gesucht wird — kein Name.
const privat = fs.existsSync(H + 'pruefe_privat.json')
  ? JSON.parse(fs.readFileSync(H + 'pruefe_privat.json', 'utf8')) : [];
const verboten = [
  ['Rechnerpfad eines Arbeitsbereichs', /\/(?:home|workspace|Users)\/[A-Za-z0-9_.-]+/],
  ['Rechnerpfad C:\\', /[Cc]:\\\\?[A-Za-z]/],
  ['Heimnetzadresse', /192\.168\./],
  ['Tailscale-Adresse', /100\.\d+\.\d+\.\d+/],
  ['Kennwort im Klartext', /(passwor[dt]|kennwort)\s*[:=]\s*"(?!x*")[^"]+"/i],
  ['Befundliste', /BEFUNDE_zur_Durchsicht/],
  ['Reiter „Befunde"', /data-ziel="befunde"/],
].concat(privat.map((r, k) => ['Firmen- oder Personenname Nr. ' + (k + 1), new RegExp(r, 'i')]));
// Im Arbeitsbereich MUSS die Liste da sein; im ausgelieferten Repositorium darf
// sie es gerade nicht — das ist der Sinn von Regel 11.
sage(privat.length > 0 || imRepo,
  privat.length > 0
    ? `Namensliste aus pruefe_privat.json geladen: ${privat.length} Muster ` +
      `(sie steht nicht in diesem Prüfer und geht nicht mit hinaus)`
    : 'pruefe_privat.json ist hier nicht vorhanden — so soll es sein: die Namensliste ' +
      'gehört nach Regel 11 nicht in die Veröffentlichung',
  privat.length);
for (const [n, re] of verboten) {
  const m = roh.match(re);
  sage(!m, `${n}: ${m ? 'GEFUNDEN' : 'nicht enthalten'}`);
}
const kopf = await seite.$eval('header', n => n.innerText);
sage(kopf.includes('Fassung ' + V), `Kopfzeile nennt die Fassung ${V}`);
sage(/\d{2}\.\d{2}\.\d{4}/.test(kopf), 'Kopfzeile nennt das Datum');
sage(kopf.includes('Prof. Dr.-Ing. Ralph Wystup M.Sc.') && kopf.includes('Claude Code, Anthropic'),
     'Kopfzeile trägt die Namensnennung');
sage(/Schaltungssimulation-von-nichtlinearen-Differentialgleichungssystemen/.test(roh),
     'Verweis auf das Grundlagenprojekt vorhanden');

console.log('\nK18 — Bildschirmfotos aller Reiter (zum Ansehen)');
let fotos = 0;
for (const z of knoepfe) {
  await seite.click(`#schiene button[data-ziel="${z}"]`);
  await seite.waitForTimeout(250);
  const r = await seite.$(`#r_${z}`);
  if (r) { await r.scrollIntoViewIfNeeded(); await seite.waitForTimeout(200); }
  await seite.screenshot({ path: `${S}schuss/${z}.png` });
  fotos++;
}
// zusätzlich die Handybreite
await seite.setViewportSize({ width: 400, height: 900 });
await seite.click('#schiene button[data-ziel="start"]');
await seite.waitForTimeout(300);
const ueberlauf = await seite.evaluate(
  () => document.documentElement.scrollWidth - document.documentElement.clientWidth);
await seite.screenshot({ path: `${S}schuss/handy.png` });
fotos++;
sage(fotos === knoepfe.length + 1, `Bildschirmfotos abgelegt: ${fotos}`, fotos);
sage(ueberlauf <= 2, `waagerechter Überlauf bei 400 px: ${ueberlauf} px (Schranke 2)`, ueberlauf);

await browser.close();

/* ------------------------------------------------------------------ Ergebnis */
const erg = {
  fassung: V, datei: path.basename(datei),
  groesse_byte: fs.statSync(datei).size,
  gepruefte_kriterien: BEF.length,
  fehler,
  befunde: BEF,
};
fs.writeFileSync(H + 'pruefe_seite.json', JSON.stringify(erg, null, 1), 'utf8');
console.log(`\n${BEF.length - fehler} von ${BEF.length} Prüfungen bestanden.`);
console.log('Ergebnis: ' + H + 'pruefe_seite.json');
console.log('Bildschirmfotos: ' + S + 'schuss/');
process.exit(fehler ? 1 : 0);
