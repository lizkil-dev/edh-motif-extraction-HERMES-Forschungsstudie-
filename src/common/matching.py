"""
Matching helpers shared by the EDH methods: scope filter, vocabulary
preparation, false friends, compounds, multi-word forms, counts and signal
words. The methods differ in how they test a single word (substring for
method 1, lemma for methods 2 and 3); everything around that test is shared
here, so differences in the results come from the methods, not from helpers.
"""

# a record is in scope if not_after is missing, or greater than this value
SCOPE_MIN_NOT_AFTER = 150


def is_in_scope(record):
    """True if not_after is missing or unparseable (dating unknown, kept) or
    greater than SCOPE_MIN_NOT_AFTER."""
    not_after = record.get("not_after")
    try:
        return int(not_after) > SCOPE_MIN_NOT_AFTER
    except (TypeError, ValueError):
        return True  # missing/unparseable dating: kept by default


def stoplist_for(stoplist, method):
    """The stoplist entries that apply to method ('dictionary', 'nlp_lemma',
    'dependency'). An entry without "methods" applies to all three; one with
    it only to those listed - e.g. "Tisch" is stopped for method 1 only,
    whose substring search finds "tisch" in every adjective on -tisch
    ("identisch", "keltisch"), while methods 2 and 3 match it cleanly."""
    return [entry for entry in stoplist if method in entry.get('methods', [method])]


def build_element_forms(synonyms, stoplist):
    """element key -> lowercased German search forms, stoplist elements dropped.

    The stoplist is about ambiguous single words ("Person" mostly means the
    people named in the inscription); a stopped element's multi-word forms
    are unambiguous and stay ("figürliche Darstellung" -> person).
    """
    stopped = {entry['element'] for entry in stoplist}
    forms = {}
    for key, syn in synonyms.items():
        de_forms = [w.lower() for w in syn.get('de', []) if w]
        if key in stopped:
            de_forms = [w for w in de_forms if ' ' in w]
        if de_forms:
            forms[key] = de_forms
    return forms


def occurrences(text, part):
    """Start positions of every occurrence of part in text."""
    start = text.find(part)
    while start != -1:
        yield start
        start = text.find(part, start + 1)


def is_false_friend(token, form, false_friend_words):
    """True if every occurrence of form in token overlaps a false friend
    without covering it ("ente" in "Ornamente" overlaps "ornament"; "mann"
    in "Lehmann" sits inside "lehmann").

    Blocks just that one form, not the whole token. A form that covers the
    whole false friend is the more specific word and stays: "ornament" itself
    (the false friend listed to stop "ente"), "pflanzenornament" around
    "pflanz".
    """
    spans = [(p, p + len(ff)) for ff in false_friend_words for p in occurrences(token, ff)]
    if not spans:
        return False

    def blocked(p):
        q = p + len(form)
        return any(p < end and start < q and not (p <= start and end <= q)
                   for start, end in spans)

    return all(blocked(p) for p in occurrences(token, form))


def matching_elements(token, element_forms, matches, false_friend_words=()):
    """Element keys whose forms match token, nested matches and false
    friends dropped.

    matches(token, form) is the per-method test (substring for method 1,
    lemma suffix for methods 2 and 3). If one element's matching form sits
    inside another's ("figur" in "halbfigur", "zweig" in "palmzweig"), only
    the longer, more specific one counts - otherwise "Halbfigur" would fire
    both bust and full_figure. Unrelated matches in the same token ("frau"
    and "porträt" in "Frauenporträt" for a substring search) are both kept.
    Multi-word forms never match a single token, see find_phrases().
    """
    hits = {}
    for key, forms in element_forms.items():
        best = max((f for f in forms
                    if matches(token, f) and not is_false_friend(token, f, false_friend_words)),
                   key=len, default=None)
        if best is not None:
            hits[key] = best
    return [key for key, form in hits.items()
            if not any(form != other and form in other for other in hits.values())]


# German compounds put the depicted thing first and a generic word last
# ("Wagenszene", "Totenmahlrelief", "Rankenornament"); for these heads only
# the first part names an element
GENERIC_HEADS = ('darstellung', 'verzierung', 'ornament', 'relief', 'motiv', 'szene', 'fries', 'dekor')
HEAD_ENDINGS = ('', 'n', 'en', 'e', 's', 'es')
# linking sounds between the parts of a compound ("Hase-n-jagd")
LINKING_ENDINGS = ('', 's', 'n', 'en', 'e', 'es')


def build_compounds(element_forms, exceptions):
    """Vocabulary for compound_elements(): single-word forms (form -> element
    key) plus the compound exceptions (compound_exceptions.json)."""
    single = {}
    for key, forms in element_forms.items():
        for form in forms:
            if ' ' not in form:
                single.setdefault(form, key)
    return {
        'single': single,
        'no_modifier': [entry['word'].lower() for entry in exceptions.get('no_modifier', [])],
        'replaces': {entry['modifier']: set(entry['heads'])
                     for entry in exceptions.get('modifier_replaces_head', [])},
    }


