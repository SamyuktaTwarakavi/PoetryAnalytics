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
├── lexicons.py            # shared loader for the Brysbaert / NRC-VAD files
├── validate.py            # check measures vs Brysbaert / NRC-VAD lexicons
└── closeread.py           # list the highest/lowest poems per measure to read
```

## How it works

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
