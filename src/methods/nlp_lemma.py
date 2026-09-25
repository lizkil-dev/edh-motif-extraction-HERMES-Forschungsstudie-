"""
EDH method 2: lemmatisation (Stanza) with compound analysis.

For every EDH comment, independently of the other methods:

  - has_depiction: the same signal-word check as method 1 OR a recognised
    element.
  - elements: nouns, proper nouns and adjectives (NOUN_LIKE_UPOS). A word's
    Stanza lemma equals a German search term or ends with one - the depicted
    object sits at the tail of a German compound ("Giebelrelief"); the first
    part of a compound counts too under strict conditions
    (matching.compound_elements: "Lorbeerkranz" -> laurel + wreath,
    "Wagenszene" -> cart). Multi-word forms are matched first. Elements on
    the stoplist are skipped; false friends are checked on the lemma.
  - motifs: elements found within the same sentence are grouped via
    schema.resolve_motifs() (motif_rules.json) - unlike method 1, which never
    groups anything.

Not implemented: variant and uncertainty detection. The count comes from a
number word before the match or Stanza's plural feature, see word_count().

Output: results/nlp_lemma.json.

Usage:
    python src/methods/nlp_lemma.py
"""

import json
import os
import sys

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
    EDH_RESULT_NLP_LEMMA,
)
from schema import resolve_motifs, fold_forms  # noqa: E402
from matching import (is_in_scope,  # noqa: E402 stoplist_for, build_element_forms, has_signal_word, matching_elements,
                      phrase_forms, find_phrases, normalise_word, lemma_matches,
                      number_value, rule_count, build_compounds, compound_elements)


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


# PROPN: Stanza's German model tags real nouns as PROPN unreliably in this
# genre. ADJ: some search terms are adjectives ("männlich"/"weiblich" for
# man/woman, "eine männliche Büste") - excluding ADJ would miss most man/woman
# mentions.
NOUN_LIKE_UPOS = {'NOUN', 'PROPN', 'ADJ'}


def word_count(sentence, index):
    """Count for the matched word at sentence.words[index]: a number word or
    digit among the determiners/adjectives/numerals directly before it ("zwei
    Büsten", "3 weibliche Büsten", "die beiden Büsten"), else ">1" if Stanza
    marks it plural, else 1."""
    for prev in reversed(sentence.words[:index]):
        if prev.upos not in {'NUM', 'ADJ', 'DET'}:
            break
        n = number_value(prev.text)
        if n is not None:
            return n
    if 'Number=Plur' in (sentence.words[index].feats or ''):
        return '>1'
    return 1


def find_elements_in_sentence(sentence, element_forms, false_friend_words, compounds):
    """Every noun (or proper noun) in this Stanza sentence whose lemma matches
    an element, exactly or as a compound tail; false friends checked on the
    lemma.

    PROPN is included alongside NOUN: Stanza's German tagger frequently
    mistags plain nouns as PROPN in the terse, article-less description style
    EDH comments use ("Kranz mit Tänien", "Reiter nach rechts") - the same
    word gets tagged NOUN or PROPN depending on surrounding sentence
    structure, so restricting to NOUN alone drops real matches essentially at
    random.

    Multi-word forms ("Alpha und Omega") are matched first, on word or lemma
    and regardless of part of speech ("und" is CCONJ); the words they cover
    aren't searched again, see matching.find_phrases().
    """
    words = sentence.words
    found = []
    covered = set()
    token_texts = [{normalise_word(w.text), normalise_word(w.lemma or w.text)} for w in words]
    for element_key, start, end in find_phrases(token_texts, phrase_forms(element_forms, split_contractions=True),
                                                str.endswith):
        found.append({'element': element_key,
                      'matched_text': ' '.join(w.text for w in words[start:end]),
                      'count': word_count(sentence, start)})
        covered.update(range(start, end))
    # the same element on two neighbouring words is one mention: "stehende
    # Figur" is one full figure, not two (which would make it a couple)
    previous = set()
    for index, word in enumerate(words):
        if index in covered or word.upos not in NOUN_LIKE_UPOS:
            previous = set()
            continue
        # normalised like the word itself: before "Z." Stanza can give the
        # lemma "Frau." with the full stop
        lemma = normalise_word(word.lemma or word.text)
        keys = matching_elements(lemma, element_forms, lemma_matches(word.upos), false_friend_words)
        if not keys and word.upos == 'PROPN':
            # Stanza lemmatises names badly ("Selene" -> "Selen"), so a proper
            # noun is also tried as written
            keys = matching_elements(normalise_word(word.text), element_forms,
                                     lemma_matches(word.upos), false_friend_words)
        if word.upos != 'ADJ':
            # the first part of a compound ("Lorbeerkranz", "Wagenszene")
            keys = compound_elements(lemma, keys, element_forms, compounds, false_friend_words)
        for element_key in keys:
            if element_key not in previous:
                found.append({'element': element_key, 'matched_text': word.text,
                              'count': word_count(sentence, index)})
        previous = set(keys)
    return found


def analyze(doc, element_forms, signal_words, false_friend_words, motif_rules, elements_meta, compounds):
    """Run method 2 on one already-processed Stanza document, in the
    annotation/results shape."""
    all_elements = []
    motifs = []
    for sentence in doc.sentences:
        sentence_elements = find_elements_in_sentence(sentence, element_forms, false_friend_words, compounds)
        all_elements.extend(sentence_elements)
        element_keys = [e['element'] for e in sentence_elements for _ in range(rule_count(e['count']))]
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
    stoplist = stoplist_for(load_json(EDH_FILTER_STOPLIST), 'nlp_lemma')
    false_friends = load_json(EDH_FILTER_FALSE_FRIENDS)

    element_forms = build_element_forms(synonyms, stoplist)
    false_friend_words = {entry['word'].lower() for entry in false_friends}
    compounds = build_compounds(element_forms, load_json(EDH_COMPOUND_EXCEPTIONS))

    comments = load_json(EDH_COMMENTS)

    print('Loading Stanza German model (this takes a moment)...')
    nlp = stanza.Pipeline('de', processors='tokenize,mwt,pos,lemma', verbose=False)

    results = {}
    n_in_scope = 0
    n_with_comment = 0
    n_depiction = 0
    n_element_hits = 0

    to_process = [
        record for record in comments
        if is_in_scope(record) and record.get('commentary')
    ]
    n_in_scope = sum(1 for r in comments if is_in_scope(r))
    n_with_comment = len(to_process)

    print(f'Tagging {n_with_comment} comments (this is the slow part)...')
    for i, record in enumerate(to_process, 1):
        doc = nlp(record['commentary'])
        result = analyze(doc, element_forms, signal_words, false_friend_words, motif_rules, elements_meta,
                         compounds)
        results[record['id']] = result
        if result['has_depiction']:
            n_depiction += 1
        n_element_hits += len(result['elements'])
        if i % 1000 == 0:
            print(f'  {i}/{n_with_comment}...')

    os.makedirs(os.path.dirname(EDH_RESULT_NLP_LEMMA), exist_ok=True)
    with open(EDH_RESULT_NLP_LEMMA, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'Comments in date range:   {n_in_scope}')
    print(f'  with comment text:      {n_with_comment}')
    print(f'  has_depiction=True:     {n_depiction}')
    print(f'  total element hits:     {n_element_hits}')
    print(f'Output: {EDH_RESULT_NLP_LEMMA}')


if __name__ == '__main__':
    main()
