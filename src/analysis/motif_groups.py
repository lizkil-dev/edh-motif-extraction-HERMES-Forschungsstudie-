"""
Which motif groups have the highest occurence and how do the five most frequent groups
develop over time.

Two figures, each in German and English (PNG and SVG):
  - motif_groups_top10: the 10 most frequent motif groups, sorted by their
    share of the comments with a depiction;
  - motif_groups_timeline: the 5 most frequent of them per 50-year period,
    AD 150-600, as share of the dated comments with a depiction.

A motif group is a second-level category of categories.json ("christian
symbols", "birds", "wreaths" ...); a top-level category without subgroups
("weapons", "architecture") is a group of its own; "miscellaneous" is left
out. A comment counts once per group, however many of its motifs belong to it.

Motifs come from method 2 (results/full_corpus/m2_nlp_lemma.json, best motif F1 on the test
data), so the figures are preliminary. In the timeline each comment is spread evenly over the years of
its dating range (not_before..not_after, "aoristic" weighting), so a comment
dated 200-400 counts half in 200-299 and half in 300-399 instead of landing
in one period by its midpoint. After 600 there are too few dated comments per
period for a share, so the timeline stops there.

Usage:
    python src/methods/m2_nlp_lemma.py     # first, for results/full_corpus/m2_nlp_lemma.json
    python src/analysis/motif_groups.py
    -> figures/motif_groups_top10_de.png / _en.png, motif_groups_timeline_de.png / _en.png (and .svg)
"""

import json
import os
import sys
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import CATEGORIES, EDH_RESULT_NLP_LEMMA, EDH_COMMENTS, FIGURES  # noqa: E402

START, END, STEP = 150, 600, 50
TOP, TOP_TIMELINE = 10, 5
EXCLUDED = {'miscellaneous'}
# German names of the motif groups (categories.json has English labels only)
GERMAN = {
    'christian_symbols': 'Christliche Symbole', 'jewish_symbols': 'Jüdische Symbole',
    'pagan_symbols': 'Pagane Symbole', 'other_symbols': 'Sonstige Symbole',
    'birds': 'Vögel', 'fish': 'Fische', 'other_animals': 'Sonstige Tiere', 'animal_scene': 'Tierszenen',
    'branches_and_fronds': 'Zweige und Palmwedel', 'leaves': 'Blätter', 'trees': 'Bäume',
    'fruits': 'Früchte', 'flowers': 'Blumen', 'other_plants': 'Sonstige Pflanzen',
    'wreaths': 'Kränze und Girlanden', 'rosettes': 'Rosetten', 'vegetal_ornament': 'Pflanzenornament',
    'tablet_held_by_erotes': 'Von Eroten gehaltene Tafel', 'patterns': 'Muster',
    'vessels': 'Gefäße', 'tools': 'Werkzeuge', 'other': 'Sonstige Gegenstände', 'games': 'Spiele',
    'furniture': 'Möbel', 'fabrics': 'Textilien', 'jewelry': 'Schmuck',
    'food': 'Speisen', 'nautical': 'Schifffahrt', 'celestial_bodies': 'Himmelskörper',
    'architecture': 'Architektur', 'weapons': 'Waffen', 'framing': 'Rahmung',
    'biblical': 'Biblische Figuren und Szenen', 'secular': 'Weltliche Figuren und Porträts',
    'mythological': 'Mythologische Figuren und Szenen',
}
# English names where the category label is only an adjective
ENGLISH = {
    'biblical': 'Biblical figures and scenes', 'secular': 'Secular figures and portraits',
    'mythological': 'Mythological figures and scenes',
}
# one colour per motif group, the same in both figures (the five groups of
# the timeline; the other bars stay neutral). Wine, ochre, sky, indigo, moss:
# checked with the dataviz validator on the light surface, all pairs (lines
# cross): CVD and normal-vision separation pass; ochre is below 3:1 contrast,
# hence the value labels and the legend.
GROUP_COLOURS = {
    'secular': '#a23a5a', 'christian_symbols': '#d49a1c', 'birds': '#3d8fd1',
    'tools': '#3f55a8', 'mythological': '#4f8a3a',
}
OTHER = '#c9c6bd'
INK, INK_2, MUTED, GRID, SURFACE = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#fcfcfb'
TEXT = {
    'de': {'top_title': 'Die zehn häufigsten Motivgruppen',
           'top_subtitle': '{n} Kommentare mit Darstellung · Motive maschinell ermittelt (Methode 2), vorläufig',
           'time_title': 'Die fünf häufigsten Motivgruppen, 150–600 n. Chr.',
           'time_subtitle': 'Datierte Kommentare mit Darstellung · Motive maschinell ermittelt (Methode 2), vorläufig',
           'x_share': 'Anteil der Kommentare mit Darstellung', 'y_share': 'Anteil der Kommentare',
           'n': 'n = datierte Kommentare mit Darstellung je Abschnitt',
           'source': 'Daten: Epigraphische Datenbank Heidelberg (CC BY-SA 4.0); Auswertung: L. Kilbinger'},
    'en': {'top_title': 'The ten most frequent motif groups',
           'top_subtitle': '{n} comments with a depiction · motifs extracted by machine (method 2), preliminary',
           'time_title': 'The five most frequent motif groups, AD 150–600',
           'time_subtitle': 'Dated comments with a depiction · motifs extracted by machine (method 2), preliminary',
           'x_share': 'Share of comments with a depiction', 'y_share': 'Share of comments',
           'n': 'n = dated comments with a depiction per period',
           'source': 'Data: Epigraphic Database Heidelberg (CC BY-SA 4.0); analysis: L. Kilbinger'},
}


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def motif_groups():
    """category key -> (group key, English label of the group)."""
    groups = {}

    def walk(tree, group):
        for key, node in tree.items():
            groups[key] = group
            walk(node.get('children', {}), group)
    for top, node in load_json(CATEGORIES).items():
        if top in EXCLUDED:
            continue
        children = node.get('children', {})
        if children:
            groups[top] = None  # a motif filed directly under the top level belongs to no subgroup
            for sub, child in children.items():
                groups[sub] = (sub, child['label'])
                walk(child.get('children', {}), (sub, child['label']))
        else:
            groups[top] = (top, node['label'])
    return groups


