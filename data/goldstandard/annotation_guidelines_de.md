# Annotationsrichtlinien

Gilt für alle von Hand annotierten Stichproben, die zusammen den
Goldstandard bilden: `edh_devsample.json` (500, Entwicklungsdaten),
`edh_former_testsample.json` (300, ehemalige Teststichprobe, nach einer
Fehleranalyse zu Entwicklungsdaten geworden) und `edh_testsample.json`
(300, zurückgehaltene Testdaten, Methodenvergleich). Beispiele stammen aus
annotierten EDH-Kommentaren (HD-Nummer in Klammern).

---

## 1. Grundsätze

1. **Nur eindeutige Erwähnungen.** Annotiert wird, was im Kommentartext
   ausdrücklich beschrieben ist, nicht was auf dem Stein vermutlich zu sehen
   ist. Kein Ergänzen aus eigenem Wissen über das Monument oder aus
   Abbildungen.
2. **Nur das festgelegte Vokabular.** Elemente, Kategorien und Varianten
   stammen aus dem Vokabular (`elements.json`, `categories.json`,
   `variant_conditions.json`). Fehlt ein Element, wird das
   nächstliegende vorhandene gewählt und die Lücke notiert, statt ein neues
   Element spontan anzulegen.
3. **Eine dargestellte Sache = ein Element.** Eine Figur ist ein Element,
   auch wenn sie mit mehreren Wörtern beschrieben wird („stehende Figur
   eines bärtigen Mannes“ → ein `man`).
4. **Erneute Nennung ist kein neues Element.** Wird eine bereits genannte
   Figur oder Sache später wieder aufgegriffen, entsteht kein zweites
   Element (Abschnitt 4.4).
5. **Das Spezifischste wählen**, beim Element wie bei der Kategorie.
6. **Unsicherheit übernehmen, nicht erzeugen.** „unsicher“ wird nur
   angekreuzt, wenn der Kommentar die Deutung selbst als unsicher
   kennzeichnet („(?)“, „wohl“, „vielleicht“, „möglicherweise“).
7. **Nicht annotiert werden** Lesungen, Buchstabenformen, Ligaturen,
   Worttrenner, Maße, Fundumstände, Aufbewahrungsort und Literatur.

## 2. Ablauf

Folgende Kriterien werden bei der Annotation beachtet

1. **Darstellung ja/nein** entscheiden (Abschnitt 3).
2. **Elemente** erfassen, mit Anzahl (Abschnitt 4).
3. **Varianten** an die Elemente hängen (Abschnitt 5).
4. **Motive** bilden und ihre **Kategorie** wählen (Abschnitte 6 und 7).

---

## 3. Darstellung ja/nein

Beschreibt der Kommentar eine bildliche Darstellung oder
Verzierung auf dem Denkmal?

**Regeln**
- Ja, sobald eine Darstellung erwähnt wird, auch ohne ein Element zu nennen. 
- Nein, wenn nur der Träger, seine architektonische Rahmung oder die Schrift beschrieben ist.

**Beispiele (Ja).**
- „Oberhalb der Inschrift Reliefreste“ → Ja, keine Elemente.
- „Z. 1 hinter M lateinisches Kreuz“ → Ja, `latin_cross`: Ein Kreuzzeichen
  in der Schriftzeile ist eine Darstellung (HD080027).

**Gegenbeispiele (Nein).**
- Nur der Inschriftträger: „Fragment einer Tafel“, „Statuenbasis“,
  „Cupa“, „Aschenkiste“.
- Worttrenner (Hedera), Buchstabenformen, Ligaturen, Lesungen.

---

## 4. Elemente

Ein Element ist eine Figur, ein dargestelltes Objekt, Ornament oder Symbol: beschreibt *was* dargestellt ist.

**Regeln**
- Ein Eintrag pro Elementtyp und Kommentar, inkl. Angabe der Häufigkeit.
- Es wird immer das spezifischste vorhandene Element gewählt (z.B. „Taube“ → `dove` anstatt `bird`)

**Beispiele**
- „Adler innerhalb eines Kranzes; darüber Gorgoneion“ → `eagle`, `wreath`,
  `gorgon` (HD072318).
- „Fries mit laufenden Tieren“ → `animal` (>1, Variante `running`)
  (HD037507).


## 5. Varianten

Eine Variante beschreibt verschiedene Darstellungsformen eines Elementes.

**Regeln** 
- Ändert die Angabe die Darstellungsweise, wird daraus eine Variante.
- Mehrere Varianten pro Element sind möglich („stehender bärtiger Mann“ → `man`: `standing`, `bearded`, `full_figure`).

**Varianten.**
- **Darstellungsform von Personen:** 
  - z.B. `bust`, `clipeus`, `orant`, `full_figure` 
- **Haltung und Handlung:** 
  - z.B. stehend, sitzend, laufend
