# Test the Textbook -- Full Code & Instructions

README first, then the one-page proposal, then the complete source of every file.

---

# Test the Textbook

A digital-humanities study that checks famous claims about how English poetry
changed -- against the data. Each claim from literary history becomes a number
(the share of certain theme words across ~34,000 public-domain poems), and we
report which claims hold up and which don't. Descriptive only: just counting
and averaging, with confidence intervals. No prediction.

## In plain English

Literary history says things like "the Romantics wrote about nature," "poetry
grew more secular across the 1800s," and "the Industrial Revolution put machines
into poetry." We turn each claim into a simple measurement -- the share of nature
words, religious words, machine words, and so on -- average it per 25-year era
across thousands of poems, and check whether the trend matches the claim. The
claims the data **confirms** show the method works; the ones it **challenges**
are the interesting findings.

## Install

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Build the corpus

```bash
# PoeTree -- the big, dated source
# 1. download en.zip (~388 MB) from https://zenodo.org/records/10907309
# 2. unzip it so the json files sit in  data/poetree_en/
python peek.py             # (optional) confirm the dump's layout
python fetch.py            # PoeTree dump  -> data/poetree.csv

# PoetryDB -- adds more public-domain poems
python fetch_poetrydb.py   # PoetryDB      -> data/poetrydb.csv

# merge the two, removing duplicates
python combine.py          # -> data/poems.csv  (this is what the study reads)
```

## Run the study

```bash
python test_textbook.py    # -> outputs/ figures + results_textbook.md
python validate.py         # -> check the rulers vs lexicons (optional)
```

`validate.py` needs two free lexicon files in `data/lexicons/` (Brysbaert
concreteness and NRC-VAD) -- see the header of `validate.py` for where to get them.

## Files

```
poetry/
├── data/                  # inputs (the *.csv sources + final poems.csv)
├── outputs/               # results (figures + result tables)
├── config.py              # where the two folders are
├── poems_data.py          # word lists + the poet-year table
├── corpus.py              # load poems and sort them into eras
├── peek.py                # inspect the PoeTree dump before parsing
├── fetch.py               # parse the PoeTree en.zip dump -> poetree.csv
├── fetch_poetrydb.py      # pull PoetryDB              -> poetrydb.csv
├── combine.py             # merge sources + dedupe     -> poems.csv
├── test_textbook.py       # THE study: claim verdicts, per-era CIs, figures
└── validate.py            # check measures vs Brysbaert / NRC-VAD lexicons
```

## How it works

1. **fetch / fetch_poetrydb / combine** build one deduplicated `data/poems.csv`.
2. **corpus** loads it and bins poems into 25-year eras (analysis starts at 1600;
   earlier bins are too sparse and use Middle English).
3. **test_textbook** scores every poem on a few theme measures (nature, sacred,
   industrial, concreteness, valence), averages per era with 95% confidence
   intervals from bootstrapping whole poets, and gives each textbook claim a
   verdict: CONFIRMED, WEAKLY SUPPORTED, or CHALLENGED.
4. **validate** (optional) correlates the concreteness and valence measures with
   the published Brysbaert and NRC-VAD lexicons, to show the homemade rulers
   agree with the experts.

See `PROPOSAL.md` for the one-page write-up (question, hypotheses, method, figures).

## The corpus, and the limit on "up to 2025"

Both sources are public domain, so the corpus ends in the early 1900s. There is
no free, legal, dated corpus that reaches 2025 (everything after ~1929 is under
copyright). The study is comprehensive across the sources' range.

## Limitations

Word lists are hand-built (hence `validate.py`); dating is by author floruit, not
composition date; the corpus is canonical and public-domain. All measures are
descriptive -- the study makes no claims about cause.

## Requirements

Python 3.9+ · numpy · matplotlib · certifi


---

# Test the Textbook — Project Proposal

## Question
Literary history makes confident claims about how English poetry changed over
the centuries. **Which of those claims survive when you measure them across tens
of thousands of poems — and which don't?**

## Background
Distant reading (Moretti, Jockers, Underwood) studies literary change at scale.
This project takes specific, named claims from literary history, turns each into
a number, and checks it against the data — foregrounding the claims the data
confirms and, more usefully, the ones it challenges. It is descriptive, not
predictive: every step is counting and averaging.

