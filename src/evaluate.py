"""
Evaluates one EDH method against the development sample or a test
sample. One call = one method.

Three independently evaluated levels:
  1. has_depiction: confusion matrix -> recall, precision, F1.
  2. elements: presence only (not count) per element type, both micro- and
     macro-averaged - the micro average is dominated by frequent elements,
     only the macro average shows whether rare ones are found at all.
     Reported twice: strict (every element type on its own) and lenient
     (subtypes collapsed onto their "group" from elements.json, e.g.
     man/woman/boy/girl/child -> person), so "finds the person at all" can be
     told apart from "gets the gender/age right".
  3. motifs: exact match (element set AND category both have to match an
     annotated motif).

Usage:
    python src/evaluate.py regex                 against the development sample
    python src/evaluate.py regex --test          against the test sample, with the
                                                 results of measure_testsample.py
    python src/evaluate.py regex --former-test   against the former test sample
"""

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import (ELEMENTS, EDH_DEVSAMPLE, EDH_TESTSAMPLE, EDH_FORMER_TESTSAMPLE, EDH_RESULT_REGEX,
                   EDH_RESULT_NLP_LEMMA, EDH_RESULT_DEPENDENCY, EDH_RESULT_BERT, EDH_RESULTS_TESTSAMPLE)

RESULT_FILES = {
    'regex': EDH_RESULT_REGEX,
    'nlp_lemma': EDH_RESULT_NLP_LEMMA,
    'dependency': EDH_RESULT_DEPENDENCY,
    'bert': EDH_RESULT_BERT,
}


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def prf(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


def evaluate_depiction(gold, pred, ids):
    rp = rn = fp = fn = 0
    for i in ids:
        g = gold[i]['has_depiction']
        p = pred.get(i, {}).get('has_depiction', False)
        if g and p:
            rp += 1
        elif (not g) and (not p):
            rn += 1
        elif (not g) and p:
            fp += 1
        else:
            fn += 1
    precision, recall, f1 = prf(rp, fp, fn)
    return {'rp': rp, 'rn': rn, 'fp': fp, 'fn': fn,
            'precision': precision, 'recall': recall, 'f1': f1}


def evaluate_elements(gold, pred, ids, parents=None):
    # parents: element -> group name; given = lenient mode, subtypes
    # count as their group on both sides. Each distinct element type still
    # counts once, so "man, woman" is two persons, not one: a method that
    # finds "man, boy" there gets both persons right leniently (one strictly).
    # Collapsing to a plain set instead would turn "man, woman" into a single
    # "person" hit and put the lenient score below the strict one.
    parents = parents or {}
    gold_sets = {i: Counter(parents.get(t, t) for t in {e['element'] for e in gold[i]['elements']})
                 for i in ids}
    pred_sets = {i: Counter(parents.get(t, t) for t in {e['element']
                                                        for e in pred.get(i, {}).get('elements', [])})
                 for i in ids}

    # Micro: all element occurrences pooled together
    micro_tp = sum(sum((gold_sets[i] & pred_sets[i]).values()) for i in ids)
    micro_fp = sum(sum((pred_sets[i] - gold_sets[i]).values()) for i in ids)
    micro_fn = sum(sum((gold_sets[i] - pred_sets[i]).values()) for i in ids)
    micro_p, micro_r, micro_f1 = prf(micro_tp, micro_fp, micro_fn)

    # Macro: computed per element type, then averaged with equal weight, over
    # the union of every type that appears anywhere in gold or predictions
    all_types = set()
    for s in gold_sets.values():
        all_types.update(s)
    for s in pred_sets.values():
        all_types.update(s)

    per_type = {}
    for t in sorted(all_types):
        tp = sum(min(gold_sets[i][t], pred_sets[i][t]) for i in ids)
        fp = sum(max(pred_sets[i][t] - gold_sets[i][t], 0) for i in ids)
        fn = sum(max(gold_sets[i][t] - pred_sets[i][t], 0) for i in ids)
        per_type[t] = prf(tp, fp, fn) + (tp, fp, fn)

    n = len(per_type) or 1
    macro_p = sum(v[0] for v in per_type.values()) / n
    macro_r = sum(v[1] for v in per_type.values()) / n
    macro_f1 = sum(v[2] for v in per_type.values()) / n

    return {
        'micro': {'tp': micro_tp, 'fp': micro_fp, 'fn': micro_fn,
                   'precision': micro_p, 'recall': micro_r, 'f1': micro_f1},
        'macro': {'precision': macro_p, 'recall': macro_r, 'f1': macro_f1, 'n_types': len(per_type)},
        'per_type': per_type,
    }


def motif_key(motif):
    return (frozenset(motif['elements']), motif['category'])


def evaluate_motifs(gold, pred, ids):
    tp = fp = fn = 0
    for i in ids:
        gold_counts = Counter(motif_key(m) for m in gold[i].get('motifs', []))
        pred_counts = Counter(motif_key(m) for m in pred.get(i, {}).get('motifs', []))
        common = gold_counts & pred_counts
        tp += sum(common.values())
        fp += sum((pred_counts - gold_counts).values())
        fn += sum((gold_counts - pred_counts).values())
    precision, recall, f1 = prf(tp, fp, fn)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'precision': precision, 'recall': recall, 'f1': f1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('method', choices=sorted(RESULT_FILES))
    sample = parser.add_mutually_exclusive_group()
    sample.add_argument('--former-test', action='store_true',
                        help='evaluate against the former test sample (edh_former_testsample.json)')
    sample.add_argument('--test', action='store_true',
                        help='evaluate against the held-out test sample (edh_testsample.json), with the results of '
                             'measure_testsample.py')
    args = parser.parse_args()

    if args.test:
        gold, label = load_json(EDH_TESTSAMPLE), 'test sample'
        pred = load_json(EDH_RESULTS_TESTSAMPLE / f'{args.method}.json')
    else:
        gold = load_json(EDH_FORMER_TESTSAMPLE if args.former_test else EDH_DEVSAMPLE)
        label = 'former test sample' if args.former_test else 'development sample'
        pred = load_json(RESULT_FILES[args.method])
    ids = list(gold)

    depiction = evaluate_depiction(gold, pred, ids)
    elements = evaluate_elements(gold, pred, ids)
    parents = {name: meta['group'] for name, meta in load_json(ELEMENTS).items() if meta.get('group')}
    lenient = evaluate_elements(gold, pred, ids, parents)
    motifs = evaluate_motifs(gold, pred, ids)

    print(f'Method: {args.method}  (against {len(ids)} {label} rows)')
    print()
    print('Level 1 - has_depiction')
    print(f'  true positive  {depiction["rp"]:4d}   false positive {depiction["fp"]:4d}')
    print(f'  false negative {depiction["fn"]:4d}   true negative  {depiction["rn"]:4d}')
    print(f'  recall {depiction["recall"]:.1%}   precision {depiction["precision"]:.1%}   F1 {depiction["f1"]:.1%}')
    print()
    print('Level 2 - elements (presence)')
    m = elements['micro']
    ma = elements['macro']
    print(f'  micro: recall {m["recall"]:.1%}   precision {m["precision"]:.1%}   F1 {m["f1"]:.1%}')
    print(f'  macro: recall {ma["recall"]:.1%}   precision {ma["precision"]:.1%}   F1 {ma["f1"]:.1%}   ({ma["n_types"]} element types)')
    lm = lenient['micro']
    lma = lenient['macro']
    print('  lenient (subtypes -> group, e.g. man/woman -> person):')
    print(f'    micro: recall {lm["recall"]:.1%}   precision {lm["precision"]:.1%}   F1 {lm["f1"]:.1%}')
    print(f'    macro: recall {lma["recall"]:.1%}   precision {lma["precision"]:.1%}   F1 {lma["f1"]:.1%}   ({lma["n_types"]} element types)')
    print()
    print('  Weakest element types (by F1, only ones attested in the sample):')
    gold_present = {t for i in ids for t in {e['element'] for e in gold[i]['elements']}}
    weakest = sorted(
        (t for t in elements['per_type'] if t in gold_present),
        key=lambda t: elements['per_type'][t][2],
    )[:10]
    for t in weakest:
        p, r, f1, tp, fp, fn = elements['per_type'][t]
        print(f'    {t:25s} F1 {f1:.0%}   (tp={tp} fp={fp} fn={fn})')
    print()
    print('Level 3 - motifs (exact match)')
    print(f'  recall {motifs["recall"]:.1%}   precision {motifs["precision"]:.1%}   F1 {motifs["f1"]:.1%}')
    print(f'  (tp={motifs["tp"]} fp={motifs["fp"]} fn={motifs["fn"]})')


if __name__ == '__main__':
    main()
