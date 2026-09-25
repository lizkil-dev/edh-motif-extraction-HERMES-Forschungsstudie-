"""
EDH method 4: BERT (deepset/gbert-base), fine-tuned for word-level element
labels.

  - Task: multi-label token classification - every word gets zero, one or
    more element labels ("Lorbeerkranz" -> laurel + wreath). Label space =
    the search vocabulary incl. form and marker words (bust, portrait,
    couple ...), as in bert_markings.py.
  - Training data: the goldstandard's reviewed word markings (all 500 rows)
    plus a silver standard: comments outside goldstandard and test set where
    methods 2 and 3 agree, marked with the same logic as the goldstandard
    (bert_markings.candidates, only the elements both methods found
    allowed), and a sample of comments both methods call "no depiction".
    One training run, no cross-validation; BERT is measured on the test set
    only (a goldstandard score would be training fit).
  - Words and sentences are Stanza tokens, as in the markings. A word's
    labels sit on its first subword.
  - From labels to the result: per sentence as in method 2 - the same
    element on neighbouring words is one mention, counts via
    nlp_lemma.word_count(), then the shared resolve_motifs() and
    fold_forms(); has_depiction = any element or a signal word.

The silver standard comes from the rule-based methods, so BERT partly learns
their behaviour; what it learns beyond them comes from the goldstandard.

Usage:
    python src/methods/bert.py silver    # needs results/nlp_lemma.json, results/dependency.json
    python src/methods/bert.py train     # CPU: about half an hour
    python src/methods/bert.py predict   # test set -> results/bert.json
"""

import json
import os
import random
import sys
import time

import stanza
import torch
from transformers import BertModel, BertTokenizerFast, get_linear_schedule_with_warmup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from paths import (  # noqa: E402
    ELEMENTS,
    ELEMENT_SYNONYMS,
    MOTIF_RULES,
    EDH_SIGNAL_WORDS,
    EDH_FILTER_FALSE_FRIENDS,
    EDH_COMPOUND_EXCEPTIONS,
    EDH_COMMENTS,
    EDH_GOLDSTANDARD,
    EDH_TESTSET,
    EDH_GOLDSTANDARD_MARKINGS,
    EDH_RESULT_NLP_LEMMA,
    EDH_RESULT_DEPENDENCY,
    EDH_RESULT_BERT,
    EDH_BERT_SILVER,
    EDH_BERT_MODEL,
)
from schema import resolve_motifs, fold_forms  # noqa: E402
from matching import (build_element_forms, phrase_forms, build_compounds, has_signal_word,  # noqa: E402
                      rule_count)
from bert_markings import candidates, allowed_labels  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from nlp_lemma import word_count  # noqa: E402

MODEL_NAME = 'deepset/gbert-base'
SEED = 42
N_NEGATIVE = 500        # silver comments both methods call "no depiction"
MAX_SUBWORDS = 256      # sentences are packed into windows up to this length
EPOCHS = 2
BATCH_SIZE = 16
LEARNING_RATE = 3e-5
THRESHOLD = 0.5
# marked words are rare (nearly every output is "no element"); positives weigh
# more so the model doesn't learn to mark nothing
POS_WEIGHT = 5.0


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def stanza_pipeline(processors):
    return stanza.Pipeline('de', processors=processors, verbose=False, download_method=None)


# -----------------------------------------------------------------------------
# silver standard
# -----------------------------------------------------------------------------

