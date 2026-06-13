"""
Export data for the D3 "Poet Atlas" page (atlas.html).

Scores every poem on the five measures (lexicon for concreteness/valence if the
files are in data/lexicons/, otherwise word lists), aggregates to author level,
and writes two files into outputs/:
    atlas_data.js   atlas.html loads this automatically when it sits beside it
    atlas.json      same data, for the page's "load file" button

Run:  python export_viz.py
"""

import json
import os
import random

import config
from corpus import poems
from test_textbook import measure_poem
from lexicons import load_concreteness, load_valence, poem_mean

MEASURES = ["nature", "sacred", "industrial", "concreteness", "valence"]
MIN_POEMS = 5          # drop authors with fewer poems (too noisy to profile)
SAMPLE_POEMS = 1500    # cap the optional poem layer so the page stays snappy


def main():
    conc, val = load_concreteness(), load_valence()

    def score(text, name):
        if name == "concreteness" and conc:
            return poem_mean(text, conc)
        if name == "valence" and val:
            return poem_mean(text, val)
        return measure_poem(text, name)

    scored = []
    for p in poems:
        if not p.get("year"):
            continue
        row = {"poet": p["poet"], "year": p["year"], "era": p["era"]}
        ok = True
        for m in MEASURES:
            v = score(p["text"], m)
            if v is None:
                ok = False
                break
            row[m] = round(v, 4)
        if ok:
            scored.append(row)

    by_poet = {}
    for r in scored:
        by_poet.setdefault(r["poet"], []).append(r)

    authors = []
    for poet, rows in by_poet.items():
        if len(rows) < MIN_POEMS:
            continue
        a = {"poet": poet, "n": len(rows),
             "year": round(sum(r["year"] for r in rows) / len(rows))}
        for m in MEASURES:
            a[m] = round(sum(r[m] for r in rows) / len(rows), 4)
        authors.append(a)
    authors.sort(key=lambda a: a["year"])

    random.seed(0)
    poems_layer = random.sample(scored, min(SAMPLE_POEMS, len(scored)))

    data = {
        "measures": MEASURES,
        "authors": authors,
        "poems": poems_layer,
        "scoring": {
            "concreteness": "Brysbaert lexicon" if conc else "word list",
            "valence": "NRC-VAD lexicon" if val else "word list",
        },
    }

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    js_path = os.path.join(config.OUTPUT_DIR, "atlas_data.js")
    json_path = os.path.join(config.OUTPUT_DIR, "atlas.json")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.ATLAS = " + json.dumps(data) + ";")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    print(f"wrote {len(authors)} authors and {len(poems_layer)} sampled poems")
    print(f"  -> {js_path}")
    print(f"  -> {json_path}")
    print("Put atlas.html next to atlas_data.js and open it, or use the page's "
          "load button on atlas.json.")


if __name__ == "__main__":
    main()