## Corpus
~34,000 public-domain English poems (PoeTree + PoetryDB, deduplicated), each
dated by its author's active year and binned into 25-year eras. The study runs
from **1600 onward**; earlier bins are dropped because they are sparse and written
in Middle English, which distorts any word-based measure.

## Hypotheses
Each is a textbook claim → a measure → a predicted direction.

1. **Romantic nature turn** — nature-word rate is higher around 1800 than in the mid-1700s.
2. **Secularization** — sacred-word rate falls across the 1800s.
3. **Turn to concreteness** — the abstract→concrete score rises after ~1800.
4. **Industrial imagery** — industrial-word rate rises through the 1800s.
5. **Darker modern mood** — valence (positive vs negative) falls into the 20th century.

## Method
- Score every poem on the relevant measure: a **word-list rate** (e.g., % nature
  words) or a **polarity score** (concrete minus abstract, positive minus negative).
- Average per era, with **95% confidence intervals from bootstrapping whole poets**
  (so one prolific poet can't carry an era).
- For each claim, compare the "before" era with the era the claim is about, and
  assign a verdict: **CONFIRMED** (right direction, confidence intervals don't
  overlap), **WEAKLY SUPPORTED** (right direction, intervals overlap), or
  **CHALLENGED** (wrong direction).
- **Validate the rulers**: correlate the concreteness measure with the published
  Brysbaert concreteness norms and valence with the NRC-VAD lexicon, and
  hand-score ~30 poems to confirm the numbers agree with a human reader.
- **Close reading**: read two or three poems at each measure's extremes to check
  that the numbers match what is on the page.

## What each figure shows
- **Figure 1 — `textbook_claims.png`**: one panel per claim, showing the measure
  across the eras with a shaded 95% band; the "before" era (gray line) and the
  era the claim is about (red line) are marked, and the verdict is in the title.
- **Figure 2 — `textbook_counts.png`**: poems per era, so a reader can see exactly
  where the corpus is thick or thin before trusting any trend.
- **Table — `results_textbook.md`**: a scoreboard of every claim with its
  before/after values and verdict, followed by per-claim detail and CIs.

## Why it matters
The confirmed claims show the method works; the **challenged** claims are the real
contribution — if, say, industrial imagery barely rises despite the Industrial
Revolution, that is a genuine literary-historical argument, not a null result.
Every claim becomes a sentence, a graph, and a confidence interval anyone can check.

## Limitations
Word lists are hand-built (hence the validation step); dating is by author
floruit, not composition date; the corpus is canonical and public-domain, so it
ends in the early 1900s. All measures are descriptive — the study makes no claims
about cause.


---

# The code

## config.py

```python
# config.py -- where the input and output folders are.

import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")        # input poems go here
OUTPUT_DIR = os.path.join(HERE, "outputs")   # figures are saved here
POEMS_CSV = os.path.join(DATA_DIR, "poems.csv")
```

## poems_data.py

```python
# poems_data.py -- the data: word lists and the poet-year table.


# Word lists for step 2 (word-count dimensions).
POSITIVE = ["love", "joy", "bright", "light", "beauty", "beautiful", "sweet", "golden",
            "dancing", "glory", "blest", "bless", "fair", "delight", "hope", "warm",
            "gentle", "song", "spring", "bloom", "rose", "loveliest"]
NEGATIVE = ["death", "dark", "darkness", "grave", "weary", "desolate", "broken", "fear",
            "fearful", "cold", "sorrow", "grief", "pain", "tears", "gloom", "lonely",
            "shattered", "knell", "weakening", "sunless", "vain", "wounds"]
CONCRETE = ["sea", "tree", "trees", "stone", "iron", "hand", "eye", "eyes", "cloud",
            "daffodils", "lake", "breeze", "desert", "sand", "river", "gate", "frost",
            "bird", "cherry", "bough", "boughs", "sky", "moon", "herd", "leaf", "leaves",
            "fruit", "vines", "cow", "trout", "wings", "coast", "cliffs", "engine",
            "smoke", "sail", "rose"]
ABSTRACT = ["truth", "soul", "beauty", "time", "immortal", "fate", "mind", "study",
            "struggle", "circumstance", "wonder", "vision", "future", "change",
            "sacrifice", "symmetry", "observation", "state", "glory"]
NATURE = ["flower", "tree", "trees", "sky", "sea", "spring", "cloud", "bird", "river",
          "leaf", "leaves", "rose", "sun", "moon", "fruit", "breeze"]
INDUSTRIAL = ["iron", "engine", "steam", "smoke", "machine", "wheel", "grooves",
              "city", "factory", "coal"]
RELIGIOUS = ["god", "gods", "soul", "heaven", "sacred", "holy", "prayer", "sin",
             "eternal", "divine", "hallowed", "blest", "immortal", "spirit"]


# Poet -> rough active year, used to date PoetryDB poems (which carry no date).
AUTHOR_YEARS = {
    "Geoffrey Chaucer": 1380, "Thomas Wyatt": 1535, "Edmund Spenser": 1590,
    "Philip Sidney": 1580, "Walter Raleigh": 1590, "Christopher Marlowe": 1590,
    "William Shakespeare": 1600, "Michael Drayton": 1600,
    "John Donne": 1610, "Ben Jonson": 1610, "William Browne": 1620,
    "George Herbert": 1630, "Robert Herrick": 1640, "Richard Crashaw": 1640,
    "John Suckling": 1640, "Richard Lovelace": 1645, "Anne Bradstreet": 1650,
    "Henry Vaughan": 1655, "Andrew Marvell": 1660, "John Milton": 1660,
    "Thomas Flatman": 1670, "John Wilmot": 1675, "John Dryden": 1680,
    "Edward Taylor": 1685, "Anne Killigrew": 1683,
    "Lady Mary Chudleigh": 1700, "Anne Kingsmill Finch": 1700, "Matthew Prior": 1700,
    "Isaac Watts": 1715, "Jonathan Swift": 1715, "Alexander Pope": 1730,
    "James Thomson": 1730, "Samuel Johnson": 1750, "Thomas Gray": 1750,
    "William Collins": 1746, "Christopher Smart": 1755, "Joseph Warton": 1755,
    "Thomas Warton": 1765, "Oliver Goldsmith": 1765, "Charlotte Smith": 1785,
    "William Cowper": 1785, "Thomas Chatterton": 1768, "George Crabbe": 1790,
    "Robert Burns": 1790, "William Blake": 1794, "William Lisle Bowles": 1795,
    "John Keble": 1827,
    "Phillis Wheatley": 1773, "Philip Freneau": 1785, "John Trumbull": 1782,
    "Hugh Henry Brackenridge": 1780, "Henry Livingston": 1785,
    "Walter Scott": 1805, "William Wordsworth": 1805, "Samuel Taylor Coleridge": 1800,
    "Robert Southey": 1805, "Walter Savage Landor": 1810, "Charles Lamb": 1810,
    "Thomas Campbell": 1805, "Thomas Moore": 1810, "Leigh Hunt": 1815,
    "George Gordon Byron": 1815, "Percy Bysshe Shelley": 1819, "John Keats": 1819,
    "John Clare": 1820, "Jane Taylor": 1806,
    "Thomas Hood": 1830, "Elizabeth Barrett Browning": 1845, "Alfred Tennyson": 1845,
    "Robert Browning": 1845, "Edward Lear": 1850, "Emily Bronte": 1846,
    "Anne Bronte": 1846, "Charlotte Bronte": 1847, "Arthur Hugh Clough": 1850,
    "Charles Kingsley": 1855, "Matthew Arnold": 1860, "Coventry Patmore": 1860,
    "George Eliot": 1860, "Eliza Cook": 1850, "William Allingham": 1860,
    "Dante Gabriel Rossetti": 1865, "Christina Rossetti": 1860, "George Meredith": 1865,
    "Lewis Carroll": 1870, "William Morris": 1870, "Algernon Charles Swinburne": 1870,
    "Adam Lindsay Gordon": 1865, "William Topaz McGonagall": 1880,
    "Gerard Manley Hopkins": 1880, "Robert Bridges": 1885, "Oscar Wilde": 1885,
    "William Ernest Henley": 1888, "Francis Thompson": 1893, "Ernest Dowson": 1895,
    "Robert Louis Stevenson": 1885, "Katharine Tynan": 1895,
    "Mary Elizabeth Coleridge": 1895,
    "Thomas Hardy": 1895, "Rudyard Kipling": 1892, "Alfred Edward Housman": 1896,
    "Rupert Brooke": 1914, "Wilfred Owen": 1917, "John McCrae": 1915,
    "Charles Sorley": 1915, "Edward Thomas": 1915, "Joyce Kilmer": 1913,
    "William Cullen Bryant": 1820, "Ralph Waldo Emerson": 1840,
    "Henry Wadsworth Longfellow": 1850, "John Greenleaf Whittier": 1850,
    "Edgar Allan Poe": 1845, "Oliver Wendell Holmes": 1855, "Henry David Thoreau": 1850,
    "James Russell Lowell": 1855, "Walt Whitman": 1860, "Julia Ward Howe": 1862,
    "Emily Dickinson": 1862, "Helen Hunt Jackson": 1870, "Louisa May Alcott": 1870,
    "Mark Twain": 1875, "Emma Lazarus": 1880, "Sidney Lanier": 1875,
    "Eugene Field": 1885, "Ambrose Bierce": 1885, "James Whitcomb Riley": 1890,
    "Paul Laurence Dunbar": 1896, "Stephen Crane": 1895, "William Vaughn Moody": 1900,
    "Sara Teasdale": 1915, "Alan Seeger": 1916,
}
```

## corpus.py

```python
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
```

## peek.py

```python
# peek.py -- look at the PoeTree dump before parsing, to confirm its layout.
# Run:  python peek.py            (looks in data/poetree_en/)
#       python peek.py SOME/DIR   (look somewhere else)

import json
import os
import sys

import config

DUMP_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(config.DATA_DIR, "poetree_en")
TALLY = 3000   # how many json files to scan for the tally


def shape(value, depth=0, max_depth=3):
    """A short, human-readable sketch of a JSON value's structure."""
    pad = "  " * depth
    if isinstance(value, dict):
        if depth >= max_depth:
            return "{ ... }"
        inner = "\n".join(f"{pad}  {k}: {shape(v, depth + 1, max_depth)}"
                          for k, v in value.items())
        return "{\n" + inner + f"\n{pad}}}"
    if isinstance(value, list):
        if not value:
            return "[] (empty)"
        return f"[{len(value)} items] e.g. " + shape(value[0], depth + 1, max_depth)
    if isinstance(value, str):
        one_line = value.replace("\n", " ")
        return '"' + one_line[:50] + ('..."' if len(one_line) > 50 else '"')
    return repr(value)


def is_poem(rec):
    return isinstance(rec, dict) and "body" in rec and isinstance(rec.get("author"), dict)


def main():
    if not os.path.isdir(DUMP_DIR):
        print("PoeTree dump not found. To set it up:")
        print("  1) download en.zip from https://zenodo.org/records/10907309")
        print(f"  2) unzip it so the json files sit in: {DUMP_DIR}")
        print("  3) run  python peek.py  again")
        return

    paths = []
    for root, _, files in os.walk(DUMP_DIR):
        for fn in files:
            if fn.endswith(".json"):
                paths.append(os.path.join(root, fn))

    print(f"found {len(paths)} json files under {DUMP_DIR}\n")
    if not paths:
        print("no .json files -- did the unzip put them somewhere else?")
        return

    print("first few files:")
    for p in paths[:12]:
        print("  " + os.path.relpath(p, DUMP_DIR))
    print()

    # show one poem record in full so you can see the structure
    for p in paths[:TALLY]:
        try:
            with open(p, encoding="utf-8") as f:
                obj = json.load(f)
        except Exception:
            continue
        rec = obj[0] if isinstance(obj, list) and obj else obj
        if is_poem(rec):
            print("a POEM record looks like:\n" + shape(rec) + "\n")
            break

    # tally what the first TALLY files contain
    poems = dups = undated = other = 0
    for p in paths[:TALLY]:
        try:
            with open(p, encoding="utf-8") as f:
                obj = json.load(f)
        except Exception:
            continue
        for rec in (obj if isinstance(obj, list) else [obj]):
            if is_poem(rec):
                poems += 1
                if rec.get("duplicate"):
                    dups += 1
                elif not (rec.get("year_created") or rec["author"].get("born")):
                    undated += 1
            else:
                other += 1

    scanned = min(len(paths), TALLY)
    print(f"in the first {scanned} files: {poems} poems "
          f"({dups} duplicates, {undated} undated), {other} other.\n")

    if poems:
        print("Looks good -- fetch.py will parse this. Run:  python fetch.py")
    else:
        print("No poem records recognized. Paste one record (above) and I can")
        print("adjust the parser to match.")


if __name__ == "__main__":
    main()
```

## fetch.py

```python
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
    return " ".join(parts).strip()


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
```

## fetch_poetrydb.py

```python
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
            text = " ".join(poem.get("lines", [])).strip()
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
```

## combine.py

```python
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
```

## test_textbook.py

```python
"""
Test the Textbook -- check famous claims about English poetry against the data.

For each claim from literary history we measure one simple theme rate (or an
abstract<->concrete style score) per era, compare the era the claim is "about"
with an earlier era, and report whether the prediction holds. Descriptive only:
just counting and averaging, with bootstrap confidence intervals. No prediction.

Run (after building data/poems.csv):  python test_textbook.py
Outputs (in outputs/):
    textbook_claims.png    one panel per claim: the trend + 95% band
    textbook_counts.png    poems per era (shows where the data is thin)
    results_textbook.md    the numbers and a verdict for each claim
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
import poems_data as words
from corpus import poems, era_order

START_YEAR = 1600     # ignore the sparse, Middle-English bins before this
N_BOOTSTRAP = 500
rng = np.random.default_rng(0)


# ---- the claims, each tied to a measure we can count ----
CLAIMS = [
    {"name": "The Romantic nature turn",
     "textbook": "Romantic poets (~1800) wrote about nature far more than the Augustan poets before them.",
     "measure": "nature", "before": 1760, "after": 1810, "expect": "rise"},
    {"name": "Secularization",
     "textbook": "Poetry grew more secular (less religious) across the 1800s.",
     "measure": "sacred", "before": 1810, "after": 1910, "expect": "fall"},
    {"name": "The turn to concreteness",
     "textbook": "The 1700s were abstract; Romanticism and then Imagism made poetry concrete.",
     "measure": "concreteness", "before": 1760, "after": 1910, "expect": "rise"},
    {"name": "Industrial imagery",
     "textbook": "Industrialization put machines and cities into poetry.",
     "measure": "industrial", "before": 1785, "after": 1885, "expect": "rise"},
    {"name": "A darker modern mood",
     "textbook": "Poetry grew darker / less positive in the modern era.",
     "measure": "valence", "before": 1760, "after": 1910, "expect": "fall"},
]


# ---- the measures (simple word counting) ----
def rate(text, wordlist):
    w = text.split()
    return 100.0 * sum(1 for x in w if x in wordlist) / len(w) if w else 0.0


def polarity(text, high, low):
    w = text.split()
    h = sum(1 for x in w if x in high)
    l = sum(1 for x in w if x in low)
    return (h - l) / (h + l) if (h + l) else 0.0


def measure_poem(text, name):
    if name == "nature":       return rate(text, words.NATURE)
    if name == "industrial":   return rate(text, words.INDUSTRIAL)
    if name == "sacred":       return rate(text, words.RELIGIOUS)
    if name == "concreteness": return polarity(text, words.CONCRETE, words.ABSTRACT)
    if name == "valence":      return polarity(text, words.POSITIVE, words.NEGATIVE)
    raise ValueError("unknown measure: " + name)


# ---- small helpers ----
def era_start(era):
    return int(era.split("-")[0])


def era_containing(year, eras):
    for e in eras:
        if era_start(e) <= year <= int(e.split("-")[1]):
            return e
    return min(eras, key=lambda e: abs(era_start(e) - year))   # nearest, as a fallback


def ci(values):
    if not len(values):
        return (float("nan"), float("nan"))
    return tuple(float(x) for x in np.percentile(values, [2.5, 97.5]))


def main():
    eras = [e for e in era_order if era_start(e) >= START_YEAR]
    kept = [p for p in poems if p["era"] in eras]
    print(f"using {len(kept)} poems across {len(eras)} eras (from {START_YEAR})")

    by_era = {e: [p for p in kept if p["era"] == e] for e in eras}
    counts = {e: len(by_era[e]) for e in eras}

    needed = {c["measure"] for c in CLAIMS}
    for p in kept:
        for m in needed:
            p[m] = measure_poem(p["text"], m)

    # per-era mean + bootstrap CI (resample whole poets, not poems)
    def era_stats(measure):
        means, los, his = [], [], []
        for e in eras:
            group = by_era[e]
            vals = np.array([p[measure] for p in group])
            means.append(float(vals.mean()))
            poets = {}
            for i, p in enumerate(group):
                poets.setdefault(p["poet"], []).append(i)
            names, boot = list(poets), []
            for _ in range(N_BOOTSTRAP):
                chosen = rng.choice(names, size=len(names), replace=True)
                idx = np.concatenate([poets[n] for n in chosen])
                boot.append(vals[idx].mean())
            lo, hi = ci(boot)
            los.append(lo)
            his.append(hi)
        return np.array(means), np.array(los), np.array(his)

    stats = {m: era_stats(m) for m in needed}

    results = []
    for c in CLAIMS:
        means, los, his = stats[c["measure"]]
        eb, ea = era_containing(c["before"], eras), era_containing(c["after"], eras)
        ib, ia = eras.index(eb), eras.index(ea)
        rose = means[ia] > means[ib]
        direction_ok = rose == (c["expect"] == "rise")
        overlap = not (his[ib] < los[ia] or his[ia] < los[ib])
        verdict = ("CONFIRMED" if direction_ok and not overlap
                   else "WEAKLY SUPPORTED" if direction_ok
                   else "CHALLENGED")
        results.append({**c, "eb": eb, "ea": ea,
                        "before_m": means[ib], "after_m": means[ia],
                        "before_ci": (los[ib], his[ib]), "after_ci": (los[ia], his[ia]),
                        "verdict": verdict})
        print(f"  {c['name']}: {verdict}")

    plot_claims(eras, stats, results)
    plot_counts(eras, counts)
    write_report(eras, counts, results)


def _save(fig, name):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(config.OUTPUT_DIR, name), dpi=140)
    plt.close(fig)
    print("saved", os.path.join("outputs", name))


def plot_claims(eras, stats, results):
    n = len(results)
    rows = (n + 1) // 2
    fig, axes = plt.subplots(rows, 2, figsize=(12, 4 * rows))
    axes = np.array(axes).flatten()
    x = range(len(eras))
    for k, r in enumerate(results):
        means, los, his = stats[r["measure"]]
        ax = axes[k]
        ax.plot(x, means, "o-", color="tab:purple", lw=2)
        ax.fill_between(x, los, his, alpha=0.2, color="tab:purple")
        ax.axvline(eras.index(r["eb"]), color="gray", ls="--", lw=1.5)
        ax.axvline(eras.index(r["ea"]), color="tab:red", ls="--", lw=1.5)
        ax.set_title(f"{r['name']}  --  {r['verdict']}", fontsize=11)
        ax.set_xticks(list(x))
        ax.set_xticklabels(eras, rotation=60, fontsize=7, ha="right")
        ax.grid(alpha=0.3)
    for j in range(n, len(axes)):
        axes[j].axis("off")
    fig.suptitle("Test the Textbook: each claim's measure across the eras "
                 "(gray = 'before' era, red = the era the claim is about)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    _save(fig, "textbook_claims.png")


def plot_counts(eras, counts):
    fig = plt.figure(figsize=(11, 4.5))
    plt.bar(range(len(eras)), [counts[e] for e in eras], color="tab:blue")
    plt.xticks(range(len(eras)), eras, rotation=60, fontsize=8, ha="right")
    plt.ylabel("poems")
    plt.title("Poems per era (where the data is thick or thin)")
    plt.tight_layout()
    _save(fig, "textbook_counts.png")


def write_report(eras, counts, results):
    L = ["# Test the Textbook -- results\n"]
    L.append(f"Corpus: {sum(counts.values())} poems across {len(eras)} eras "
             f"({eras[0]} to {eras[-1]}). Eras before {START_YEAR} were excluded "
             f"(too few poems, Middle English).\n")

    L.append("## Scoreboard\n")
    L.append("| claim | measure | before | after | verdict |")
    L.append("|---|---|---|---|---|")
    for r in results:
        L.append(f"| {r['name']} | {r['measure']} | {r['eb']}: {r['before_m']:.3f} "
                 f"| {r['ea']}: {r['after_m']:.3f} | {r['verdict']} |")
    L.append("")

    L.append("## Poems per era\n")
    L.append("| era | poems |")
    L.append("|---|---|")
    for e in eras:
        L.append(f"| {e} | {counts[e]} |")
    L.append("")

    for r in results:
        bl, bh = r["before_ci"]
        al, ah = r["after_ci"]
        L.append(f"## {r['name']} -- {r['verdict']}\n")
        L.append(f"> {r['textbook']}\n")
        L.append(f"- Measure **{r['measure']}**, expected to **{r['expect']}**.")
        L.append(f"- {r['eb']}: {r['before_m']:.3f}  (95% CI [{bl:.3f}, {bh:.3f}])")
        L.append(f"- {r['ea']}: {r['after_m']:.3f}  (95% CI [{al:.3f}, {ah:.3f}])")
        L.append("")

    path = os.path.join(config.OUTPUT_DIR, "results_textbook.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("saved", os.path.join("outputs", "results_textbook.md"))


if __name__ == "__main__":
    main()
```

## validate.py

```python
"""
Validate the rulers -- do our word-list measures agree with the experts?

We check two of our measures against published psycholinguistic lexicons:
    concreteness  vs  Brysbaert concreteness norms (~40k words)
    valence       vs  NRC-VAD valence lexicon (~20k words)

For each poem we compute our score and the lexicon's average score over the
poem's words, then correlate the two. A high correlation means our homemade
ruler agrees with the experts and can be trusted.

Get the lexicons (both free) and put them in data/lexicons/ :
  - Brysbaert: search "Brysbaert concreteness ratings 40 thousand" (crr.ugent.be);
    download the tab-separated file and save it as  data/lexicons/concreteness.txt
  - NRC-VAD:   from Saif Mohammad's NRC-VAD page; save it as
    data/lexicons/nrc_vad.txt   (word <tab> valence <tab> arousal <tab> dominance)

Run:  python validate.py
If a file is missing it skips that check and tells you where to put it.
"""

import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
import poems_data as words
from corpus import poems, era_order

LEX_DIR = os.path.join(config.DATA_DIR, "lexicons")
BRYSBAERT = os.path.join(LEX_DIR, "concreteness.txt")
NRC_VAD = os.path.join(LEX_DIR, "nrc_vad.txt")


def polarity(text, high, low):
    w = text.split()
    h = sum(1 for x in w if x in high)
    l = sum(1 for x in w if x in low)
    return (h - l) / (h + l) if (h + l) else 0.0


# ---- loading a word -> value lexicon, tolerant of format ----
def sniff_delim(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        line = f.readline()
    return "\t" if line.count("\t") >= line.count(",") else ","


def load_lexicon(path, value_names, value_index):
    """Return {word: float}, picking the value column by header name or position."""
    delim = sniff_delim(path)
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
    vals = [lex[w] for w in text.split() if w in lex]
    return float(np.mean(vals)) if vals else None


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

    if os.path.exists(BRYSBAERT):
        print("concreteness vs Brysbaert:")
        lex = load_lexicon(BRYSBAERT, ["conc.m", "concreteness", "conc"], 2)
        print(f"  loaded {len(lex)} concreteness words")
        r = check("concreteness", words.CONCRETE, words.ABSTRACT, lex,
                  "Brysbaert concreteness", "validate_concreteness.png")
        if r:
            results.append(r)
    else:
        print(f"skip concreteness -- put the Brysbaert file at {BRYSBAERT}")

    if os.path.exists(NRC_VAD):
        print("valence vs NRC-VAD:")
        lex = load_lexicon(NRC_VAD, ["valence", "v"], 1)
        print(f"  loaded {len(lex)} valence words")
        r = check("valence", words.POSITIVE, words.NEGATIVE, lex,
                  "NRC-VAD valence", "validate_valence.png")
        if r:
            results.append(r)
    else:
        print(f"skip valence -- put the NRC-VAD file at {NRC_VAD}")

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
```

## requirements.txt

```text
numpy
matplotlib
certifi
```