def silver():
    """Word markings for comments outside goldstandard and test set on which
    methods 2 and 3 agree (see module docstring)."""
    m2, m3 = load_json(EDH_RESULT_NLP_LEMMA), load_json(EDH_RESULT_DEPENDENCY)
    excluded = set(load_json(EDH_GOLDSTANDARD)) | set(load_json(EDH_TESTSET))
    positives, negatives = {}, []
    for edh_id in sorted(set(m2) & set(m3) - excluded):
        a, b = m2[edh_id], m3[edh_id]
        if a['has_depiction'] and b['has_depiction']:
            both = {e['element'] for e in a['elements']} & {e['element'] for e in b['elements']}
            if both:
                positives[edh_id] = {
                    'elements': [e for e in a['elements'] if e['element'] in both],
                    'motifs': a['motifs'] + b['motifs'],
                }
        elif not a['has_depiction'] and not b['has_depiction']:
            negatives.append(edh_id)
    random.Random(SEED).shuffle(negatives)
    negatives = negatives[:N_NEGATIVE]

    elements_meta = load_json(ELEMENTS)
    forms = build_element_forms(load_json(ELEMENT_SYNONYMS), [])
    phrases = phrase_forms(forms, split_contractions=True)
    compounds = build_compounds(forms, load_json(EDH_COMPOUND_EXCEPTIONS))
    false_friend_words = {e['word'].lower() for e in load_json(EDH_FILTER_FALSE_FRIENDS)}
    comments = {r['id']: r['commentary'] for r in load_json(EDH_COMMENTS) if r.get('commentary')}
    nlp = stanza_pipeline('tokenize,mwt,pos,lemma')

    out = {}
    ids = list(positives) + negatives
    print(f'silver: {len(positives)} agreeing comments with elements, {len(negatives)} without', flush=True)
    for i, edh_id in enumerate(ids, 1):
        doc = nlp(comments[edh_id])
        allowed = allowed_labels(positives[edh_id], elements_meta) if edh_id in positives else set()
        sentences = []
        for sentence in doc.sentences:
            cands = candidates(sentence, forms, phrases, compounds, false_friend_words)
            sentences.append({'tokens': [t.text for t in sentence.tokens],
                              'labels': [sorted(k for k in keys if k in allowed) for keys in cands]})
        out[edh_id] = {'sentences': sentences}
        if i % 250 == 0:
            print(f'  {i}/{len(ids)}', flush=True)
    EDH_BERT_SILVER.parent.mkdir(parents=True, exist_ok=True)
    with open(EDH_BERT_SILVER, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)
    print(f'-> {EDH_BERT_SILVER}')


# -----------------------------------------------------------------------------
# model
# -----------------------------------------------------------------------------

class TokenTagger(torch.nn.Module):
    """BERT encoder + one sigmoid output per label (multi-label)."""

    def __init__(self, n_labels):
        super().__init__()
        self.bert = BertModel.from_pretrained(MODEL_NAME, add_pooling_layer=False)
        self.dropout = torch.nn.Dropout(0.1)
        self.head = torch.nn.Linear(self.bert.config.hidden_size, n_labels)

    def forward(self, input_ids, attention_mask):
        hidden = self.bert(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        return self.head(self.dropout(hidden))


def windows(sentences, tokenizer):
    """Sentences packed into windows of at most MAX_SUBWORDS subwords, as
    lists of sentence indices (a longer single sentence is its own window and
    gets truncated)."""
    out, current, length = [], [], 0
    for i, s in enumerate(sentences):
        n = sum(len(tokenizer.tokenize(t)) or 1 for t in s['tokens'])
        if current and length + n > MAX_SUBWORDS - 2:
            out.append(current)
            current, length = [], 0
        current.append(i)
        length += n
    if current:
        out.append(current)
    return out


def encode(words, tokenizer):
    enc = tokenizer(words, is_split_into_words=True, truncation=True, max_length=MAX_SUBWORDS)
    first = {}
    for pos, w in enumerate(enc.word_ids()):
        if w is not None and w not in first:
            first[w] = pos
    return enc['input_ids'], first


def examples(markings, tokenizer, label_index):
    """(input_ids, [(subword position, label ids)]) per window."""
    out = []
    for row in markings.values():
        if row is None:
            continue
        for win in windows(row['sentences'], tokenizer):
            words, labels = [], []
            for i in win:
                words += row['sentences'][i]['tokens']
                labels += row['sentences'][i]['labels']
            ids, first = encode(words, tokenizer)
            out.append((ids, [(first[w], [label_index[k] for k in labels[w]]) for w in first]))
    return out


def batches(data, n_labels, shuffle, rng):
    order = list(range(len(data)))
    if shuffle:
        rng.shuffle(order)
    for start in range(0, len(order), BATCH_SIZE):
        chunk = [data[i] for i in order[start:start + BATCH_SIZE]]
        width = max(len(ids) for ids, _ in chunk)
        input_ids = torch.zeros(len(chunk), width, dtype=torch.long)
        attention = torch.zeros(len(chunk), width, dtype=torch.long)
        targets = torch.zeros(len(chunk), width, n_labels)
        mask = torch.zeros(len(chunk), width)
        for b, (ids, marks) in enumerate(chunk):
            input_ids[b, :len(ids)] = torch.tensor(ids)
            attention[b, :len(ids)] = 1
            for pos, labels in marks:
                mask[b, pos] = 1
                targets[b, pos, labels] = 1
        yield input_ids, attention, targets, mask


def train():
    torch.manual_seed(SEED)
    torch.set_num_threads(os.cpu_count())
    gold = load_json(EDH_GOLDSTANDARD_MARKINGS)
    assert all(v is not None for v in gold.values()), 'unreviewed goldstandard markings'
    silver_markings = load_json(EDH_BERT_SILVER)
    markings = {**silver_markings, **gold}
    labels = sorted({k for row in markings.values() for s in row['sentences'] for ls in s['labels'] for k in ls})
    label_index = {k: i for i, k in enumerate(labels)}
    tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)
    data = examples(markings, tokenizer, label_index)
    print(f'{len(gold)} goldstandard + {len(silver_markings)} silver comments -> {len(data)} windows, '
          f'{len(labels)} labels', flush=True)

    model = TokenTagger(len(labels))
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    steps = EPOCHS * -(-len(data) // BATCH_SIZE)
    scheduler = get_linear_schedule_with_warmup(optimizer, int(0.1 * steps), steps)
    loss_fn = torch.nn.BCEWithLogitsLoss(reduction='none', pos_weight=torch.full((len(labels),), POS_WEIGHT))
    rng = random.Random(SEED)
    model.train()
    step, started = 0, time.time()
    for epoch in range(EPOCHS):
        for input_ids, attention, targets, mask in batches(data, len(labels), True, rng):
            logits = model(input_ids, attention)
            loss = (loss_fn(logits, targets).mean(-1) * mask).sum() / mask.sum()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            step += 1
            if step % 25 == 0:
                print(f'  epoch {epoch + 1} step {step}/{steps} loss {loss.item():.4f} '
                      f'({(time.time() - started) / 60:.1f} min)', flush=True)
    EDH_BERT_MODEL.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), EDH_BERT_MODEL / 'model.pt')
    with open(EDH_BERT_MODEL / 'labels.json', 'w', encoding='utf-8') as f:
        json.dump(labels, f)
    print(f'-> {EDH_BERT_MODEL}')


