"""
Validate the rulers -- do our word-list measures agree with the experts?

We check two of our measures against published psycholinguistic lexicons:
    concreteness  vs  Brysbaert concreteness norms (~40k words)
    valence       vs  NRC-VAD valence lexicon (~20k words)

For each poem we compute our score and the lexicon's average score over the
poem's words, then correlate the two. A high correlation means our homemade
ruler agrees with the experts and can be trusted.

Get the lexicons (both free for research) and put them in data/lexicons/ :

  Brysbaert concreteness  ->  data/lexicons/concreteness.txt
    Direct file (right-click "Save link as"):
      https://raw.githubusercontent.com/ArtsEngine/concreteness/master/Concreteness_ratings_Brysbaert_et_al_BRM.txt
    Repo page (has a .xlsx too): https://github.com/ArtsEngine/concreteness
    Tab-separated; the value the loader uses is the "Conc.M" column.

  NRC-VAD valence  ->  data/lexicons/nrc_vad.txt
    Download the zip:  http://saifmohammad.com/WebDocs/Lexicons/NRC-VAD-Lexicon.zip
    Unzip it, find  NRC-VAD-Lexicon.txt  inside, and save/rename it as
      data/lexicons/nrc_vad.txt
    Project page: https://saifmohammad.com/WebPages/nrc-vad.html
    Tab-separated (Word, Valence, Arousal, Dominance); free for non-commercial
    research use. The loader uses the "Valence" column.

Run:  python validate.py
If a file is missing it skips that check and tells you where to put it.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
import poems_data as words
from corpus import poems, era_order
from lexicons import load_concreteness, load_valence, poem_mean


def polarity(text, high, low):
    w = text.split()
    h = sum(1 for x in w if x in high)
    l = sum(1 for x in w if x in low)
    return (h - l) / (h + l) if (h + l) else 0.0


# ---- correlation + plotting ----
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
          f"era-level r={r_era:.2f} ({label(r_era)})  "
          f"[{len(rows)} poems]")
    return {"measure": name, "lexicon": lex_label,
            "r_poem": r_poem, "r_era": r_era, "n": len(rows)}


def main():
    results = []

    conc = load_concreteness()
    if conc is not None:
        print(f"concreteness vs Brysbaert ({len(conc)} words):")
        r = check("concreteness", words.CONCRETE, words.ABSTRACT, conc,
                  "Brysbaert concreteness", "validate_concreteness.png")
        if r:
            results.append(r)
    else:
        print("skip concreteness -- put the Brysbaert file at data/lexicons/concreteness.txt")

    val = load_valence()
    if val is not None:
        print(f"valence vs NRC-VAD ({len(val)} words):")
        r = check("valence", words.POSITIVE, words.NEGATIVE, val,
                  "NRC-VAD valence", "validate_valence.png")
        if r:
            results.append(r)
    else:
        print("skip valence -- put the NRC-VAD file at data/lexicons/nrc_vad.txt")

    if not results:
        print("\nNo lexicons found. See the instructions at the top of validate.py.")
        return

    path = os.path.join(config.OUTPUT_DIR, "results_validation.md")
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Ruler validation\n\n")
        f.write("Correlation of our word-list measures with published lexicons. "
                "Higher means our ruler agrees with the experts. The era-level "
                "number is the one that matters for the study's claims, since the "
                "claims are about era averages.\n\n")
        f.write("| our measure | lexicon | poem-level r | era-level r | poems |\n")
        f.write("|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['measure']} | {r['lexicon']} | {r['r_poem']:.2f} "
                    f"| {r['r_era']:.2f} | {r['n']} |\n")
    print("saved", os.path.join("outputs", "results_validation.md"))


if __name__ == "__main__":
    main()
