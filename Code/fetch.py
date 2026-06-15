"""
Build the corpus from the PoeTree English bulk dump (fast, no API calls).

Steps:
  1. Download en.zip (~388 MB) from https://zenodo.org/records/10907309
  2. Unzip it so the poem JSON files sit in  data/poetree_en/
  3. python fetch.py   ->  writes data/poems.csv

In the dump each poem is one JSON file with an embedded "author" block
(name, born, died) and a "body" (list of line objects). We date each poem by
year_created when present, otherwise by the author's active year (birth + 35),
and we skip poems the dataset flags as duplicates.
"""

import csv
import json
import os

import config

DUMP_DIR = os.path.join(config.DATA_DIR, "poetree_en")
OUT = os.path.join(config.DATA_DIR, "poetree.csv")   # a source file; combine.py merges it
FLOURISH_OFFSET = 35
MAX_POEMS_PER_POET = 300
MIN_WORDS = 20


def line_text(body):
    """Join a poem's body (a list of line objects) into one plain string."""
    if not isinstance(body, list):
        return ""
    parts = [ln["text"] for ln in body
             if isinstance(ln, dict) and isinstance(ln.get("text"), str)]
    return "\n".join(parts).strip()


def iter_poems(dump_dir):
    """Yield every poem record found under the dump directory."""
    for root, _, files in os.walk(dump_dir):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            try:
                with open(os.path.join(root, fn), encoding="utf-8") as f:
                    obj = json.load(f)
            except Exception:
                continue
            for rec in (obj if isinstance(obj, list) else [obj]):
                if isinstance(rec, dict) and "body" in rec and isinstance(rec.get("author"), dict):
                    yield rec


def main():
    if not os.path.isdir(DUMP_DIR):
        print("PoeTree dump not found. To set it up:")
        print("  1) download en.zip from https://zenodo.org/records/10907309")
        print(f"  2) unzip it so the json files sit in: {DUMP_DIR}")
        print("  3) run  python fetch.py  again")
        return

    rows, per_poet = [], {}
    found = dups = undated = short = 0
    for poem in iter_poems(DUMP_DIR):
        found += 1
        if poem.get("duplicate"):          # a string id here means it's a duplicate copy
            dups += 1
            continue
        author = poem["author"]
        name = author.get("name") or "unknown"
        year = poem.get("year_created") or (
            author["born"] + FLOURISH_OFFSET if author.get("born") else None)
        if not year:
            undated += 1
            continue
        if per_poet.get(name, 0) >= MAX_POEMS_PER_POET:
            continue
        text = line_text(poem.get("body"))
        if len(text.split()) < MIN_WORDS:
            short += 1
            continue
        rows.append({"poet": name, "year": int(year), "text": text})
        per_poet[name] = per_poet.get(name, 0) + 1

    print(f"scanned {found} poems  (skipped {dups} duplicates, {undated} undated, {short} too short)")
    if not rows:
        print("no poems written -- paste a sample JSON and I can adjust the parser.")
        return

    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["poet", "year", "text"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} poems by {len(per_poet)} poets to data/poetree.csv")


if __name__ == "__main__":
    main()