# -----------------------------------------------------------------------------
# prediction
# -----------------------------------------------------------------------------

def predict():
    torch.set_num_threads(os.cpu_count())
    labels = load_json(EDH_BERT_MODEL / 'labels.json')
    tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)
    model = TokenTagger(len(labels))
    model.load_state_dict(torch.load(EDH_BERT_MODEL / 'model.pt'))
    model.eval()
    elements_meta, motif_rules = load_json(ELEMENTS), load_json(MOTIF_RULES)
    signal_words = load_json(EDH_SIGNAL_WORDS)
    comments = {r['id']: r['commentary'] for r in load_json(EDH_COMMENTS) if r.get('commentary')}
    nlp = stanza_pipeline('tokenize,mwt,pos')

    results = {}
    ids = list(load_json(EDH_TESTSET))
    for edh_id in ids:
        doc = nlp(comments[edh_id])
        sents = [{'tokens': [t.text for t in s.tokens]} for s in doc.sentences]
        token_labels = [[[] for _ in s['tokens']] for s in sents]
        for win in windows(sents, tokenizer):
            words, where = [], []
            for i in win:
                words += sents[i]['tokens']
                where += [(i, j) for j in range(len(sents[i]['tokens']))]
            ids_, first = encode(words, tokenizer)
            with torch.no_grad():
                probs = torch.sigmoid(model(torch.tensor([ids_]), torch.ones(1, len(ids_), dtype=torch.long)))[0]
            for w, pos in first.items():
                s, j = where[w]
                token_labels[s][j] = [labels[k] for k in (probs[pos] >= THRESHOLD).nonzero().flatten().tolist()]

        all_elements, motifs = [], []
        for sentence, labs in zip(doc.sentences, token_labels):
            found, previous = [], set()
            for token, keys in zip(sentence.tokens, labs):
                index = token.words[0].id - 1
                for key in keys:
                    if key not in previous:
                        found.append({'element': key, 'matched_text': token.text,
                                      'count': word_count(sentence, index)})
                previous = set(keys)
            all_elements.extend(found)
            motifs.extend(resolve_motifs([e['element'] for e in found for _ in range(rule_count(e['count']))],
                                         motif_rules, elements_meta))
        result_elements, motifs = fold_forms([
            {'element': e['element'], 'count': e['count'], 'uncertain': False,
             'variant_condition': None, 'matched_text': e['matched_text']}
            for e in all_elements], motifs, elements_meta)
        results[edh_id] = {
            'has_depiction': bool(all_elements) or has_signal_word(doc.text, signal_words),
            'elements': result_elements,
            'motifs': motifs,
        }
    with open(EDH_RESULT_BERT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'{len(results)} test comments, {sum(r["has_depiction"] for r in results.values())} with depiction '
          f'-> {EDH_RESULT_BERT}')


if __name__ == '__main__':
    commands = {'silver': silver, 'train': train, 'predict': predict}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]]()