def count():
    """Per comment with a depiction: the set of motif groups it mentions, and
    its dating (None if undated)."""
    groups = motif_groups()
    records = {r['id']: r for r in load_json(EDH_COMMENTS)}
    comments = []
    labels = {}
    for edh_id, result in load_json(EDH_RESULT_NLP_LEMMA).items():
        if not result['has_depiction']:
            continue
        present = set()
        for motif in result['motifs']:
            group = groups.get(motif['category'])
            if group:
                present.add(group[0])
                labels[group[0]] = group[1]
        try:
            dating = int(records[edh_id].get('not_before')), int(records[edh_id].get('not_after'))
        except (TypeError, ValueError):
            dating = None
        comments.append((present, dating))
    return comments, labels


def top_shares(comments):
    """[(group, share in %)], most frequent first, over all comments with a depiction."""
    counts = defaultdict(int)
    for present, _ in comments:
        for g in present:
            counts[g] += 1
    return [(g, 100 * c / len(comments)) for g, c in sorted(counts.items(), key=lambda x: (-x[1], x[0]))]


def timeline(comments, groups):
    """Per 50-year period: weighted number of dated comments with a depiction,
    and each group's share of them in %."""
    starts = list(range(START, END, STEP))
    total = defaultdict(float)
    found = {g: defaultdict(float) for g in groups}
    for present, dating in comments:
        if dating is None:
            continue
        a, b = dating
        for s in starts:
            overlap = min(b, s + STEP - 1) - max(a, s) + 1
            if overlap > 0:
                w = overlap / (b - a + 1)
                total[s] += w
                for g in present & set(groups):
                    found[g][s] += w
    return starts, total, {g: [100 * found[g][s] / total[s] for s in starts] for g in groups}


def label(group, labels, lang):
    if lang == 'de':
        return GERMAN.get(group, labels[group])
    return ENGLISH.get(group, labels[group].capitalize())


def number(value, lang, digits=0):
    """No thousands separator; decimal comma in German."""
    text = f'{value:.{digits}f}'
    return text.replace('.', ',') if lang == 'de' else text


