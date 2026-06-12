"""
Alternative corpus builder: stream PoeTree via its live API (slow).

The main path is fetch.py (parsing the Zenodo en.zip dump), which is much
faster. Use this only if you'd rather not download the dump. Same output:
it writes data/poems.csv, dating each poem by the author's active year
(birth + 35).

Setup:  pip install poetree     (needs an internet connection)
Run:    python fetch_api.py
"""

import csv
import os

import poetree  # pip install poetree

import config

OUT = config.DATA_DIR + "/poetree.csv"

LANG = "en"
BORN_AFTER = 1500
BORN_BEFORE = 2025
FLOURISH_OFFSET = 35
MAX_POEMS_PER_POET = 300
MIN_WORDS = 20


def poem_text(poem):
    try:
        return " ".join(line.get("text", "") for line in poem.get_body()).strip()
    except Exception:
        return ""


def main():
    corpus = poetree.Corpus(LANG)
    print(f"PoeTree {LANG}: {corpus.n_poems} poems, {corpus.n_authors} authors")
    print("Pulling poems (this is slow for the full corpus) ...")

    rows = []
    for author in corpus.get_authors(born_after=BORN_AFTER, born_before=BORN_BEFORE):
        born = getattr(author, "born", None)
        if not born:
            continue
        year = born + FLOURISH_OFFSET
        try:
            poems = author.get_poems()
        except Exception:
            continue
        kept = 0
        for poem in poems:
            if kept >= MAX_POEMS_PER_POET:
                break
            text = poem_text(poem)
            if len(text.split()) < MIN_WORDS:
                continue
            rows.append({"poet": author.name, "year": year, "text": text})
            kept += 1
        if kept:
            print(f"  {author.name} (b.{born} -> ~{year}): {kept}")

    if not rows:
        print("no poems collected -- check your connection or the born-year range")
        return

    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["poet", "year", "text"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote {len(rows)} poems to data/poetree.csv")


if __name__ == "__main__":
    main()
