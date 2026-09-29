"""
Estimates the statistical uncertainty of the results. As 300 test comments
are a rather small sample, a measurement on 300 other comments would produce
slightly different F1 scores. The bootstrap estimates how large this
variation is: it gives a 95 % range for every score and for the differences
between methods.

How it works: draw 300 comments from the 300 test comments with replacement
(some comments come up twice, others not at all) and compute all scores
again; repeat 10,000 times. The range runs from the 2.5th to the 97.5th
percentile of these scores. The scores are computed with evaluate.py's own
functions, once per comment; the counts (tp/fp/fn, overall and per element
type) are then summed for each draw. Macro-F1 averages over the element types
that occur in the draw, as in evaluate.py. As a check, the scores on all
comments, each drawn once, have to equal evaluate.py's.

Differences between methods are paired: both methods are compared on the
same draws, so the choice of comments affects both alike and only the
difference between the methods remains.

BERT: in each draw, the mean of its training runs is used
(m4_bert_seed<N>.json: seed 42 from m4_bert.py train, seeds 43 and 44 from
m4_bert.py runs); mean and standard deviation across the runs are
reported separately.

Reads results/method_comparison/predictions/, writes
results/method_comparison/bootstrap.json.

Usage:
    python src/evaluation/bootstrap.py
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from paths import EDH_TESTSAMPLE, EDH_COMPARISON, EDH_PREDICTIONS, METHOD_FILES  # noqa: E402
from evaluate import evaluate_depiction, evaluate_elements, evaluate_motifs, load_json  # noqa: E402

N_SAMPLES = 10_000
SEED = 20260928
MEASURES = ['depiction_f1', 'elements_micro_f1', 'elements_macro_f1', 'motifs_f1']
LABELS = {'depiction_f1': 'Depiction F1', 'elements_micro_f1': 'Elements micro-F1',
          'elements_macro_f1': 'Elements macro-F1', 'motifs_f1': 'Motifs F1'}
METHODS = {'M1': 'm1_dictionary', 'M2': 'm2_nlp_lemma', 'M3': 'm3_dependency'}
PAIRS = [('M2', 'M3'), ('M2', 'BERT'), ('M3', 'BERT'), ('M2', 'M1')]


def f1(tp, fp, fn):
    """F1 from counts, array-wise; equals evaluate.prf (0 when there is nothing)."""
    denominator = 2 * tp + fp + fn
    return np.divide(2 * tp, denominator, out=np.zeros_like(denominator, dtype=float), where=denominator > 0)


def per_comment_counts(gold, pred, ids, types):
    """Counts per test comment: depiction, micro and motif (tp, fp, fn) and
    per element type (tp, fp, fn), from evaluate.py's own functions."""
    index = {t: k for k, t in enumerate(types)}
    depiction = np.zeros((len(ids), 3))
    micro = np.zeros((len(ids), 3))
    motifs = np.zeros((len(ids), 3))
    per_type = np.zeros((len(ids), len(types), 3))
    for n, i in enumerate(ids):
        d = evaluate_depiction(gold, pred, [i])
        depiction[n] = d['rp'], d['fp'], d['fn']
        e = evaluate_elements(gold, pred, [i])
        micro[n] = e['micro']['tp'], e['micro']['fp'], e['micro']['fn']
        for t, (_, _, _, tp, fp, fn) in e['per_type'].items():
            per_type[n, index[t]] = tp, fp, fn
        m = evaluate_motifs(gold, pred, [i])
        motifs[n] = m['tp'], m['fp'], m['fn']
    return depiction, micro, motifs, per_type


def scores(weights, counts):
    """All measures for every row of weights (how often each comment is drawn)."""
    depiction, micro, motifs, per_type = counts
    summed = lambda a: weights @ a  # noqa: E731
    t = np.tensordot(weights, per_type, axes=(1, 0))  # samples x types x 3
    present = t.sum(axis=2) > 0
    type_f1 = f1(t[..., 0], t[..., 1], t[..., 2])
    macro = np.where(present, type_f1, 0).sum(axis=1) / np.maximum(present.sum(axis=1), 1)
    return {
        'depiction_f1': f1(*summed(depiction).T),
        'elements_micro_f1': f1(*summed(micro).T),
        'elements_macro_f1': macro,
        'motifs_f1': f1(*summed(motifs).T),
    }


