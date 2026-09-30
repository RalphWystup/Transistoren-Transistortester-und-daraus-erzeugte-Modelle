**Manuskript zur Auswertung und Modellierung**

**der Diodenkennlinie mittels Shockley-Gleichung,**

**Newton-Raphson- und Bisektionsverfahren**

*Begleitendes Manuskript zum Python-Programm „Optimierung_AP_1.py“*

# 1. Einleitung und Zielsetzung

Das vorliegende Manuskript beschreibt ausführlich die physikalischen Grundlagen, mathematischen Herleitungen und numerischen Verfahren, die dem Python-Programm „Optimierung_AP_1.py“ zugrunde liegen. Ziel des Programms ist es, gemessene Strom-Spannungs-Kennlinien einer Diode mit dem Shockley-Modell zu approximieren und anschließend für eine gegebene Schaltung (Diode in Reihe mit einem Vorwiderstand an einer Versorgungsspannung) den Arbeitspunkt zu bestimmen. Zusätzlich kann das Programm denjenigen Vorwiderstand R bestimmen, der zu einem gewünschten Diodenstrom führt.

Dazu werden drei numerische bzw. statistische Verfahren eingesetzt, die im Folgenden vollständig hergeleitet werden:

-   Nichtlineare Ausgleichsrechnung (curve_fit, Methode der kleinsten Quadrate) zur Bestimmung der Modellparameter Is und n,

-   das Newton-Raphson-Verfahren zur Lösung der transzendenten Maschengleichung (Bestimmung des Arbeitspunktes Vd),

-   das Bisektionsverfahren zur Bestimmung des Widerstands R für einen vorgegebenen Diodenstrom.

# 2. Physikalisches Modell der Diode

## 2.1 Die Shockley-Gleichung

Das elektrische Verhalten einer idealen pn-Diode wird durch die nach William Shockley benannte Diodengleichung beschrieben. Sie verknüpft den durch die Diode fließenden Strom Id mit der an ihr anliegenden Spannung Vd:

I~d~ = I~S~ · \[ exp( V~d~ / (n · V~T~) ) − 1 \] (2.1)

Hierbei bedeuten:

-   Id : Diodenstrom durch das Bauteil \[A\]

-   Vd : Spannung über der Diode \[V\]

-   IS : Sättigungssperrstrom (Reverse Saturation Current), ein für jede Diode charakteristischer, sehr kleiner Parameter (typ. 10⁻¹⁰-- 10⁻¹² A)

-   n : Emissionskoeffizient (Idealitätsfaktor), dimensionslos, üblicherweise zwischen 1 (ideale Diode) und 2 (reale Diode mit Rekombinationseffekten)

-   VT : Temperaturspannung \[V\]

## 2.2 Herleitung der Diodengleichung aus der pn-Übergangstheorie

Die Shockley-Gleichung folgt aus der Lösung der stationären Minoritätsträger-Diffusionsgleichung in einem pn-Übergang. An den Rändern der Raumladungszone gilt im thermodynamischen Gleichgewicht ohne äußere Spannung das Massenwirkungsgesetz für die Ladungsträgerkonzentrationen:

n~0~ · p~0~ = n~i~^2^ (2.2)

Wird eine äußere Spannung Vd angelegt, so verschiebt sich das Ferminiveau der Minoritätsträger am Rand der Raumladungszone gemäß der Boltzmann-Statistik. Für die Minoritätsträgerkonzentration der Löcher auf der n-Seite (pn) am Rand der Raumladungszone gilt dann:

p~n~(0) = p~n0~ · exp( V~d~ / V~T~ ) (2.3)

Setzt man dies in die stationäre Diffusionsgleichung für Minoritätsträger ein und löst die resultierende lineare Differentialgleichung zweiter Ordnung unter den Randbedingungen eines langen bzw. kurzen Diodengebiets, so erhält man für die Diffusionsstromdichte exponentiell abklingende Trägerprofile. Die Integration der Diffusionsströme über die Querschnittsfläche A der Diode liefert den Gesamtstrom:

I~d~ = q·A· ( D~p~·p~n0~/L~p~ + D~n~·n~p0~/L~n~ ) · \[ exp(V~d~/V~T~) − 1 \] (2.4)

