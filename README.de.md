# edh-motif-extraction

*[English version](README.md)*

Automatische Erkennung ikonografischer Motive in den Freitext-Kommentaren der
[Epigraphischen Datenbank Heidelberg (EDH)](https://edh.ub.uni-heidelberg.de/)

## Methoden

1. Wörterbuchabgleich (Regex): Suche deutscher Suchwörter als Zeichenfolge im Text
`src/methods/dictionary.py`
2. Lemmatisierung (Stanza): Kompositazerlegung, Motive je Satz 
`src/methods/nlp_lemma.py`
3. Satzanalyse (Dependency Parsing mit Stanza): Motive je grammatisch verbundener Satzgruppe
`src/methods/dependency.py`
4. BERT (deepset/gbert-base): feinabgestimmte Wortklassifikation
`src/methods/bert.py`

Alle Methoden teilen die Vorbereitung des Vokabulars und die Suchhilfen
(`src/matching.py`) sowie den Schritt von den Elementen zu den Motiven
(`src/motifs.py`, Regeln in `data/vocabulary/motif_rules.json`).
Unterschiede in den Ergebnissen gehen daher auf die Elementerkennung und die
Gruppierung zurück, nicht auf den umgebenden Code.

## Aufbau

```
data/      Eingabe: Vokabular, Annotationen, EDH-Kommentartexte      
src/       Code: liest data/, schreibt nach results/                 
results/   alles, was der Code erzeugt – jederzeit neu erzeugbar      
```

```
edh_comments.json ──┐
Vokabular ──────────┼─► Methoden 1–3 ─────────────► Ergebnisse ──┐
                    │                                            ├─► evaluate.py / bootstrap.py ─► Werte
Entwicklungsdaten ──┼─► Methode 4 (BERT) lernt ───► Ergebnisse ──┘         ▲
                    │                                                       │
Testdaten ──────────┴───────────────────────────────────────────────────────┘  (Maßstab)
```

Jede Methode schreibt ihre Ergebnisse im selben Format wie die Annotationen
(`has_depiction`, `elements`, `motifs`), um einen direkten Vergleich mit dem von Hand annotierten Goldstandard zu gewährleisten.

## Daten

```
data/edh/edh_comments.json   EDH-Kommentartexte mit Datierung
data/vocabulary/             ikonografisches Vokabular
  elements.json                374 Elemente (Bezeichnung, Kategorie, Iconclass-Notation, EAGLE-Begriff aus dem Vokabular „Decoration“, wo vorhanden)
  element_synonyms.json        Suchwörter: de, la, en
  categories.json              Kategorienbaum (Iconclass-Notationen)
  motif_rules.json             Regeln, nach denen Elemente zu Motiven verbunden werden
  variant_conditions*.json     Varianten (Büste, Ganzfigur, stehend, rahmend …)
  edh_filters/                 Sucheinstellungen für EDH:
    signal_words.json            Wörter, die auch ohne bekanntes Element eine Darstellung anzeigen („abgebildet“)
    stoplist.json                mehrdeutige Wörter, ausgeschlossen oder nach Kontext entschieden („Säule“)
    false_friends.json           Wörter, in denen ein Suchwort zufällig steckt („esel“ in „dieselbe“)
    compound_exceptions.json     Komposita, deren erster Teil kein Element ist („Volutenkrater“)
data/annotations/            von Hand annotierte EDH-Kommentare (Goldstandard), aufgeteilt
                             in Entwicklungsdaten und zurückgehaltene Testdaten
  edh_devsample.json           500 Kommentare, Entwicklungsdaten; Trainingsdaten von Methode 4
  edh_former_testsample.json   300 Kommentare, erste Teststichprobe, seither für die
                               Fehleranalyse genutzt, daher inzwischen Entwicklungsdaten
  edh_testsample.json          300 Kommentare, gezogen nach Abschluss aller
                               Methodenentwicklung; der Methodenvergleich
  edh_devsample_word_markings.json   die 500 Entwicklungskommentare Wort für Wort markiert
                                     (Trainingsdaten von Methode 4)
  annotation_guidelines_de.md  Annotationsrichtlinien
```

Annotationsformat je Kommentar (EDH-Nummer `HD…`): `has_depiction`;
`elements` (Element, Anzahl, Variante, Unsicherheit); `motifs`
(Elemente, Kategorie).

### Standards

Das Vokabular ist mit zwei etablierten Standards abgeglichen, damit sich
seine Elemente mit anderen Sammlungen zusammenführen lassen:

- **Iconclass**, das kunsthistorische Klassifikationssystem:
  `iconclass_notation` in `elements.json` und `categories.json`, für jedes
  Element mit passender Notation; jede Notation ist gegen die
  Iconclass-Schnittstelle geprüft.
- **EAGLE-Vokabular „Decoration“** (Europeana network of Ancient Greek and
  Latin Epigraphy, https://www.eagle-network.eu/voc/decor.html), der
  epigraphische Standard für die Dekoration beschrifteter Denkmäler.
  Jedes Element wurde von Hand mit EAGLE verglichen; wo es eine
  Entsprechung gibt, steht der EAGLE-Begriff in `eagle_decoration` in
  `elements.json` (98 von 374 Elementen). Übernommen werden nur Begriffe,
  die EAGLE auf Deutsch, Englisch oder Latein führt; ist EAGLE gröber,
  steht der Oberbegriff (Leier → „Musikinstrument“). Die Bezeichnungen der
  Kreuzformen (crux quadrata, immissa, gammata, decussata) und die Formen
  des Christogramms folgen EAGLE.

## Dateien

### Gemeinsame Bausteine (von den Methoden genutzt, nicht einzeln ausgeführt)

| Datei | Was sie tut | Liest |
|---|---|---|
| `src/paths.py` | alle Dateipfade an einer Stelle | – |
| `src/matching.py` | gemeinsame Suchhilfen: Datierungsfilter (150–800 n. Chr.), Suchformen, False Friends, Komposita („Lorbeerkranz“ → Lorbeer + Kranz), Mehrwort-Ausdrücke, Zahlwörter, Signalwörter | Vokabular und Filter |
| `src/motifs.py` | von Elementen zu Motiven: wendet die Motivregeln an (`resolve_motifs`) und macht aus Formwörtern Varianten („Büste eines Mannes“ → Mann, Variante Büste) | `motif_rules.json`, `elements.json` |

### Methoden (`src/methods/`)

Alle lesen die Kommentartexte und das Vokabular und laufen über alle Kommentare.

| Datei | Was sie tut | Schreibt |
|---|---|---|
| `dictionary.py` | Methode 1: Suche als Zeichenfolge, keine Gruppierung | `results/regex.json` |
| `nlp_lemma.py` | Methode 2: Abgleich über die Grundform (Lemma), Motive je Satz | `results/nlp_lemma.json` |
| `dependency.py` | Methode 3: wie 2, Motive je grammatisch verbundener Gruppe, mehrdeutige Wörter nach Kontext | `results/dependency.json` |
| `dependency_chunked.py` | Methode 3 in Portionen, je ein eigener Prozess (weniger Arbeitsspeicher), gleiches Ergebnis | `results/dependency_parts/`, dann `results/dependency.json` |
| `bert.py silver` | Methode 4: Silberstandard – Kommentare, in denen Methode 2 und 3 übereinstimmen, automatisch markiert | `results/bert/silver_markings.json` |
| `bert.py train` | Methode 4: Feinabstimmung von BERT auf Wortmarkierungen + Silberstandard (Seed 42) | `results/bert/model/` |
| `bert.py predict` | Methode 4 auf der früheren Teststichprobe | `results/bert.json` |

### Messen und Auswerten

| Datei | Was sie tut | Liest | Schreibt |
|---|---|---|---|
| `src/measure_testsample.py` | lässt alle vier Methoden nur auf den 300 Testkommentaren laufen | Testdaten, Texte, Vokabular, BERT-Modell | `results/testsample/<methode>.json` |
| `src/bert_runs.py` | trainiert Methode 4 erneut mit Seed 43 und 44 und misst jeden Lauf auf den Testdaten | wie `bert.py` | `results/bert/runs/seed<N>/`, `results/testsample/bert_runs/seed<N>.json`, `runs.json` (Prüfsummen) |
| `src/evaluate.py` | bewertet eine Methode: Precision, Recall und F1 für Darstellung, Elemente (Mikro und Makro) und Motive | Ergebnisse einer Methode + passende Annotationen | nur Bildschirmausgabe |
| `src/bootstrap.py` | 95-%-Unsicherheitsbereiche für alle Werte und gepaarte Abstände zwischen den Methoden, mit den Bewertungsregeln von `evaluate.py` | Testdaten, `results/testsample/` | `results/testsample/bootstrap.json` + Tabelle am Bildschirm |

### Weitere Skripte

| Datei | Was sie tut | Liest | Schreibt |
|---|---|---|---|
| `src/gen_motif_rules.py` | erzeugt den Personen- und Porträtteil der Motivregeln (Kreuzprodukt aus Darstellungsformen und Personengruppen, über 100 Regeln) | `motif_rules.json`, `elements.json`, `categories.json` | überschreibt diesen Teil in `data/vocabulary/motif_rules.json` |
| `src/motif_timeline.py` | Grafik: Anteil von Porträts, christlichen Symbolen und Tieren je 50 Jahre, 150–600 n. Chr. | Ergebnisse von Methode 2, Texte mit Datierung, `categories.json` | `results/figures/motif_timeline_de/en.png/.svg` |

## Ausführen

Python 3.11 oder neuer.

```
pip install -r requirements.txt
python -c "import stanza; stanza.download('de')"

python src/methods/dictionary.py              # Methode 1, Sekunden
python src/methods/nlp_lemma.py               # Methode 2, etwa eine halbe Stunde auf der CPU
python src/methods/dependency_chunked.py all  # Methode 3, etwa eine Stunde, in Portionen
python src/methods/bert.py silver             # Methode 4: Silberstandard aus Methode 2 + 3
python src/methods/bert.py train              #            etwa 40 Minuten auf der CPU

python src/measure_testsample.py              # alle vier Methoden auf den Testdaten -> results/testsample/
python src/bert_runs.py                       # Methode 4 mit Seed 43 und 44, etwa 85 Minuten
python src/bootstrap.py                       # Werte mit 95-%-Bereichen, gepaarte Abstände
python src/evaluate.py nlp_lemma --test       # eine Methode gegen die Testdaten
python src/evaluate.py nlp_lemma              # gegen die Entwicklungsdaten (voller Lauf der Methode)
```

Die Reihenfolge ist wichtig: Der Silberstandard braucht die vollständigen
Ergebnisse von Methode 2 und 3, und `bootstrap.py` braucht
`measure_testsample.py` und `bert_runs.py`.

## Ergebnisse

Auf den 300 Testkommentaren (70 mit Darstellung), F1 in %, in Klammern der
95-%-Bereich; Methode 4 als Mittelwert ± Standardabweichung ihrer drei
Trainingsläufe:

| | Methode 1 | Methode 2 | Methode 3 | Methode 4 |
|---|---|---|---|---|
| Darstellung | 97,2 [94,1–99,4] | 98,6 [96,3–100] | 98,6 [96,3–100] | 96,1 ± 1,7 [93,2–98,4] |
| Elemente, Mikro | 84,6 [79,0–89,4] | 91,8 [86,5–96,0] | 92,5 [88,1–96,3] | 83,3 ± 2,7 [77,1–89,3] |
| Elemente, Makro | 73,1 [67,0–83,2] | 77,8 [71,4–88,4] | 80,8 [75,0–89,5] | 64,2 ± 2,7 [58,0–77,1] |
| Motive | 52,7 [43,0–62,7] | 73,9 [64,5–82,7] | 73,5 [64,0–82,6] | 66,7 ± 2,3 [57,7–76,0] |

Methode 2 und 3 liegen gleichauf; beide liegen bei Elementen und Motiven vor
Methode 4, und Methode 2 liegt bei den Motiven vor Methode 1. Diese
Unterschiede halten über die Bootstrap-Stichproben. Ob ein Kommentar
überhaupt eine Darstellung beschreibt, erkennt keine Methode nachweisbar
besser als die anderen. Gepaarte Abstände und Grenzen: siehe README des
Datensatzes auf Zenodo.

## Hinweis zu den berichteten Werten

Der mit dem Datensatz veröffentlichte Methodenvergleich ist
`measure_testsample.py` mit diesem Code: Vokabular, Regeln, Code und die
BERT-Einstellungen waren eingefroren, bevor die Testdaten annotiert wurden,
und jede Methode lief einmal (eine übersehene Darstellung in den Testdaten,
HD033851, wurde danach korrigiert und die Ergebnisse neu ausgewertet, nicht
neu berechnet). Methode 4 steht als Mittelwert dreier Trainingsläufe, die
sich nur im Seed unterscheiden (42 aus `bert.py train`, 43 und 44 aus
`bert_runs.py`). `bootstrap.py` ergänzt 95-%-Bereiche (10.000
Bootstrap-Stichproben der 300 Testkommentare) und gepaarte Abstände zwischen
den Methoden; es nutzt die Bewertung von `evaluate.py` unverändert. Kleine
Abweichungen beim Nachrechnen haben zwei Quellen: Stanzas Parser liefert
nicht immer exakt denselben Satzbaum (Methode 3), und ein BERT-Training auf
einem anderen Rechner ergibt nicht bitgenau dieselben Gewichte.

Eine erste Teststichprobe wurde einmal mit den Methoden 1–3 gemessen und
danach für die Fehleranalyse genutzt; die daraus folgenden Verbesserungen
stecken in diesem Code. Sie liegt als `edh_former_testsample.json` bei
(`evaluate.py --former-test`), ihre Werte sind aber nicht mehr unabhängig vom
Code.

## Lizenz

Code: MIT (siehe `LICENSE`). Daten in `data/`: CC BY-SA 4.0 – die
Kommentartexte und EDH-Nummern stammen aus der Epigraphischen Datenbank
Heidelberg (CC BY-SA 4.0); Vokabular und Annotationen von Lisa Kilbinger.
