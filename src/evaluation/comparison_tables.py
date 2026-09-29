"""
The method comparison as tables: one row per method (scores with their 95 %
bootstrap range; method 4 as the mean of its training runs, plus their
standard deviation) and one row per paired difference between methods.

Reads bootstrap.json and predictions/ of a method comparison, writes
scores.csv and differences.csv next to bootstrap.json and prints both tables
in Markdown (as in the README). By default it reads your own run
(results/method_comparison/, from measure_testsample.py, m4_bert.py runs and
bootstrap.py); with --published the published measurement
(data/method_comparison/, same layout).

Usage:
    python src/evaluation/comparison_tables.py               # your own run
    python src/evaluation/comparison_tables.py --published   # the published measurement
"""

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from paths import EDH_TESTSAMPLE, EDH_COMPARISON, PUBLISHED_COMPARISON, METHOD_FILES, bert_file  # noqa: E402
from evaluate import evaluate_depiction, load_json  # noqa: E402

METHODS = [
    ('1', 'Dictionary matching', 'M1', 'Substring match of German search terms, no linguistic analysis'),
    ('2', 'Lemmatisation', 'M2', 'Stanza lemmas, compound tails, sentence-level motif grouping'),
    ('3', 'Dependency parsing', 'M3', 'As 2, motif grouping and context rules via the dependency tree'),
    ('4', 'BERT (gbert-base)', 'BERT', 'Fine-tuned token classification (development data + silver standard), '
                                        'mean of the training runs'),
]
MEASURES = ['depiction_f1', 'elements_micro_f1', 'elements_macro_f1', 'motifs_f1']
HEADERS = ['Depiction F1', 'Elements micro-F1', 'Elements macro-F1', 'Motifs F1']


def comparison(folder):
    """Rows per method and per paired difference, from folder/bootstrap.json
    (which bootstrap.py checks against evaluate.py); precision and recall of
    the depiction level from evaluate.py directly."""
    gold = load_json(EDH_TESTSAMPLE)
    ids = list(gold)
    boot = load_json(folder / 'bootstrap.json')
    p = folder / 'predictions'
    files = {'M1': [p / METHOD_FILES['m1_dictionary']], 'M2': [p / METHOD_FILES['m2_nlp_lemma']],
             'M3': [p / METHOD_FILES['m3_dependency']],
             'BERT': [p / bert_file(run.removeprefix('seed')) for run in boot['bert_runs']]}
    rows = []
    for number, name, key, how in METHODS:
        preds = [load_json(f) for f in files[key]]
        depiction = [evaluate_depiction(gold, pred, ids) for pred in preds]
        row = {'method': number, 'name': name, 'description': how,
               'training_runs': len(preds) if key == 'BERT' else ''}
        for measure in MEASURES:
            s = boot['methods'][key][measure]
            row[measure] = round(s['value'], 3)
            row[f'{measure}_low'] = round(s['low'], 3)
            row[f'{measure}_high'] = round(s['high'], 3)
            row[f'{measure}_sd_runs'] = round(boot['bert_across_runs'][measure]['sd'], 3) if key == 'BERT' else ''
        row['depiction_precision'] = round(sum(d['precision'] for d in depiction) / len(preds), 3)
        row['depiction_recall'] = round(sum(d['recall'] for d in depiction) / len(preds), 3)
        rows.append(row)
    differences = []
    for pair, per_measure in boot['differences'].items():
        row = {'comparison': ' minus '.join(f'method {number}' for key in pair.split('-')
                                            for number, _, k, _ in METHODS if k == key)}
        for measure in MEASURES:
            s = per_measure[measure]
            row[measure] = round(s['value'], 3)
            row[f'{measure}_low'] = round(s['low'], 3)
            row[f'{measure}_high'] = round(s['high'], 3)
        differences.append(row)
    return rows, differences


def cell(row, measure):
    """'73.9 % [64.5-82.7]'; method 4 with '± sd' of its training runs."""
    spread = f" ± {100 * row[f'{measure}_sd_runs']:.1f}" if row['training_runs'] else ''
    return (f"{100 * row[measure]:.1f}{spread} % "
            f"[{100 * row[f'{measure}_low']:.1f}–{100 * row[f'{measure}_high']:.1f}]")


def points(row, measure):
    """A difference in percentage points with its range, '+8.9 [+2.9 to +15.2]'."""
    def pp(value):
        value = 100 * value
        return f'{0.0 if abs(value) < 0.05 else value:+.1f}'  # no "-0.0"
    return f"{pp(row[measure])} [{pp(row[f'{measure}_low'])} to {pp(row[f'{measure}_high'])}]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--published', action='store_true',
                        help='use the published measurement in data/method_comparison/')
    args = parser.parse_args()
    folder = PUBLISHED_COMPARISON if args.published else EDH_COMPARISON

    rows, differences = comparison(folder)
    for name, data in (('scores.csv', rows), ('differences.csv', differences)):
        with open(folder / name, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)

    print('| Method | | ' + ' | '.join(HEADERS) + ' |')
    print('|---|---|' + '---|' * len(MEASURES))
    for r in rows:
        print(f"| {r['method']} | {r['name']} | " + ' | '.join(cell(r, m) for m in MEASURES) + ' |')
    print('\n| Comparison | ' + ' | '.join(HEADERS) + ' |')
    print('|---|' + '---|' * len(MEASURES))
    for d in differences:
        print(f"| {d['comparison']} | " + ' | '.join(points(d, m) for m in MEASURES) + ' |')
    print(f'\n-> {folder}')


if __name__ == '__main__':
    main()
