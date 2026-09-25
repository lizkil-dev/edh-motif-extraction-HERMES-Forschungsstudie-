"""
EDH method 3: dependency parsing (Stanza).

For every EDH comment, independently of the other methods:

  - has_depiction / elements: element recognition as in method 2 (lemma
    match of nouns, proper nouns and adjectives, compounds, multi-word
    forms, false friends) - the difference lies in motif grouping and in
    the stoplist (see below).
  - motifs: method 2 pools every element of a sentence before calling
    resolve_motifs(). That over-connects unrelated elements that just sit in
    the same sentence ("von Tauben flankiertes Staurogramm, darüber Vase"
    would feed dove + vessel to the bird_at_or_in_vessel rule). Here,
    elements are grouped by dependency connectivity within the sentence:
    every non-appos, non-punct edge connects, appos edges ("darüber Vase")
    don't - each connected component goes to resolve_motifs() on its own.
  - stoplist elements with a context rule ("Kopf", "Tafel", "Altar" ...):
    methods 1 and 2 exclude them outright; method 3 keeps them if a context
    word (requires_context in stoplist.json) sits in the same dependency
    component. Entries without a context rule ("Säule", "Pilaster",
    "Bogen" - almost always the architectural frame) are excluded as in
    methods 1 and 2.

Not implemented: variant and uncertainty detection. The count comes from a
number word before the match or the noun's plural feature, see word_count().

Output: results/dependency.json.

Usage:
    python src/methods/dependency.py

If the full run runs out of memory, use dependency_chunked.py instead
(same result, one process per chunk).
"""

import json
import os
import sys
from collections import defaultdict

import stanza

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import (  # noqa: E402
    ELEMENTS,
    ELEMENT_SYNONYMS,
    MOTIF_RULES,
    EDH_SIGNAL_WORDS,
    EDH_FILTER_STOPLIST,
    EDH_FILTER_FALSE_FRIENDS,
    EDH_COMPOUND_EXCEPTIONS,
    EDH_COMMENTS,
    EDH_RESULT_DEPENDENCY,
)
from schema import resolve_motifs, fold_forms  # noqa: E402
from matching import (is_in_scope,  # noqa: E402 stoplist_for, build_element_forms, has_signal_word, matching_elements,
                      is_false_friend, phrase_forms, find_phrases, normalise_word, lemma_matches,
                      number_value, rule_count, build_compounds, compound_elements)


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


# PROPN: Stanza's German model tags real nouns as PROPN unreliably in this
# genre. ADJ: some search terms are adjectives ("männlich"/"weiblich" for
# man/woman, "eine männliche Büste") - excluding ADJ would miss most man/woman
# mentions.
NOUN_LIKE_UPOS = {'NOUN', 'PROPN', 'ADJ'}

# edges a motif-grouping component may cross; "darüber Vase" (appos) and
# punctuation don't connect two elements into the same group
NON_CONNECTING_DEPREL = {'appos', 'punct'}


def build_stoplist_forms(synonyms, stoplist):
    """element key -> lowercased German search forms, for stoplist elements
    only - the complement of matching.build_element_forms(). Method 3
    doesn't drop these outright, it keeps them in the right context.

    An entry without requires_context has nothing to decide by and is
    dropped here too, as in methods 1 and 2 ("arch", "column", "pilaster")."""
    stopped = {entry['element'] for entry in stoplist if entry.get('requires_context')}
    forms = {}
    for key, syn in synonyms.items():
        if key not in stopped:
            continue
        de_forms = [w.lower() for w in syn.get('de', []) if w]
        if de_forms:
            forms[key] = de_forms
    return forms


def build_stoplist_meta(stoplist):
    """element key -> {requires_context}, a lowercased lemma set."""
    return {
        entry['element']: {
            'requires_context': {t.lower() for t in entry.get('requires_context', [])},
        }
        for entry in stoplist
    }


