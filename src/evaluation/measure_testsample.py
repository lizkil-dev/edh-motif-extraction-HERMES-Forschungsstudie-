"""
Runs all four methods on the 300 test comments and writes one result file
per method to results/method_comparison/predictions/ (m1_dictionary.json,
m2_nlp_lemma.json, m3_dependency.json, m4_bert_seed42.json). These files are
the basis of the method comparison: evaluate.py, bootstrap.py and
comparison_tables.py compute all scores from them.

The test sample was drawn only after all methods were finished, so none of
them was adjusted to it.

Method 4 needs a trained model first (src/methods/m4_bert.py silver, then
train); its further training runs (seeds 43, 44) come from m4_bert.py runs.

Usage:
    python src/evaluation/measure_testsample.py
    python src/evaluation/evaluate.py <method> --test   # scores of one method
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'methods')))
from paths import (ELEMENTS, ELEMENT_SYNONYMS, MOTIF_RULES, EDH_SIGNAL_WORDS, EDH_FILTER_STOPLIST,  # noqa: E402
                   EDH_FILTER_FALSE_FRIENDS, EDH_COMPOUND_EXCEPTIONS, EDH_COMMENTS,
                   EDH_TESTSAMPLE, EDH_PREDICTIONS, METHOD_FILES, bert_file)
import m1_dictionary as dictionary  # noqa: E402
import m2_nlp_lemma as nlp_lemma  # noqa: E402
import m3_dependency as dependency  # noqa: E402
import m4_bert as bert  # noqa: E402


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def write(filename, results):
    EDH_PREDICTIONS.mkdir(parents=True, exist_ok=True)
    with open(EDH_PREDICTIONS / filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'{filename}: {sum(r["has_depiction"] for r in results.values())} of {len(results)} with depiction')


def main():
    ids = list(load_json(EDH_TESTSAMPLE))
    comments = {r['id']: r['commentary'] for r in load_json(EDH_COMMENTS) if r['id'] in ids}
    synonyms, meta = load_json(ELEMENT_SYNONYMS), load_json(ELEMENTS)
    rules, signal = load_json(MOTIF_RULES), load_json(EDH_SIGNAL_WORDS)
    stoplist = load_json(EDH_FILTER_STOPLIST)
    ff = {e['word'].lower() for e in load_json(EDH_FILTER_FALSE_FRIENDS)}
    exceptions = load_json(EDH_COMPOUND_EXCEPTIONS)

    # method 1
    forms1 = dictionary.build_element_forms(synonyms, dictionary.stoplist_for(stoplist, 'dictionary'))
    write(METHOD_FILES['m1_dictionary'],{i: dictionary.analyze(comments[i], forms1, signal, ff, rules, meta) for i in ids})

    # method 2
    forms2 = nlp_lemma.build_element_forms(synonyms, nlp_lemma.stoplist_for(stoplist, 'nlp_lemma'))
    compounds2 = nlp_lemma.build_compounds(forms2, exceptions)
    nlp = nlp_lemma.stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma', verbose=False, download_method=None)
    write(METHOD_FILES['m2_nlp_lemma'], {i: nlp_lemma.analyze(nlp(comments[i]), forms2, signal, ff, rules, meta,
                                                              compounds2)
                                         for i in ids})

    # method 3
    stop3 = dependency.stoplist_for(stoplist, 'dependency')
    forms3 = dependency.build_element_forms(synonyms, stop3)
    args3 = (forms3, dependency.build_stoplist_forms(synonyms, stop3), dependency.build_stoplist_meta(stop3),
             signal, ff, rules, meta, dependency.build_compounds(forms3, exceptions))
    nlp3 = dependency.stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma,depparse', verbose=False,
                                      download_method=None)
    write(METHOD_FILES['m3_dependency'],{i: dependency.analyze(nlp3(comments[i]), *args3) for i in ids})

    # method 4
    write(bert_file(bert.SEED), bert.predict_ids(ids))


if __name__ == '__main__':
    main()
