"""
Validate the rulers -- how far can each measure be trusted?

There are three kinds of check here, because the measures are not all the same:

1. WORD-LIST RULERS vs their LEXICONS  (concreteness, valence)
   These two measures have BOTH a homemade word list AND a published lexicon,
   so we can correlate the two independent rulers. A high correlation means our
   cheap word list agrees with the experts.

2. LEXICON COVERAGE  (every lexicon)
   The share of the corpus's words that a lexicon actually scores. A measure
   built on a lexicon that covers only a sliver of the words is noisier than one
   that covers most of them. This is a basic health check for every lexicon,
   including Lancaster and EmoLex.

3. CONVERGENT VALIDITY  (arousal, dominance, visual, auditory, joy, sadness, fear)
   These measures have ONLY a lexicon -- there is no second independent ruler to
   compare against. So instead we check that they line up with measures we
   already trust, in the direction theory predicts: sad-word poems should score
   LOW on valence, fear should track HIGH arousal, visual imagery should track
   concreteness, joy and sadness should pull opposite ways. If the signs come
   out as expected, that is evidence the measure is capturing something real.
   (If you download a second VAD lexicon -- Glasgow Norms or Warriner et al. --
   you could add a true ruler-vs-ruler check for arousal/dominance too.)

Lexicons (all free for research) go in data/lexicons/ :
  Brysbaert concreteness  -> data/lexicons/concreteness.txt
    https://github.com/ArtsEngine/concreteness  (uses the "Conc.M" column)
  NRC-VAD (valence+arousal+dominance) -> data/lexicons/nrc_vad.txt
    https://saifmohammad.com/WebPages/nrc-vad.html
  Lancaster Sensorimotor (visual/auditory) -> data/lexicons/sensorimotor.csv
    https://www.lancaster.ac.uk/psychology/lsnorms/
  NRC EmoLex (joy/sadness/fear) -> data/lexicons/nrc_emolex.txt
    https://saifmohammad.com/WebPages/AccessResource.htm

Run:  python validate.py
Any lexicon that's missing is simply skipped, with a note.
"""

import os
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
import poems_data as words
from corpus import poems, era_order
from lexicons import (load_concreteness, load_valence, load_arousal, load_dominance,
                      load_sensory, load_emotion, poem_mean)
from poetryAnalytics import build_measures


def polarity(text, high, low):
    w = text.split()
    h = sum(1 for x in w if x in high)
    l = sum(1 for x in w if x in low)
    return (h - l) / (h + l) if (h + l) else 0.0


def pearson(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def label(r):
    r = abs(r)
    return "strong" if r >= 0.5 else "moderate" if r >= 0.3 else "weak"


def scatter(ours, theirs, xlabel, ylabel, title, name):
    fig = plt.figure(figsize=(6.5, 6))
    plt.scatter(ours, theirs, s=10, alpha=0.3, color="tab:purple")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(config.OUTPUT_DIR, name), dpi=140)
    plt.close(fig)
    print("saved", os.path.join("outputs", name))


# ---- 1. word-list ruler vs its lexicon ----
def check(name, our_high, our_low, lex, lex_label, plot_name):
    rows = []
    for p in poems:
        lm = poem_mean(p["text"], lex)
        if lm is None:
            continue
        rows.append((p["era"], polarity(p["text"], our_high, our_low), lm))
    if len(rows) < 10:
        print(f"  too few poems contain {lex_label} words")
        return None

    ours = [o for _, o, _ in rows]
    theirs = [t for _, _, t in rows]
    r_poem = pearson(ours, theirs)

    e_ours, e_theirs = [], []
    for e in era_order:
        sub = [(o, t) for (er, o, t) in rows if er == e]
        if sub:
            e_ours.append(np.mean([o for o, _ in sub]))
            e_theirs.append(np.mean([t for _, t in sub]))
    r_era = pearson(e_ours, e_theirs)

    scatter(ours, theirs, f"our {name} score", lex_label,
            f"{name}: ours vs {lex_label}  (poem r={r_poem:.2f})", plot_name)
    print(f"  {name}: poem-level r={r_poem:.2f} ({label(r_poem)}), "
          f"era-level r={r_era:.2f} ({label(r_era)})  [{len(rows)} poems]")
    return {"measure": name, "lexicon": lex_label,
            "r_poem": r_poem, "r_era": r_era, "n": len(rows)}


# ---- 2. coverage ----
def corpus_counter():
    C = Counter()
    for p in poems:
        C.update(p["text"].split())
    return C, sum(C.values())


def coverage(lex, C, total):
    if not total or not lex:
        return 0.0
    return 100.0 * sum(c for t, c in C.items() if t in lex) / total


# ---- 3. convergent validity ----
# (measure_a, measure_b, expected sign, why we expect it)
EXPECT = [
    ("sadness", "valence", "-", "sad-word poems should score lower valence"),
    ("joy", "valence", "+", "joy-word poems should score higher valence"),
    ("fear", "valence", "-", "fear-word poems should score lower valence"),
    ("fear", "arousal", "+", "fear-word poems should score higher arousal"),
    ("visual", "concreteness", "+", "visual imagery should track concreteness"),
    ("joy", "sadness", "-", "joy and sadness should pull opposite ways"),
]