def sentence_components(sentence):
    """word id -> connected-component id, via dependency edges other than
    NON_CONNECTING_DEPREL (see module docstring, "Motiv-Gruppierung")."""
    parent = {w.id: w.id for w in sentence.words}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for w in sentence.words:
        if w.head and w.deprel not in NON_CONNECTING_DEPREL:
            root_a, root_b = find(w.id), find(w.head)
            if root_a != root_b:
                parent[root_a] = root_b

    return {w.id: find(w.id) for w in sentence.words}


def word_count(word, words_by_id):
    """Count for a matched word via the dependency tree: a number word/digit
    attached to its noun ("zwei Büsten": nummod), else ">1" if the noun is
    plural, else 1. An adjective match ("zwei männliche Büsten") reads the
    count off the noun it modifies."""
    noun = word
    if word.upos == 'ADJ' and word.head in words_by_id:
        noun = words_by_id[word.head]
    for child in words_by_id.values():
        if child.head == noun.id:
            n = number_value(child.text)
            if n is not None:
                return n
    if 'Number=Plur' in (noun.feats or ''):
        return '>1'
    return 1


def find_elements_in_sentence(sentence, element_forms, stoplist_forms, stoplist_meta,
                                false_friend_words, components, compounds):
    """Every noun (or proper noun, see method 2) whose lemma matches a known
    element - stoplist elements with a context rule included, resolved via
    requires_context (see build_stoplist_meta()) instead of being skipped
    outright.

    Multi-word forms ("Alpha und Omega") are matched first, as in method 2;
    the phrase stands in the tree as its root word (the one whose head lies
    outside the phrase, "Kranz" in "Kranz mit Tänien"), which gives it its
    motif group and its count."""
    words_by_id = {w.id: w for w in sentence.words}
    # normalised like the word itself: before "Z." Stanza gives the lemma
    # "Frau." with the full stop
    lemma_by_id = {w.id: normalise_word(w.lemma or w.text) for w in sentence.words}
    words_by_component = defaultdict(list)
    for word_id, component_id in components.items():
        words_by_component[component_id].append(word_id)

    found = []
    covered = set()
    words = sentence.words
    token_texts = [{normalise_word(w.text), normalise_word(w.lemma or w.text)} for w in words]
    for element_key, start, end in find_phrases(token_texts, phrase_forms(element_forms, split_contractions=True),
                                                str.endswith):
        span_ids = {w.id for w in words[start:end]}
        root = next((w for w in words[start:end] if w.head not in span_ids), words[start])
        found.append({'element': element_key,
                      'matched_text': ' '.join(w.text for w in words[start:end]),
                      'word_id': root.id, 'count': word_count(root, words_by_id)})
        covered.update(span_ids)

    # the same element on two neighbouring words is one mention: "stehende
    # Figur" is one full figure, not two (which would make it a couple)
    previous = None
    for word in words:
        if word.id in covered or word.upos not in NOUN_LIKE_UPOS:
            previous = None
            continue
        lemma = lemma_by_id[word.id]

        matches = lemma_matches(word.upos)
        candidates = matching_elements(lemma, element_forms, matches, false_friend_words)
        if not candidates and word.upos == 'PROPN':
            # names as written, see method 2 ("Selene" -> lemma "Selen")
            candidates = matching_elements(normalise_word(word.text), element_forms, matches, false_friend_words)
        modifier = None
        if word.upos != 'ADJ':
            # the first part of a compound ("Lorbeerkranz", "Wagenszene"),
            # see method 2; it stands on the same word in the tree
            with_modifier = compound_elements(lemma, candidates, element_forms, compounds, false_friend_words)
            if with_modifier != candidates:
                modifier, candidates = with_modifier[0], with_modifier[1:]
        matched = candidates[0] if candidates else None

        if matched is None:
            for element_key, forms in stoplist_forms.items():
                if not any(matches(lemma, form) and not is_false_friend(lemma, form, false_friend_words)
                           for form in forms):
                    continue
                meta = stoplist_meta[element_key]
                has_context = any(
                    lemma_by_id[wid] in meta['requires_context']
                    for wid in words_by_component[components[word.id]]
                    if wid != word.id
                )
                if has_context:
                    matched = element_key
                break

        if modifier and modifier != previous:
            found.append({'element': modifier, 'matched_text': word.text, 'word_id': word.id,
                          'count': word_count(word, words_by_id)})
        if matched and matched != previous:
            found.append({'element': matched, 'matched_text': word.text, 'word_id': word.id,
                          'count': word_count(word, words_by_id)})
        previous = matched or modifier
    return found


