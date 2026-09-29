# Projektbeschreibung

**NLP-gestützte Erschließung von Metadaten in epigraphischen Datenbanken: Vokabular,
Goldstandard und Methodenvergleich geprüft am Datensatz der Epigraphischen Datenbank Heidelberg (EDH)**

Lisa Kilbinger, Philipps-Universität Marburg. Version 1.0, September 2026.
DOI: [DOI] · Technische Dokumentation: [README](readme_kurz.de.md)

Die Datenpublikation ist im Rahmen der HERMES-Forschungsstudie
[„NLP-gestützte Erschließung von Metadaten in epigraphischen Datenbanken“](https://www.hermes-hub.de/forschen/forschungsstudien/2026/IEG/nlp-gest%C3%BCtzte-erschlie%C3%9Fung-von-metadaten-in-epigraphischen-datenbanken.html)
(2026, Leibniz-Institut für Europäische Geschichte, IEG) entstanden.

## A. Forschungsfrage und Kontext

Die vorliegende Datenpublikation ist ein Teilprojekt meiner Dissertation im
Bereich Digital Humanities an der Philipps-Universität Marburg. Ziel der
Dissertation ist die systematische Erfassung und Analyse figürlicher
Darstellungen auf spätantiken Grabinschriften. Diese Motive sind wichtige
Zeugnisse einer entstehenden christlichen Ikonographie, wurden jedoch bisher
nicht großflächig ausgewertet. Bearbeitet wurden figürliche Darstellungen
bislang nur in einer Dissertation (Ehler [Jahr]), die sich auf Loculusplatten
aus den stadtrömischen Katakomben beschränkt. Eine systematische,
materialübergreifende Erfassung fehlt.

Bestehende epigraphische Datenbanken erfassen figürliche Darstellungen auf
Inschriftenträgern bislang ausschließlich in unstrukturierter Form: als
Freitext im Kommentarbereich oder als editorische Anmerkung innerhalb der
Transkription. Diese Praxis verhindert eine systematische Auswertung und
maschinelle Verarbeitung der enthaltenen ikonographischen Informationen.
Die vorliegende Datenpublikation testet verschiedene Methoden, um diese
ikonographischen Informationen in strukturierte Daten zu überführen.

## B. Datengrundlage

Herangezogen wurden zwei der größten frei zugänglichen epigraphischen
Datenbanken: Die Epigraphische Datenbank Heidelberg (EDH) liefert die
Kommentartexte für den Methodenvergleich, die Epigraphic Database Bari (EDB,
https://www.edb.uniba.it/) die lateinischen Suchbegriffe des Vokabulars.

**Die EDH.** Die EDH gilt als eine der etabliertesten digitalen Ressourcen
der lateinischen Epigraphik. Sie wurde 1986 aufgebaut, wird seither
kontinuierlich gepflegt und betreut seit 2003 im EAGLE-Verbund (Electronic
Archive of Greek and Latin Epigraphy) die Inschriften der römischen
Provinzen. Sie folgt den FAIR-Prinzipien und stellt ihre Daten unter
CC BY-SA 4.0 bereit. Für Inschriftentyp, Inschriftenträger, Material und
Dekoration verwendet sie die im EAGLE Europeana Project (2013–2015)
entwickelten Vokabulare, die auch in diesem Projekt übernommen werden. Ein
Feld für figürliche Darstellungen gibt es nicht: Vermerkt wird nur, ob Dekor
vorhanden ist; was dargestellt ist, steht allenfalls als Freitext im
Kommentar, zusammen mit Bemerkungen zu Erhaltungszustand, Textinterpretation
u. Ä.

**Abfrage und Umfang.** Die Daten wurden am 6. Mai 2026 über die öffentliche
Programmierschnittstelle (API) der EDH abgerufen (`src/corpus/fetch_edh.py`,
Aufbau des Korpus: `src/corpus/build_corpus.py`):

- abgefragt: Grabinschriften (Inschriftengattung *titulus sepulcralis*),
  deren Datierung in den Zeitraum 150–800 n. Chr. fällt oder ihn berührt,
  dazu undatierte: 22837 Inschriften, bei 6990 davon ist Dekor vermerkt;
- davon mit Kommentar: 12676 (`data/corpus/edh_comments.json`);
- davon später als 150 n. Chr. datiert oder undatiert (Zeitfilter der
  Methoden, `src/common/matching.py`): 11458.

**Bereinigung und Anreicherung.**

- In der API-Antwort sind Anfangs- und Enddatierung teils vertauscht; sie
  werden beim Abruf korrigiert.
- Fehlende Felder (Provinz, Dekor, Personen, Verweise auf Trismegistos und
  EDCS) werden von den Detailseiten der EDH ergänzt.
- Für die Veröffentlichung sind die Daten auf EDH-Nummer, Kommentar und
  Datierung reduziert; die Verweise auf Trismegistos und EDCS sind nur für
  die 1100 annotierten Kommentare enthalten.

**Kritik.**

- Ob und wie ausführlich Darstellungen im Kommentar erwähnt werden, hängt
  von der jeweiligen Bearbeitung ab; die Angaben sind entsprechend
  uneinheitlich.
- Für die Benennung der Dekoration gibt es keinen Standard. Das
  EAGLE-Vokabular „Decoration“ ist recht klein, und für die übrigen
  Darstellungen fehlt ein einheitliches Vokabular.

**Vokabular.** Ein mehrsprachiges ikonographisches Vokabular aus 374
Bildelementen, in Kategorien sortiert, mit Suchbegriffen auf Deutsch,
Latein und Englisch; 354 Motivregeln zur Zuordnung verschiedener Elemente
zu einem ikonographischen Motiv (z. B. Dextrarum Iunctio, Schafträger).

**Normdaten und Fachvokabulare.** Die Bildelemente sind, wo eine
Entsprechung vorhanden ist, mit Iconclass (297 von 374) verknüpft und mit
dem [EAGLE-Vokabular „Decoration“](https://www.eagle-network.eu/voc/decor.html)
(Europeana Network of Ancient Greek and Latin Epigraphy) abgeglichen. Die
Inschriften sind über ihre EDH-Nummer mit Trismegistos (1042 von 1100) und
EDCS (947 von 1100) verknüpft.

**Formate und Lizenz.** Offene Formate (JSON, CSV, UTF-8). Daten unter
CC BY-SA 4.0 (kompatibel mit der EDH-Lizenz), Code unter MIT.

## C. Goldstandard

Die 1100 annotierten Kommentare wurden in drei Stichproben aus derselben
Zufallsfolge (fester Seed) gezogen und überschneiden sich nicht (alle in
`data/goldstandard/`):

| Datei | Kommentare | Rolle |
|---|---|---|
| `edh_devsample.json` | 500 | Entwicklungsdaten: an ihnen wurden Vokabular, Regeln und Methoden entwickelt |
| `edh_former_testsample.json` | 300 | ursprünglich als Testdaten gezogen; beim Annotieren zeigten sich Lücken im Vokabular, die ergänzt wurden. Da das Sample damit zur Entwicklung beigetragen hat, zählt es jetzt zu den Entwicklungsdaten und dient der Fehleranalyse |
| `edh_testsample.json` | 300, davon 70 mit Darstellung | die eigentlichen Testdaten: erst nach Abschluss der Methodenentwicklung gezogen und ausschließlich für die abschließende Messung verwendet |

Die Testdaten wurden nach denselben Richtlinien annotiert wie die
Entwicklungsdaten (`annotation_guidelines_de.md`), ohne Kenntnis der
Methodenergebnisse. Annotiert sind Bildelemente und Motive; Varianten,
Anzahlen und Unsicherheitsangaben sind ebenfalls annotiert, werden aber von
keiner Methode erkannt und nicht bewertet.


## D. Methodenvergleich

### Methoden

| | Methode | Vorgehen | Skript (`src/methods/`) |
|---|---|---|---|
| 1 | Wörterbuchabgleich | Suchbegriffe als Zeichenfolge im Text, ohne sprachliche Analyse; jedes Element ein eigenes Motiv | `m1_dictionary.py` |
| 2 | Lemmatisierung (Stanza) | Abgleich über die Grundform, Komposita; Motive je Satz | `m2_nlp_lemma.py` |
| 3 | Satzanalyse (Dependency Parsing, Stanza) | Erkennung wie 2; Motive je grammatisch verbundener Wortgruppe, mehrdeutige Wörter nach Kontext | `m3_dependency_chunked.py` |
| 4 | BERT (deepset/gbert-base) | feinabgestimmte Wortklassifikation, drei Trainingsläufe | `m4_bert.py` |

Alle Methoden nutzen dieselben Bausteine (`src/common/`), damit Unterschiede
allein auf Elementerkennung und Gruppierung zurückgehen:

- `matching.py`: Zeitfilter, Aufbereitung des Vokabulars, False Friends,
  Komposita, Mehrwortausdrücke, Zahlwörter, Signalwörter;
- `motifs.py`: Ableitung der Motive aus den gefundenen Elementen über
  `motif_rules.json` und Umwandlung von Formwörtern in Varianten.

**Methode 4 (BERT)** erfordert als lernende Methode zusätzliche Festlegungen:

- **Aufgabe:** Wortklassifikation (Token Classification). Jedes Wort erhält
  kein, ein oder mehrere Element-Labels; jede im Training vorkommende
  Labelkombination ist eine eigene Klasse. Die Motive werden wie bei
  Methode 2 je Satz über `motifs.py` aus den Labels abgeleitet. Methode 4
  unterscheidet sich also nur in der Elementerkennung.
- **Trainingsdaten:**
  - die 500 Entwicklungskommentare, wortweise markiert
    (`edh_devsample_word_markings.json`, aus den Annotationen abgeleitet und
    von Hand geprüft);
  - ein **Silberstandard** (`m4_bert.py silver`): 2137 nicht annotierte
    Kommentare, in denen Methode 2 und 3 dieselben Elemente finden, nach
    derselben Logik markiert, dazu 500 Kommentare, die beide Methoden als
    „keine Darstellung“ einstufen. Der Silberstandard gleicht die geringe
    Menge an Handannotation aus. Er ist nicht von Hand geprüft und übernimmt
    daher die Lücken der Methoden 2 und 3. Alle drei annotierten Stichproben
    sind aus ihm ausgeschlossen.
- **Feste Einstellungen:** 2 Epochen, Lernrate 5·10⁻⁵, Stapelgröße 16, im
  von Devlin et al. (2019) empfohlenen Bereich. Die Einstellungen wurden
  nicht systematisch optimiert: Dafür wären eigene Validierungsdaten und
  mehrere Läufe je Einstellung nötig gewesen.
- **Drei Trainingsläufe:** Das Ergebnis hängt vom Zufall im Training ab
  (Anfangsgewichte, Reihenfolge der Beispiele). Methode 4 wurde daher dreimal
  mit identischen Daten und Einstellungen trainiert, die sich nur im Seed
  unterscheiden (42, 43, 44). Jeder Lauf wurde einmal gemessen. Berichtet
  wird der Mittelwert; in den Bootstrap geht das Mittel der drei Läufe ein.
  Prüfsummen der Modelle und des Silberstandards stehen in
  `data/method_comparison/m4_bert_runs.json`.

### Versuchsaufbau

**Einmalige Messung.** Vokabular, Regeln, Code und die Einstellungen von
Methode 4 wurden vor der Annotation der Testdaten festgeschrieben. Jede
Methode wurde einmal auf die Testdaten angewandt; nichts wurde anhand der
Testdaten ausgewählt oder angepasst.

**Bewertung.** Precision, Recall und F1 auf drei Ebenen:

1. **Darstellung:** Enthält der Kommentar eine figürliche Darstellung (ja/nein)?
2. **Bildelemente:** Welche Bildelemente kommen im Kommentar vor? Gezählt
   wird jedes Element einmal je Kommentar, unabhängig von der Anzahl.
   Angegeben werden zwei Mittelwerte:
   - *Mikro-Mittel* über alle Vorkommen: häufige Elemente (z. B. Büste)
     bestimmen den Wert;
   - *Makro-Mittel* über die Elementtypen: jeder Typ zählt gleich, seltene
     Elemente fallen also stärker ins Gewicht.
3. **Motive:** Ein Motiv gilt nur als richtig, wenn Elementmenge und
   Kategorie genau mit dem Goldstandard übereinstimmen.

**Unsicherheit.** Mit 300 Testkommentaren hängen alle Werte auch davon ab,
welche Kommentare zufällig in der Stichprobe gelandet sind. Aus den 300
Testkommentaren werden daher 10000-mal 300 Kommentare mit Zurücklegen
gezogen und alle Maße nach denselben Regeln neu berechnet. Der 95-%-Bereich
reicht vom 2,5. bis zum 97,5. Perzentil (Efron/Tibshirani 1993). Der Zufall
ist über einen festen Startwert festgelegt; dieselben Methodenausgaben
ergeben also immer dieselben Bereiche.

Für den Vergleich zweier Methoden wird der Abstand ihrer Werte auf jeweils
derselben gezogenen Stichprobe berechnet (gepaarter Vergleich). Schließt der
Bereich des Abstands 0 aus, ist der Unterschied nicht allein durch die
Stichprobenauswahl zu erklären. Statt p-Werten werden diese Bereiche
berichtet, weil sie neben der Richtung auch die Größe des Unterschieds zeigen.

### Ergebnisse

F1 in % auf den 300 Testkommentaren (70 mit Darstellung), darunter klein
der 95-%-Bereich (`data/method_comparison/scores.csv`). Für Methode 4 steht
der Mittelwert der drei Trainingsläufe (Einzelwerte in
`data/method_comparison/bootstrap.json`):

| | 1 Wörterbuch | 2 Lemmatisierung | 3 Satzanalyse | 4 BERT |
|---|:---:|:---:|:---:|:---:|
| **Darstellung** | 97,2<br><sub>94,1–99,4</sub> | 98,6<br><sub>96,3–100</sub> | 98,6<br><sub>96,3–100</sub> | 96,1<br><sub>93,2–98,4</sub> |
| **Elemente, Mikro** | 84,6<br><sub>79,0–89,4</sub> | 91,8<br><sub>86,5–96,0</sub> | 92,5<br><sub>88,1–96,3</sub> | 83,3<br><sub>77,1–89,3</sub> |
| **Elemente, Makro** | 73,1<br><sub>67,0–83,2</sub> | 77,8<br><sub>71,4–88,4</sub> | 80,8<br><sub>75,0–89,5</sub> | 64,2<br><sub>58,0–77,1</sub> |
| **Motive** | 52,7<br><sub>43,0–62,7</sub> | 73,9<br><sub>64,5–82,7</sub> | 73,5<br><sub>64,0–82,6</sub> | 66,7<br><sub>57,7–76,0</sub> |

Ob ein Abstand zwischen zwei Methoden belegt ist, zeigt der gepaarte
Vergleich: Belegt ist er, wenn sein 95-%-Bereich 0 ausschließt (Werte in
`data/method_comparison/differences.csv`).

- **Belegt:** Methode 2 und 3 liegen vor Methode 4 bei den Elementen
  (Mikro +8,5 bzw. +9,3 Punkte, Makro +13,6 bzw. +16,6) und bei den Motiven
  (+7,2 bzw. +6,9). Methode 2 liegt vor Methode 1 bei den Elementen (Mikro
  +7,2) und vor allem bei den Motiven (+21,2).
- **Nicht belegt:** alle Abstände bei der Frage, ob eine Darstellung
  vorliegt; alle Abstände zwischen Methode 2 und 3; der Abstand zwischen
  Methode 2 und 1 beim Makro-Mittel.

### Diskussion und Fehleranalyse

**Darstellung vorhanden.** Ob ein Kommentar überhaupt eine Darstellung
beschreibt, erkennen alle vier Methoden etwa gleich gut. Alle finden
sämtliche 70 Darstellungen (Recall 100 %); die Unterschiede entstehen allein
durch Fehlalarme (Methode 1: 4, Methode 2 und 3: je 2, Methode 4: 3 bis 8
je Lauf). Kein Abstand ist belegt. Für eine Vorauswahl der Kommentare mit
Darstellung genügt damit bereits der einfache Wörterbuchabgleich.

**Methode 1.** Methode 1 findet die Elemente recht zuverlässig (Mikro 84,6),
liegt beim Motiv aber gut 21 Punkte hinter Methode 2. Das liegt vor allem an
der fehlenden Gruppierung: Jedes Element wird ein eigenes Motiv, sodass etwa
„Büste eines Mannes und einer Frau“ drei Einzelmotive statt eines
Ehepaar-Porträts ergibt. Hinzu kommen Treffer in Wortteilen (z. B.
„**Frau**ennamen“ → Frau), da die Methode keine Wortgrenzen und Grundformen
kennt.

**Methode 2 und 3.** Bei Elementen und Motiven liegen die beiden
Stanza-basierten Methoden vorn. Die Lemmatisierung erkennt Wörter über ihre
Grundform und an Wortgrenzen und vermeidet so die meisten Teilwort-Treffer
der Zeichenfolgensuche.

Bei den Motiven sind Methode 2 und 3 gleichauf (+0,3 [−1,8; +2,8]). Die
grammatische Gruppierung von Methode 3 bringt gegenüber der Gruppierung je
Satz keinen messbaren Vorteil. Das liegt an der Textsorte: EDH-Kommentare
sind knappe Aufzählungen („im Giebel Delphine; darunter Kranz“), ein Satz
ist meist schon eine Bildeinheit. Zugleich ist die Satzanalyse bei solchen
Satzfragmenten unzuverlässig. Standardmodelle für die Satzanalyse lassen
sich also nicht ohne Weiteres auf Fachtext im Telegrammstil übertragen.

Bei den Elementen liegt Methode 3 leicht vorn (Makro +3,0). Sie nutzt
dieselbe Elementerkennung wie Methode 2 und verwirft zusätzlich über
Kontextregeln einzelne Fehltreffer, etwa „Steuerruder“ aus
„Glaubensbrüder“. Deshalb ist sie in keiner Bootstrap-Stichprobe
schlechter als Methode 2. Weil die obere Grenze des Bereichs genau bei 0
liegt, ist der Vorsprung aber klein und nicht gesichert.

Restfehler beider Methoden: Die Zerlegung von Komposita geht teils zu weit
und komplexe Gruppen wie mythologische Figuren, Familien oder Motive über
Satzgrenzen hinweg werden verfehlt.

**Methode 4.** Methode 4 liegt bei Elementen und Motiven hinter Methode 2
und 3 (Motive rund 7 Punkte), und zwar in allen drei Trainingsläufen.
Seltene Elemente kommen im Training zu selten vor und werden kaum erkannt
(Makro 64,2). Außerdem lernt das Modell eher Wortfelder als
Bildbeschreibungen: Ein Personenwort wie „Sohn“ oder ein christlicher
Kontext wie „Martyrium“ führt schon zu einem Treffer, auch wenn keine
Darstellung beschrieben ist. Hinzu kommt, dass der größte Teil der
Trainingsdaten aus dem Silberstandard stammt; Methode 4 übernimmt damit die
Lücken der Methoden 2 und 3. Vor Methode 1 liegt sie beim Motiv, weil sie
wie Methode 2 je Satz gruppiert.

Für die Übertragbarkeit folgt daraus: Bei wenig handannotierten Daten lohnt
ein sorgfältig gebautes regelbasiertes Verfahren mehr als ein
feinabgestimmtes Sprachmodell.

### Grenzen

- **Kleine Testdaten:** Mit 70 Kommentaren mit Darstellung sind die
  Bereiche breit (Motive rund ±9 Punkte). Abstände unter etwa 5 Punkten
  sind nicht nachweisbar.
- **Makro-Bereiche:** Das Makro-Mittel beruht auf vielen Elementtypen mit
  ein oder zwei Belegen. In vielen Bootstrap-Stichproben fehlen solche
  seltenen Typen ganz, und mit ihnen ihre meist schlechten Werte. Deshalb
  liegen die Bereiche überwiegend über dem Punktwert (z. B. Methode 4:
  64,2 [58,0–77,1]). Sie sind nur ein grober Anhaltspunkt.
- **Methode 4:** drei Läufe, Einstellungen nicht abgestimmt; der
  Silberstandard überträgt die Lücken der Methoden 2 und 3.
- **Nicht bewertet:** Varianten, Anzahlen und Unsicherheitsangaben sind
  annotiert, werden aber von keiner Methode erkannt.

### Ausblick

- **Kombination der Methoden**, etwa als Vereinigung (höherer Recall), als
  Mehrheitsentscheidung (höhere Precision), als Verbindung der
  Elementerkennung von Methode 3 mit der Satzgruppierung von Methode 2 oder
  mit Methode 4 als Ergänzung für nicht im Vokabular enthaltene Ausdrücke.
- Zweite, unabhängige Annotation eines Teils der Testdaten und größere
  Testdaten; nach Änderungen an den Methoden sind neue Testdaten
  erforderlich.
- Methode 4: Training ohne Silberstandard bzw. mit reduzierter
  Handannotation, Abstimmung der Einstellungen.
- Eine Methode auf Basis großer Sprachmodelle.
- Erkennung und Bewertung von Varianten, Anzahlen und Unsicherheit.

## E. Reproduzierbarkeit

Der Weg von den Daten zum Ergebnis:

1. **Daten:** EDH-Kommentare (`data/corpus/`), Vokabular (`data/gazetteer/`),
   Goldstandard (`data/goldstandard/`).
2. **Methoden 1–3 über alle Kommentare** → `results/full_corpus/`.
3. **Methode 4:** Silberstandard aus den Ergebnissen von Methode 2 und 3,
   Training mit drei Seeds.
4. **Messung:** alle Methoden einmal auf den Testdaten
   (`measure_testsample.py`) → `predictions/`.
5. **Bewertung:** Precision, Recall, F1 (`evaluate.py`), Bereiche und
   gepaarte Abstände (`bootstrap.py`), Tabellen (`comparison_tables.py`).
6. **Erste Auswertung:** Abbildungen (`motif_groups.py`).

Die veröffentlichte Messung liegt in `data/method_comparison/` und lässt sich
ohne eigenen Lauf prüfen (`--published`). Befehle und Laufzeiten: siehe
[README](readme_kurz.de.md#installation-und-reproduktion).

Beim Nachrechnen sind geringe Abweichungen möglich: Die Satzanalyse von
Stanza ist nicht in jedem Fall deterministisch (Methode 3), und ein
BERT-Training auf anderer Hardware ergibt nicht bitgenau dieselben Gewichte.

## F. Nachnutzungspotenzial

Ziel ist, ikonographische Angaben, die bisher nur als Freitext vorliegen,
als strukturierte Metadaten nachnutzbar zu machen, und zwar nach den
FAIR-Prinzipien:

- **Normdaten und Fachvokabulare:** Verknüpfung der Bildelemente (wo
  Entsprechung vorhanden) mit Iconclass und dem EAGLE-Vokabular
  „Decoration“, Verknüpfung der Inschriften über ihre EDH-Nummer mit
  Trismegistos und EDCS.
- **Datenqualität:** Goldstandard mit Annotationsrichtlinien, getrennte
  Entwicklungs- und Testdaten, Werte mit Unsicherheitsbereichen.
- **Zugang:** DOI je Version über Zenodo, offene Formate (JSON, CSV, UTF-8),
  Metadaten in `.zenodo.json` und `CITATION.cff`.
- **Nachnutzung:** Daten unter CC BY-SA 4.0 (kompatibel mit der EDH-Lizenz),
  Code unter MIT; der Workflow ist auf andere epigraphische und
  (kunst-)historische Datenbanken übertragbar.

### Beispiel: erste Auswertung

Eine vorläufige Auswertung aller EDH-Kommentare mit Methode 2 ist in
`figures/` dokumentiert (`src/analysis/motif_groups.py`). Methode 2 hat das
höchste Motiv-F1, liegt damit aber gleichauf mit Methode 3. Die Werte
stammen aus einem eigenen Lauf (`results/full_corpus/m2_nlp_lemma.json`,
nicht versioniert) und sind entsprechend vorläufig. Motivgruppen sind die
Unterkategorien des Kategorienbaums. Unter den 2520 Kommentaren mit
Darstellung überwiegen weltliche Figuren und Porträts (43 %) und
christliche Symbole (16 %).

![Die zehn häufigsten Motivgruppen](figures/motif_groups_top10_de.png)

Im zeitlichen Verlauf (jeder Kommentar gleichmäßig über seinen
Datierungszeitraum verteilt) gehen weltliche Figuren und Porträts ab etwa
300 n. Chr. zurück, während der Anteil christlicher Symbole bis zum
6. Jahrhundert auf über 80 % steigt. Ab 300 n. Chr. umfasst jeder Abschnitt
nur 67–96 Kommentare.

![Die fünf häufigsten Motivgruppen im zeitlichen Verlauf](figures/motif_groups_timeline_de.png)

### Ausblick: nächste Schritte in der Dissertation

- **Weitere Datenbanken:** Als Nächstes wird die EDB einbezogen. Sie
  kennzeichnet Bildbeschreibungen in der Transkription mit doppelten Klammern
  `((…))` (9531 Inschriften); diese Phrasen lassen sich direkt in die
  Bildelemente des Vokabulars zerlegen. EDH und EDB werden über die
  Trismegistos-Nummer zu einem gemeinsamen Datenbestand verbunden. Darüber
  hinaus sollen weitere Datenbanken abgefragt werden, etwa die Epigraphic
  Database Roma (EDR) und die Epigraphik-Datenbank Clauss/Slaby (EDCS), um
  stadtrömische und christliche Inschriften breiter abzudecken.
- **Methode 5:** ein Verfahren auf Basis großer Sprachmodelle, gemessen auf
  denselben Testdaten wie die Methoden 1–4.
- **Auswertung:** Häufigkeit, Kombination sowie chronologische und regionale
  Verteilung der Motive über den gesamten Datenbestand, auch im Vergleich
  mit den Ergebnissen für die stadtrömischen Katakomben (Ehler [Jahr]).
- **Übertragbarkeit:** Prüfung, ob der Methodenvergleich auch für andere
  Datenbanken mit Freitext-Metadaten gilt (Archive, Sammlungskataloge,
  Objektdatenbanken), wenn Textstil, Sprache oder Fachvokabular wechseln.
- **Vokabular:** Ausbau der Normdaten (Wikidata, Getty AAT), Elemente ohne
  Iconclass-Entsprechung, fehlende EAGLE-Begriffe.

## Literatur

- Devlin, J. et al. (2019): BERT: Pre-training of Deep Bidirectional
  Transformers for Language Understanding. NAACL-HLT 2019.
- Efron, B./Tibshirani, R. J. (1993): An Introduction to the Bootstrap. New
  York/London: Chapman & Hall.
- Ehler, [Vorname] ([Jahr]): [Titel der Dissertation zu figürlichen
  Darstellungen auf Loculusplatten]. [Ort].
