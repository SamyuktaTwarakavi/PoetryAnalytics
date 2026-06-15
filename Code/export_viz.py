"""
Export data for the D3 "Poet Atlas" page (atlas.html).

Scores every poem on the five measures (lexicon for concreteness/valence if the
files are in data/lexicons/, otherwise word lists), groups poems under their
author, and writes two files into outputs/:
    atlas_data.js   atlas.html loads this automatically when it sits beside it
    atlas.json      same data

Each author carries their aggregate scores AND the list of their poems (each
poem's five values plus its text), so the page can list a poet's poems and show
any one of them.

Run:  python export_viz.py
"""

import json
import os

import config
from corpus import poems
from poetryAnalytics import build_measures

MIN_POEMS = 5          # drop authors with fewer poems (too noisy to profile)
MAX_TEXT = 1500        # truncate a poem's displayed text to this many characters


def main():
    order, scorers, scoring = build_measures()
    print("scoring", len(order), "measures:", ", ".join(order))

    by_poet = {}
    for p in poems:
        if not p.get("year"):
            continue
        rec = {"year": p["year"], "era": p["era"]}
        ok = True
        for m in order:
            v = scorers[m](p["text"])
            if v is None:
                ok = False
                break
            rec[m] = round(v, 4)
        if not ok:
            continue
        text = p.get("raw") or p["text"]
        rec["text"] = text[:MAX_TEXT] + ("…" if len(text) > MAX_TEXT else "")
        by_poet.setdefault(p["poet"], []).append(rec)

    authors = []
    for poet, plist in by_poet.items():
        if len(plist) < MIN_POEMS:
            continue
        plist.sort(key=lambda r: r["year"])
        a = {"poet": poet, "n": len(plist),
             "year": round(sum(r["year"] for r in plist) / len(plist))}
        for m in order:
            a[m] = round(sum(r[m] for r in plist) / len(plist), 4)
        a["poems"] = plist
        authors.append(a)
    authors.sort(key=lambda a: a["year"])

    def short(label):
        if "Brysbaert" in label:
            return "Brysbaert lexicon"
        if "NRC-VAD" in label:
            return "NRC-VAD lexicon"
        return "word list" if "word list" in label else label

    data = {
        "measures": order,
        "authors": authors,
        "scoring": {"concreteness": short(scoring["concreteness"]),
                    "valence": short(scoring["valence"])},
    }

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    js_path = os.path.join(config.OUTPUT_DIR, "atlas_data.js")
    json_path = os.path.join(config.OUTPUT_DIR, "atlas.json")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.ATLAS = " + json.dumps(data) + ";")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    total = sum(a["n"] for a in authors)
    print(f"wrote {len(authors)} authors and {total} poems")
    print(f"  -> {js_path}")
    print(f"  -> {json_path}")
    print("Put atlas.html next to atlas_data.js and open it.")


if __name__ == "__main__":
    main()
