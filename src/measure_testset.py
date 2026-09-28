"""
Runs all four methods, as they are, on the test set only and writes one
result file per method (results/testset/<method>.json) - the method
comparison published with the dataset.

The test set was drawn after all method development; this script only calls
the methods' own analyze()/predict functions on its 300 comments. Every
comment is analysed independently, so the output is identical to a full run
restricted to these ids. Method 4 needs a trained model (src/methods/bert.py
silver, train).

Usage:
    python src/measure_testset.py
    python src/evaluate.py <method> --test
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'methods')))
from paths import (ELEMENTS, ELEMENT_SYNONYMS, MOTIF_RULES, EDH_SIGNAL_WORDS, EDH_FILTER_STOPLIST,  # noqa: E402
                   EDH_FILTER_FALSE_FRIENDS, EDH_COMPOUND_EXCEPTIONS, EDH_COMMENTS,
                   EDH_TESTSET, EDH_RESULTS_TESTSET)
import dictionary  # noqa: E402
import nlp_lemma  # noqa: E402
import dependency  # noqa: E402
import bert  # noqa: E402


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def write(name, results):
    EDH_RESULTS_TESTSET.mkdir(parents=True, exist_ok=True)
    with open(EDH_RESULTS_TESTSET / f'{name}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'{name}: {sum(r["has_depiction"] for r in results.values())} of {len(results)} with depiction')


def main():
    ids = list(load_json(EDH_TESTSET))
    comments = {r['id']: r['commentary'] for r in load_json(EDH_COMMENTS) if r['id'] in ids}
    synonyms, meta = load_json(ELEMENT_SYNONYMS), load_json(ELEMENTS)
    rules, signal = load_json(MOTIF_RULES), load_json(EDH_SIGNAL_WORDS)
    stoplist = load_json(EDH_FILTER_STOPLIST)
    ff = {e['word'].lower() for e in load_json(EDH_FILTER_FALSE_FRIENDS)}
    exceptions = load_json(EDH_COMPOUND_EXCEPTIONS)

    # method 1
    forms1 = dictionary.build_element_forms(synonyms, dictionary.stoplist_for(stoplist, 'dictionary'))
    write('regex', {i: dictionary.analyze(comments[i], forms1, signal, ff, rules, meta) for i in ids})

    # method 2
    forms2 = nlp_lemma.build_element_forms(synonyms, nlp_lemma.stoplist_for(stoplist, 'nlp_lemma'))
    compounds2 = nlp_lemma.build_compounds(forms2, exceptions)
    nlp = nlp_lemma.stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma', verbose=False, download_method=None)
    write('nlp_lemma', {i: nlp_lemma.analyze(nlp(comments[i]), forms2, signal, ff, rules, meta, compounds2)
                        for i in ids})

    # method 3
    stop3 = dependency.stoplist_for(stoplist, 'dependency')
    forms3 = dependency.build_element_forms(synonyms, stop3)
    args3 = (forms3, dependency.build_stoplist_forms(synonyms, stop3), dependency.build_stoplist_meta(stop3),
             signal, ff, rules, meta, dependency.build_compounds(forms3, exceptions))
    nlp3 = dependency.stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma,depparse', verbose=False,
                                      download_method=None)
    write('dependency', {i: dependency.analyze(nlp3(comments[i]), *args3) for i in ids})

    # method 4
    write('bert', bert.predict_ids(ids))


if __name__ == '__main__':
    main()
