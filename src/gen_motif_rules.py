"""
gen_motif_rules.py - generates the person/portrait block of motif_rules.json.

Why a generator: the person rules are a full cross product - every form
(clipeus, bust, orant, full_figure, head, unspecified) times every person
group (single man/woman/boy/girl/child/person, couple, family, man/person
with child, group). That is well over 100 rules that differ in one or two
places. Written by hand they drift apart; generated, a schema change is one
edit here and a rerun.

Rule order matters, since resolve_motifs() tries rules top to bottom and a
rule consumes the elements it matched. The block is built most specific
first:
  1. scenes (funerary banquet, ox cart, boy with ball, a hunt with its
     animals): a person inside a scene is not a portrait, so scenes claim
     their people first;
  2. couple with tripod and dextrarum iunctio, whatever form word stands
     next to them;
  3. portraits by form, for each form every person group, then the single
     persons, then - if no person is named - the form words themselves
     counted ("zwei Büsten" -> couple; in a clipeus the busts inside count,
     the clipeus is only the frame);
  4. couples, families and groups without any form word: always portraits.

Categories are portrait x person group only (portrait_couple,
portrait_family, ...): the form is the persons' variant in the result
(motifs.fold_forms), not part of the category. The rules still go form by
form because they need the form word to tell a portrait from a lone figure,
and to count "zwei Büsten" as two persons. Objects a figure holds or wears
join its motif afterwards ("attribute" in elements.json), and "Ehepaar"
(couple) is expanded to man + woman before the rules run
(motifs.expand_couples), so no rule needs "couple".

Flags used in the requirements (see motifs.resolve_motifs()):
  take_all  the rule consumes every occurrence of the element, not just
            min_count (three children -> one family, not three motifs)
  shared    the element is required but not consumed ("Büste" describes
            every person of the group)

Only the block from the funerary_banquet rule to the last *_no_form_word
rule is replaced; every other rule's text is left byte for byte as it is.

Usage:
    python src/gen_motif_rules.py
"""

import json
import os

from paths import MOTIF_RULES, ELEMENTS, CATEGORIES

PERSON_ONLY = ['man', 'woman', 'boy', 'girl', 'child', 'person', 'servant']
ALLFORMS = ['clipeus', 'bust', 'orant', 'full_figure', 'head', 'portrait']
# (category name, form element, other form words folded in). "head" (Kopf)
# is the weakest form: next to any other form word it only names
# the preserved part ("Ganzfiguren ..., von denen noch die Köpfe erhalten
# sind"), so every other form folds it in.
FORMS = [('clipeus', 'clipeus', ['bust', 'head', 'portrait']), ('bust', 'bust', ['head', 'portrait']),
         ('orant', 'orant', ['head', 'portrait']), ('full_figure', 'full_figure', ['head', 'portrait']),
         ('head', 'head', ['portrait']), ('unspecified', 'portrait', [])]


def req(el, mn=1, mx=None, take_all=False, shared=False):
    d = {'element': el, 'min_count': mn}
    if mx is not None:
        d['max_count'] = mx
    if take_all:
        d['take_all'] = True
    if shared:
        d['shared'] = True
    return d


def shared_opt(el):
    return req(el, 0, shared=True)


def person_groups():
    """(group, variant, requirements) - most specific first."""
    g = []
    for k in ['child', 'boy', 'girl']:
        g.append(('family', k, [req('man', 1, 1), req('woman', 1, 1), req(k, take_all=True)]))
        # two adults of unknown sex + child is a family too
        g.append(('family', f'{k}_via_two_persons', [req('person', 2, 2), req(k, take_all=True)]))
    for k in ['child', 'boy', 'girl']:
        g.append(('man_with_child', k, [req('man', 1, 1), req(k, take_all=True)]))
        # "Erwachsener"/"Person" + child: unsexed adult
        g.append(('person_with_child', k, [req('person', 1, 1), req(k, take_all=True)]))
    # three or more adults of any sex are a group ("Büsten einer Frau und
    # dreier Männer"), not only three unsexed persons
    g.append(('group', 'men_and_women', [req('man', 2, take_all=True), req('woman', 1, take_all=True)]))
    g.append(('group', 'man_and_women', [req('man', 1, 1), req('woman', 2, take_all=True)]))
    g.append(('group', 'men', [req('man', 3, take_all=True)]))
    g.append(('group', 'women', [req('woman', 3, take_all=True)]))
    g.append(('couple', 'man_woman', [req('man', 1, 1), req('woman', 1, 1)]))
    g.append(('couple', 'two_men', [req('man', 2, 2)]))
    g.append(('couple', 'two_women', [req('woman', 2, 2)]))
    g.append(('couple', 'two_persons', [req('person', 2, 2)]))
    g.append(('group', 'persons', [req('person', 3, take_all=True)]))
    return g


