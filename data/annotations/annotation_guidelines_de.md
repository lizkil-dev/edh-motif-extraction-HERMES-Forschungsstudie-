# Annotationsrichtlinien EDH

Stand: 2026-09-25. Gilt für alle von Hand annotierten Stichproben, die
zusammen den Goldstandard bilden (`data/annotations/`):
`edh_devsample.json` (500, Entwicklungsdaten), `edh_former_testsample.json`
(300, ehemalige Teststichprobe, seit der Fehleranalyse Entwicklungsdaten)
und `edh_testsample.json` (300, zurückgehaltene Testdaten,
Methodenvergleich). Beispiele stammen aus annotierten EDH-Kommentaren
(HD-Nummer in Klammern).

---

## 1. Grundsätze

1. **Nur was der Kommentar sagt.** Annotiert wird, was im Kommentartext
   ausdrücklich beschrieben ist, nicht was auf dem Stein vermutlich zu sehen
   ist. Kein Ergänzen aus eigenem Wissen über das Monument oder aus
   Abbildungen.
2. **Nur das festgelegte Vokabular.** Elemente, Kategorien und Varianten
   stammen aus `data/gazetteer/` (`elements.json`, `categories.json`,
   `rules/variant_conditions.json`). Fehlt ein Element, wird das
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

**Beschreibung.** Beschreibt der Kommentar eine bildliche Darstellung oder
Verzierung auf dem Denkmal?

**Entscheidungsregel.** Ja, sobald irgendetwas Dargestelltes genannt ist –
auch ohne benennbares Element. Nein, wenn nur der Träger, seine
architektonische Rahmung oder die Schrift beschrieben ist.

**Beispiele (Ja).**
- „Oberhalb der Inschrift Reliefreste“ → Ja, keine Elemente.
- „Z. 1 hinter M lateinisches Kreuz“ → Ja, `latin_cross`: Ein Kreuzzeichen
  in der Schriftzeile ist eine Darstellung (HD080027).
- „Maske auf Eckbuckel eines Sarkophagdeckels“ → Ja, `mask` (HD060127).

**Gegenbeispiele (Nein).**
- Nur der Inschriftträger: „Fragment einer Tafel“, „Statuenbasis“,
  „Cupa“, „Aschenkiste“.
- Worttrenner (Hedera), Buchstabenformen, Ligaturen, Lesungen.

---

## 4. Elemente

**Beschreibung.** Ein Element ist eine dargestellte Sache, Figur oder ein
Zeichen: *was* dargestellt ist.

**Entscheidungsregel.**
- Ein Eintrag pro Elementtyp und Kommentar. Die **Anzahl**: Zahlwort oder
  Ziffer → diese Zahl („zwei Delphine“ → 2); Plural ohne Zahl → „>1“
  („Delphine“); sonst 1.
- Das **spezifischste** vorhandene Element („Taube“ → `dove`, nicht `bird`;
  „Palmzweig“ → `palm_branch`, nicht `branch`).
- **Ein Wort kann mehrere Elemente tragen**, wenn es mehrere Dinge nennt:
  „Hasenjagd“ → `hare` + `hunt` (HD040236); „Lorbeerkranz“ → `laurel` +
  `wreath` (HD033283).

**Beispiele.**
- „Adler innerhalb eines Kranzes; darüber Gorgoneion“ → `eagle`, `wreath`,
  `gorgon` (HD072318).
- „Fries mit laufenden Tieren“ → `animal` (>1, Variante `running`)
  (HD037507).

**Gegenbeispiele.**
- Hedera (Worttrenner), tabula ansata, Basis: keine Elemente.
- Wörter in anderem Sinn: „häufiger männliches als weibliches cognomen“
  (HD001248) nennt Namen, keine Figuren; eine „im Sarkophag gefundene
  Münze“ (HD068655) ist ein Fundstück.

**Abgrenzung zur Variante.** Ändert eine Form, *was* dargestellt ist, ist
sie ein eigenes Element: Kreuzarten (griechisches, lateinisches Kreuz,
Andreaskreuz = `decussis`), Chi-Rho, radiales Chi-Rho, Christogramm im
Kreis, Staurogramm im Kreis, Speichenrad. Ändert sie nur, *wie* es
dargestellt ist, ist sie eine Variante (Abschnitt 5).

### 4.4 Erneute Nennung

**Regel.** Greift der Kommentar eine bereits genannte Figur oder Sache
wieder auf, entsteht kein neues Element und keine neue Anzahl.