Der gesamte, von Material- und Geometriegrößen (Diffusionskonstanten Dp, Dn, Diffusionslängen Lp, Ln, Gleichgewichts-Minoritätsträgerdichten pn0, np0, Elementarladung q und Querschnittsfläche A) abhängige Vorfaktor wird als Sättigungssperrstrom IS zusammengefasst:

I~S~ = q·A· ( D~p~·p~n0~/L~p~ + D~n~·n~p0~/L~n~ ) (2.5)

Damit ergibt sich unmittelbar die ideale Diodengleichung Id = IS·\[exp(Vd/VT) − 1\]. Da reale Dioden zusätzliche Effekte wie Rekombination in der Raumladungszone, Hochstrominjektion und Serienwiderstände im Halbleitermaterial aufweisen, wird empirisch der Idealitätsfaktor n eingeführt, der die effektive Steigung der Kennlinie im halblogarithmischen Diagramm korrigiert. Dies führt auf die in (2.1) verwendete, in der Praxis übliche Form der Shockley-Gleichung.

## 2.3 Die Temperaturspannung VT

Die Temperaturspannung ergibt sich aus der Boltzmann-Statistik der Ladungsträger zu:

V~T~ = (k·T) / q (2.6)

-   k : Boltzmann-Konstante (1,380649 × 10⁻²³ J/K)

-   T : absolute Temperatur \[K\]

-   q : Elementarladung (1,602176634 × 10⁻¹⁹ C)

Bei Raumtemperatur (T ≈ 300 K) ergibt sich VT ≈ 25,85 mV, was exakt dem im Programm fest hinterlegten Wert Vt = 0,02585 V entspricht.

# 3. Einlesen der Messdaten und nichtlineare Kurvenanpassung

## 3.1 Datenimport

Das Programm liest die Messdatei „Diode.txt“ zeilenweise ein. Ab der Kopfzeile, die mit „Point“ beginnt, werden je Zeile die Diodenspannung (zweite Spalte) und der Diodenstrom in mA (dritte Spalte) extrahiert. Dezimalkommata werden in Dezimalpunkte umgewandelt, um eine korrekte Konvertierung in Gleitkommazahlen (float) zu gewährleisten. Alle gültigen Messpunkte werden in den Feldern spannung_alle und strom_alle gespeichert; für den eigentlichen Fit werden nur Punkte mit positivem Strom (i_ma \> 0) verwendet, da der Logarithmus bzw. die Exponentialfunktion im Sperrbereich (negative oder verschwindende Ströme) numerisch instabile bzw. physikalisch wenig aussagekräftige Fitresultate liefern würde.

## 3.2 Methode der kleinsten Quadrate (Least-Squares-Fit)

Die Funktion curve_fit aus scipy.optimize bestimmt die Parameter IS und n so, dass die Summe der quadratischen Abweichungen zwischen den gemessenen Stromwerten Id,i (Messpunkt i) und dem Modellwert nach Shockley-Gleichung minimal wird:

S(I~S~, n) = Σ~i=1~^N^ \[ I~d,i~ − f(V~d,i~, I~S~, n) \]^2^ (3.1)

mit der Modellfunktion f(Vd, IS, n) = IS·\[exp(Vd/(n·VT)) − 1\]. Gesucht ist also:

(I~S~, n) = argmin~(IS,n)~ S(I~S~, n) (3.2)

Da das Modell nichtlinear in den Parametern ist (IS und n erscheinen multiplikativ bzw. im Exponenten), kann das Minimum nicht analytisch in geschlossener Form bestimmt werden. curve_fit verwendet daher iterativ den Levenberg-Marquardt-Algorithmus, eine Kombination aus Gauß-Newton-Verfahren und Gradientenabstieg. Ausgehend von einem Startwert p0 = \[IS = 10⁻¹² A, n = 2\] wird in jedem Iterationsschritt k das lineare Gleichungssystem

(J^T^J + λ·diag(J^T^J)) · Δp~k~ = J^T^·r~k~ (3.3)

