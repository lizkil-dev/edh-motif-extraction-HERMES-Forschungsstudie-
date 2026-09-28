"""
motif_timeline.py - a first look at the evaluation: how often three motif
groups occur in dated EDH comments, per 50-year period, AD 150-600.

Motifs come from method 2 (results/nlp_lemma.json, best motif F1 on the test
set), so the chart is preliminary - automatically extracted, not
hand-checked. Share = weighted number of comments with the group / weighted
number of dated comments in the period. Each comment is spread evenly over
the years of its dating range (not_before..not_after, "aoristic"
weighting), so a comment dated 200-400 counts half in 200-299 and half in
300-399 instead of landing in one period by its midpoint. After 600 there
are fewer than 50 dated comments per period - too few for a share, so the
chart stops there.

Usage:
    python src/methods/nlp_lemma.py     # first, for results/nlp_lemma.json
    python src/motif_timeline.py
    -> results/figures/motif_timeline_de.png / _en.png (and .svg)
"""

import json
import os
import sys
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

from paths import CATEGORIES, EDH_RESULT_NLP_LEMMA, EDH_COMMENTS, FIGURES  # noqa: E402

START, END, STEP = 150, 600, 50
# (key, German label, English label, category path prefix, line colour); the
# three colours stay distinguishable from each other on a white background
GROUPS = [
    ('portraits', 'Porträts und Figuren', 'Portraits and figures', ['people_and_scenes', 'secular'], '#2a78d6'),
    ('christian', 'Christliche Symbole', 'Christian symbols', ['symbols', 'christian_symbols'], '#eb6834'),
    ('animals', 'Tiere', 'Animals', ['animals'], '#1baf7a'),
]
TEXT = {
    'de': {'title': 'Motivgruppen in EDH-Kommentaren zu Grabinschriften, 150–600 n. Chr.',
           'subtitle': 'Anteil der datierten Kommentare, in denen die Motivgruppe vorkommt. Automatisch erkannt '
                       '(Methode 2), vorläufig.',
           'y': 'Anteil der Kommentare', 'n': 'datierte Kommentare je Abschnitt',
           'source': 'Daten: Epigraphische Datenbank Heidelberg (CC BY-SA 4.0); Auswertung: L. Kilbinger'},
    'en': {'title': 'Motif groups in EDH comments on funerary inscriptions, AD 150–600',
           'subtitle': 'Share of dated comments mentioning the motif group. Automatically extracted '
                       '(method 2), preliminary.',
           'y': 'Share of comments', 'n': 'dated comments per period',
           'source': 'Data: Epigraphic Database Heidelberg (CC BY-SA 4.0); analysis: L. Kilbinger'},
}
INK, INK_2, MUTED, GRID, SURFACE = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0', '#fcfcfb'


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def category_paths():
    paths = {}

    def walk(tree, path):
        for key, node in tree.items():
            paths[key] = path + [key]
            walk(node.get('children', {}), path + [key])
    walk(load_json(CATEGORIES), [])
    return paths


def shares():
    paths = category_paths()
    results = load_json(EDH_RESULT_NLP_LEMMA)
    records = {r['id']: r for r in load_json(EDH_COMMENTS)}
    starts = list(range(START, END, STEP))
    total = defaultdict(float)
    found = {g[0]: defaultdict(float) for g in GROUPS}
    for edh_id, result in results.items():
        try:
            a, b = int(records[edh_id].get('not_before')), int(records[edh_id].get('not_after'))
        except (TypeError, ValueError):
            continue
        present = set()
        if result['has_depiction']:
            for motif in result['motifs']:
                path = paths.get(motif['category'], [])
                present |= {key for key, _, _, prefix, _ in GROUPS if path[:len(prefix)] == prefix}
        for s in starts:
            overlap = min(b, s + STEP - 1) - max(a, s) + 1
            if overlap > 0:
                w = overlap / (b - a + 1)
                total[s] += w
                for key in present:
                    found[key][s] += w
    return starts, total, {k: [100 * v[s] / total[s] for s in starts] for k, v in found.items()}


def draw(lang, starts, total, values):
    t = TEXT[lang]
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    x = [s + STEP / 2 for s in starts]
    for key, de, en, _, colour in GROUPS:
        label = de if lang == 'de' else en
        ax.plot(x, values[key], color=colour, linewidth=2, marker='o', markersize=5,
                markeredgecolor=SURFACE, markeredgewidth=1.5, label=label, solid_capstyle='round')
        # direct label at the line end, in ink (the line beside it carries the colour)
        ax.annotate(label, (x[-1], values[key][-1]), xytext=(8, 0), textcoords='offset points',
                    va='center', fontsize=9, color=INK)
    ax.set_xlim(START, END + 95)
    ax.set_ylim(0, max(max(v) for v in values.values()) * 1.12)
    ax.set_xticks(x)
    ax.set_xticklabels([f'{s}–{s + STEP - 1}\n' + (f'n={total[s]:,.0f}'.replace(',', '.') if lang == 'de'
                                                   else f'n={total[s]:,.0f}') for s in starts],
                       fontsize=7.5, color=INK_2)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.0f} %'))
    ax.tick_params(axis='y', labelsize=8, colors=INK_2)
    ax.tick_params(length=0)
    ax.grid(axis='y', color=GRID, linewidth=0.8)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color(GRID)
    ax.set_ylabel(t['y'], fontsize=8.5, color=INK_2)
    ax.legend(loc='upper left', frameon=False, fontsize=8.5, labelcolor=INK)
    fig.text(0.06, 0.945, t['title'], ha='left', va='top', fontsize=11.5, color=INK, fontweight='bold')
    fig.text(0.06, 0.885, t['subtitle'], ha='left', va='top', fontsize=8.5, color=INK_2)
    fig.text(0.06, 0.015, t['n'] + ' (n)  ·  ' + t['source'], fontsize=7, color=MUTED)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.17)
    FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(FIGURES / f'motif_timeline_{lang}.{ext}', facecolor=SURFACE)
    plt.close(fig)


def main():
    starts, total, values = shares()
    for lang in ('de', 'en'):
        draw(lang, starts, total, values)
    for s in starts:
        print(s, f'n={total[s]:.0f}', {k: round(v[starts.index(s)], 1) for k, v in values.items()})
    print(f'-> {FIGURES}')


if __name__ == '__main__':
    main()
