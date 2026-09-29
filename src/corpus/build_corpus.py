"""
Builds the corpus from an EDH download (src/corpus/fetch_edh.py): id, comment
text and dating of every record that has a comment - the input of every
method. Same format as the published data/corpus/edh_comments.json.

The result goes to results/corpus/edh_comments.json and does not replace the
published snapshot; to run the methods on a new download, copy it to
data/corpus/ yourself (the published scores then no longer apply).

Usage:
    python src/corpus/build_corpus.py   # -> results/corpus/edh_comments.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import EDH_COMMENTS_REBUILT, EDH_DOWNLOAD  # noqa: E402


def corpus(records):
    """id, comment text and dating of each record that has a comment."""
    return [{'id': r['id'], 'commentary': r['commentary'], 'not_before': r.get('not_before'),
             'not_after': r.get('not_after')} for r in records if r.get('commentary')]


def main():
    with open(EDH_DOWNLOAD, encoding='utf-8') as f:
        comments = corpus(json.load(f))
    EDH_COMMENTS_REBUILT.parent.mkdir(parents=True, exist_ok=True)
    with open(EDH_COMMENTS_REBUILT, 'w', encoding='utf-8', newline='\r\n') as f:
        json.dump(comments, f, ensure_ascii=False, indent=0)
        f.write('\n')
    print(f'{len(comments)} comments -> {EDH_COMMENTS_REBUILT}')


if __name__ == '__main__':
    main()
