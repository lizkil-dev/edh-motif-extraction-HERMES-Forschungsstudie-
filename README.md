# edh-motif-extraction

**NLP-gestützte Erschließung von Metadaten in epigraphischen Datenbanken**

*Figürliche Darstellungen auf spätantiken Grabinschriften: Ikonographisches
Vokabular, Goldstandard und Methodenvergleich am Datensatz der EDH*

Lisa Kilbinger, Philipps-Universität Marburg. Version 1.0, September 2026.
DOI: [DOI]

*[English version](README.en.md)*

## Kontext

Figürliche Darstellungen auf spätantiken Grabinschriften sind wichtige
Zeugnisse einer entstehenden christlichen Ikonographie, wurden bisher jedoch
nicht großflächig ausgewertet. Epigraphische Datenbanken erfassen sie nur
unstrukturiert und uneinheitlich: als Freitext im Kommentarbereich oder als
editorische Anmerkung innerhalb der Transkription. Diese Erfassungspraxis
verhindert eine systematische Auswertung dieser Bildmotive.

Die vorliegende Datenpublikation ist im Rahmen des
[HERMES-Forschungsstudienprogramms][hermes] entstanden. Sie evaluiert
vergleichend automatisierte Verfahren zur Überführung ikonographischer
Informationen in strukturierte Daten: vom regelbasierten Wörterbuchabgleich
über linguistische Analysen bis zu einem feinabgestimmten Sprachmodell. Der
Vergleich stützt sich auf ein eigens entwickeltes ikonographisches Vokabular
und einen von Hand annotierten Goldstandard. Die Ergebnisse zeigen Stärken und
Grenzen der einzelnen Ansätze auf und schaffen damit die Grundlage für eine
umfassende Analyse der frühchristlichen Bildkunst auf Inschriftenträgern.

## Inhalt

Dieses Repositorium enthält dafür:

- ein mehrsprachiges **ikonographisches Vokabular**: 374 Bildelemente in
  einem Kategorienbaum, Suchbegriffe auf Deutsch, Latein und Englisch,
  354 Motivregeln; verknüpft mit Iconclass (297 von 374) und abgeglichen mit
  dem EAGLE-Vokabular „Decoration“;
- einen **Goldstandard** aus 1100 zufällig gezogenen, von Hand annotierten
  EDH-Kommentaren (800 Entwicklungs-, 300 Testdaten) mit Konkordanz zu
  Trismegistos (1042) und EDCS (947);
- **vier Methoden** zur automatischen Erkennung der Motive
  (Wörterbuchabgleich, Lemmatisierung, Satzanalyse, BERT) und den
  **Methodenvergleich** auf den 300 Testkommentaren, mit vollständigem Code
  zur Reproduktion aller Werte.

## Datengrundlage

Als Datengrundlage dienen die Kommentarspalten der Epigraphischen Datenbank
Heidelberg (EDH). Die EDH gilt als eine der etabliertesten digitalen
Ressourcen der lateinischen Epigraphik. Sie folgt den FAIR-Prinzipien und
stellt ihre Daten unter CC BY-SA 4.0 bereit. Ein eigenes Feld für figürliche
Darstellungen gibt es nicht; Erwähnungen von Bildmotiven finden sich lediglich
als Freitext in der Kommentarspalte, zusammen mit Bemerkungen zu
Erhaltungszustand, Textinterpretation u. Ä.

**Abfrage und Umfang.** Die Daten wurden am 6. Mai 2026 über die
öffentliche Programmierschnittstelle (API) der EDH abgerufen:

- 22.837 Grabinschriften (Inschriftengattung „titulus sepulcralis“), deren
  Datierung in den Zeitraum 150–800 n. Chr. fällt oder ihn berührt
- davon mit Kommentarspalte: 12.676 (`data/corpus/edh_comments.json`)
- davon später als 150 n. Chr. datiert oder undatiert (Zeitfilter der
  Methoden): 11.458

**Bereinigung.** In der API-Antwort sind Anfangs- und Enddatierung teils
vertauscht; sie werden beim Abruf korrigiert. Für die Veröffentlichung sind
die Daten auf EDH-Nummer, Kommentar und Datierung reduziert; die Verweise
auf Trismegistos und EDCS sind nur für die 1100 annotierten Kommentare
enthalten.

**Datenkritik.** Ob und wie ausführlich Darstellungen im Kommentar erwähnt
werden, hängt von der jeweiligen Bearbeitung ab; die Angaben sind
entsprechend uneinheitlich und folgen mehrheitlich keinem Standard.

## Normdaten und Fachvokabulare

