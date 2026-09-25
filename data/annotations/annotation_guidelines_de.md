# Annotationsrichtlinien EDH

Stand: 2026-09-25. Gilt für den Goldstandard (Entwicklungsdaten,
`data/goldstandard/edh_goldstandard.json`) und die Teststichprobe
(`data/goldstandard/edh_teststandard.json`). Fasst die Entscheidungen
zusammen, die bei Aufbau und Migration des Goldstandards getroffen wurden
(Details und Begründungen: `docs/edh_methoden.md`,
`docs/ausgeschlossene_vokabeln.md`, `docs/architektur.md`).

## Vorgehen bei der Teststichprobe

- Annotiert wird **ohne Ergebnisse der Methoden**. Jede Zeile startet mit
  einer Voreannotation durch Claude (nur aus Kommentartext und dieser
  Richtlinie) und zählt erst nach ausdrücklicher Prüfung
  (`data/goldstandard/edh_teststandard_annotator.html`, erzeugt von
  `src/edh/build_annotator.py`; Begründung und Einschränkungen:
  Verschriftlichung 7.1).
- Annotiert wird, was der **Kommentar sagt**, nicht was auf dem Stein
  vermutlich zu sehen ist. Kein Ergänzen aus eigenem Wissen über das
  Monument.
- Die Teststichprobe wird nach Abschluss nicht mehr zur Fehleranalyse
  oder zum Nachbessern der Methoden verwendet (Verschriftlichung, 7.1).

## 1. Darstellung ja/nein

**Ja**, wenn der Kommentar eine bildliche Darstellung oder Verzierung auf
dem Denkmal beschreibt – auch ohne benennbares Element („Oberhalb der
Inschrift Reliefreste“: Ja, keine Elemente). Auch ein Kreuzzeichen
innerhalb des Schriftfeldes oder einer Zeile ist eine Darstellung („Z. 1
hinter M lateinisches Kreuz“ → `latin_cross`; Lisa 2026-09-25).

**Nein**, wenn der Kommentar nur Folgendes beschreibt:

- den Inschriftträger selbst („Fragment einer Tafel“, „Statuenbasis“,
  „Cupa“, „Aschenkiste“),
- die architektonische Rahmung des Inschrift- oder Bildfeldes
  (Profilrahmen, „Inschriftfeld von Säulen eingefasst“, „Bildfeld von
  Halbsäulen eingefasst“, Pilaster, Bögen, tabula ansata). Rahmende oder
  flankierende Architekturelemente sind nie ein Element (Lisa 2026-09-25).
  Alles andere, was rahmt (Ranken, Voluten, Eroten …), ist ein normales
  Element mit Variante `framing` (Abschnitt 4),
- Worttrenner (Hedera), Buchstabenformen, Ligaturen, Lesungen,
  Fundumstände, Maße, Literatur.

## 2. Elemente

- **Ein Eintrag pro Elementtyp und Kommentar**, die Anzahl steht im Feld
  *Anzahl*: Zahlwort oder Ziffer → diese Zahl („zwei Delphine“ → 2);
  Plural ohne Zahl → „>1“ („Delphine“); sonst 1.
- **Das spezifischste vorhandene Element** wählen („Taube“ → `dove`, nicht
  `bird`; „Palmzweig“ → `palm_branch`, nicht `branch`).
- **Ein Wort kann mehrere Elemente tragen** („Hasenjagd“ → `hare` +
  `hunt`), aber eine dargestellte Sache ist nur ein Element („stehende
  Figur“ ist eine Ganzfigur; „Frauenporträt“ ist `woman` im Motiv
  `portrait_unspecified_woman`).
- **unsicher** ankreuzen, wenn der Kommentar die Deutung selbst als
  unsicher kennzeichnet („(?)“, „wohl“, „vielleicht“, „möglicherweise“).