gelöst, wobei J die Jacobi-Matrix der partiellen Ableitungen des Residuenvektors r nach den Parametern (IS, n) ist und λ ein Dämpfungsparameter, der zwischen Gauß-Newton-Schritt (λ klein) und Gradientenabstieg (λ groß) interpoliert. Der Parametervektor wird gemäß

p~k+1~ = p~k~ + Δp~k~ (3.4)

aktualisiert, bis die Änderung der Residuensumme einen vorgegebenen Toleranzwert unterschreitet (Konvergenz) oder die maximale Anzahl von Funktionsauswertungen (maxfev = 10000) erreicht ist. Das Ergebnis sind die im Programm ausgegebenen Parameter IS und n, die anschließend für alle weiteren Berechnungen (Arbeitspunktbestimmung, Bisektion) als feste Diodenparameter verwendet werden.

# 4. Schaltungsmodell und Maschengleichung

Im Hauptmenü betrachtet das Programm eine einfache Reihenschaltung aus einer Versorgungsspannungsquelle Uges, einem ohmschen Vorwiderstand R und der Diode. Nach der Kirchhoffschen Maschenregel gilt für diesen Stromkreis, dass die Summe aller Teilspannungen der Quellenspannung entspricht:

U~ges~ = I·R + V~d~ (4.1)

Da im stationären Fall (Gleichstrom) derselbe Strom I durch Widerstand und Diode fließt (Reihenschaltung), gilt I = Id, sodass mit der Shockley-Gleichung (2.1) eine implizite, transzendente Gleichung für die unbekannte Diodenspannung Vd entsteht:

$$f(V_{d}) = R\text{ }I_{S}\left\lbrack \exp\text{ ⁣}\left( \frac{V_{d}}{nV_{T}} \right) - 1 \right\rbrack + V_{d} - U_{ges} = 0
$$ (4.2)

Diese Gleichung lässt sich nicht nach Vd auflösen, da Vd sowohl linear als auch im Exponenten auftritt. Sie muss daher numerisch gelöst werden -- im Programm geschieht dies mit dem Newton-Raphson-Verfahren (Funktion solve_for_Vd).

Geometrisch entspricht die Lösung von (4.2) dem Schnittpunkt der Diodenkennlinie Id(Vd) mit der sogenannten Lastgeraden (auch Widerstandsgerade genannt), die durch Umstellen von (4.1) nach dem Strom entsteht:

I~R~(V~d~) = (U~ges~ − V~d~) / R (4.3)

Dieser Schnittpunkt wird als Arbeitspunkt der Schaltung bezeichnet und im Diagramm des Programms als blauer Punkt markiert.

# 5. Das Newton-Raphson-Verfahren

## 5.1 Allgemeine Herleitung

Das Newton-Raphson-Verfahren dient der iterativen Bestimmung einer Nullstelle x\* einer differenzierbaren Funktion f(x), also einer Lösung von f(x\*) = 0. Die Herleitung erfolgt über die Taylorreihenentwicklung von f um einen Näherungswert xk:

f(x) ≈ f(x~k~) + f′(x~k~)·(x − x~k~) + O((x−x~k~)^2^) (5.1)

Bricht man die Reihe nach dem linearen Glied ab (lineare Approximation der Funktion durch ihre Tangente im Punkt xk) und fordert, dass diese lineare Näherung an der Stelle x = xk+1 verschwindet, also f(xk) + f′(xk)·(xk+1 − xk) = 0, so folgt nach Umstellen die Newton-Iterationsvorschrift:

x~k+1~ = x~k~ − f(x~k~) / f′(x~k~) (5.2)

Geometrisch bedeutet dies: Man legt im aktuellen Näherungspunkt die Tangente an die Funktion und verwendet deren Nullstelle als neue, verbesserte Näherung. Bei hinreichend glatten Funktionen und einem Startwert nahe der gesuchten Nullstelle konvergiert das Verfahren quadratisch, d.h. die Anzahl der korrekten Nachkommastellen verdoppelt sich (näherungsweise) mit jedem Iterationsschritt.

## 5.2 Anwendung auf die Diodengleichung

Im Programm wird das Newton-Raphson-Verfahren auf die Maschengleichung (4.2) angewendet, wobei die gesuchte Variable die Diodenspannung Vd ist:

