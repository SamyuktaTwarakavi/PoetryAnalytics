# corpus.py -- load the poems and sort them into eras.
# Other scripts use:  from corpus import poems, era_order

import csv
import os
import re
import sys
import random
from collections import Counter

import config

# some poems are longer than Python's default 128 KB CSV field limit
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(2**31 - 1)

BIN_YEARS = 25          # years per era (finer, since the corpus is large)
MAX_PER_POET = None     # e.g. 40 to limit a prolific poet; None = keep all
MAX_PER_ERA = None      # e.g. 300 to balance eras; None = keep all


def clean(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z\s]", " ", text.lower())).strip()


def era_of(year):
    start = (year // BIN_YEARS) * BIN_YEARS
    return f"{start}-{start + BIN_YEARS - 1}"


def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            text = clean(r.get("text", "") or "")
            era = (r.get("era") or "").strip()
            year = (r.get("year") or "").strip()
            if not text or (not era and not year.isdigit()):
                continue
            rows.append({
                "poet": (r.get("poet") or "unknown").strip() or "unknown",
                "year": int(year) if year.isdigit() else None,
                "era": era or era_of(int(year)),
                "text": text,
            })
    return rows


def balance(rows):
    random.seed(1)
    for cap, field in [(MAX_PER_POET, "poet"), (MAX_PER_ERA, "era")]:
        if not cap:
            continue
        groups = {}
        for r in rows:
            groups.setdefault(r[field], []).append(r)
        rows = []
        for items in groups.values():
            random.shuffle(items)
            rows.extend(items[:cap])
    return rows


# load now, so other scripts can import the results
if not os.path.exists(config.POEMS_CSV):
    raise SystemExit(
        "No data/poems.csv found. Build the corpus first:\n"
        "  python fetch.py            # PoeTree  -> data/poetree.csv\n"
        "  python fetch_poetrydb.py   # PoetryDB -> data/poetrydb.csv\n"
        "  python combine.py          # merge + dedupe -> data/poems.csv")

poems = balance(load_csv(config.POEMS_CSV))
print(f"loaded {len(poems)} poems from data/poems.csv")

era_order = sorted({p["era"] for p in poems}, key=lambda e: int(e.split("-")[0]))

_counts = Counter(p["era"] for p in poems)
for _e in era_order:
    if _counts[_e] < 3:
        print(f"warning: era {_e} has only {_counts[_e]} poem(s)")
