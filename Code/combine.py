"""
Combine the source corpora into one deduplicated data/poems.csv.

Reads whichever of these exist and merges them, dropping repeated poems
(matched on a normalized fingerprint of their opening words):
    data/poetree.csv     (from fetch.py or fetch_api.py)
    data/poetrydb.csv    (from fetch_poetrydb.py)

When the same poem appears in both, the PoeTree copy is kept (it is dated by
the author's birth year and already deduplicated within PoeTree).

Run after the fetchers:  python combine.py
"""

import csv
import os
import re
import sys

import config

# some poems are longer than Python's default 128 KB CSV field limit
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(2**31 - 1)

SOURCES = ["poetree.csv", "poetrydb.csv"]   # first listed wins when a poem is shared


def fingerprint(text):
    """First dozen normalized words -- a simple key for spotting the same poem."""
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).split()
    return " ".join(words[:12])


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    present = [s for s in SOURCES if os.path.exists(os.path.join(config.DATA_DIR, s))]
    if not present:
        print("no source files found. Build them first:")
        print("  python fetch.py            # PoeTree  -> data/poetree.csv")
        print("  python fetch_poetrydb.py   # PoetryDB -> data/poetrydb.csv")
        return

    rows, seen = [], set()
    total = duplicates = blank = 0
    for src in present:
        kept = src_total = 0
        for r in read(os.path.join(config.DATA_DIR, src)):
            src_total += 1
            total += 1
            text = (r.get("text") or "").strip()
            fp = fingerprint(text)
            if not fp:
                blank += 1
                continue
            if fp in seen:
                duplicates += 1
                continue
            seen.add(fp)
            rows.append({"poet": r.get("poet") or "unknown",
                         "year": r.get("year", ""), "text": text})
            kept += 1
        print(f"{src}: kept {kept} of {src_total}")

    with open(config.POEMS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["poet", "year", "text"])
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "-" * 36)
    print(f"  total poems read:    {total}")
    print(f"  duplicates removed:  {duplicates}")
    if blank:
        print(f"  blank (no text):     {blank}")
    print(f"  final corpus:        {len(rows)}  -> data/poems.csv")
    print("-" * 36)


if __name__ == "__main__":
    main()