f(V~d~) = R·I~S~·\[exp(V~d~/(n·V~T~)) − 1\] + V~d~ − U~ges~ (5.3)

Die für das Verfahren benötigte Ableitung f′(Vd) nach Vd ergibt sich durch Anwendung der Kettenregel auf den Exponentialterm:

f′(V~d~) = d/dV~d~ { R·I~S~·exp(V~d~/(n·V~T~)) } + 1 (5.4)

f′(V~d~) = (R·I~S~)/(n·V~T~)·exp(V~d~/(n·V~T~)) + 1 (5.5)

Eingesetzt in (5.2) ergibt sich die im Quellcode implementierte Iterationsvorschrift:

V~d,k+1~ = V~d,k~ − \[ R·I~S~·(exp(V~d,k~/(n·V~T~)) − 1) + V~d,k~ − U~ges~ \] / \[ (R·I~S~)/(n·V~T~)·exp(V~d,k~/(n·V~T~)) + 1 \] (5.6)

Diese Vorschrift entspricht exakt den Zeilen f = R·(Is·(exp(Vd/(n·Vt))−1)) + Vd − Uges, df = R·Is·exp(Vd/(n·Vt))/(n·Vt) + 1 und Vd_new = Vd − f/df im Quellcode der Funktion solve_for_Vd.

Als Startwert wird Vd = 0 V verwendet. Das Verfahren bricht ab, sobald die Änderung zwischen zwei aufeinanderfolgenden Iterationen kleiner als die Toleranz (1×10⁻⁶ V) ist, spätestens jedoch nach 1000 Iterationen (max_iterations). Da f′(Vd) wegen des stets positiven Exponentialterms und des additiven Terms +1 für alle reellen Vd strikt positiv und die Funktion f monoton steigend und konvex ist, konvergiert das Verfahren für diesen Anwendungsfall robust gegen die eindeutige Lösung.

# 6. Das Bisektionsverfahren

## 6.1 Allgemeine Herleitung

Das Bisektionsverfahren (Intervallhalbierungsverfahren) basiert auf dem Zwischenwertsatz für stetige Funktionen: Ist g(x) auf einem Intervall \[a, b\] stetig und besitzen g(a) und g(b) unterschiedliche Vorzeichen,

g(a)·g(b) \< 0 (6.1)

so existiert nach dem Zwischenwertsatz mindestens eine Nullstelle x\* ∈ \[a, b\] mit g(x\*) = 0. Das Verfahren halbiert das Intervall iterativ: Man berechnet den Mittelpunkt

x~m~ = (a + b) / 2 (6.2)

und prüft das Vorzeichen von g(xm). Hat g(xm) dasselbe Vorzeichen wie g(a), liegt die Nullstelle im rechten Teilintervall, und man setzt a ∶= xm; andernfalls liegt sie im linken Teilintervall, und man setzt b ∶= xm. Dieses Vorgehen wird wiederholt, bis die Intervallbreite (b − a) eine vorgegebene Toleranz unterschreitet. Da sich die Intervallbreite in jedem Schritt halbiert,

(b~k~ − a~k~) = (b~0~ − a~0~) / 2^k^ (6.3)

ist die Konvergenz linear, aber unbedingt garantiert, solange die Vorzeichenbedingung (6.1) zu Beginn erfüllt ist -- im Gegensatz zum Newton-Verfahren, das bei ungünstigen Startwerten divergieren kann.

## 6.2 Anwendung zur Bestimmung des Widerstands R

Im Programm wird das Bisektionsverfahren in der Funktion finde_R_bisektion verwendet, um zu einem gewünschten Diodenstrom Id,soll denjenigen Widerstand R zu finden, der diesen Strom im Arbeitspunkt erzeugt. Hierzu wird die Hilfsfunktion

g(R) = I~d~(V~d~(R)) − I~d,soll~ (6.4)

