"""Word-level markings of the goldstandard for BERT (method 4), as proposals.

The goldstandard says which elements a comment contains, not at which word;
token classification needs the word. This script proposes the markings
automatically; the reviewed version is data/annotations/
edh_goldstandard_word_markings.json (every row with a depiction checked by
hand).

  - Words are Stanza tokens (a multi-word token like "im" stays one word);
    sentences as Stanza splits them, since the motifs are later built per
    sentence as in method 2.
  - Label space = the search vocabulary, form and marker words included
    ("Büste" -> bust, "Porträt" -> portrait, "Ehepaar" -> couple): BERT's
    output goes through the same resolve_motifs()/fold_forms() as method 2,
    which turns them into variants and man + woman.
  - Marking rules: every occurrence is marked, not just the first; a
    multi-word form is marked on all its words ("Alpha und Omega"); a word
    can carry several labels ("Lorbeerkranz" -> laurel + wreath,
    "Mädchenbüste" -> girl + bust).
  - A candidate label is any element whose search form matches the word as
    in method 2 (lemma, compound tail and first part, multi-word forms),
    the stoplist ignored. It is kept only if the goldstandard row allows it:
    one of its elements, a form word from its variants, "portrait"/
    "dextrarum_iunctio" for a portrait/dextrarum-iunctio motif, "couple" if
    the row has a man and a woman. Everything else is "no element".

Goldstandard elements that no word got are listed per row ("missing"); the
ones placed by hand are in MANUAL and marked as "manual" in the output.
Dropped candidates are listed too ("dropped"), so a wrongly rejected word
can be spotted.

Usage:
    python src/bert_markings.py
    -> results/edh_goldstandard_word_markings_proposals.json
"""

import json
import os
import sys

import stanza

from paths import (  # noqa: E402
    ELEMENTS,
    ELEMENT_SYNONYMS,
    EDH_FILTER_FALSE_FRIENDS,
    EDH_COMPOUND_EXCEPTIONS,
    EDH_COMMENTS,
    EDH_GOLDSTANDARD,
    EDH_MARKINGS_PROPOSALS,
)
from schema import FORMS, MARKERS  # noqa: E402
from matching import (build_element_forms, matching_elements, phrase_forms, find_phrases,  # noqa: E402
                      normalise_word, lemma_matches, build_compounds, compound_elements)


# words the vocabulary didn't reach: (word sequence, label) per row
MANUAL = {
    'HD067738': [(['Stauros'], 'stauros')],
    'HD081273': [(['Tafeln/Polyptychon'], 'writing_tablet'), (['Objekt'], 'unidentified')],
    'HD012022': [(['girlandentragenden'], 'garland')],
    'HD057010': [(['Personifikationen', 'der', 'Jahreszeiten'], 'season_personification')],
    'HD079072': [(['Akanthusdreipass'], 'acanthus')],
    'HD018127': [(['Akanthusdreipass'], 'acanthus')],
    'HD026784': [(['Gespannführer'], 'man')],
    'HD078379': [(['Netz', 'rautenförmiger', 'Linien'], 'pattern')],
    'HD020786': [(['Hibe'], 'hebe')],  # misspelt Hebe, deliberately no search form
}


def apply_manual(sentences, entries):
    """Add each manual label to its word sequence; returns what was added."""
    added = []
    for words, label in entries:
        for s in sentences:
            toks = s['tokens']
            starts = [i for i in range(len(toks) - len(words) + 1) if toks[i:i + len(words)] == words]
            if starts:
                for i in range(starts[0], starts[0] + len(words)):
                    if label not in s['labels'][i]:
                        s['labels'][i] = sorted(s['labels'][i] + [label])
                added.append([' '.join(words), label])
                break
        else:
            raise ValueError(f'manual marking not found: {words}')
    return added


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def allowed_labels(row, elements_meta):
    """Labels the goldstandard row allows (see module docstring)."""
    allowed = {e['element'] for e in row['elements']}
    for e in row['elements']:
        variant = e.get('variant_condition')
        for v in (variant if isinstance(variant, list) else [variant]):
            if v in FORMS:
                allowed.add(v)
    categories = {m['category'] for m in row.get('motifs', [])}
    if any(c.startswith('portrait_') for c in categories):
        allowed.add('portrait')
    if 'portrait_dextrarum_iunctio' in categories:
        allowed.add('dextrarum_iunctio')
    if {'man', 'woman'} <= allowed:
        allowed.add('couple')
    return allowed


