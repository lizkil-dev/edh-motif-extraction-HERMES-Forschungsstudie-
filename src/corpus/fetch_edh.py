"""
Downloads the EDH funerary inscriptions from the public EDH API: the first
step of the corpus (data/corpus/edh_comments.json).

  - Query: inscription type "titsep" (titulus sepulcralis), every record
    whose dating touches AD 150-800, undated records included.
  - Cleaning: the API returns not_before and not_after swapped for part of
    the records; both are put in order (min/max) before the date filter.
  - Records are sorted by EDH id.

The published corpus comes from a download of 6 May 2026 (22837 records).
The EDH changes over time, so a new download gives slightly different data;
all published scores rest on the snapshot in data/corpus/.

Missing fields (province, decoration, persons, EDCS links) were added from
the EDH record pages in the working repository; of these, the publication
only uses the EDCS links of the annotated comments
(data/goldstandard/inscription_identifiers.csv).

Usage:
    python src/corpus/fetch_edh.py      # -> results/corpus/edh_titsep_150_800.json
    python src/corpus/build_corpus.py   # -> results/corpus/edh_comments.json
"""

import json
import os
import sys
import time

import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import EDH_DOWNLOAD  # noqa: E402

API_URL = 'https://edh.ub.uni-heidelberg.de/data/api/inschrift/suche'
INSCRIPTION_TYPE = 'titsep'
START_YEAR, END_YEAR = 150, 800
PAGE_SIZE = 100
DELAY = 0.5  # seconds between requests


def ordered_dating(item):
    """(not_before, not_after) as numbers in order; a missing bound becomes
    -9999 or 9999, so undated records pass the date filter."""
    not_before = int(item['not_before']) if item.get('not_before') is not None else -9999
    not_after = int(item['not_after']) if item.get('not_after') is not None else 9999
    if not_before != -9999 and not_after != 9999:
        not_before, not_after = min(not_before, not_after), max(not_before, not_after)
        item['not_before'], item['not_after'] = str(not_before), str(not_after)
    return not_before, not_after


def fetch():
    records, offset = [], 0
    while True:
        response = requests.get(API_URL, params={'inschriftgattung': INSCRIPTION_TYPE,
                                                 'offset': offset, 'limit': PAGE_SIZE}, timeout=30)
        response.raise_for_status()
        data = response.json()
        items = data if isinstance(data, list) else data.get('items', [])
        for item in items:
            try:
                not_before, not_after = ordered_dating(item)
            except (TypeError, ValueError):
                continue  # dating that is not a number
            if not_after >= START_YEAR and not_before <= END_YEAR:
                records.append(item)
        print(f'offset {offset}: {len(records)} records so far', flush=True)
        if len(items) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
        time.sleep(DELAY)
    records.sort(key=lambda r: r.get('id', ''))
    return records


def main():
    records = fetch()
    EDH_DOWNLOAD.parent.mkdir(parents=True, exist_ok=True)
    with open(EDH_DOWNLOAD, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f'{len(records)} records -> {EDH_DOWNLOAD}')


if __name__ == '__main__':
    main()