Die Bildelemente sind, wo eine Entsprechung vorhanden ist, mit Iconclass (297
von 374) verknüpft und mit dem EAGLE-Vokabular „Decoration“ (Europeana Network
of Ancient Greek and Latin Epigraphy) abgeglichen. Dieses Vokabular wurde im
EAGLE Europeana Project (2013–2015) entwickelt und wird auch von der EDH
verwendet. Es umfasst jedoch nur wenige Begriffe; für die Mehrheit der
Darstellungen fehlt ein einheitliches Vokabular. Die Inschriften sind über
ihre EDH-Nummer mit Trismegistos (1042 von 1100) und EDCS (947 von 1100)
verknüpft.

## Daten und Dateien

Alle Daten als JSON oder CSV (UTF-8).

```
data/
  corpus/
    edh_comments.json         EDH-Kommentartexte (Abruf vom 6. Mai 2026)
  gazetteer/                  Vokabular
    rules/                       Motivregeln und Varianten
    filters/                     signal_words, stoplist, false_friends, compound_exceptions
    categories.json           Kategorienbaum
    element_synonyms.json     Synonyme, mehrsprachig (de, la, en)
    elements.json             Vokabelliste
  goldstandard/               von Hand annotierte Kommentare, Richtlinien, Konkordanz
  method_comparison/          veröffentlichte Messung auf den Testdaten
    predictions/                 Ausgaben der Methoden: m1_dictionary.json … m4_bert_seed44.json
    bootstrap.json               Berechnung der statistischen Unsicherheit der Ergebnisse
    scores.csv, differences.csv  Ergebnistabellen
    m4_bert_runs.json            Prüfsummen und Trainingszeit der BERT-Läufe
src/
  paths.py                     alle Dateipfade und Dateinamen
  corpus/                      Abruf aus der EDH und Aufbau des Korpus
  common/                      von allen Methoden geteilt (matching.py, motifs.py)
  methods/                     die vier Methoden
  evaluation/                  Messung und Auswertung
  analysis/                    erste Auswertung (Abbildungen)
figures/                       Abbildungen zur Veranschaulichung einer ersten Auswertung
results/                       Ergebnisse eigener Läufe (nicht versioniert, wird erzeugt)
  corpus/                        eigener Abruf aus der EDH und daraus gebautes Korpus
  full_corpus/                   Methoden 1–3 über alle Kommentare
  method_comparison/             eigene Messung, aufgebaut wie data/method_comparison/
  bert/                          Silberstandard und Modelle von Methode 4
```

**Goldstandard** (`data/goldstandard/`): Die 1100 annotierten Kommentare
wurden in drei Stichproben aus derselben Zufallsfolge (fester Seed) gezogen
und überschneiden sich nicht.

| Datei | Inhalt |
|---|---|
| `edh_devsample.json` | 500 Kommentare. Entwicklungsdaten: an ihnen wurden Vokabular, Regeln und Methoden entwickelt |
| `edh_former_testsample.json` | 300 Kommentare, ursprünglich als Testdaten gezogen; beim Annotieren zeigten sich Lücken im Vokabular, die ergänzt wurden. Zählt seither zu den Entwicklungsdaten und dient der Fehleranalyse |
| `edh_testsample.json` | 300 Kommentare (70 mit Darstellung). Die eigentlichen Testdaten: erst nach Abschluss der Methodenentwicklung gezogen, ausschließlich für die abschließende Messung verwendet |
| `edh_devsample_word_markings.json` | wortweise Markierungen der Entwicklungskommentare (Trainingsdaten für Methode 4) |
| `annotation_guidelines_de.md` | Annotationsrichtlinien |
| `inscription_identifiers.csv` | Konkordanz EDH – Trismegistos – EDCS |

Die Testdaten wurden nach denselben Richtlinien annotiert wie die
Entwicklungsdaten (`annotation_guidelines_de.md`), ohne Kenntnis der
Methodenergebnisse. Annotiert sind Bildelemente und Motive; Varianten,
Anzahlen und Unsicherheitsangaben sind ebenfalls annotiert, werden aber von
keiner Methode erkannt und nicht bewertet.

## Skripte