- **Ausrichtung:** 
  - nach links, nach rechts.
- **Gestaltung:** 
  - bärtig, kanneliert, spiegelverkehrt

**Beispiele.**
- „ganzfigurige Darstellung eines bärtigen Mannes, in der Linken einen
  Beutel(?)“ → `man`, `full_figure`, `bearded`; `pouch` (unsicher)
  (HD079094).
- „Inschriftfeld von zwei Eroten mit gesenkter Fackel flankiert“ → `putto`,
  `framing`; `torch`, `reversed` (HD039488).

---

## 6. Motive

Ein Motiv fasst Elemente zusammen, die gemeinsam ein ikonographisches Motiv ergeben.

**Regeln**
- Jedes Element gehört zu genau einem Motiv.
- Stehen Elemente in einer ausdrücklichen Beziehung zueinander (hält,
  trägt, sitzt auf, im Kranz, zwischen, führt) → ein Motiv.
- Sind sie nur nebeneinander aufgezählt oder räumlich getrennt
  beschrieben („darüber …“, „unterhalb …“) → getrennte Motive
- Übrige Elemente bilden je ein eigenes Motiv mit der Kategorie des
  Elements 

**Beispiele (ein Motiv, mehrere Elemente).**
- „Adler in Kranz“ → Elemente `eagle` + `wreath` → Motiv `eagle_in_wreath`
  (HD067346).
- „zwei Tauben, jeweils auf einem Zweig“ → Elemente `dove` + `branch` →
  Motiv `bird_with_branch` (HD056653).
- „Frau im Mantel, in der Linken einen Spiegel haltend“ → Elemente `woman` +
  `mirror` → Motiv `portrait_woman` (HD080761).


**Gegenbeispiele (mehrere Elemente, getrennte Motive).**
- „Adler innerhalb eines Kranzes; darüber Gorgoneion“ → Motiv
  `eagle_in_wreath` (Elemente `eagle` + `wreath`) und Motiv
  `mythological_figures` (Element `gorgon`) (HD072318).
- „Im Hauptbild Adler in Kranz; im Giebelfeld Büste eines Mannes zwischen
  Delfinen“ → Motiv `eagle_in_wreath` (Elemente `eagle` + `wreath`), Motiv
  `portrait_man` (Element `man`, Variante `bust`) und Motiv `dolphins`
  (Element `dolphin`) (HD067346).

---

## 7. Kategorien

Die Kategorie ordnet ein Motiv in den Kategorienbaum ein (`categories.json`).

**Regeln**
- Jedes Motiv erhält genau eine Kategorie, die spezifischste passende, in
  dieser Reihenfolge:
  1. **Szene:** Personen in einer Handlung (`funerary_banquet`,
     `hunting_scene`).
  2. **Feste Bildformel** aus `motif_rules.json` (`eagle_in_wreath`,
     `bird_with_branch`).
  3. **Porträt:** Personen ohne Handlung oder weitere Identifikation.
  4. **Element:** sonst die Kategorie des Elements (`elements.json`).


**Beispiele.**
- „Fries mit Hasenjagd“ → `hunting_scene` (HD040236).
- „Nische mit den Büsten zweier Erwachsener und eines Kindes“ →
  `portrait_family` (HD038867).

---

## 8. Markierungen auf Wortebene (für BERT)

Für die Entwicklungsdaten ist zusätzlich markiert, welches Wort im
Kommentar ein Element bezeichnet (`edh_devsample_word_markings.json`). Diese
Markierungen sind die Trainingsdaten für BERT (Methode 4). Sie wurden aus den
Annotationen automatisch vorgeschlagen und von Hand geprüft; der
Silberstandard wird nach denselben Regeln markiert (`bert.py`).

**Regeln**
- Markiert wird nur, was zur Annotation des Kommentars passt: seine
  Elemente und die Formwörter seiner Personen.
- Jedes Vorkommen wird markiert, auch erneute Nennungen.
- Ein Wort kann mehrere Labels tragen.
- Eine Wendung aus mehreren Wörtern wird auf jedem ihrer Wörter markiert
  („Alpha und Omega“).
- Formwörter werden als eigene Labels markiert („Büste“ → `bust`,
  „Porträt“ → `portrait`, „Ehepaar“ → `couple`).
- Wörter und Sätze werden so getrennt, wie Stanza sie trennt.

**Beispiele.**
- „Giebel mit weiblicher Büste“ → weiblicher `woman`, Büste `bust`
  (HD054538).
- „Fries mit Hasenjagd“ → Hasenjagd `hare` + `hunt` (HD040236).
- „Bildfeld mit Lorbeerkranz; darüber Giebel mit Rosette“ → Lorbeerkranz
  `laurel` + `wreath`, Rosette `rosette` (HD071668).


