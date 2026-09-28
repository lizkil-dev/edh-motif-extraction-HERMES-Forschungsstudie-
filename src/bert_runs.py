"""
Further BERT (method 4) training runs that differ from bert.py's own run only
in the training seed, each measured on the test set (the published
comparison uses seeds 42, 43 and 44).

Training data, silver standard and all settings are those of bert.py; seed 42
is bert.py's own run (EDH_BERT_MODEL, results in results/testset/bert.json)
and is not repeated here. Per run:
  - model -> EDH_BERT_RUNS_MODELS/seed<N>/
  - results on the test set -> EDH_BERT_RUNS_RESULTS/seed<N>.json
  - checksums of model and silver standard, training time
    -> EDH_BERT_RUNS_RESULTS/runs.json
Runs whose result file already exists are skipped, so an interrupted call
can simply be restarted.

Usage:
    python src/bert_runs.py            # seeds 43 and 44
    python src/bert_runs.py 45 46      # other seeds
"""

import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'methods')))
from paths import EDH_TESTSET, EDH_BERT_SILVER, EDH_BERT_RUNS_MODELS, EDH_BERT_RUNS_RESULTS  # noqa: E402
import bert  # noqa: E402

DEFAULT_SEEDS = [43, 44]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    seeds = [int(s) for s in sys.argv[1:]] or DEFAULT_SEEDS
    ids = list(bert.load_json(EDH_TESTSET))
    EDH_BERT_RUNS_RESULTS.mkdir(parents=True, exist_ok=True)
    log_path = EDH_BERT_RUNS_RESULTS / 'runs.json'
    log = bert.load_json(log_path) if log_path.exists() else {}

    for seed in seeds:
        name = f'seed{seed}'
        out = EDH_BERT_RUNS_RESULTS / f'{name}.json'
        if out.exists():
            print(f'{name}: already done, skipped')
            continue
        model_dir = EDH_BERT_RUNS_MODELS / name
        print(f'{name}: training', flush=True)
        started = time.time()
        bert.train(seed=seed, model_dir=model_dir)
        minutes = (time.time() - started) / 60
        results = bert.predict_ids(ids, model_dir=model_dir)
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        log[name] = {
            'seed': seed,
            'model_sha256': sha256(model_dir / 'model.pt'),
            'silver_sha256': sha256(EDH_BERT_SILVER),
            'training_minutes': round(minutes, 1),
        }
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2)
        print(f'{name}: {sum(r["has_depiction"] for r in results.values())} of {len(results)} with depiction, '
              f'{minutes:.0f} min training -> {out}', flush=True)


if __name__ == '__main__':
    main()
