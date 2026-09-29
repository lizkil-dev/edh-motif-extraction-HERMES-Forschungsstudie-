"""
Every file path in one place; no script has a hard-coded path.

    data/corpus/         EDH comment texts with dating (input of every method)
    data/gazetteer/      the iconographic vocabulary (elements, search terms,
                         categories)
    data/gazetteer/rules/
                         motif rules and variants
    data/gazetteer/filters/
                         EDH-specific search settings: signal words, stoplist,
                         false friends, compound exceptions
    data/goldstandard/   hand-annotated comments: development data and
                         held-out test data, annotation guidelines,
                         concordance with Trismegistos and EDCS
    data/method_comparison/
                         the published measurement: all four methods on the
                         test data, bootstrap ranges, result tables
    results/             method output and models - generated, not in git
    figures/             figures of a first look at the data - generated, in git

Every method carries the name of its script everywhere (m1_dictionary,
m2_nlp_lemma, m3_dependency, m4_bert); its output files are named after it.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA = PROJECT_ROOT / 'data'
RESULTS = PROJECT_ROOT / 'results'

EDH_COMMENTS = DATA / 'corpus' / 'edh_comments.json'

GAZETTEER = DATA / 'gazetteer'
GAZETTEER_RULES = GAZETTEER / 'rules'
GAZETTEER_FILTERS = GAZETTEER / 'filters'
ELEMENTS = GAZETTEER / 'elements.json'
ELEMENT_SYNONYMS = GAZETTEER / 'element_synonyms.json'
CATEGORIES = GAZETTEER / 'categories.json'
MOTIF_RULES = GAZETTEER_RULES / 'motif_rules.json'
VARIANT_CONDITIONS = GAZETTEER_RULES / 'variant_conditions.json'
VARIANT_CONDITION_SYNONYMS = GAZETTEER_RULES / 'variant_condition_synonyms.json'

# words that signal a depiction even without a known element ("Relief")
EDH_SIGNAL_WORDS = GAZETTEER_FILTERS / 'signal_words.json'
# ambiguous element words ("Säule" as frame vs. depiction), excluded or
# decided by context
EDH_FILTER_STOPLIST = GAZETTEER_FILTERS / 'stoplist.json'
# words an element form sits in by accident ("esel" in "dieselbe")
EDH_FILTER_FALSE_FRIENDS = GAZETTEER_FILTERS / 'false_friends.json'
# compounds whose first part is no element ("Volutenkrater"), modifiers that
# replace the head ("Akanthusranke")
EDH_COMPOUND_EXCEPTIONS = GAZETTEER_FILTERS / 'compound_exceptions.json'

GOLDSTANDARD = DATA / 'goldstandard'
EDH_DEVSAMPLE = GOLDSTANDARD / 'edh_devsample.json'
# drawn after all method development, used only for the method comparison
EDH_TESTSAMPLE = GOLDSTANDARD / 'edh_testsample.json'
# the first test sample; used for error analysis since its measurement, so
# development data now
EDH_FORMER_TESTSAMPLE = GOLDSTANDARD / 'edh_former_testsample.json'
EDH_DEVSAMPLE_WORD_MARKINGS = GOLDSTANDARD / 'edh_devsample_word_markings.json'
# EDH id -> EDH record URL, Trismegistos and EDCS URIs, for the annotated comments
INSCRIPTION_IDENTIFIERS = GOLDSTANDARD / 'inscription_identifiers.csv'

# methods 1-3 over all comments, same has_depiction/elements/motifs shape as
# the annotations
FULL_CORPUS = RESULTS / 'full_corpus'
EDH_RESULT_DICTIONARY = FULL_CORPUS / 'm1_dictionary.json'
EDH_RESULT_NLP_LEMMA = FULL_CORPUS / 'm2_nlp_lemma.json'
EDH_RESULT_DEPENDENCY = FULL_CORPUS / 'm3_dependency.json'
EDH_RESULT_DEPENDENCY_PARTS = FULL_CORPUS / 'm3_dependency_parts'

# method 4: silver standard, models (seed 42 in model/, further seeds in
# runs/seed<N>/) and its result on the former test sample
BERT_DIR = RESULTS / 'bert'
EDH_BERT_SILVER = BERT_DIR / 'silver_markings.json'
EDH_BERT_MODEL = BERT_DIR / 'model'
EDH_BERT_RUNS_MODELS = BERT_DIR / 'runs'
EDH_RESULT_BERT = BERT_DIR / 'former_testsample.json'

# a method comparison: predictions/<method>.json (the methods' output on the
# test sample), m4_bert_runs.json, bootstrap.json, scores.csv, differences.csv;
# EDH_COMPARISON is your own run, PUBLISHED_COMPARISON the published one
EDH_COMPARISON = RESULTS / 'method_comparison'
EDH_PREDICTIONS = EDH_COMPARISON / 'predictions'
PUBLISHED_COMPARISON = DATA / 'method_comparison'
# file names inside predictions/
METHOD_FILES = {
    'm1_dictionary': 'm1_dictionary.json',
    'm2_nlp_lemma': 'm2_nlp_lemma.json',
    'm3_dependency': 'm3_dependency.json',
}
# checksums and training time of the BERT runs, next to bootstrap.json
BERT_RUNS_LOG = 'm4_bert_runs.json'


def bert_file(seed):
    """File name inside predictions/ of the BERT run with this seed."""
    return f'm4_bert_seed{seed}.json'


# figures of the first look at the data (src/analysis/motif_groups.py), in git
# so the README can show them
FIGURES = PROJECT_ROOT / 'figures'
