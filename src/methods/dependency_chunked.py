"""
EDH method 3, run in chunks: same result as dependency.py, with less memory.

Why: dependency.py parses all ~11,500 comments with Stanza in one process,
and memory use grows over the run (on a 16 GB machine the operating system
may kill the process). This script splits the comments into fixed chunks and
analyses each chunk in its own process, so memory is fully released between
chunks.

The analysis itself is not duplicated: every comment goes through
dependency.analyze() with the same vocabulary, stoplist, false friends and
motif rules as dependency.main(). Every comment is analysed independently of
all others, so the merged result is identical to a single full run.

Steps:
  1. `chunk <n>` analyses comments n*CHUNK_SIZE .. (n+1)*CHUNK_SIZE-1 and
     writes them to EDH_RESULT_DEPENDENCY_PARTS/part_<n>.json. A chunk that
     already has its part file is skipped, so after a crash you just rerun
     the missing chunks. The file is written as .tmp and renamed at the end,
     so a crash mid-write never leaves a half file that looks finished.
  2. `merge` joins all part files into EDH_RESULT_DEPENDENCY, in the same
     key order dependency.main() produces, and prints the same summary.

After changing the vocabulary or rules, delete the part files first,
otherwise the old chunks are skipped and merged again.

Usage:
    python src/methods/dependency_chunked.py chunk 0
    ...
    python src/methods/dependency_chunked.py chunk 7
    python src/methods/dependency_chunked.py merge

    # or everything in one go, still one process per chunk:
    python src/methods/dependency_chunked.py all
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import EDH_RESULT_DEPENDENCY_PARTS  # noqa: E402
import dependency as dep  # noqa: E402

CHUNK_SIZE = 1500


def load_records():
    """All comments, and those dependency.main() would analyse."""
    comments = dep.load_json(dep.EDH_COMMENTS)
    records = [r for r in comments if dep.is_in_scope(r) and r.get('commentary')]
    return comments, records


def n_chunks(records):
    return -(-len(records) // CHUNK_SIZE)


def part_path(idx):
    return EDH_RESULT_DEPENDENCY_PARTS / f'part_{idx:02d}.json'


def run_chunk(idx):
    out = part_path(idx)
    if out.exists():
        print(f'chunk {idx} already done, skipped', flush=True)
        return

    synonyms = dep.load_json(dep.ELEMENT_SYNONYMS)
    elements_meta = dep.load_json(dep.ELEMENTS)
    motif_rules = dep.load_json(dep.MOTIF_RULES)
    signal_words = dep.load_json(dep.EDH_SIGNAL_WORDS)
    stoplist = dep.stoplist_for(dep.load_json(dep.EDH_FILTER_STOPLIST), 'dependency')
    false_friends = dep.load_json(dep.EDH_FILTER_FALSE_FRIENDS)

    element_forms = dep.build_element_forms(synonyms, stoplist)
    stoplist_forms = dep.build_stoplist_forms(synonyms, stoplist)
    stoplist_meta = dep.build_stoplist_meta(stoplist)
    false_friend_words = {entry['word'].lower() for entry in false_friends}
    compounds = dep.build_compounds(element_forms, dep.load_json(dep.EDH_COMPOUND_EXCEPTIONS))

    _, records = load_records()
    chunk = records[idx * CHUNK_SIZE:(idx + 1) * CHUNK_SIZE]

    print(f'chunk {idx}: loading Stanza German model...', flush=True)
    # local models only: by default Stanza first checks online for model
    # updates, and a dropped connection would kill the chunk
    nlp = dep.stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma,depparse', verbose=False,
                              download_method=None)

    results = {}
    for i, record in enumerate(chunk, 1):
        doc = nlp(record['commentary'])
        results[record['id']] = dep.analyze(doc, element_forms, stoplist_forms, stoplist_meta,
                                            signal_words, false_friend_words, motif_rules,
                                            elements_meta, compounds)
        if i % 250 == 0:
            print(f'  chunk {idx}: {i}/{len(chunk)}', flush=True)

    EDH_RESULT_DEPENDENCY_PARTS.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix('.json.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False)
    os.replace(tmp, out)
    print(f'chunk {idx} done ({len(chunk)} comments)', flush=True)


def merge():
    comments, records = load_records()
    missing = [idx for idx in range(n_chunks(records)) if not part_path(idx).exists()]
    if missing:
        sys.exit(f'Missing chunks: {missing} - run them first.')

    results = {}
    for idx in range(n_chunks(records)):
        results.update(dep.load_json(part_path(idx)))
    # same key order as dependency.main()
    results = {r['id']: results[r['id']] for r in records}

    with open(dep.EDH_RESULT_DEPENDENCY, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'Comments in date range:   {sum(1 for r in comments if dep.is_in_scope(r))}')
    print(f'  with comment text:      {len(records)}')
    print(f'  has_depiction=True:     {sum(1 for v in results.values() if v["has_depiction"])}')
    print(f'  total element hits:     {sum(len(v["elements"]) for v in results.values())}')
    print(f'Output: {dep.EDH_RESULT_DEPENDENCY}')


def run_all():
    _, records = load_records()
    for idx in range(n_chunks(records)):
        # a fresh interpreter per chunk - that is the whole point
        subprocess.run([sys.executable, os.path.abspath(__file__), 'chunk', str(idx)], check=True)
    merge()


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ('chunk', 'merge', 'all'):
        sys.exit(__doc__)
    if sys.argv[1] == 'chunk':
        run_chunk(int(sys.argv[2]))
    elif sys.argv[1] == 'merge':
        merge()
    else:
        run_all()
