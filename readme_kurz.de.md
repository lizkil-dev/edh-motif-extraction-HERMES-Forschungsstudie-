# edh-motif-extraction

**NLP-gestützte Erschließung von Metadaten in epigraphischen Datenbanken: Vokabular,
Goldstandard und Methodenvergleich geprüft am Datensatz der Epigraphischen Datenbank Heidelberg (EDH)**

Lisa Kilbinger, Philipps-Universität Marburg. Version 1.0, September 2026.
DOI: [DOI] · Daten: CC BY-SA 4.0 · Code: MIT · *[English version](README.md)*

Die Datenpublikation ist im Rahmen der HERMES-Forschungsstudie
[„NLP-gestützte Erschließung von Metadaten in epigraphischen Datenbanken“](https://www.hermes-hub.de/forschen/forschungsstudien/2026/IEG/nlp-gest%C3%BCtzte-erschlie%C3%9Fung-von-metadaten-in-epigraphischen-datenbanken.html)
(2026, Leibniz-Institut für Europäische Geschichte, IEG) entstanden.
Methodik, Versuchsaufbau und Diskussion: [Projektbeschreibung](projektbeschreibung.de.md).

## Inhalt

Epigraphische Datenbanken erfassen figürliche Darstellungen auf
Inschriftenträgern bislang nur als Freitext. Dieses Repositorium enthält
Daten und Code, um diese Angaben in strukturierte Metadaten zu überführen:

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
  method_comparison/           veröffentlichte Messung auf den Testdaten
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

**Goldstandard** (`data/goldstandard/`):

| Datei | Inhalt |
|---|---|
| `edh_devsample.json` | 500 Entwicklungskommentare |
| `edh_former_testsample.json` | 300 Kommentare, ehemalige Teststichprobe, heute Entwicklungsdaten |
| `edh_testsample.json` | 300 Testkommentare für die abschließende Messung |
| `edh_devsample_word_markings.json` | wortweise Markierungen der Entwicklungskommentare (Trainingsdaten für Methode 4) |
| `annotation_guidelines_de.md` | Annotationsrichtlinien |
| `inscription_identifiers.csv` | Konkordanz EDH – Trismegistos – EDCS |

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
`data/method_comparison/scores.csv`, `differences.csv` und
[Projektbeschreibung](projektbeschreibung.de.md).

| | 1 Wörterbuch | 2 Lemmatisierung | 3 Satzanalyse | 4 BERT |
|---|:---:|:---:|:---:|:---:|
| Darstellung | 97,2 | 98,6 | 98,6 | 96,1 |
| Elemente, Mikro | 84,6 | 91,8 | 92,5 | 83,3 |
| Elemente, Makro | 73,1 | 77,8 | 80,8 | 64,2 |
| Motive | 52,7 | 73,9 | 73,5 | 66,7 |

Methode 2 und 3 liegen gleichauf vorn; beide liegen belegt vor Methode 4
bei Elementen und Motiven. Ob eine Darstellung vorliegt, erkennen alle vier
Methoden etwa gleich gut.


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

Die EDH ändert sich laufend; ein neuer Abruf ergibt daher leicht andere
Daten als das veröffentlichte Korpus in `data/corpus/`, auf dem alle
berichteten Werte beruhen. Das neu gebaute Korpus ersetzt es deshalb nicht.
Die EDCS-Verweise der Konkordanz wurden zusätzlich von den EDH-Detailseiten
übernommen; dieser Schritt ist nicht enthalten.

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
epigraphischen Datenbanken: Vokabular, Goldstandard und Methodenvergleich
geprüft am Datensatz der Epigraphischen Datenbank Heidelberg (EDH). Version
1.0. Zenodo. [DOI] (maschinenlesbar: `CITATION.cff`)

## Quellen und Lizenz

- Kommentartexte, EDH-Nummern, Datierungen, Trismegistos- und EDCS-Verweise:
  Epigraphische Datenbank Heidelberg, https://edh.ub.uni-heidelberg.de/
  (CC BY-SA 4.0).
- Lateinische Suchbegriffe nach den Bildbeschreibungen der Epigraphic
  Database Bari (EDB), https://www.edb.uniba.it/.
- Normdaten: Iconclass (https://iconclass.org/), EAGLE-Vokabular
  „Decoration“ (https://www.eagle-network.eu/voc/decor.html).
- Vokabular, Annotationen, Methoden und Auswertung: Lisa Kilbinger.

Daten in `data/` und `figures/`: CC BY-SA 4.0 (`LICENSE-DATA`); Code: MIT
(`LICENSE`).
