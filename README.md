# Test the Textbook — Complete Project

_A digital-humanities study that checks famous claims about how English poetry changed against ~34,000 public-domain poems. This single file bundles the overview, the one-page proposal, and a guide to what every file does._

## Contents

1. [Overview](#overview)
2. [Proposal](#proposal)
3. [What each file does](#what-each-file-does)
   - [config.py](#configpy)
   - [poems_data.py](#poems_datapy)
   - [corpus.py](#corpuspy)
   - [peek.py](#peekpy)
   - [fetch.py](#fetchpy)
   - [fetch_poetrydb.py](#fetch_poetrydbpy)
   - [combine.py](#combinepy)
   - [test_textbook.py](#test_textbookpy)
   - [lexicons.py](#lexiconspy)
   - [validate.py](#validatepy)
   - [closeread.py](#closereadpy)
   - [export_viz.py](#export_vizpy)
   - [requirements.txt](#requirementstxt)
   - [atlas.html](#atlashtml)

---

## Overview

A digital-humanities study that checks famous claims about how English poetry
changed -- against the data. Each claim from literary history becomes a number
(the share of certain theme words across ~34,000 public-domain poems), and we
report which claims hold up and which don't. Descriptive only: just counting
and averaging, with confidence intervals. No prediction.

### In plain English

Literary history says things like "the Romantics wrote about nature," "poetry
grew more secular across the 1800s," and "the Industrial Revolution put machines
into poetry." We turn each claim into a simple measurement -- the share of nature
words, religious words, machine words, and so on -- average it per 25-year era
across thousands of poems, and check whether the trend matches the claim. The
claims the data **confirms** show the method works; the ones it **challenges**
are the interesting findings.

### Install

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Build the corpus

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

### Run the study

```bash
python test_textbook.py    # -> outputs/ figures + results_textbook.md
python validate.py         # -> check the rulers vs lexicons (optional)
python closeread.py        # -> list the extreme poems per measure (optional)
```

`test_textbook.py` writes to `outputs/`:
- `textbook_claims.png` — one trend panel per claim, with the 95% band and verdict
- `textbook_heatmap.png` — all five measures across the eras at a glance
- `textbook_effects.png` — how big each shift was, coloured by verdict
- `textbook_counts.png` — poems per era (where the data is thick or thin)
- `results_textbook.md` — the scoreboard, per-era counts, and per-claim detail

`validate.py` needs two free lexicon files in `data/lexicons/` (Brysbaert
concreteness and NRC-VAD) -- see the header of `validate.py` for where to get them.

### Files

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
├── lexicons.py            # shared loader for the Brysbaert / NRC-VAD files
├── validate.py            # check measures vs Brysbaert / NRC-VAD lexicons
├── closeread.py           # list the highest/lowest poems per measure to read
├── export_viz.py          # dump author/poem scores -> outputs/atlas_data.js
└── atlas.html             # D3 'Poet Atlas' -- explore authors across aspects
```

### How it works

1. **fetch / fetch_poetrydb / combine** build one deduplicated `data/poems.csv`.
2. **corpus** loads it and bins poems into 25-year eras (analysis starts at 1600;
   earlier bins are too sparse and use Middle English).
3. **test_textbook** scores every poem on a few theme measures (nature, sacred,
   industrial, concreteness, valence), averages per era with 95% confidence
   intervals from bootstrapping whole poets, and gives each textbook claim a
   verdict: CONFIRMED, WEAKLY SUPPORTED, or CHALLENGED. If the lexicon files are
   present, concreteness and valence are scored directly from Brysbaert/NRC-VAD
   (smoother and validated); otherwise from the word lists.
4. **validate** (optional) correlates the concreteness and valence measures with
   the published Brysbaert and NRC-VAD lexicons, to show the homemade rulers
   agree with the experts.

See `PROPOSAL.md` for the one-page write-up (question, hypotheses, method, figures).

### Sidequest: the Poet Atlas (interactive)

`atlas.html` is a standalone D3 page that maps every author across the five
aspects: pick what the axes measure, then hover a point to see that poet's
fingerprint (a radar of all five). To load your own data:

```bash
python export_viz.py       # writes outputs/atlas_data.js (and atlas.json)
```

Then open `atlas.html` beside `atlas_data.js` (move the file next to it, or use
the page's "Load atlas.json" button). With no data file it shows a small sample
so you can see how it works.

### The corpus, and the limit on "up to 2025"

Both sources are public domain, so the corpus ends in the early 1900s. There is
no free, legal, dated corpus that reaches 2025 (everything after ~1929 is under
copyright). The study is comprehensive across the sources' range.

### Limitations

Word lists are hand-built (hence `validate.py`); dating is by author floruit, not
composition date; the corpus is canonical and public-domain. All measures are
descriptive -- the study makes no claims about cause.

### Requirements

Python 3.9+ · numpy · matplotlib · certifi

---

## Proposal

### Question
Literary history makes confident claims about how English poetry changed over
the centuries. **Which of those claims survive when you measure them across tens
of thousands of poems — and which don't?**

### Background
Distant reading (Moretti, Jockers, Underwood) studies literary change at scale.
This project takes specific, named claims from literary history, turns each into
a number, and checks it against the data — foregrounding the claims the data
confirms and, more usefully, the ones it challenges. It is descriptive, not
predictive: every step is counting and averaging.

### Corpus
~34,000 public-domain English poems (PoeTree + PoetryDB, deduplicated), each
dated by its author's active year and binned into 25-year eras. The study runs
from **1600 onward**; earlier bins are dropped because they are sparse and written
in Middle English, which distorts any word-based measure.

### Hypotheses
Each is a textbook claim → a measure → a predicted direction.

1. **Romantic nature turn** — nature-word rate is higher around 1800 than in the mid-1700s.
2. **Secularization** — sacred-word rate falls across the 1800s.
3. **Turn to concreteness** — the abstract→concrete score rises after ~1800.
4. **Industrial imagery** — industrial-word rate rises through the 1800s.
5. **Darker modern mood** — valence (positive vs negative) falls into the 20th century.

### Method
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

### What each figure shows
- **`textbook_claims.png`**: one panel per claim, showing the measure across the
  eras with a shaded 95% band; the "before" era (gray line) and the era the claim
  is about (red line) are marked, and the verdict is in the title.
- **`textbook_heatmap.png`**: all five measures across all eras in one grid, each
  cell coloured by how high or low that measure is relative to its own average
  (red = high, blue = low). The whole "shape of literary change" at a glance.
- **`textbook_effects.png`**: one bar per claim showing how big the shift was from
  the "before" era to the claim era (in standard deviations), coloured by verdict
  (green = confirmed, orange = weakly supported, red = challenged).
- **`textbook_counts.png`**: poems per era, so a reader can see exactly where the
  corpus is thick or thin before trusting any trend.
- **`results_textbook.md`**: a scoreboard of every claim with its before/after
  values and verdict, how each measure was scored, and per-claim detail with CIs.

### Why it matters
The confirmed claims show the method works; the **challenged** claims are the real
contribution — if, say, industrial imagery barely rises despite the Industrial
Revolution, that is a genuine literary-historical argument, not a null result.
Every claim becomes a sentence, a graph, and a confidence interval anyone can check.

### Limitations
Word lists are hand-built (hence the validation step); dating is by author
floruit, not composition date; the corpus is canonical and public-domain, so it
ends in the early 1900s. All measures are descriptive — the study makes no claims
about cause.

---

## What each file does

The scripts run in a chain — build the corpus, then analyse it — and a few shared modules sit underneath. Listed in that order.

### config.py

Defines where things live: the paths to the `data/` (inputs) and `outputs/` (results) folders, built relative to the project so it works on any machine. Every other script imports its paths from here, so there's one place to change them.

### poems_data.py

Holds the project's hand-built tables. First, the word lists for each theme (nature, religious, industrial, concrete, abstract, positive, negative) that the measures count. Second, `AUTHOR_YEARS`, a table mapping poets to a rough active year, used to date PoetryDB poems (which carry no date of their own).

### corpus.py

Loads `data/poems.csv`, cleans each poem's text (lowercase, letters only), and sorts the poems into 25-year eras. It exposes `poems` (each tagged with its era) and `era_order` for the other scripts to import. If `poems.csv` doesn't exist yet, it stops with a clear message telling you how to build it.

### peek.py

A one-time diagnostic for the PoeTree download. It opens the unzipped dump and prints what the JSON looks like — how many poems there are and how the author and text are stored — so you can confirm the structure before parsing. Optional.

### fetch.py

Parses the large PoeTree `en.zip` dump (unzipped into `data/poetree_en/`) into `data/poetree.csv`. For each poem it pulls the author, joins the body lines into one block of text, dates it from the author's birth year, and skips the duplicates the dataset flags.

### fetch_poetrydb.py

Pulls extra public-domain poems from the PoetryDB web API into `data/poetrydb.csv`. Because those poems carry no dates, it dates them using the `AUTHOR_YEARS` table in `poems_data.py`, matching on the poet's name.

### combine.py

Merges `poetree.csv` and `poetrydb.csv` into the single `data/poems.csv` the study reads. It removes duplicate poems by fingerprinting their first few words (keeping the PoeTree copy when a poem appears in both) and prints a summary of how many were read, removed, and kept.

### test_textbook.py

The heart of the project. It scores every poem on the five measures, averages each per era with 95% confidence intervals (bootstrapping whole poets so no single prolific poet dominates), and for each of the five textbook claims compares the 'before' era with the era the claim is about — assigning a verdict of CONFIRMED, WEAKLY SUPPORTED, or CHALLENGED. It writes the four figures (claims, heatmap, effects, counts) and `results_textbook.md`. If the lexicon files are present it scores concreteness and valence straight from them; otherwise it uses the word lists.

### lexicons.py

A small shared helper that loads a 'word → number' lexicon file (the Brysbaert concreteness norms or the NRC-VAD valence lexicon), tolerant of format — it sniffs the delimiter and finds the right column by name — and scores a poem as the average value over its words. Both `validate.py` and `test_textbook.py` use it, so the loading logic lives in one place.

### validate.py

Checks that the homemade rulers agree with the experts. For concreteness and valence it correlates the study's score against the published lexicon score, both per poem and per era, and writes scatter plots plus `results_validation.md`. If the lexicon files aren't downloaded it skips that check with a message instead of failing.

### closeread.py

Supports the close-reading step. For each measure it lists the highest- and lowest-scoring poems (author, era, score, and the opening words) so you can check by eye that the numbers match what's on the page. Writes `outputs/closeread.md`.

### export_viz.py

Prepares data for the Poet Atlas. It scores every poem, aggregates to the author level (the mean of each measure, the poem count, the average year), samples some poems for the optional poem layer, and writes `outputs/atlas_data.js` and `atlas.json` for the visualization to load.

### requirements.txt

The three Python libraries the project needs: numpy, matplotlib, and certifi.

### atlas.html

The interactive D3 'Poet Atlas' page. A scatter where you pick any aspect for each axis; points are authors, sized by poem count and coloured by era, and hovering one shows that poet's fingerprint across all five aspects. It loads `atlas_data.js` from `export_viz.py`, or runs on built-in sample data if none is present.