def animal_elements():
    """Every element whose category sits under "animals" in categories.json."""
    with open(CATEGORIES, encoding='utf-8') as f:
        tree = json.load(f)['animals']
    animal_categories = set()
    stack = [tree['children']]
    while stack:
        for key, node in stack.pop().items():
            animal_categories.add(key)
            stack.append(node['children'])
    with open(ELEMENTS, encoding='utf-8') as f:
        elements = json.load(f)
    return sorted((key, meta['category']) for key, meta in elements.items()
                  if meta['category'] in animal_categories)


def build():
    rules = []
    R = lambda id_, reqs, cat: rules.append({'id': id_, 'requires': reqs, 'category': cat})
    # scenes first: people inside a scene are not portraits
    R('funerary_banquet', [req('banquet', take_all=True)] + [req(x, 0, take_all=True) for x in PERSON_ONLY],
      'funerary_banquet')
    R('field_work_ox_cart', [req('ox_cart', take_all=True), req('man', 0, take_all=True),
                             req('person', 0, take_all=True)], 'field_work')
    R('boy_with_ball', [req('boy', 1), req('ball', 1)], 'boy_with_ball')
    # a hunt and the hunted animals are one scene ("Hasenjagd")
    for key, _ in animal_elements():
        R(f'hunting_scene_{key}', [req('hunt', take_all=True), req(key, take_all=True)], 'hunting_scene')
    for var, who in [('man_woman', [req('man', 1, 1), req('woman', 1, 1)]),
                     ('two_persons', [req('person', 2, 2)])]:
        R(f'couple_with_tripod_{var}', who + [req('tripod', take_all=True)] + [shared_opt(f) for f in ALLFORMS],
          'couple_with_tripod')
    # a couple in the dextrarum iunctio is its own portrait category
    for var, who in [('man_woman', [req('man', 1, 1), req('woman', 1, 1)]),
                     ('two_persons', [req('person', 2, 2)])]:
        R(f'dextrarum_iunctio_{var}', who + [req('dextrarum_iunctio', take_all=True)]
          + [shared_opt(f) for f in ALLFORMS], 'portrait_dextrarum_iunctio')
    # portraits by form
    for fname, fel, absorb in FORMS:
        form = [req(fel, shared=True)] + [shared_opt(x) for x in absorb]
        pre = f'portrait_{fname}'
        for grp, var, reqs in person_groups():
            R(f'{pre}_{grp}_{var}', reqs + form, f'portrait_{grp}')
        for k in ['man', 'woman', 'boy', 'girl', 'child']:
            R(f'{pre}_{k}', [req(k, take_all=True)] + form, f'portrait_{k}')
        R(f'{pre}_person', [req('person', 1, 1)] + form, 'portrait_person')
        # no person named: count the form words themselves ("zwei Büsten").
        # A clipeus is only a frame - there the busts inside it are counted.
        counted, extra = (('bust', [req('clipeus', shared=True), shared_opt('portrait')]) if fel == 'clipeus'
                          else (fel, [shared_opt(x) for x in absorb]))
        if fel == 'clipeus':
            R(f'{pre}_one_unsexed', [req('bust', 1, 1)] + extra, 'portrait_person')
        R(f'{pre}_couple_two_unsexed', [req(counted, 2, 2)] + extra, 'portrait_couple')
        R(f'{pre}_group_unsexed', [req(counted, 3, take_all=True)] + extra, 'portrait_group')
    # a head next to an animal and no person is the animal's head ("caput
    # agni", "Löwenköpfe"), not a portrait - after the portrait rules, so
    # "Kopf eines Mannes" next to a lion stays a portrait head
    for key, category in animal_elements():
        R(f'animal_head_{key}', [req('head', 1, 1), req(key, take_all=True)], category)
    # couples/families/groups are always portraits, even without a form word
    for grp, var, reqs in person_groups():
        R(f'portrait_unspecified_{grp}_{var}_no_form_word', reqs, f'portrait_{grp}')
    return rules


def compact(r):
    def one(q):
        return '{ ' + ', '.join(f'"{k}": {json.dumps(v)}' for k, v in q.items()) + ' }'
    lines = ['  {', f'    "id": "{r["id"]}",', '    "requires": [']
    lines += ['      ' + one(q) + (',' if i < len(r['requires']) - 1 else '') for i, q in enumerate(r['requires'])]
    lines += ['    ],', f'    "category": "{r["category"]}"', '  }']
    return '\n'.join(lines)


def main():
    raw = open(MOTIF_RULES, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    s = raw.replace('\r\n', '\n')
    old = json.loads(s)
    ids = [r['id'] for r in old]
    start = ids.index('funerary_banquet')
    end = max(i for i, x in enumerate(ids) if x.endswith('_no_form_word'))
    start_pos = s.index(f'  {{\n    "id": "{ids[start]}"')
    end_pos = s.index(f'  {{\n    "id": "{ids[end + 1]}"')
    new = build()
    assert len({r['id'] for r in new}) == len(new)
    s = s[:start_pos] + ',\n'.join(compact(r) for r in new) + ',\n' + s[end_pos:]
    assert json.loads(s)[start:start + len(new)] == new
    open(MOTIF_RULES, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
    print(len(old), '->', len(json.loads(s)), 'rules')


if __name__ == '__main__':
    main()
