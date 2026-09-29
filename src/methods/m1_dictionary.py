"""
Method 1: dictionary lookup (substring search, no linguistic analysis).

For every EDH comment in the time window (not_after > 150 or undated, see
matching.is_in_scope()), independently of the other methods:

  - has_depiction: a signal word (signal_words.json) OR a recognised element
    makes the comment a hit.
  - elements: substring search against the German search terms in
    element_synonyms.json. Elements on the stoplist (ambiguous words like
    "Säule") are never searched for. A hit sitting inside a false-friend word
    ("esel" in "dieselbe") doesn't count. Multi-word forms ("Alpha und
    Omega") are matched over consecutive words first; words they cover
    aren't searched again ("Kranz mit Tänien" is corona_vittata, not also
    wreath), see matching.find_phrases().
  - motifs: no grouping - every found element forms its own motif
    (resolve_motifs() on that element alone). Form words ("Büste",
    "Ganzfigur") become the variant of the person they describe
    (motifs.fold_forms()).

Not implemented: compound analysis beyond the substring search itself,
other variants (posture, orientation, design) and uncertainty detection. The count comes from a number word or
digit right before the match, see find_elements().

Output: results/full_corpus/m1_dictionary.json.

Usage:
    python src/methods/m1_dictionary.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import (  # noqa: E402
    ELEMENTS,
    ELEMENT_SYNONYMS,
    MOTIF_RULES,
    EDH_SIGNAL_WORDS,
    EDH_FILTER_STOPLIST,
    EDH_FILTER_FALSE_FRIENDS,
    EDH_COMMENTS,
    EDH_RESULT_DICTIONARY,
)
from common.motifs import resolve_motifs, fold_forms  # noqa: E402
from common.matching import (is_in_scope, stoplist_for, build_element_forms, has_signal_word, matching_elements,  # noqa: E402
                      phrase_forms, find_phrases, normalise_word, number_value, rule_count)


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def tokenize(text):
    """Words for the false-friends check: runs of letters (incl. Umlaute/ß)
    or digits - digits kept so "2 Büsten" can be counted."""
    word = []
    for ch in text:
        if ch.isalnum():
            word.append(ch)
        elif word:
            yield ''.join(word)
            word = []
    if word:
        yield ''.join(word)


def find_elements(text, element_forms, false_friend_words):
    """Every element mention in text via substring search, false friends dropped.

    False-friend entries are themselves substrings to look for in the token
    (e.g. "schaft" has to catch "Schaftblock", "Säulenschaft", "Säulenschaftes"
    alike, not just the bare word "schaft"), not exact whole-word matches.

    Count: a number word or digit in the two tokens before ("zwei Büsten",
    "3 weibliche Büsten"), else 1. plural endings are deliberately not read,
    a substring search can't tell "weibliche" (adjective ending) or "eines
    Knaben" (weak noun, singular) from a real plural.
    """
    def count_before(i):
        return next((n for n in (number_value(t) for t in reversed(tokens[max(0, i - 2):i]))
                     if n is not None), 1)

    found = []
    tokens = list(tokenize(text))
    covered = set()
    for element_key, start, end in find_phrases([[normalise_word(t)] for t in tokens],
                                                phrase_forms(element_forms), lambda t, f: f in t):
        found.append({'element': element_key, 'matched_text': ' '.join(tokens[start:end]),
                      'count': count_before(start)})
        covered.update(range(start, end))
    # the same element on two neighbouring words is one mention: "stehende
    # Figur" is one full figure, not two (which would make it a couple)
    previous = set()
    for i, token in enumerate(tokens):
        if i in covered:
            previous = set()
            continue
        keys = matching_elements(token.lower(), element_forms, lambda t, f: f in t, false_friend_words)
        for element_key in keys:
            if element_key not in previous:
                found.append({'element': element_key, 'matched_text': token, 'count': count_before(i)})
        previous = set(keys)
    return found


def analyze(text, element_forms, signal_words, false_friend_words, motif_rules, elements_meta):
    """Run method 1 on a single comment, in the annotation/results shape.

    Every found element is passed to resolve_motifs() on its own (a
    single-element list), which structurally rules out any combination.
    method 1 never attempts grouping.
    """
    elements = find_elements(text, element_forms, false_friend_words)
    motifs = [
        m
        for e in elements
        for m in resolve_motifs([e['element']] * rule_count(e['count']), motif_rules, elements_meta)
    ]
    # one depicted figure = one element: form words become the persons'
    # variant (motifs.fold_forms)
    result_elements, motifs = fold_forms([
        {
            'element': e['element'],
            'count': e['count'],
            'uncertain': False,
            'variant_condition': None,
            'matched_text': e['matched_text'],
        }
        for e in elements
    ], motifs, elements_meta)
    return {
        'has_depiction': bool(elements) or has_signal_word(text, signal_words),
        'elements': result_elements,
        'motifs': motifs,
    }


def main():
    synonyms = load_json(ELEMENT_SYNONYMS)
    elements_meta = load_json(ELEMENTS)
    motif_rules = load_json(MOTIF_RULES)
    signal_words = load_json(EDH_SIGNAL_WORDS)
    stoplist = stoplist_for(load_json(EDH_FILTER_STOPLIST), 'dictionary')
    false_friends = load_json(EDH_FILTER_FALSE_FRIENDS)

    element_forms = build_element_forms(synonyms, stoplist)
    false_friend_words = {entry['word'].lower() for entry in false_friends}

    comments = load_json(EDH_COMMENTS)

    results = {}
    n_in_scope = 0
    n_with_comment = 0
    n_depiction = 0
    n_element_hits = 0

    for record in comments:
        if not is_in_scope(record):
            continue
        n_in_scope += 1
        comment = record.get('commentary')
        if not comment:
            continue
        n_with_comment += 1

        result = analyze(comment, element_forms, signal_words, false_friend_words, motif_rules, elements_meta)
        results[record['id']] = result
        if result['has_depiction']:
            n_depiction += 1
        n_element_hits += len(result['elements'])

    os.makedirs(os.path.dirname(EDH_RESULT_DICTIONARY), exist_ok=True)
    with open(EDH_RESULT_DICTIONARY, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'Comments in date range:   {n_in_scope}')
    print(f'  with comment text:      {n_with_comment}')
    print(f'  has_depiction=True:     {n_depiction}')
    print(f'  total element hits:     {n_element_hits}')
    print(f'Output: {EDH_RESULT_DICTIONARY}')


if __name__ == '__main__':
    main()
