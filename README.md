# edh-motif-extraction

*[Deutsche Fassung](README.de.md)*

Extracting iconographic motifs from the free-text comments of the
[Epigraphic Database Heidelberg (EDH)](https://edh.ub.uni-heidelberg.de/):
four methods, one shared vocabulary, one evaluation.

EDH describes the imagery of ancient funerary monuments in its comment field
("Oberhalb des Inschriftfeldes Nische mit den Büsten eines Ehepaares in der
dextrarum iunctio; im Giebel Delphine"). The task, identical for every
method: does a comment describe a depiction, which elements are depicted,
and how do they combine into motifs? Part of a PhD project on iconographic
patterns in Latin funerary inscriptions (c. AD 150–800), Lisa Kilbinger.

The dataset (vocabulary, annotations, method comparison) is published on
Zenodo: [DOI]. This repository holds the code to reproduce it.

## Methods

| # | Method | Script |
|---|---|---|
| 1 | Dictionary lookup: substring search of German search terms | `src/methods/dictionary.py` |
| 2 | Lemmatisation (Stanza), compound analysis, motifs per sentence | `src/methods/nlp_lemma.py` |
| 3 | Dependency parsing (Stanza), motifs per dependency component | `src/methods/dependency.py` |
| 4 | BERT (`deepset/gbert-base`), fine-tuned token classification (development data + silver standard: comments labelled automatically where methods 2 and 3 agree) | `src/methods/bert.py` |

All methods share the vocabulary preparation and matching helpers
(`src/matching.py`) and the step from elements to motifs (`src/motifs.py`,
rules in `data/vocabulary/motif_rules.json`), so differences in the results
come from element recognition and grouping, not from the surrounding code.

## How it fits together

```
data/      input: vocabulary, annotations, EDH comment texts      (in git)
src/       code: reads data/, writes results/                     (in git)
results/   everything the code produces - regenerable              (not in git)
```

```
edh_comments.json ──┐
vocabulary ─────────┼─► methods 1-3 ──────────────► results ──┐
                    │                                         ├─► evaluate.py / bootstrap.py ─► scores
development data ───┼─► method 4 (BERT) learns ───► results ──┘         ▲
                    │                                                    │
test data ──────────┴────────────────────────────────────────────────────┘  (reference)
```

Every method writes the same shape as the annotations (`has_depiction`,
`elements`, `motifs`), so any method output can be compared directly with
the hand-annotated reference.

## Data

```
data/edh/edh_comments.json   EDH comment texts with dating - the input of every method
data/vocabulary/             iconographic vocabulary
  elements.json                374 elements (label, category, Iconclass notation, EAGLE Decoration term)
  element_synonyms.json        search terms: de (EDH), la (EDB), en
  categories.json              category tree (Iconclass notations)
  motif_rules.json             rules combining elements into motifs
  variant_conditions*.json     variants (bust, full figure, standing, framing ...)
  edh_filters/                 EDH search settings:
    signal_words.json            words that mark a depiction without a known element ("Relief")
    stoplist.json                ambiguous words, excluded or decided by context ("Säule")
    false_friends.json           words a search term sits in by accident ("esel" in "dieselbe")
    compound_exceptions.json     compounds whose first part is no element ("Volutenkrater")
data/annotations/            hand-annotated EDH comments (goldstandard), split
                             into development data and held-out test data
  edh_devsample.json           500 comments, development data; training data of method 4
  edh_former_testsample.json   300 comments, first test sample, used for error
                               analysis since, so development data now
  edh_testsample.json          300 comments, drawn after all method
                               development; the method comparison
  edh_devsample_word_markings.json   the 500 development comments labelled word by word
                                     (training data of method 4)
  annotation_guidelines_de.md
```

Annotation format per comment (EDH id `HD...`): `has_depiction`;
`elements` (element, count, variant_condition, uncertain); `motifs`
(elements, category).

### Standards

The vocabulary is linked to two established standards, so that its elements
can be matched with other collections:

- **Iconclass**, the art-historical classification system:
  `iconclass_notation` in `elements.json` and `categories.json`, for every
  element with a matching notation; each notation was checked against the
  Iconclass service.
- **EAGLE vocabulary "Decoration"** (Europeana network of Ancient Greek
  and Latin Epigraphy, https://www.eagle-network.eu/voc/decor.html), the
  epigraphic standard for the decoration of inscribed monuments:
  `eagle_decoration` in `elements.json`, the matching EAGLE term for every
  element that has one. The names of the cross types (crux quadrata,
  immissa, gammata, decussata) and the forms of the Christogram follow
  EAGLE.

## Files

### Shared building blocks (used by the methods, not run on their own)

| File | What it does | Reads |
|---|---|---|
| `src/paths.py` | every file path in one place | – |
| `src/matching.py` | shared search helpers: dating filter (AD 150–800), search forms, false friends, compounds ("Lorbeerkranz" → laurel + wreath), multi-word forms, number words, signal words | vocabulary and filters |
| `src/motifs.py` | from elements to motifs: applies the motif rules (`resolve_motifs`) and turns form words into variants ("Büste eines Mannes" → man, variant bust) | `motif_rules.json`, `elements.json` |

### Methods (`src/methods/`)

All read the comment texts and the vocabulary and run over every comment.

| File | What it does | Writes |
|---|---|---|
| `dictionary.py` | method 1: substring search, no grouping | `results/regex.json` |
| `nlp_lemma.py` | method 2: lemma match, motifs per sentence | `results/nlp_lemma.json` |
| `dependency.py` | method 3: as 2, motifs per dependency component, ambiguous words decided by context | `results/dependency.json` |
| `dependency_chunked.py` | method 3 in chunks, one process each (less memory), same result | `results/dependency_parts/`, then `results/dependency.json` |
| `bert.py silver` | method 4: silver standard - comments where methods 2 and 3 agree, labelled automatically | `results/bert/silver_markings.json` |
| `bert.py train` | method 4: fine-tunes BERT on the word markings + silver standard (seed 42) | `results/bert/model/` |
| `bert.py predict` | method 4 on the former test sample | `results/bert.json` |

### Measuring and scoring

| File | What it does | Reads | Writes |
|---|---|---|---|
| `src/measure_testsample.py` | runs all four methods on the 300 test comments only | test data, texts, vocabulary, BERT model | `results/testsample/<method>.json` |
| `src/bert_runs.py` | trains method 4 again with seeds 43 and 44 and measures each on the test data | as `bert.py` | `results/bert/runs/seed<N>/`, `results/testsample/bert_runs/seed<N>.json`, `runs.json` (checksums) |
| `src/evaluate.py` | scores one method: precision, recall and F1 for depiction, elements (micro and macro) and motifs | one method's results + the matching annotations | screen only |
| `src/bootstrap.py` | 95 % ranges for every score and paired differences between methods, with the scoring of `evaluate.py` | test data, `results/testsample/` | `results/testsample/bootstrap.json` + table on screen |

### Further scripts

| File | What it does | Reads | Writes |
|---|---|---|---|
| `src/gen_motif_rules.py` | generates the person/portrait block of the motif rules (a cross product of forms and person groups, over 100 rules) | `motif_rules.json`, `elements.json`, `categories.json` | overwrites that block in `data/vocabulary/motif_rules.json` |
| `src/motif_timeline.py` | chart: share of portraits, Christian symbols and animals per 50 years, AD 150–600 | method 2 results, texts with dating, `categories.json` | `results/figures/motif_timeline_de/en.png/.svg` |

## Running

Python 3.11+.

```
pip install -r requirements.txt
python -c "import stanza; stanza.download('de')"

python src/methods/dictionary.py              # method 1, seconds
python src/methods/nlp_lemma.py               # method 2, about half an hour on CPU
python src/methods/dependency_chunked.py all  # method 3, about an hour, chunked to save memory
python src/methods/bert.py silver             # method 4: silver standard from methods 2 + 3
python src/methods/bert.py train              #           about 40 minutes on CPU

python src/measure_testsample.py              # all four methods on the test sample -> results/testsample/
python src/bert_runs.py                       # method 4 with seeds 43 and 44, about 85 minutes
python src/bootstrap.py                       # scores with 95 % ranges, paired differences
python src/evaluate.py nlp_lemma --test       # one method against the test sample
python src/evaluate.py nlp_lemma              # against the development sample (full run of the method)
```

The order matters: the silver standard needs the full results of methods 2
and 3, and `bootstrap.py` needs `measure_testsample.py` and `bert_runs.py`.

## Results

On the 300 test comments (70 with a depiction), F1 in %, 95 % range in
brackets; method 4 as mean ± standard deviation of its three training runs:

| | Method 1 | Method 2 | Method 3 | Method 4 |
|---|---|---|---|---|
| Depiction | 97.2 [94.1–99.4] | 98.6 [96.3–100] | 98.6 [96.3–100] | 96.1 ± 1.7 [93.2–98.4] |
| Elements, micro | 84.6 [79.0–89.4] | 91.8 [86.5–96.0] | 92.5 [88.1–96.3] | 83.3 ± 2.7 [77.1–89.3] |
| Elements, macro | 73.1 [67.0–83.2] | 77.8 [71.4–88.4] | 80.8 [75.0–89.5] | 64.2 ± 2.7 [58.0–77.1] |
| Motifs | 52.7 [43.0–62.7] | 73.9 [64.5–82.7] | 73.5 [64.0–82.6] | 66.7 ± 2.3 [57.7–76.0] |

Methods 2 and 3 are level; both are ahead of method 4 on elements and
motifs, and method 2 is ahead of method 1 on motifs - these differences hold
across the bootstrap samples. No method is reliably better at telling
whether a comment describes a depiction at all. Paired differences and
limitations: see the dataset's README on Zenodo.

## Note on the reported figures

The method comparison published with the dataset is `measure_testsample.py`
with this code: vocabulary, rules, code and the BERT settings were frozen
before the test sample was annotated, and each method was run once (one
overlooked depiction in the test sample, HD033851, was corrected afterwards and
the results re-evaluated). Method 4 is reported as the mean of three
training runs that differ only in the seed (42 from `bert.py train`, 43 and
44 from `bert_runs.py`). `bootstrap.py` adds 95 % ranges (10,000 bootstrap
samples of the 300 test comments) and paired differences between the
methods; it uses the scoring of `evaluate.py` unchanged. Two sources
of small deviations when re-running: Stanza's dependency parser does not
always give the same parse (method 3), and BERT training on another machine
does not give bit-identical weights.

A first test sample was measured once with methods 1–3 and then used for error
analysis; the revisions that followed are in this code. It is kept as
`edh_former_testsample.json` (`evaluate.py --former-test`), but its figures are
no longer independent of the code.

## Licence

Code: MIT (see `LICENSE`). Data in `data/`: CC BY-SA 4.0 - the comment texts
and EDH ids come from the Epigraphic Database Heidelberg (CC BY-SA 4.0);
vocabulary and annotations by Lisa Kilbinger.
