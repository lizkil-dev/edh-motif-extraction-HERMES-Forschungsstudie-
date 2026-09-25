"""
From found elements to motifs - shared by every method, so that the motif
categories are derived identically for all of them and differences in the
results come from element recognition alone.

A method hands over the elements it found per group (a sentence, a
dependency component); resolve_motifs() combines them into motifs via
motif_rules.json, fold_forms() then turns form words (bust, full figure ...)
into variants of the persons they describe.
"""

from collections import Counter, deque

# Portrait form words, most specific first (annotation guidelines, "Personen").
# They are searched for as elements, because the motif rules need them to
# tell the form, but in the result a depicted figure is ONE element: the
# person, with the form as its variant ("weibliche Büste" -> woman, variant
# bust - not bust + woman).
FORMS = ('clipeus', 'bust', 'orant', 'full_figure', 'head')
# words that only name the motif ("Porträt", "dextrarum iunctio"): the motif
# category carries them, they are no depicted element of their own; alone
# they stand for these persons
MARKERS = {'portrait': ('person',), 'dextrarum_iunctio': ('man', 'woman')}
# "Ehepaar" is searched as its own element, but a couple is always a man and a
# woman, one each ("zwei Ehepaare": two of each)
COUPLE = ('man', 'woman')


def expand_couples(element_keys):
    """element keys with every "couple" replaced by "man" and "woman"."""
    return [part for key in element_keys for part in (COUPLE if key == 'couple' else (key,))]


def _expand_couple_entries(elements):
    """Result entries with a "couple" entry replaced by a man and a woman
    entry of the same count, uncertainty and variant."""
    result = []
    for entry in elements:
        if entry['element'] != 'couple':
            result.append(entry)
            continue
        for person in COUPLE:
            result.append(dict(entry, element=person))
    return result


def _count(entries):
    """Total count of element entries; '>1' stays '>1'."""
    if any(e['count'] == '>1' for e in entries):
        return '>1'
    return sum(e['count'] for e in entries)


def _add_variant(entry, variant):
    current = entry.get('variant_condition')
    values = current if isinstance(current, list) else ([current] if current else [])
    if variant not in values:
        values = values + [variant]
    entry['variant_condition'] = values[0] if len(values) == 1 else values


def fold_forms(elements, motifs, elements_meta):
    """Turn form words into the variant of the persons they describe.

    elements: result entries ({'element', 'count', 'variant_condition', ...},
    possibly several per type); motifs: [{'elements', 'category'}] as
    returned by resolve_motifs(). Per motif:

      - form word + person(s): the persons get the form as variant, the form
        word disappears ("Büsten eines Mannes und einer Frau" -> man (bust),
        woman (bust));
      - form word without any person: it becomes that many persons of
        unknown sex ("zwei Büsten" -> person x2, bust). A clipeus alone is
        only a frame ("die Inschrift befindet sich auf einem Medaillon") and
        stays an element;
      - "Porträt"/"dextrarum iunctio" disappear into the motif category; on
        their own they stand for a person / a man and a woman;
      - a form word without any person whose form already came up earlier in
        the comment is a second mention of the same figure ("Büste eines
        Knaben. Z. 1: D und M links und rechts der Büste"), not a new person:
        it is dropped. Rarely wrong ("auf der Nebenseite eine weitere Büste").

    Motifs and element entries are both in text order, so each motif takes
    the next entry of each of its form words; a new person's count comes
    from its own entries only, not from every entry of that form.

    The motif category is left as it is. Returns (elements, motifs).
    """
    def is_person(key):
        return elements_meta.get(key, {}).get('group') == 'person'

    elements = _expand_couple_entries(elements)
    variants = {}          # person key -> forms to add
    converted = {}         # (counted form, variant form) -> entries that became persons
    kept_forms = set()
    seen_forms = set()     # forms mentioned so far, for second mentions
    queues = {}
    for entry in elements:
        if entry['element'] in FORMS:
            queues.setdefault(entry['element'], deque()).append(entry)
    new_motifs = []
    for motif in motifs:
        keys = list(motif['elements'])
        forms = [k for k in FORMS if k in keys]
        own = {f: [queues[f].popleft()] if queues.get(f) else [] for f in forms}
        if forms == ['clipeus'] and not any(is_person(k) for k in keys):
            kept_forms.add('clipeus')
            forms = []
        markers = [k for k in keys if k in MARKERS]
        keys = [k for k in keys if k not in forms and k not in markers]
        persons = [k for k in keys if is_person(k)]
        if forms and not persons and not (motif['category'] or '').startswith(('portrait_', 'figure_')):
            # a form word in a non-portrait motif is no person: Jupiter
            # Ammon's head, an animal's head ("caput agni") - it stays
            kept_forms.update(forms)
            keys += forms
            forms = []
        if forms and persons:
            for key in persons:
                variants.setdefault(key, []).append(forms[0])
        elif forms and any(f in seen_forms for f in forms):
            # second mention of a figure already found: no new person
            seen_forms.update(forms)
            if not keys:
                continue
        elif forms:
            # the number of persons is the number of busts/figures, not of
            # clipei ("Medaillon mit 5 Büsten"); the variant is the most
            # specific form (a bust in a clipeus is a clipeus portrait)
            counted = next(k for k in forms if k != 'clipeus')
            converted.setdefault((counted, forms[0]), []).extend(own[counted])
            keys.append('person')
        seen_forms.update(forms)
        if markers and not persons and not forms:
            keys.extend(MARKERS[markers[0]])
        new_motifs.append({'elements': sorted(set(keys)), 'category': motif['category']})
    # entries no motif took (two mentions grouped into one motif) count
    # with the first person made from that form
    for (counted, form), entries in converted.items():
        entries.extend(queues.pop(counted, []))

    by_key = {}
    for entry in elements:
        by_key.setdefault(entry['element'], []).append(entry)
    result = []
    for entry in elements:
        key = entry['element']
        if (key in FORMS and key not in kept_forms) or key in MARKERS:
            continue
        entry = dict(entry)
        for form in variants.get(key, []):
            _add_variant(entry, form)
        result.append(entry)
    for (counted, form), sources in converted.items():
        entry = {'element': 'person', 'count': _count(sources or [{'count': 1}]),
                 'uncertain': any(e.get('uncertain') for e in sources),
                 'variant_condition': None}
        for source in sources:  # "stehende Figur": keep "standing"
            current = source.get('variant_condition')
            for variant in (current if isinstance(current, list) else [current] if current else []):
                _add_variant(entry, variant)
        _add_variant(entry, form)
        result.append(entry)
    for marker, persons in MARKERS.items():
        for person in persons:
            if marker in by_key and not any(e['element'] == person for e in result) \
                    and any(person in m['elements'] for m in new_motifs):
                result.append({'element': person, 'count': 1, 'uncertain': False, 'variant_condition': None})
    return result, new_motifs