def main():
    C, total = corpus_counter()
    print(f"corpus: {len(poems)} poems, {total} tokens, {len(C)} word types\n")

    rulers = []        # section 1
    coverage_rows = [] # section 2
    conv_rows = []     # section 3

    # ---- 1. word-list rulers vs lexicons ----
    print("1. word-list rulers vs published lexicons")
    conc = load_concreteness()
    if conc is not None:
        r = check("concreteness", words.CONCRETE, words.ABSTRACT, conc,
                  "Brysbaert concreteness", "validate_concreteness.png")
        if r:
            rulers.append(r)
        coverage_rows.append(("concreteness (Brysbaert)", coverage(conc, C, total), len(conc)))
    else:
        print("  skip concreteness -- put Brysbaert at data/lexicons/concreteness.txt")

    val = load_valence()
    if val is not None:
        r = check("valence", words.POSITIVE, words.NEGATIVE, val,
                  "NRC-VAD valence", "validate_valence.png")
        if r:
            rulers.append(r)
        coverage_rows.append(("valence (NRC-VAD)", coverage(val, C, total), len(val)))
    else:
        print("  skip valence -- put NRC-VAD at data/lexicons/nrc_vad.txt")

    # ---- 2. coverage of the extra lexicons ----
    print("\n2. lexicon coverage (share of corpus words each lexicon scores)")
    arou, domi = load_arousal(), load_dominance()
    vis, aud = load_sensory("visual"), load_sensory("auditory")
    joy, sad, fear = load_emotion("joy"), load_emotion("sadness"), load_emotion("fear")
    for lbl, lx in [("arousal (NRC-VAD)", arou), ("dominance (NRC-VAD)", domi),
                    ("visual (Lancaster)", vis), ("auditory (Lancaster)", aud)]:
        if lx:
            coverage_rows.append((lbl, coverage(lx, C, total), len(lx)))
    emo = set().union(*[s for s in (joy, sad, fear) if s]) if any((joy, sad, fear)) else None
    if emo:
        coverage_rows.append(("emotion words (EmoLex joy/sad/fear)", coverage(emo, C, total), len(emo)))
    for lbl, cov, n in coverage_rows:
        print(f"  {lbl}: {cov:.1f}% of corpus words  ({n} words in lexicon)")

    # ---- 3. convergent validity for the lexicon-only measures ----
    print("\n3. convergent validity (do the lexicon-only measures point the right way?)")
    order, scorers, scoring = build_measures()
    avail = set(order)
    needed = sorted({m for a, b, _, _ in EXPECT for m in (a, b)} & avail)
    pairs_to_test = [(a, b, s, why) for (a, b, s, why) in EXPECT if a in avail and b in avail]

    if not pairs_to_test:
        print("  no extra lexicons installed -- nothing to cross-check yet")
    else:
        scored = [{m: scorers[m](p["text"]) for m in needed} for p in poems]
        for a, b, sign, why in pairs_to_test:
            xy = [(row[a], row[b]) for row in scored if row[a] is not None and row[b] is not None]
            if len(xy) < 10:
                continue
            r = pearson([x for x, _ in xy], [y for _, y in xy])
            ok = (r < 0) if sign == "-" else (r > 0)
            verdict = "as expected" if ok else "UNEXPECTED"
            conv_rows.append({"a": a, "b": b, "sign": sign, "r": r,
                              "verdict": verdict, "why": why, "n": len(xy)})
            print(f"  {a} vs {b}: r={r:+.2f} (expected {sign}, {label(r)}) -> {verdict}")

    if not rulers and not coverage_rows and not conv_rows:
        print("\nNo lexicons found. See the instructions at the top of validate.py.")
        return

    # ---- write the report ----
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUT_DIR, "results_validation.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Ruler validation\n\n")

        f.write("## 1. Word-list rulers vs published lexicons\n\n")
        f.write("Concreteness and valence are the only measures with both a homemade "
                "word list and a lexicon, so we can correlate the two. Higher means "
                "our word list agrees with the experts; the era-level number is the "
                "one that matters, since the claims are about era averages.\n\n")
        if rulers:
            f.write("| our measure | lexicon | poem-level r | era-level r | poems |\n")
            f.write("|---|---|---|---|---|\n")
            for r in rulers:
                f.write(f"| {r['measure']} | {r['lexicon']} | {r['r_poem']:.2f} "
                        f"| {r['r_era']:.2f} | {r['n']} |\n")
        else:
            f.write("_No word-list lexicons installed._\n")

        f.write("\n## 2. Lexicon coverage\n\n")
        f.write("Share of the corpus's words each lexicon actually scores. A measure "
                "built on a low-coverage lexicon is noisier and should be read with "
                "more caution.\n\n")
        if coverage_rows:
            f.write("| lexicon (measure) | corpus words covered | lexicon size |\n")
            f.write("|---|---|---|\n")
            for lbl, cov, n in coverage_rows:
                f.write(f"| {lbl} | {cov:.1f}% | {n} |\n")
        else:
            f.write("_No lexicons installed._\n")

        f.write("\n## 3. Convergent validity (lexicon-only measures)\n\n")
        f.write("Arousal, dominance, visual, auditory and the emotions have no second "
                "independent ruler, so instead we check they relate to trusted "
                "measures in the expected direction. A matching sign is evidence the "
                "measure is capturing something real; an UNEXPECTED sign is a red "
                "flag worth investigating.\n\n")
        if conv_rows:
            f.write("| measure | vs | expected | r | result | poems |\n")
            f.write("|---|---|---|---|---|---|\n")
            for c in conv_rows:
                f.write(f"| {c['a']} | {c['b']} | {c['sign']} | {c['r']:+.2f} "
                        f"| {c['verdict']} | {c['n']} |\n")
            f.write("\nExpected directions: " +
                    "; ".join(f"{c['a']} vs {c['b']} ({c['why']})" for c in conv_rows) + ".\n")
        else:
            f.write("_The extra lexicons (Lancaster, EmoLex) are not installed, so there "
                    "is nothing to cross-check yet. Add them to data/lexicons/ and re-run._\n")

    print("\nsaved", os.path.join("outputs", "results_validation.md"))


if __name__ == "__main__":
    main()