def compound_elements(word, keys, element_forms, compounds, false_friend_words=()):
    """keys (the elements found for word via its tail) plus the element its
    first part names (methods 2 and 3).

    Methods 2 and 3 match a noun by its tail, which alone makes
    "Lorbeerkranz" only a wreath and "Wagenszene" or "Totenmahlrelief"
    nothing at all. The first part counts only if it is exactly a search
    form, at most plus a linking sound ("Hase-n-jagd"), and the rest is
    either the matched element ("Lorbeer|kranz" -> laurel + wreath) or a
    generic head ("Wagen|szene" -> cart) - a looser test would bring back the
    accidental matches of a substring search ("Pila-stern"). A generic head
    that is itself an element ("ornament") gives way to the first part
    ("Rankenornament" -> vine_tendril only).
    """
    if any(word_part in word for word_part in compounds['no_modifier']):
        return keys
    head_key = keys[0] if keys else None
    generic_head = False
    rest = ''
    if head_key:
        tail = max((f for f in element_forms[head_key] if word.endswith(f)), key=len, default=None)
        if tail is None:
            return keys
        rest = word[:len(word) - len(tail)]
        generic_head = tail in GENERIC_HEADS
    else:
        for head in GENERIC_HEADS:
            i = word.rfind(head)
            if i > 0 and word[i + len(head):] in HEAD_ENDINGS:
                rest = word[:i]
                break
    if not rest:
        return keys
    modifier = None
    for ending in LINKING_ENDINGS:
        if ending and not rest.endswith(ending):
            continue
        stem = rest[:len(rest) - len(ending)]
        if len(stem) >= 3 and stem in compounds['single'] \
                and not is_false_friend(word, stem, false_friend_words):
            modifier = compounds['single'][stem]
            break
    if modifier is None or modifier in keys:
        return keys
    replaced = compounds['replaces'].get(modifier, set())
    return [modifier] + [k for k in keys
                         if not (generic_head and k == head_key) and k not in replaced]


def lemma_matches(upos):
    """The single-word test for methods 2 and 3: a noun matches its form
    exactly or as a compound tail ("Grabpfeiler" ends with "pfeiler"), an
    adjective only exactly ("männlich") - adjectives aren't compounds, and a
    suffix test would make "identisch" a "tisch"."""
    return str.endswith if upos != 'ADJ' else str.__eq__


# German preposition + article contractions. Stanza's multi-word token
# expansion splits them into two words ("im" -> "in dem"), so a form like
# "staurogramm im kreis" needs a split variant in methods 2 and 3
CONTRACTIONS = {
    'im': ['in', 'dem'], 'am': ['an', 'dem'], 'vom': ['von', 'dem'],
    'zum': ['zu', 'dem'], 'zur': ['zu', 'der'], 'beim': ['bei', 'dem'],
    'ins': ['in', 'das'], 'ans': ['an', 'das'],
}


def phrase_forms(element_forms, split_contractions=False):
    """Multi-word forms ("alpha und omega", "kranz mit tänien") as
    (element key, [words]), longest first.

    split_contractions (methods 2 and 3): a form containing a contraction is
    also added with it split up ("staurogramm in dem kreis"), as Stanza
    tokenises it; the form as written stays, in case Stanza leaves the
    contraction whole."""
    phrases = []
    for key, forms in element_forms.items():
        for form in forms:
            if ' ' not in form:
                continue
            words = form.split()
            phrases.append((key, words))
            if split_contractions and any(w in CONTRACTIONS for w in words):
                phrases.append((key, [part for w in words for part in CONTRACTIONS.get(w, [w])]))
    return sorted(phrases, key=lambda p: len(p[1]), reverse=True)


def normalise_word(text):
    """Lowercased, punctuation stripped at both ends ("Ω." -> "ω")."""
    return text.lower().strip('.,;:!?()[]"\'')


def find_phrases(token_texts, phrases, head_matches):
    """Multi-word element mentions in a token sequence, as (element key,
    start, end) with end exclusive, non-overlapping, left to right.

    token_texts: per token, the normalised strings to test (method 1 only
    the word itself, methods 2 and 3 word and lemma). Every word of the form
    but the last matches as a prefix, since the inflection sits at the end
    ("floralen" for "floral", "Kranzes" for "kranz"); the last word, the
    phrase's head, uses the method's own single-word test head_matches(text,
    word), so compound heads work as for single words. At each position the
    longest form wins ("gefäß mit zwei henkeln" over a shorter one).
    """
    found = []
    i = 0
    while i < len(token_texts):
        for key, words in phrases:
            end = i + len(words)
            if end > len(token_texts):
                continue
            modifiers_match = all(
                any(t.startswith(w) for t in token_texts[i + j])
                for j, w in enumerate(words[:-1]))
            if modifiers_match and any(head_matches(t, words[-1]) for t in token_texts[end - 1]):
                found.append((key, i, end))
                i = end
                break
        else:
            i += 1
    return found


# German number words as they show up in EDH comments ("zwei Büsten",
# "Büsten einer Frau und zweier Männer", "die beiden Büsten")
NUMBER_WORDS = {
    'zwei': 2, 'zweier': 2, 'beide': 2, 'beiden': 2, 'beider': 2,
    'drei': 3, 'dreier': 3, 'vier': 4, 'fünf': 5, 'sechs': 6,
    'sieben': 7, 'acht': 8, 'neun': 9, 'zehn': 10,
}


def number_value(token):
    """int for a digit string or German number word, else None."""
    token = token.lower()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def rule_count(count):
    """How many instances a found element contributes to resolve_motifs():
    ">1" (plural without a number) counts as two, so "Büsten" without any
    person still reaches the couple rules."""
    return 2 if count == '>1' else count


def has_signal_word(text, signal_words):
    """True if any signal word appears anywhere in text - a depiction even
    when no specific element was recognised ("Reliefreste")."""
    text_lower = text.lower()
    return any(w.lower() in text_lower for w in signal_words)
