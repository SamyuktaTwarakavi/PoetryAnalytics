"""
Load a "word -> number" lexicon and score a poem by its average value.

Tolerant of tab- or comma-separated files and of an optional header row; the
value column is found by name (e.g. "Conc.M", "Valence") or by position. Shared
by validate.py (to check our rulers) and test_textbook.py (to optionally score
concreteness and valence straight from the lexicon).

Put the files in data/lexicons/ -- see the header of validate.py for the links.
"""

import csv
import os
import numpy as np

import config

LEX_DIR = os.path.join(config.DATA_DIR, "lexicons")
BRYSBAERT = os.path.join(LEX_DIR, "concreteness.txt")
NRC_VAD = os.path.join(LEX_DIR, "nrc_vad.txt")


def _sniff_delim(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        line = f.readline()
    return "\t" if line.count("\t") >= line.count(",") else ","


def load_lexicon(path, value_names, value_index):
    """Return {word: float}, picking the value column by header name or position."""
    delim = _sniff_delim(path)
    with open(path, encoding="utf-8", errors="ignore") as f:
        rows = list(csv.reader(f, delimiter=delim))
    if not rows:
        return {}

    # treat the first row as a header if its value cell isn't a number
    header = rows[0]
    has_header = True
    try:
        float(header[value_index])
        has_header = False
    except (ValueError, IndexError):
        has_header = True

    vi = value_index
    if has_header:
        names = {h.strip().lower(): i for i, h in enumerate(header)}
        for cand in value_names:
            if cand in names:
                vi = names[cand]
                break
        rows = rows[1:]

    out = {}
    for row in rows:
        if len(row) <= vi or not row or not row[0]:
            continue
        try:
            out[row[0].strip().lower()] = float(row[vi])
        except ValueError:
            continue
    return out


def poem_mean(text, lex):
    """Average lexicon value over the poem's words, or None if none are covered."""
    vals = [lex[w] for w in text.split() if w in lex]
    return float(np.mean(vals)) if vals else None


def load_concreteness():
    """Brysbaert concreteness, or None if the file isn't in data/lexicons/."""
    if os.path.exists(BRYSBAERT):
        return load_lexicon(BRYSBAERT, ["conc.m", "concreteness", "conc"], 2)
    return None


def load_valence():
    """NRC-VAD valence, or None if the file isn't in data/lexicons/."""
    if os.path.exists(NRC_VAD):
        return load_lexicon(NRC_VAD, ["valence", "v"], 1)
    return None
