# edh-motif-extraction

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
| 4 | BERT (`deepset/gbert-base`), fine-tuned token classification (goldstandard + silver standard from methods 2 and 3) | `src/methods/bert.py` |

All methods share the vocabulary preparation and matching helpers
(`src/matching.py`) and the step from elements to motifs (`src/schema.py`,
rules in `data/vocabulary/motif_rules.json`), so differences in the results
come from element recognition and grouping, not from the surrounding code.

## Data

```
data/vocabulary/           iconographic vocabulary
  elements.json              374 elements (label, category, Iconclass notation)
  element_synonyms.json      search terms: de (EDH), la (EDB), en
  categories.json            category tree (Iconclass notations)
  motif_rules.json           rules combining elements into motifs
  variant_conditions*.json   variants (bust, full figure, standing, framing ...)
  edh_filters/               EDH search settings: signal words, stoplist,
                             false friends, compound exceptions
data/annotations/          hand-annotated EDH comments
  edh_goldstandard.json      500 comments, development data
  edh_former_testset.json    300 comments, first test set, used for error
                             analysis since, so development data now
  edh_testset.json           300 comments, drawn after all method
                             development; the method comparison
  edh_goldstandard_word_markings.json   word-level labels for BERT
  annotation_guidelines_de.md
data/edh/edh_comments.json EDH comment texts with dating (input of all methods)
```

Annotation format per comment (EDH id `HD...`): `has_depiction`;
`elements` (element, count, variant_condition, uncertain); `motifs`
(elements, category). The method outputs in `results/` have the same shape.

## Running

Python 3.11+.

```
pip install -r requirements.txt
python -c "import stanza; stanza.download('de')"

python src/methods/dictionary.py              # method 1, seconds
python src/methods/nlp_lemma.py               # method 2, about half an hour on CPU
python src/methods/dependency_chunked.py all  # method 3, about an hour, chunked to save memory
python src/methods/bert.py silver             # method 4: silver standard from methods 2 + 3
python src/methods/bert.py train              #           about 35 minutes on CPU

python src/measure_testset.py                 # all four methods on the test set -> results/testset/
python src/evaluate.py nlp_lemma --test       # against the test set
python src/evaluate.py nlp_lemma              # against the goldstandard (full run of the method)
```

Further scripts: `src/gen_motif_rules.py` regenerates the person/portrait
block of `motif_rules.json`, `src/bert_markings.py` proposes the word-level
markings from the goldstandard, `src/motif_timeline.py` draws the chart of
motif groups over time from the method 2 results.

## Note on the reported figures

The method comparison published with the dataset is `measure_testset.py`
with this code: vocabulary, rules, code and the BERT settings were frozen
before the test set was annotated, and each method was run once (one
overlooked depiction in the test set, HD033851, was corrected afterwards and
the results re-evaluated). Two sources
of small deviations when re-running: Stanza's dependency parser does not
always give the same parse (method 3), and BERT training on another machine
does not give bit-identical weights.

A first test set was measured once with methods 1–3 and then used for error
analysis; the revisions that followed are in this code. It is kept as
`edh_former_testset.json` (`evaluate.py --former-test`), but its figures are
no longer independent of the code.

## Licence

Code: MIT (see `LICENSE`). Data in `data/`: CC BY-SA 4.0 - the comment texts
and EDH ids come from the Epigraphic Database Heidelberg (CC BY-SA 4.0);
vocabulary and annotations by Lisa Kilbinger.