def covered(element, labels_found, row):
    """True if a goldstandard element is represented by some marked word: by
    its own label, a person by its form word ("Büste" alone -> person), a
    man/woman by "Ehepaar"."""
    if element in labels_found:
        return True
    if element in ('man', 'woman') and 'couple' in labels_found:
        return True
    for e in row['elements']:
        if e['element'] != element:
            continue
        variant = e.get('variant_condition')
        if any(v in labels_found for v in (variant if isinstance(variant, list) else [variant]) if v in FORMS):
            return True
    return element in ('person', 'couple') and any(m in labels_found for m in MARKERS)


def candidates(sentence, forms, phrases, compounds, false_friend_words):
    """Per Stanza token of the sentence: the set of element keys its words
    match, as method 2 finds them (stoplist ignored)."""
    token_of = {}
    for ti, token in enumerate(sentence.tokens):
        for word in token.words:
            token_of[word.id] = ti
    found = [set() for _ in sentence.tokens]
    words = sentence.words
    token_texts = [{normalise_word(w.text), normalise_word(w.lemma or w.text)} for w in words]
    covered_words = set()
    for key, start, end in find_phrases(token_texts, phrases, str.endswith):
        for w in words[start:end]:
            found[token_of[w.id]].add(key)
            covered_words.add(w.id)
    for w in words:
        if w.id in covered_words or w.upos == 'PUNCT':
            continue
        lemma = normalise_word(w.lemma or w.text)
        keys = matching_elements(lemma, forms, lemma_matches(w.upos), false_friend_words)
        if not keys and w.upos == 'PROPN':
            keys = matching_elements(normalise_word(w.text), forms, lemma_matches(w.upos), false_friend_words)
        if w.upos != 'ADJ':
            keys = compound_elements(lemma, keys, forms, compounds, false_friend_words)
        found[token_of[w.id]].update(keys)
    return found


def main():
    elements_meta = load_json(ELEMENTS)
    forms = build_element_forms(load_json(ELEMENT_SYNONYMS), [])  # stoplist ignored
    phrases = phrase_forms(forms, split_contractions=True)
    compounds = build_compounds(forms, load_json(EDH_COMPOUND_EXCEPTIONS))
    false_friend_words = {entry['word'].lower() for entry in load_json(EDH_FILTER_FALSE_FRIENDS)}
    gold = load_json(EDH_GOLDSTANDARD)
    comments = {r['id']: r.get('commentary', '') for r in load_json(EDH_COMMENTS)}

    nlp = stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma', verbose=False, download_method=None)

    out = {}
    n_missing = n_marked = 0
    for edh_id, row in gold.items():
        doc = nlp(comments[edh_id])
        allowed = allowed_labels(row, elements_meta) if row['has_depiction'] else set()
        sentences, dropped, found_labels = [], [], set()
        for sentence in doc.sentences:
            cands = candidates(sentence, forms, phrases, compounds, false_friend_words)
            labels = []
            for token, keys in zip(sentence.tokens, cands):
                kept = sorted(k for k in keys if k in allowed)
                labels.append(kept)
                found_labels.update(kept)
                dropped.extend([token.text, k] for k in sorted(keys - set(kept)))
            sentences.append({'tokens': [t.text for t in sentence.tokens], 'labels': labels})
        manual = apply_manual(sentences, MANUAL.get(edh_id, []))
        found_labels.update(label for _, label in manual)
        missing = sorted({e['element'] for e in row['elements']
                          if not covered(e['element'], found_labels, row)})
        n_missing += len(missing)
        n_marked += sum(1 for s in sentences for labels in s['labels'] if labels)
        out[edh_id] = {'sentences': sentences, 'missing': missing, 'dropped': dropped, 'manual': manual}

    with open(EDH_MARKINGS_PROPOSALS, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    n_elements = sum(len({e['element'] for e in r['elements']}) for r in gold.values())
    print(f'{len(out)} rows, {n_marked} marked words, '
          f'{n_elements - n_missing} of {n_elements} goldstandard elements placed, {n_missing} missing')


if __name__ == '__main__':
    main()
