"""
Pull poems from PoetryDB into data/poetrydb.csv (one of the two sources).

PoetryDB (~3,000 public-domain poems) carries no dates, so we date each poem
by its author's active year from the AUTHOR_YEARS table in poems_data.py.
Run this, run fetch.py for PoeTree, then combine.py to merge and dedupe.

Run:  python fetch_poetrydb.py
"""

import csv
import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request

import config
from poems_data import AUTHOR_YEARS

OUT = os.path.join(config.DATA_DIR, "poetrydb.csv")
MIN_WORDS = 20
MAX_POEMS_PER_POET = None     # None = take everything PoetryDB has for each poet

try:
    import certifi
    SSL = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL = ssl.create_default_context()

IGNORE = {"sir", "lord", "lady", "dr", "mr", "mrs", "st", "major", "the",
          "earl", "of", "rev", "jr", "sr", "von", "van"}


def name_words(name):
    toks = re.sub(r"[^a-z ]", " ", name.lower()).split()
    return {t for t in toks if t not in IGNORE and len(t) > 1}


def find_author(key, authors):
    kt = name_words(key)
    for a in authors:
        at = name_words(a)
        if kt and at and (kt <= at or at <= kt):
            return a
    return None


def get(url):
    req = urllib.request.Request(urllib.parse.quote(url, safe=":/?&=,;"),
                                 headers={"User-Agent": "poetry-study/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as error:
        print("  fetch error:", error)
        return None


def main():
    catalogue = get("https://poetrydb.org/author")
    if not catalogue or "authors" not in catalogue:
        print("could not reach PoetryDB (check connection / certificates)")
        return
    authors = catalogue["authors"]

    rows, seen = [], set()
    for key, year in AUTHOR_YEARS.items():
        match = find_author(key, authors)
        if not match:
            continue
        poems = get(f"https://poetrydb.org/author/{match}/author,title,lines")
        time.sleep(0.4)
        if not isinstance(poems, list):
            continue
        kept = 0
        for poem in poems:
            if MAX_POEMS_PER_POET and kept >= MAX_POEMS_PER_POET:
                break
            title_id = (match, poem.get("title", ""))
            text = "\n".join(poem.get("lines", [])).strip()
            if title_id in seen or len(text.split()) < MIN_WORDS:
                continue
            rows.append({"poet": match, "year": year, "text": text})
            seen.add(title_id)
            kept += 1
        print(f"  {match} (~{year}): {kept}")

    if not rows:
        print("no poems collected")
        return

    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["poet", "year", "text"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote {len(rows)} poems to data/poetrydb.csv")


if __name__ == "__main__":
    main()