- **Nicht annotiert** werden: Hedera, tabula ansata, Cupa, Basis (keine
  Elemente mehr). Tafel, Turm, Kreis, Altar, Säule, Kopf nur, wenn wirklich
  eine *Darstellung* gemeint ist, nicht der Träger, der Fundort, eine
  Formbeschreibung oder die Rahmung des Inschriftfeldes (Tafel etwa, wenn
  sie von Eroten gehalten wird).
- **Formen, die verändern, *was* dargestellt ist, sind eigene Elemente**,
  keine Varianten: Kreuzarten (griechisches, lateinisches Kreuz,
  Andreaskreuz = `decussis` …), Chi-Rho, radiales Chi-Rho, Christogramm im
  Kreis, Staurogramm im Kreis, Speichenrad.

## 3. Personen

- **Eine dargestellte Figur = ein Element** (Entscheidung 2026-09-24).
  Das Element ist die Person: `man`, `woman`, `boy`, `girl`, `child`,
  `person` (Geschlecht nicht genannt, „Erwachsener“). „Ehepaar“ ist
  `man` + `woman`, je 1 (seit 2026-09-25; vorher ein eigenes Element
  `couple`). **Kein Default Mann**: ohne Geschlechtsangabe
  `person`.
- **Die Darstellungsform ist die Variante der Person**, nicht ein eigenes
  Element: „weibliche Büste“ → `woman` mit Variante `bust`; „Büsten eines
  Mannes, einer Frau und eines Kindes“ → drei Elemente, je mit `bust`.
  - `bust`: Büste, Brustbild, Bruststück, Halbfigur, Bildniskopf,
    Porträtkopf
  - `clipeus`: Büste in Clipeus/Medaillon („Porträtmedaillon“). Ein
    Medaillon **ohne** Figur darin ist nur Rahmen und bleibt ein eigenes
    Element `clipeus` (Kategorie `framing_other`).
  - `orant`
  - `full_figure`: Figur, Ganzfigur – **und jede stehende Person** („stehender
    Mann“ = Ganzfigur)
  - `head`: Kopf, wenn ein dargestellter Kopf gemeint ist („im Bildfeld noch
    der Kopf eines Mannes“). Steht daneben ein anderes Formwort, benennt
    „Kopf“ nur den erhaltenen Teil („Ganzfiguren …, von denen noch die Köpfe
    erhalten sind“ → nur `full_figure`).
- **Form ohne Personenangabe** → so viele `person`, wie Figuren genannt sind
  („zwei Büsten“ → `person` ×2, `bust`; „Medaillon mit 5 Büsten“ → `person`
  ×5, `clipeus`).
- **„Porträt“ und „dextrarum iunctio“ sind keine Elemente**, sie stecken in
  der Motivkategorie (`portrait_…`, `portrait_dextrarum_iunctio`).
- **Tierköpfe** gehören zum Tier („Widderkopf“ → `ram`, „caput agni“ →
  `sheep`). „Bärtiger Kopf mit Widderhörnern“ → `head` (bärtig) +
  `ram_horn`, Motiv Jupiter Ammon – hier bleibt `head` ein Element, weil
  es kein Porträt ist.

## 4. Varianten

- Varianten beschreiben, **wie** etwas dargestellt ist: Darstellungsform
  (s.o.), bärtig, stehend, sitzend, liegend, tanzend, trauernd, erhoben /
  gesenkt (Fackel), nach links / nach rechts, kanneliert,
  norisch-pannonisch, sechsstrahlig, spiegelverkehrt, fragmentarisch,
  rahmend. „Stilisiert“ wird nicht annotiert.
- **Rahmend** (`framing`, Lisa 2026-09-25): für nicht-architektonische
  Elemente, die das Inschrift- oder Bildfeld einfassen oder flankieren oder
  auf dem Rahmen bzw. rahmenden Säulen sitzen („Inschriftfeld von
  Efeuranken gerahmt“ → `ivy_tendril`, `framing`; „Inschriftfeld von zwei
  Eroten flankiert“ → `putto`, `framing`). Das Element bleibt in seiner
  normalen Kategorie (`vegetal_ornament`, `secular_figures` …); eine eigene
  Rahmen-Kategorie gibt es nicht mehr.
