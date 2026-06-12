# Poetry Drift

Measure how English poetry moves through a vector space over the centuries,
and whether that drift lines up with history. The corpus combines two
public-domain sources -- PoeTree (~40,000 dated poems) and PoetryDB (~3,000) --
merged with duplicates removed.

## What Code Actuall Does

**The question.** Did English poetry *change* between the 1700s and the early
1900s, and do those changes line up with history (factories arriving, religion
fading)?

**The trick.** A computer can't feel a poem, so we turn each poem into a list
of numbers -- which is like giving it a spot on a giant map, where poems that
use similar words and have a similar mood sit close together.

**The drift.** We sort poems by time, find the middle point of each period's
cloud of dots, and join those middles oldest-to-newest. That path is "the
drift." A short path means poetry barely changed; a long, twisty path means it
changed a lot -- and we can spot the moment it changed fastest.

**The rulers.** We also build a few rulers that each measure one thing -- happy
vs sad, concrete vs abstract, nature vs machines, sacred vs worldly -- and
watch them rise and fall over time. The story comes from which rulers move,
and when.

**Being honest.** The computer's word-learning has some randomness, so we run
it several times and average, and we show "error bars" -- ranges that say how
sure we are. And since only some people wrote and kept poems, we say poetry
*records* shifts in mood and ideas, not that it proves what everyone thought.

**In one line:** turn poems into dots on a map, watch the dots drift over ~200
years, measure that drift along a few meaningful rulers, and check whether it
matches real history.

## Install


pip3 install -r requirements.txt


## Build the corpus

```bash
# PoeTree -- the big, dated source
# 1. download en.zip (~388 MB) from https://zenodo.org/records/10907309
# 2. unzip it so the json files sit in  data/poetree_en/
python3 fetch.py            # PoeTree dump  -> data/poetree.csv
```

```bash
# PoetryDB -- adds more public-domain poems
python3 fetch_poetrydb.py   # PoetryDB      -> data/poetrydb.csv
```

```bash
# merge the two, removing duplicates
python3 combine.py          # -> data/poems.csv  
```


## Run the study

```bash
python3 run_study.py        # -> outputs/ figures + results_summary.md
```

## Files

```bash
poetry-drift/
├── data/                  # inputs (the *.csv sources + final poems.csv)
├── outputs/               # results (figures + results_summary.md)
├── config.py              # where the two folders are
├── poems_data.py          # word lists, dimension seeds, poet-year table
├── corpus.py              # load poems and sort them into eras
├── tools.py               # cosine math + saving pictures
├── peek.py                # inspect the PoeTree dump before parsing
├── fetch.py               # PoeTree en.zip dump  -> data/poetree.csv
├── fetch_api.py           # alternative: PoeTree via API -> data/poetree.csv
├── fetch_poetrydb.py      # PoetryDB            -> data/poetrydb.csv
├── combine.py             # merge sources + dedupe -> data/poems.csv
├── run_study.py           # full study: many runs, bootstrap CIs, summary
├── step1_trajectory.py    # TF-IDF vectors -> era journey
├── step2_wordcount.py     # score poems by counting words
└── step3_embeddings.py    # word2vec + projection (the core method)
```

## How it works

1. **fetch.py** parses the PoeTree dump (embedded author, body lines, skipping
   PoeTree's flagged duplicates) and **fetch_poetrydb.py** pulls PoetryDB,
   dating each poem by its author's active year (birth + 35).
2. **combine.py** merges the two source CSVs and removes repeated poems,
   matching them on a normalized fingerprint of their opening words and
   keeping the PoeTree copy when a poem appears in both.
3. **corpus.py** loads `data/poems.csv` and bins poems into eras (`BIN_YEARS`).
4. **run_study.py** trains several word2vec models, measures how the era
   centroids move, projects poems onto interpretable dimensions (valence,
   concreteness, nature-machine, sacred-worldly) after Kozlowski, Taddy &
   Evans (2019), puts 95% confidence intervals on everything by resampling
   over poets, cross-checks against the lexical TF-IDF trajectory, finds the
   turning point, and writes a results_summary.md to paste into the paper.

## The corpus, and the limit on "up to 2025"

Both sources are public domain, so the corpus ends in the early 1900s. There
is no free, legal, dated corpus that reaches 2025 (everything after ~1929 is
under copyright). Extending toward the present would mean a licensed database,
scraping modern sites (legally fraught), or adding AI-generated poetry as a
"present-day" point. The study is comprehensive across the sources' range.

## Your own poems

Drop a `poems.csv` in `data/` with a `text` column (plus `poet`, `year`) to
bypass the fetchers entirely. Settings live at the top of each file: era width
in `corpus.py`, embedding size and run counts in `run_study.py`, per-poet caps
in the fetchers, and the dedup fingerprint in `combine.py`.

## Requirements

Python 3.9+ · numpy · scikit-learn · matplotlib · gensim · poetree · certifi
