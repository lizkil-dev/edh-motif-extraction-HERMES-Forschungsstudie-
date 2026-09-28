"""
Every file path in one place; no script has a hard-coded path.

    data/vocabulary/     the iconographic vocabulary (elements, search terms,
                         categories, motif rules, variants)
    data/vocabulary/edh_filters/
                         EDH-specific search settings: signal words, stoplist,
                         false friends, compound exceptions
    data/annotations/    hand-annotated comments (goldstandard): development
                         data and held-out test data
    data/edh/            EDH comment texts with dating (input of every method)
    results/             method output, models, figures - generated, not in git
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA = PROJECT_ROOT / 'data'
RESULTS = PROJECT_ROOT / 'results'

VOCABULARY = DATA / 'vocabulary'
ELEMENTS = VOCABULARY / 'elements.json'
ELEMENT_SYNONYMS = VOCABULARY / 'element_synonyms.json'
CATEGORIES = VOCABULARY / 'categories.json'
MOTIF_RULES = VOCABULARY / 'motif_rules.json'
VARIANT_CONDITIONS = VOCABULARY / 'variant_conditions.json'
VARIANT_CONDITION_SYNONYMS = VOCABULARY / 'variant_condition_synonyms.json'

EDH_FILTERS = VOCABULARY / 'edh_filters'
# words that signal a depiction even without a known element ("Relief")
EDH_SIGNAL_WORDS = EDH_FILTERS / 'signal_words.json'
# ambiguous element words ("Säule" as frame vs. depiction), excluded or
# decided by context
EDH_FILTER_STOPLIST = EDH_FILTERS / 'stoplist.json'
# words an element form sits in by accident ("esel" in "dieselbe")
EDH_FILTER_FALSE_FRIENDS = EDH_FILTERS / 'false_friends.json'
# compounds whose first part is no element ("Volutenkrater"), modifiers that
# replace the head ("Akanthusranke")
EDH_COMPOUND_EXCEPTIONS = EDH_FILTERS / 'compound_exceptions.json'

ANNOTATIONS = DATA / 'annotations'
EDH_DEVSAMPLE = ANNOTATIONS / 'edh_devsample.json'
# drawn after all method development, used only for the method comparison
EDH_TESTSAMPLE = ANNOTATIONS / 'edh_testsample.json'
# the first test sample; used for error analysis since its measurement, so
# development data now
EDH_FORMER_TESTSAMPLE = ANNOTATIONS / 'edh_former_testsample.json'
EDH_DEVSAMPLE_WORD_MARKINGS = ANNOTATIONS / 'edh_devsample_word_markings.json'

EDH_COMMENTS = DATA / 'edh' / 'edh_comments.json'

# method output, same has_depiction/elements/motifs shape as the annotations
EDH_RESULT_REGEX = RESULTS / 'regex.json'
EDH_RESULT_NLP_LEMMA = RESULTS / 'nlp_lemma.json'
EDH_RESULT_DEPENDENCY = RESULTS / 'dependency.json'
EDH_RESULT_DEPENDENCY_PARTS = RESULTS / 'dependency_parts'
EDH_RESULT_BERT = RESULTS / 'bert.json'
# all four methods on the test sample (src/measure_testsample.py)
EDH_RESULTS_TESTSAMPLE = RESULTS / 'testsample'
EDH_BERT_SILVER = RESULTS / 'bert' / 'silver_markings.json'
EDH_BERT_MODEL = RESULTS / 'bert' / 'model'
# further BERT training runs that differ only in the seed (src/bert_runs.py)
EDH_BERT_RUNS_MODELS = RESULTS / 'bert' / 'runs'
EDH_BERT_RUNS_RESULTS = EDH_RESULTS_TESTSAMPLE / 'bert_runs'
FIGURES = RESULTS / 'figures'