def check_against_evaluate(gold, pred, ids, point):
    """The point estimates have to equal evaluate.py's scores on all comments."""
    expected = {
        'depiction_f1': evaluate_depiction(gold, pred, ids)['f1'],
        'elements_micro_f1': evaluate_elements(gold, pred, ids)['micro']['f1'],
        'elements_macro_f1': evaluate_elements(gold, pred, ids)['macro']['f1'],
        'motifs_f1': evaluate_motifs(gold, pred, ids)['f1'],
    }
    for measure, value in expected.items():
        assert abs(point[measure][0] - value) < 1e-12, (measure, point[measure][0], value)


def summary(values):
    low, high = np.percentile(values[1:], [2.5, 97.5])
    return {'value': float(values[0]), 'low': float(low), 'high': float(high)}


def main():
    gold = load_json(EDH_TESTSAMPLE)
    ids = list(gold)
    preds = {name: load_json(EDH_PREDICTIONS / METHOD_FILES[key]) for name, key in METHODS.items()}
    bert_runs = {path.stem.removeprefix('m4_bert_'): load_json(path)
                 for path in sorted(EDH_PREDICTIONS.glob('m4_bert_seed*.json'))}

    types = sorted({e['element'] for p in [gold, *preds.values(), *bert_runs.values()]
                    for i in ids for e in p.get(i, {}).get('elements', [])})

    # row 0: every comment once (the actual score); rows 1..: bootstrap samples
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, len(ids), size=(N_SAMPLES, len(ids)))
    weights = np.vstack([np.ones(len(ids)), np.apply_along_axis(np.bincount, 1, draws, minlength=len(ids))])

    results = {}
    for name, pred in preds.items():
        results[name] = scores(weights, per_comment_counts(gold, pred, ids, types))
        check_against_evaluate(gold, pred, ids, results[name])
    run_scores = {}
    for run, pred in bert_runs.items():
        run_scores[run] = scores(weights, per_comment_counts(gold, pred, ids, types))
        check_against_evaluate(gold, pred, ids, run_scores[run])
    results['BERT'] = {m: np.mean([s[m] for s in run_scores.values()], axis=0) for m in MEASURES}

    out = {
        'n_comments': len(ids),
        'n_with_depiction': sum(g['has_depiction'] for g in gold.values()),
        'n_samples': N_SAMPLES,
        'seed': SEED,
        'bert_runs': list(bert_runs),
        'methods': {name: {m: summary(v[m]) for m in MEASURES} for name, v in results.items()},
        'bert_across_runs': {m: {'mean': float(np.mean([s[m][0] for s in run_scores.values()])),
                                 'sd': float(np.std([s[m][0] for s in run_scores.values()], ddof=1))
                                 if len(run_scores) > 1 else 0.0,
                                 'runs': {r: float(s[m][0]) for r, s in run_scores.items()}}
                             for m in MEASURES},
        'differences': {f'{a}-{b}': {m: summary(results[a][m] - results[b][m]) for m in MEASURES}
                        for a, b in PAIRS},
    }
    EDH_COMPARISON.mkdir(parents=True, exist_ok=True)
    with open(EDH_COMPARISON / 'bootstrap.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

    pct = lambda s: f'{100 * s["value"]:5.1f} [{100 * s["low"]:5.1f}, {100 * s["high"]:5.1f}]'  # noqa: E731
    print(f'Test sample: {out["n_comments"]} comments, {out["n_with_depiction"]} with depiction; '
          f'{N_SAMPLES} bootstrap samples; BERT = mean of {len(bert_runs)} runs ({", ".join(bert_runs)})')
    print()
    print(f'{"":20s}' + ''.join(f'{name:>22s}' for name in results))
    for m in MEASURES:
        print(f'{LABELS[m]:20s}' + ''.join(f'{pct(out["methods"][name][m]):>22s}' for name in results))
    print()
    print('BERT across runs (mean +- sd; single runs)')
    for m in MEASURES:
        b = out['bert_across_runs'][m]
        runs = ', '.join(f'{100 * v:.1f}' for v in b['runs'].values())
        print(f'  {LABELS[m]:20s} {100 * b["mean"]:5.1f} +- {100 * b["sd"]:.1f}   ({runs})')
    print()
    print('Paired differences in points [95 % range]')
    print(f'{"":20s}' + ''.join(f'{pair:>22s}' for pair in out['differences']))
    for m in MEASURES:
        print(f'{LABELS[m]:20s}' + ''.join(f'{pct(out["differences"][pair][m]):>22s}' for pair in out['differences']))
    print()
    print(f'-> {EDH_COMPARISON / "bootstrap.json"}')


if __name__ == '__main__':
    main()