def resolve_motifs(element_keys, motif_rules, elements_meta):
    """Group co-occurring elements into motifs via motif_rules.json.

    element_keys: the element keys considered together as one group (e.g.
    every element in one sentence, or a single-element list for a method
    that never attempts grouping - passing one element at a time there
    guarantees no combination is ever attempted). "couple" is expanded to
    man + woman first.

    Rules are tried in file order; the first rule whose requirements are met
    by what's still unclaimed wins and consumes its elements.

    A requirement normally consumes exactly min_count instances. With
    "take_all": true it consumes every remaining instance instead; with
    min_count 0 it becomes optional; max_count caps how many may be present.

    "shared": true is for the portrait form words: a form describes every
    person in the group rather than being one of them, so a shared
    requirement only checks it's there and doesn't consume it - in "Büsten
    einer Frau und zweier Männer" all three persons are busts. Once a shared
    requirement has matched, that element is spent: plain (non-shared)
    requirements no longer see it, so a later "two busts, no person" rule
    can't reuse "Büsten" that already named the persons, and it doesn't turn
    into a leftover motif either.

    Whatever isn't claimed by any rule becomes its own single-element motif -
    one per element type, however many instances are left ("drei Delfine" is
    one dolphin motif, the number lives in the element's count), with the
    element's default category from elements.json. A lone person thus ends
    up at figure_unspecified (no evidence for a portrait). Finally, objects a
    figure holds or wears join the figure's motif (_join_attributes).
    """
    remaining = Counter(expand_couples(element_keys))
    spent = set()
    motifs = []

    def available(r):
        if r['element'] in spent and not r.get('shared'):
            return 0
        return remaining.get(r['element'], 0)

    for rule in motif_rules:
        requires = rule['requires']
        if not all(
            r['min_count'] <= available(r) <= r.get('max_count', float('inf'))
            for r in requires
        ):
            continue
        if not any(available(r) for r in requires if not r.get('shared')):
            continue

        used = []
        for r in requires:
            key = r['element']
            if r.get('shared'):
                if available(r):
                    spent.add(key)
                    used.append(key)
                continue
            take = available(r) if r.get('take_all') else r['min_count']
            remaining[key] -= take
            used.extend([key] * take)
        motifs.append({'elements': sorted(set(used)), 'category': rule['category']})

    for key in spent:
        remaining[key] = 0
    for key, n in remaining.items():
        if n > 0:
            motifs.append({'elements': [key], 'category': elements_meta.get(key, {}).get('category')})

    return _join_attributes(motifs, elements_meta)


def _join_attributes(motifs, elements_meta):
    """Objects a figure holds or wears ("attribute": true in elements.json -
    scroll, pouch, mirror, torques ...) join the figure's motif, which keeps
    its category ("Frau mit Spiegel" -> portrait_woman [woman, mirror]). Only
    if the group has exactly one motif with a figure (a person, a form word
    or an element of a *_figures category) - with two it is unclear whose
    attribute it is, and it stays on its own."""
    def is_figure(key):
        meta = elements_meta.get(key, {})
        return (meta.get('group') == 'person' or key in FORMS or key in MARKERS
                or (meta.get('category') or '').endswith('_figures'))  # "Diener mit Buchrolle"

    figures = [m for m in motifs if any(is_figure(k) for k in m['elements'])]
    if len(figures) != 1:
        return motifs
    attributes = [m for m in motifs if len(m['elements']) == 1
                  and elements_meta.get(m['elements'][0], {}).get('attribute')]
    if not attributes:
        return motifs
    figure = figures[0]
    figure['elements'] = sorted(set(figure['elements']) | {m['elements'][0] for m in attributes})
    return [m for m in motifs if m not in attributes]