| Skript | Funktion |
|---|---|
| `corpus/fetch_edh.py` | ruft die Grabinschriften (150–800 n. Chr.) über die EDH-API ab und korrigiert vertauschte Datierungen |
| `corpus/build_corpus.py` | baut daraus das Korpus: EDH-Nummer, Kommentar und Datierung jeder Inschrift mit Kommentar |
| `methods/m1_dictionary.py` | Methode 1: Wörterbuchabgleich |
| `methods/m2_nlp_lemma.py` | Methode 2: Lemmatisierung (Stanza) |
| `methods/m3_dependency_chunked.py` | Methode 3: Satzanalyse (Stanza), in Teilen; gleiches Ergebnis wie `m3_dependency.py`, weniger Speicher |
| `methods/m4_bert.py` | Methode 4: BERT (deepset/gbert-base); `silver`, `train`, `predict`, `runs` |
| `evaluation/measure_testsample.py` | wendet alle vier Methoden auf die 300 Testkommentare an → `predictions/` |
| `evaluation/evaluate.py` | Precision, Recall und F1 einer Methode gegen Entwicklungs- oder Testdaten |
| `evaluation/bootstrap.py` | 95-%-Bereiche der Werte und der Abstände zwischen den Methoden → `bootstrap.json` |
| `evaluation/comparison_tables.py` | Ergebnistabellen `scores.csv`, `differences.csv` aus `bootstrap.json` |
| `analysis/motif_groups.py` | Abbildungen in `figures/` |

Alle Skripte liegen in `src/`. `evaluate.py` und `comparison_tables.py`
lesen wahlweise einen eigenen Lauf (`results/method_comparison/`) oder mit
`--published` die veröffentlichte Messung (`data/method_comparison/`).

## Ergebnisse auf einen Blick

F1 in % auf den 300 Testkommentaren (70 mit Darstellung); Methode 4 als
Mittelwert von drei Trainingsläufen. 95-%-Bereiche und gepaarte Abstände:
`data/method_comparison/scores.csv` und `differences.csv`.

| | 1 Wörterbuch | 2 Lemmatisierung | 3 Satzanalyse | 4 BERT |
|---|:---:|:---:|:---:|:---:|
| Darstellung | 97,2 | 98,6 | 98,6 | 96,1 |
| Elemente, Mikro | 84,6 | 91,8 | 92,5 | 83,3 |
| Elemente, Makro | 73,1 | 77,8 | 80,8 | 64,2 |
| Motive | 52,7 | 73,9 | 73,5 | 66,7 |

Methode 2 und 3 liegen gleichauf vorn und übertreffen Methode 4 bei Elementen
und Motiven statistisch gesichert. Ob eine Darstellung vorliegt, erkennen alle
vier Methoden etwa gleich gut. Bei geringem Umfang an Handannotationen ist ein
sorgfältig aufgebautes regelbasiertes Verfahren demnach einem feinabgestimmten
Sprachmodell vorzuziehen.

Methodik, Fehleranalyse und Diskussion erscheinen ausführlich im
HERMES-Forschungsbericht (DOI folgt).

## Grenzen

- **Kleine Testdaten:** Da nur 70 Testkommentare eine Darstellung enthalten,
  sind die Bereiche breit (Motive rund ±9 Punkte). Abstände unter etwa 5
  Punkten sind nicht nachweisbar.
- **Makro-Bereiche:** Das Makro-Mittel beruht auf vielen Elementtypen mit nur
  einem oder zwei Belegen. In vielen Bootstrap-Stichproben fehlen solche
  seltenen Typen ganz, und mit ihnen ihre meist schlechten Werte. Deshalb
  liegen die Bereiche überwiegend über dem Punktwert (z. B. Methode 4: 64,2
  [58,0–77,1]). Sie sind nur ein grober Anhaltspunkt.
- **Methode 4:** drei Läufe, Einstellungen nicht abgestimmt; der
  Silberstandard überträgt die Lücken der Methoden 2 und 3.

## Beispiel: erste Auswertung

Eine vorläufige Auswertung aller EDH-Kommentare mit Methode 2 ist in
`figures/` dokumentiert (`src/analysis/motif_groups.py`). Die Werte stammen
aus einem separaten Lauf über alle Kommentare und gehören nicht zur
veröffentlichten Messung. Motivgruppen sind die Unterkategorien des
Kategorienbaums. Unter den 2520 Kommentaren mit Darstellung überwiegen
weltliche Figuren und Porträts (43 %) und christliche Symbole (16 %).

![Die zehn häufigsten Motivgruppen](figures/motif_groups_top10_de.png)

*Die zehn häufigsten Motivgruppen unter den 2520 Kommentaren mit
Darstellung (Methode 2, vorläufig).*

Im zeitlichen Verlauf (jeder Kommentar gleichmäßig über seinen
Datierungszeitraum verteilt) gehen weltliche Figuren und Porträts ab etwa
300 n. Chr. zurück, während der Anteil christlicher Symbole bis zum
6. Jahrhundert auf über 80 % steigt. Ab 300 n. Chr. umfasst jeder Abschnitt
nur 67–96 Kommentare.

![Die fünf häufigsten Motivgruppen im zeitlichen Verlauf](figures/motif_groups_timeline_de.png)