def frame(fig, t, title, subtitle, footer):
    fig.patch.set_facecolor(SURFACE)
    fig.text(0.03, 0.96, title, ha='left', va='top', fontsize=13.5, color=INK, fontweight='bold')
    fig.text(0.03, 0.895, subtitle, ha='left', va='top', fontsize=8.5, color=INK_2, linespacing=1.5)
    fig.text(0.03, 0.02, footer, fontsize=7, color=MUTED)


def save(fig, name, lang):
    FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(FIGURES / f'{name}_{lang}.{ext}', facecolor=SURFACE)
    plt.close(fig)


def draw_top(lang, top, labels, n):
    t = TEXT[lang]
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
    ax.set_facecolor(SURFACE)
    names = [label(g, labels, lang) for g, _ in top][::-1]
    values = [v for _, v in top][::-1]
    colours = [GROUP_COLOURS.get(g, OTHER) for g, _ in top][::-1]
    bars = ax.barh(names, values, color=colours, height=0.62)
    for bar, value in zip(bars, values):
        ax.annotate(f'{number(value, lang, 1)} %', (bar.get_width(), bar.get_y() + bar.get_height() / 2),
                    xytext=(4, 0), textcoords='offset points', va='center', fontsize=8, color=INK_2)
    ax.set_xlim(0, max(values) * 1.15)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.0f} %'))
    ax.tick_params(axis='x', labelsize=8, colors=MUTED)
    ax.tick_params(axis='y', labelsize=9, colors=INK)
    ax.tick_params(length=0)
    ax.grid(axis='x', color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ('top', 'right', 'bottom'):
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color('#c3c2b7')
    ax.set_xlabel(t['x_share'], fontsize=8.5, color=INK_2)
    frame(fig, t, t['top_title'], t['top_subtitle'].format(n=number(n, lang)), t['source'])
    fig.subplots_adjust(left=0.3, right=0.96, top=0.8, bottom=0.14)
    save(fig, 'motif_groups_top10', lang)


def draw_timeline(lang, groups, labels, starts, total, values):
    t = TEXT[lang]
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
    ax.set_facecolor(SURFACE)
    x = [s + STEP / 2 for s in starts]
    # five series: a legend above the plot (lines ending together at 0 leave
    # no room for direct labels)
    for g in groups:
        colour = GROUP_COLOURS.get(g, OTHER)
        ax.plot(x, values[g], color=colour, linewidth=2, marker='o', markersize=5,
                markeredgecolor=SURFACE, markeredgewidth=1.5, label=label(g, labels, lang),
                solid_capstyle='round')
    ax.set_xlim(START, END)
    ax.set_ylim(0, 100)
    ax.set_xticks(x)
    ax.set_xticklabels([f'{s}–{s + STEP - 1}\nn={number(total[s], lang)}' for s in starts],
                       fontsize=7.5, color=INK_2)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.0f} %'))
    ax.tick_params(axis='y', labelsize=8, colors=MUTED)
    ax.tick_params(length=0)
    ax.grid(axis='y', color=GRID, linewidth=0.8)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#c3c2b7')
    ax.set_ylabel(t['y_share'], fontsize=8.5, color=INK_2)
    fig.legend(loc='upper left', bbox_to_anchor=(0.025, 0.81), frameon=False, fontsize=8,
               labelcolor=INK, ncol=3)
    frame(fig, t, t['time_title'], t['time_subtitle'], t['n'] + '  ·  ' + t['source'])
    fig.subplots_adjust(left=0.09, right=0.97, top=0.70, bottom=0.17)
    save(fig, 'motif_groups_timeline', lang)


def main():
    comments, labels = count()
    top = top_shares(comments)[:TOP]
    groups = [g for g, _ in top[:TOP_TIMELINE]]
    starts, total, values = timeline(comments, groups)
    for lang in ('de', 'en'):
        draw_top(lang, top, labels, len(comments))
        draw_timeline(lang, groups, labels, starts, total, values)
    print(f'{len(comments)} comments with a depiction')
    for g, share in top:
        print(f'  {labels[g]:<35} {share:5.1f} %')
    for s in starts:
        print(s, f'n={total[s]:.0f}', {g: round(values[g][starts.index(s)], 1) for g in groups})
    print(f'-> {FIGURES}')


if __name__ == '__main__':
    main()