**Beispiele.**
- „Darstellung eines Ehepaars hinter einem Dreifuß. Z. 1: D und M innerhalb
  des Bildfeldes zu Seiten des Ehepaars.“ → ein Mann, eine Frau (HD038528).
- „Brustbilder eines Ehepaares … Frau in einheimischer Tracht mit torques,
  Armreif; Mann in toga(?)“ → dieselben zwei Personen, die Attribute kommen
  in ihr Motiv (HD073492).

---

## 5. Varianten

**Beschreibung.** Eine Variante beschreibt, *wie* ein Element dargestellt
ist.

**Entscheidungsregel.** Ändert die Angabe die Darstellungsweise, nicht den
Gegenstand → Variante am Element. Mehrere Varianten pro Element sind
möglich („stehender bärtiger Mann“ → `man`: `standing`, `bearded`,
`full_figure`).

**Varianten.**
- **Darstellungsform von Personen:** `bust` (Büste, Brustbild, Bruststück,
  Halbfigur, Bildniskopf, Porträtkopf), `clipeus` (Büste in
  Clipeus/Medaillon), `orant`, `full_figure` (Figur, Ganzfigur – und jede
  stehende Person), `head` (Kopf, wenn ein dargestellter Kopf gemeint ist).
  Steht neben „Kopf“ ein anderes Formwort, benennt „Kopf“ nur den erhaltenen
  Teil („Ganzfiguren …, von denen noch die Köpfe erhalten sind“ → nur
  `full_figure`) (HD080733).
- **Haltung und Handlung:** stehend, sitzend, liegend, tanzend, laufend,
  trauernd, nackt.
- **Ausrichtung:** nach links, nach rechts.
- **Gestaltung:** bärtig, erhoben/gesenkt (Fackel), kanneliert,
  sechsstrahlig, spiegelverkehrt, fragmentarisch.
- **Rahmend** (`framing`): für nicht-architektonische Elemente, die das
  Inschrift- oder Bildfeld einfassen, flankieren oder auf dem Rahmen bzw.
  rahmenden Säulen sitzen.

**Beispiele.**
- „Inschriftfeld von Efeuranken gerahmt“ → `ivy_tendril`, `framing`
  (HD074112).
- „Inschriftfeld von zwei Eroten mit gesenkter Fackel flankiert“ → `putto`,
  `framing`; `torch`, `reversed` (HD039488).

---

## 6. Motive

**Beschreibung.** Ein Motiv fasst Elemente zusammen, die gemeinsam ein Bild
ergeben: *in welcher Verbindung* etwas dargestellt ist.

**Entscheidungsregel.**
- **Jedes Element gehört zu genau einem Motiv.**
- Stehen Elemente in einer ausdrücklichen **Beziehung** zueinander (hält,
  trägt, sitzt auf, im Kranz, zwischen, führt) → ein Motiv.
- Sind sie nur **nebeneinander aufgezählt** oder räumlich getrennt
  beschrieben („darüber …“, „unterhalb …“) → getrennte Motive, auch wenn
  eine Regel sie verbinden könnte.
- Übrige Elemente bilden je ein eigenes Motiv mit der Kategorie des
  Elements (mehrere gleichartige übrige Elemente: ein Motiv).

**Beispiele (ein Motiv).**
- „Adler in Kranz“ → [eagle, wreath] (HD067346).
- „zwei Tauben, jeweils auf einem Zweig“ → [dove, branch] (HD056653).
- „Frau im Mantel, in der Linken einen Spiegel haltend“ → [woman, mirror]
  (HD080761).
- „Leier spielender Orpheus zwischen Tieren“ → [orpheus, lyre, animal]
  (HD066821).

**Gegenbeispiele (getrennte Motive).**
- „von Tauben flankiertes Staurogramm, darüber Vase“ → [staurogram, dove]
  und [vessel].
- „Im Hauptbild Adler in Kranz; im Giebelfeld Büste eines Mannes zwischen
  Delfinen“ → Adler und Kranz, Büste und Delfine sind getrennte Motive
  (HD067346).

**Abgrenzung.**
- **Attribute** – Gegenstände, die eine Figur hält (Rolle, Beutel,
  Spiegel, Buch, Spinnrocken, Spindel) oder trägt (Torques, Armreif) –
  gehören ins Motiv der Figur; die Kategorie bleibt die der Figur
  („Diener mit Buchrolle“ → [servant, scroll], `secular_figures`,
  HD038853).

---