*Die fünf häufigsten Motivgruppen im zeitlichen Verlauf, 150–600 n. Chr.
(Methode 2, vorläufig).*

## Installation und Reproduktion

Python 3.11 oder neuer.

```
pip install -r requirements.txt
python -c "import stanza; stanza.download('de')"

# ohne eigenen Lauf: veröffentlichte Messung prüfen
python src/evaluation/comparison_tables.py --published   # Tabellen
python src/evaluation/evaluate.py m2_nlp_lemma --published  # eine Methode gegen die Testdaten

# optional: Korpus neu aus der EDH abrufen (einige Minuten)
python src/corpus/fetch_edh.py                     # -> results/corpus/edh_titsep_150_800.json
python src/corpus/build_corpus.py                  # -> results/corpus/edh_comments.json

# eigener Lauf
python src/methods/m1_dictionary.py                # Methode 1 (Sekunden)
python src/methods/m2_nlp_lemma.py                 # Methode 2 (ca. 30 min, CPU)
python src/methods/m3_dependency_chunked.py all    # Methode 3 (ca. 60 min)
python src/methods/m4_bert.py silver               # Methode 4: Silberstandard aus 2 und 3
python src/methods/m4_bert.py train                # Methode 4: Training, Seed 42 (ca. 40 min)
python src/evaluation/measure_testsample.py        # alle Methoden auf den Testdaten
python src/methods/m4_bert.py runs                 # Methode 4, Seeds 43 und 44 (ca. 85 min)
python src/evaluation/bootstrap.py                 # Bereiche und gepaarte Abstände
python src/evaluation/comparison_tables.py         # Tabellen
python src/evaluation/evaluate.py m2_nlp_lemma --test  # eine Methode gegen die Testdaten
python src/analysis/motif_groups.py                # Abbildungen (benötigt Methode 2)
```

Die EDH ändert sich laufend; ein neuer Abruf ergibt daher leicht andere Daten
als das veröffentlichte Korpus in `data/corpus/`, auf dem alle berichteten
Werte beruhen. Ein neu gebautes Korpus ersetzt es nicht. Die EDCS-Verweise der
Konkordanz wurden zusätzlich von den EDH-Detailseiten übernommen; dieser
Schritt ist nicht enthalten.

Methoden für `evaluate.py`: `m1_dictionary`, `m2_nlp_lemma`, `m3_dependency`, `m4_bert`.
Der Silberstandard setzt die vollständigen Ergebnisse von Methode 2 und 3
voraus, `bootstrap.py` die Ausgaben von `measure_testsample.py` und
`m4_bert.py runs`. Beim Nachrechnen sind geringe Abweichungen möglich: Die
Satzanalyse von Stanza ist nicht in jedem Fall deterministisch (Methode 3),
und ein BERT-Training auf anderer Hardware ergibt nicht bitgenau dieselben
Gewichte.

## Nachnutzung

- Daten unter CC BY-SA 4.0 (kompatibel mit der EDH-Lizenz), Code unter MIT.
- Vokabular und Goldstandard sind unabhängig vom Code nutzbar, etwa zum
  Testen eigener Verfahren gegen `edh_testsample.json`.
- Der Workflow ist auf andere epigraphische und (kunst-)historische
  Datenbanken übertragbar.

## Versionen

Version 1.0, September 2026. Jede Version erhält über Zenodo eine eigene DOI.

## Zitation

Kilbinger, Lisa (2026): NLP-gestützte Erschließung von Metadaten in
epigraphischen Datenbanken. Figürliche Darstellungen auf spätantiken
Grabinschriften: Ikonographisches Vokabular, Goldstandard und
Methodenvergleich am Datensatz der EDH. Version 1.0. Zenodo. [DOI] (maschinenlesbar: `CITATION.cff`)

## Quellen

- Kommentartexte, EDH-Nummern, Datierungen, Trismegistos- und EDCS-Verweise:
  Epigraphische Datenbank Heidelberg, https://edh.ub.uni-heidelberg.de/
  (CC BY-SA 4.0).
- Lateinische Suchbegriffe nach den Bildbeschreibungen der Epigraphic
  Database Bari (EDB), https://www.edb.uniba.it/.
- Normdaten: Iconclass (https://iconclass.org/), EAGLE-Vokabular
  „Decoration“ (https://www.eagle-network.eu/voc/decor.html).
- Vokabular, Annotationen, Methoden und Auswertung: Lisa Kilbinger.

## Lizenz

- Daten (`data/`) und Dokumentation: CC BY-SA 4.0, entsprechend der Lizenz der EDH
- Code (`src/`): MIT

[hermes]: https://www.hermes-hub.de/formate/forschungsstudien/