def analyze(doc, element_forms, stoplist_forms, stoplist_meta, signal_words,
            false_friend_words, motif_rules, elements_meta, compounds):
    """Run method 3 on one already-processed Stanza document, in the
    annotation/results shape."""
    all_elements = []
    motifs = []
    for sentence in doc.sentences:
        components = sentence_components(sentence)
        sentence_elements = find_elements_in_sentence(
            sentence, element_forms, stoplist_forms, stoplist_meta, false_friend_words,
            components, compounds)
        all_elements.extend(sentence_elements)

        by_component = defaultdict(list)
        for e in sentence_elements:
            by_component[components[e['word_id']]].extend([e['element']] * rule_count(e['count']))
        for element_keys in by_component.values():
            motifs.extend(resolve_motifs(element_keys, motif_rules, elements_meta))

    # one depicted figure = one element: form words become the persons'
    # variant (schema.fold_forms)
    result_elements, motifs = fold_forms([
        {
            'element': e['element'],
            'count': e['count'],
            'uncertain': False,
            'variant_condition': None,
            'matched_text': e['matched_text'],
        }
        for e in all_elements
    ], motifs, elements_meta)
    return {
        'has_depiction': bool(all_elements) or has_signal_word(doc.text, signal_words),
        'elements': result_elements,
        'motifs': motifs,
    }


def main():
    synonyms = load_json(ELEMENT_SYNONYMS)
    elements_meta = load_json(ELEMENTS)
    motif_rules = load_json(MOTIF_RULES)
    signal_words = load_json(EDH_SIGNAL_WORDS)
    stoplist = stoplist_for(load_json(EDH_FILTER_STOPLIST), 'dependency')
    false_friends = load_json(EDH_FILTER_FALSE_FRIENDS)

    element_forms = build_element_forms(synonyms, stoplist)
    stoplist_forms = build_stoplist_forms(synonyms, stoplist)
    stoplist_meta = build_stoplist_meta(stoplist)
    false_friend_words = {entry['word'].lower() for entry in false_friends}
    compounds = build_compounds(element_forms, load_json(EDH_COMPOUND_EXCEPTIONS))

    comments = load_json(EDH_COMMENTS)

    print('Loading Stanza German model (this takes a moment)...', flush=True)
    nlp = stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma,depparse', verbose=False)

    results = {}
    n_depiction = 0
    n_element_hits = 0

    to_process = [
        record for record in comments
        if is_in_scope(record) and record.get('commentary')
    ]
    n_in_scope = sum(1 for r in comments if is_in_scope(r))
    n_with_comment = len(to_process)

    print(f'Tagging {n_with_comment} comments (this is the slow part)...', flush=True)
    for i, record in enumerate(to_process, 1):
        doc = nlp(record['commentary'])
        result = analyze(doc, element_forms, stoplist_forms, stoplist_meta,
                          signal_words, false_friend_words, motif_rules, elements_meta, compounds)
        results[record['id']] = result
        if result['has_depiction']:
            n_depiction += 1
        n_element_hits += len(result['elements'])
        if i % 100 == 0:
            print(f'  {i}/{n_with_comment}...', flush=True)

    os.makedirs(os.path.dirname(EDH_RESULT_DEPENDENCY), exist_ok=True)
    with open(EDH_RESULT_DEPENDENCY, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'Comments in date range:   {n_in_scope}')
    print(f'  with comment text:      {n_with_comment}')
    print(f'  has_depiction=True:     {n_depiction}')
    print(f'  total element hits:     {n_element_hits}')
    print(f'Output: {EDH_RESULT_DEPENDENCY}')


if __name__ == '__main__':
    main()