- Die Variante steht beim Element der dargestellten Figur.
- Mehrere Varianten an einem Element sind möglich („stehender bärtiger
  Mann“ → `man`: `standing`, `bearded`, `full_figure`).

## 5. Motive

- **Jedes Element gehört zu genau einem Motiv.** Elemente, die zusammen ein
  Bild ergeben, bilden ein Motiv; alle übrigen bilden je ein eigenes Motiv
  mit der Kategorie des Elements (mehrere gleichartige übrige Elemente:
  ein Motiv).
- **Die spezifischste passende Kategorie** wählen.
- **Porträts** (Personen ohne szenische Handlung): Kategorie nur nach
  Personengruppe, z.B. `portrait_couple`, `portrait_man`,
  `portrait_group` – **immer ein Motiv** für die ganze Gruppe. Die
  Darstellungsform steht nicht in der Kategorie, sondern als Variante bei
  den Personen („drei Büsten“ → ein Motiv `portrait_group` mit `person` ×3,
  Variante `bust`).
  - **Paare, Familien, Gruppen sind immer Porträts**, auch ohne Formwort.
  - Personengruppen: Paar (zwei Personen, auch „zwei Büsten“ ohne
    Geschlecht), Familie (zwei Erwachsene – Mann + Frau oder ohne
    Geschlechtsangabe – mit Kind/ern), Mann bzw. Person mit Kind, Gruppe
    (drei oder mehr Erwachsene, auch gemischt: „Büsten einer Frau und
    dreier Männer“ → ein Motiv `portrait_group`).
  - Nackter Knabe = Eros (`putto`, Variante `nude`).
  - Paar in der dextrarum iunctio (Handschlag, auch aus Attributen
    erschlossen) → `portrait_dextrarum_iunctio`.
  - **Einzelperson ohne Form- oder Porträtwort** → `figure_unspecified`
    (könnte Teil einer Szene gewesen sein).
  - **Attribute** (Gegenstände, die eine Figur hält: Rolle, Beutel,
    Spiegel, Buch, Spinnrocken, Spindel; auch getragener Schmuck: Torques,
    Armreif – Lisa 2026-09-25) gehören ins Motiv der Figur, die
    Kategorie bleibt die der Figur („Frau mit Spiegel“ → `portrait_woman`
    [woman, mirror]; „Diener mit Buchrolle“ → `secular_figures` [servant,
    scroll]). Die früheren Kategorien `portrait_with_pouch`/`_scroll`
    entfallen (2026-09-25).
- **Szenen** gehen vor Porträts: Personen in einer Handlung gehören zur
  Szenenkategorie (Mahlszene → `funerary_banquet`, Ochsenkarren mit
  Gespannführer → `field_work`, Knabe mit Ball, Beruf, biblische Szene …).
- Feste Kombinationen: Kopf + Widderhörner → `jupiter_ammon`; Eroten
  oder Genius + gehaltene Tafel → `tablet_held_by_erotes`; Adler im Kranz
  → `eagle_in_wreath`; Tiere in einer Reihe/Handlung → `animal_scene`; Jagd
  + gejagte Tiere → `hunting_scene` („Hasenjagd“); Lorbeer, Ölzweig oder
  Efeu + Kranz → `wreaths` („Lorbeerkranz“); Vogel mit
  Zweig/Blüte, Christogramm im Kranz usw. nach `motif_rules.json`.
- Elemente, die im Kommentar räumlich getrennt beschrieben sind („von
  Tauben flankiertes Staurogramm, darüber Vase“), bilden **getrennte
  Motive**, auch wenn eine Regel sie verbinden könnte. Ausnahme Personen:
  Mann und Frau auf den beiden Nebenseiten bleiben ein Paar (HD042390).