betrachtet, wobei Vd(R) für jeden Widerstandswert R durch Lösen der Maschengleichung (4.2) mittels Newton-Raphson-Verfahren (Abschnitt 5) bestimmt wird und Id(Vd(R)) anschließend mit der Shockley-Gleichung (2.1) berechnet wird. Da bei festem Uges der Diodenstrom mit wachsendem Vorwiderstand R streng monoton fällt (ein größerer Widerstand reduziert den Spannungsabfall an der Diode und damit exponentiell den Diodenstrom), ist g(R) eine streng monoton fallende Funktion von R, und es existiert genau ein Widerstand R\*, für den g(R\*) = 0 gilt.

Das Suchintervall wird im Programm mit Rmin = 1 Ω und Rmax = 1 000 000 Ω initialisiert. In jedem Iterationsschritt wird

R~mid~ = (R~min~ + R~max~) / 2 (6.5)

berechnet und der zugehörige Diodenstrom Id,mid bestimmt. Es gilt dann die Fallunterscheidung:

-   Ist Id,mid \> Id,soll (Widerstand zu klein, Strom zu hoch), so wird Rmin := Rmid gesetzt (rechte Hälfte des Intervalls wird beibehalten),

-   andernfalls (Id,mid ≤ Id,soll) wird Rmax := Rmid gesetzt (linke Hälfte wird beibehalten).

Diese Schleife wird fortgesetzt, bis (Rmax − Rmin) kleiner als die Toleranz von 1×10⁻⁶ Ω ist; als Ergebnis wird der Mittelwert (Rmin + Rmax)/2 zurückgegeben. Anschließend wird im Hauptprogramm mit diesem R erneut der Arbeitspunkt (Vd, Id) über das Newton-Raphson-Verfahren bestimmt und zusammen mit der Last- und Diodenkennlinie sowie den Messpunkten grafisch dargestellt.

# 7. Gesamter Programmablauf

Zusammenfassend lässt sich der Ablauf des Programms in folgende Schritte gliedern:

1.  Einlesen der Messdaten aus Diode.txt und Trennung in Rohdaten (alle Punkte) und Fitdaten (nur positive Ströme).

2.  Nichtlineare Ausgleichsrechnung (Levenberg-Marquardt, Abschnitt 3.2) zur Bestimmung der Diodenparameter IS und n aus den Messdaten gemäß Shockley-Gleichung.

3.  Grafische Darstellung der Approximation (Messpunkte als Kreuze, Fitkurve als rote Linie).

4.  Interaktives Hauptmenü mit zwei Modi:

-   Modus 1 -- Arbeitspunktbestimmung: Eingabe von R und Uges; Lösung der Maschengleichung (4.2) mittels Newton-Raphson-Verfahren (Abschnitt 5) liefert den Arbeitspunkt (Vd, Id).

-   Modus 2 -- Widerstandssuche: Eingabe von Uges und gewünschtem Diodenstrom Id,soll; Bisektionsverfahren (Abschnitt 6) liefert den passenden Widerstand R, anschließend erneute Arbeitspunktbestimmung über Newton-Raphson.

5.  Grafische Ausgabe: Diodenkennlinie Id(Vd) nach Shockley-Gleichung, Lastgerade IR(Vd) nach Gleichung (4.3), eingezeichneter Arbeitspunkt sowie die ursprünglichen Messpunkte zum visuellen Abgleich von Modell und Messung.

# 8. Zusammenfassung

Das Programm verbindet drei klassische numerische Verfahren der angewandten Mathematik mit einem physikalischen Halbleitermodell: Die nichtlineare Ausgleichsrechnung (Levenberg-Marquardt) extrahiert aus Messdaten die Diodenparameter IS und n. Das Newton-Raphson-Verfahren löst die durch die Kirchhoffsche Maschenregel entstehende transzendente Gleichung für die Diodenspannung im Arbeitspunkt und nutzt dabei die quadratische Konvergenz in der Nähe der Lösung aus. Das Bisektionsverfahren schließlich invertiert die (im relevanten Bereich) monotone Beziehung zwischen Vorwiderstand und Diodenstrom, um gezielt einen gewünschten Arbeitspunkt einzustellen, und garantiert dabei -- anders als das Newton-Verfahren -- globale Konvergenz innerhalb des gewählten Suchintervalls. Durch das Zusammenspiel dieser Verfahren lässt sich die Diodenschaltung sowohl analytisch verstehen als auch numerisch vollständig und robust auswerten.