## 7. Kategorien

**Beschreibung.** Die Kategorie ordnet ein Motiv im Kategorienbaum ein
(`data/gazetteer/categories.json`).

**Entscheidungsregel.** Die **spezifischste** passende Kategorie, in dieser
Reihenfolge:

1. **Szene** vor Porträt: Personen in einer Handlung gehören zur
   Szenenkategorie (Mahlszene → `funerary_banquet`, Ochsenkarren mit
   Gespannführer → `field_work`, Knabe mit Ball, Jagd, Opfer, biblische
   Szene).
2. **Feste Bildformeln** (`motif_rules.json`): Kopf + Widderhörner →
   `jupiter_ammon`; Eroten oder Genius + gehaltene Tafel →
   `tablet_held_by_erotes`; Adler im Kranz → `eagle_in_wreath`; Tiere in
   Reihe oder Handlung → `animal_scene`; Jagd + gejagte Tiere →
   `hunting_scene`; Lorbeer, Ölzweig oder Efeu + Kranz → `wreaths`; Vogel
   mit Zweig/Blüte; Christogramm im Kranz.
3. **Porträt** (Personen ohne szenische Handlung): Kategorie nur nach
   Personengruppe – immer ein Motiv für die ganze Gruppe:
   - Einzelperson: `portrait_man`, `portrait_woman`, `portrait_boy`,
     `portrait_girl`, `portrait_child`, `portrait_person`
   - Paar (zwei Personen, auch „zwei Büsten“ ohne Geschlecht):
     `portrait_couple`
   - Familie (zwei Erwachsene – Mann + Frau oder ohne Geschlechtsangabe –
     mit Kind/ern): `portrait_family`
   - Mann bzw. Person mit Kind: `portrait_man_with_child`,
     `portrait_person_with_child`
   - Gruppe (drei oder mehr Erwachsene, auch gemischt: „Büsten einer Frau
     und dreier Männer“, HD025552): `portrait_group`
   - Paar in der dextrarum iunctio (Handschlag, auch aus Attributen
     erschlossen): `portrait_dextrarum_iunctio`
4. **Elementkategorie**: sonst die Standardkategorie des Elements aus
   `elements.json`.

**Beispiele.**
- „Nische mit den Büsten zweier Erwachsener und eines Kindes“ →
  `portrait_family` (HD038867).
- „Oberhalb des Inschriftfeldes Fries mit Hasenjagd“ → `hunting_scene`
  (HD040236).

**Gegenbeispiele.**
- **Einzelperson ohne Form- oder Porträtwort** → `figure_unspecified`,
  nicht `portrait_…`: sie könnte Teil einer Szene gewesen sein („Reste der
  Darstellung eines Mannes und eines Hundes“, HD022362).

**Abgrenzung.** Paare, Familien und Gruppen sind immer Porträts, auch ohne
Formwort. Die Darstellungsform steht nie in der Kategorie, sondern als
Variante bei den Personen.

---

## 8. Markierungen auf Wortebene (für BERT)

Für die Entwicklungsdaten gibt es zusätzlich Markierungen auf Wortebene
(`data/annotations/edh_devsample_word_markings.json`), aus den Annotationen
automatisch vorgeschlagen und von Hand geprüft (dieselbe Logik markiert den
Silberstandard, `candidates()` in `src/methods/bert.py`):

- Wörter und Sätze sind Stanza-Tokens.
- **Jedes Vorkommen** wird markiert, auch erneute Nennungen.
- Eine **Mehrwort-Wendung** wird auf allen ihren Wörtern markiert („Alpha
  und Omega“).
- Ein Wort kann **mehrere Labels** tragen („Lorbeerkranz“ → `laurel` +
  `wreath`).
- Label-Raum ist das Suchvokabular einschließlich der Formwörter („Büste“
  → `bust`, „Porträt“ → `portrait`, „Ehepaar“ → `couple`).

---

## 9. Normdaten

- Die Bildelemente sind, wo es einen passenden Begriff gibt, mit
  **Iconclass** verknüpft (`iconclass_notation` in `elements.json`; 297 von
  374). Jede Notation ist gegen die Iconclass-Schnittstelle geprüft;
  inoffizielle Klammerschlüssel werden nicht verwendet.
- Die annotierten Inschriften sind über ihre **EDH-Nummer** referenziert;
  die Konkordanz zu **Trismegistos** und **EDCS** liegt im
  Veröffentlichungspaket (`inscription_identifiers.csv`).

---

