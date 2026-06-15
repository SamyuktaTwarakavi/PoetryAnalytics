# Testing Historical Claims about English Poetry

A digital-humanities study that checks famous claims about how English poetry
changed -- against the data. Each claim from literary history becomes a number
(the share of certain theme words across ~34,000 public-domain poems), and 
report which claims hold up and which don't.  Literary history says things like 
"the Romantics wrote about nature," "poetry grew more secular across the 1800s," 
and "the Industrial Revolution put machines into poetry." The goal of this 
research is to turn each claim into a simple measurement -- the share of nature words, 
religious words, machine words, and so on -- average it per 25-year era across 
thousands of poems, and check whether the trend matches the claim. 

## Objectives and Methods
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
Each is a historical claim → a measure → a predicted direction.

1. **Romantic nature turn** — nature-word rate is higher around 1800 than in the mid-1700s.
2. **Secularization** — sacred-word rate falls across the 1800s.
3. **Turn to concreteness** — the abstract→concrete score rises after ~1800.
4. **Industrial imagery** — industrial-word rate rises through the 1800s.
5. **Darker modern mood** — valence (positive vs negative) falls into the 20th century.

When the optional lexicons are installed, three further claims are tested: **more emotional intensity** (arousal rises), **the visual turn** (visual imagery rises), and **a sadder modern mood** (the sadness-word rate rises).

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



## Code Explanation

```bash
python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip3 install -r requirements.txt
```

### Build the corpus

```bash
# PoeTree -- the big, dated source
# 1. download en.zip (~388 MB) from https://zenodo.org/records/10907309
# 2. unzip it so the json files sit in  data/poetree_en/
python peek.py             # (optional) confirm the dump's layout
python3 fetch.py            # PoeTree dump  -> data/poetree.csv

# PoetryDB -- adds more public-domain poems
python3 fetch_poetrydb.py   # PoetryDB      -> data/poetrydb.csv

# merge the sources, removing duplicates
python3 combine.py          # -> data/poems.csv  (this is what the study reads)
```

### Run the study

```bash
python3 poetryAnalytics.py    # -> outputs/ figures + results_poetryAnalytics.md
python3 validate.py         # -> validate measures: rulers, coverage, convergence (optional)
python3 closeread.py        # -> list the extreme poems per measure (optional)
```

`poetryAnalytics.py` writes to `outputs/`:
- `poetryAnalytics_claims.png` — one trend panel per claim, with the 95% band and verdict
- `poetryAnalytics_heatmap.png` — every available measure across the eras at a glance
- `poetryAnalytics_effects.png` — how big each shift was, coloured by verdict
- `poetryAnalytics_counts.png` — poems per era (where the data is thick or thin)
- `results_poetryAnalytics.md` — the scoreboard, per-era counts, and per-claim detail

`validate.py` uses whichever lexicon files are in `data/lexicons/` (Brysbaert,
NRC-VAD, Lancaster, EmoLex): it validates concreteness/valence against their
lexicons, and coverage- and convergence-checks the rest. See the header of
`validate.py` for where to download each.

### Measures 
The study scores each poem on whichever measures the installed data supports, so
extra dimensions switch on automatically when their lexicon is in `data/lexicons/`.

**Always on**
- **nature, sacred, industrial** — word-list rates (share of theme words).
- **concreteness** — Brysbaert lexicon if present, else a concrete/abstract word list.
- **valence** — NRC-VAD lexicon if present, else a positive/negative word list.
- **arousal, dominance** — the same `nrc_vad.txt` carries these two extra columns
  (calm↔intense, weak↔powerful); they turn on whenever valence does.
- **visual, auditory** (imagery): Lancaster Sensorimotor Norms, ~40k words, CC BY-NC-SA.
  https://www.lancaster.ac.uk/psychology/lsnorms/ → save as `sensorimotor.csv`.
- **joy, sadness, fear**: NRC Emotion Lexicon (EmoLex), ~14k words, research use.
  https://saifmohammad.com/WebPages/AccessResource.htm → save as `nrc_emolex.txt`.


### File Organization

```
Code/
├── data/                  # inputs (the *.csv sources + final poems.csv)
├── outputs/               # results: figures, tables, and the atlas
│   ├── atlas.html         # the Poet Atlas — open this (loads atlas_data.js)
│   └── atlas_data.js      # author + poem scores, written by export_viz.py
├── config.py              # where the two folders are
├── poems_data.py          # word lists + the poet-year table
├── corpus.py              # load poems and sort them into eras
├── peek.py                # inspect the PoeTree dump before parsing
├── fetch.py               # parse the PoeTree en.zip dump -> poetree.csv
├── fetch_poetrydb.py      # pull PoetryDB              -> poetrydb.csv
├── combine.py             # merge sources + dedupe     -> poems.csv
├── poetryAnalytics.py     # THE study: claim verdicts, per-era CIs, figures
├── lexicons.py            # loaders: Brysbaert, NRC-VAD (valence/arousal/dominance), Lancaster, EmoLex
├── validate.py            # validate measures: rulers vs lexicons, coverage, convergent validity
├── closeread.py           # list the highest/lowest poems per measure to read
└── export_viz.py          # dump author/poem scores -> outputs/atlas_data.js
```

## How it works
1. **fetch / fetch_poetrydb / combine** build one deduplicated `data/poems.csv`.
2. **corpus** loads it and bins poems into 25-year eras (analysis starts at 1600;
   earlier bins are too sparse and use Middle English).
3. **poetryAnalytics** scores every poem on whichever measures the installed data
   supports — always nature, sacred, industrial, concreteness, and valence, plus
   arousal/dominance (NRC-VAD), visual/auditory (Lancaster), and joy/sadness/fear
   (EmoLex) when those lexicons are present. It averages each per era with 95%
   confidence intervals from bootstrapping whole poets, and gives each historical
   claim a verdict: CONFIRMED, WEAKLY SUPPORTED, or CHALLENGED.
4. **validate** (optional) does three checks: it correlates the concreteness and
   valence word lists against the Brysbaert and NRC-VAD lexicons (do the homemade
   rulers agree with the experts?), reports how much of the corpus each lexicon
   covers, and -- for the lexicon-only measures (arousal, dominance, visual,
   auditory, joy, sadness, fear), which have no second ruler -- checks they line
   up with trusted measures in the expected direction (e.g. sad-word poems should
   score low on valence). Results go to `outputs/results_validation.md`.

See the **Proposal** section below for the one-page write-up (question, hypotheses, method, figures).

### Poet Atlas interactive

`atlas.html` is a standalone D3 page that places every author on a distribution
strip for each available aspect (plus year), coloured by era. Search a poet to
highlight them across all the strips, and click a poet to slide in a panel from the
right listing their poems; click a poem to read it (formatted line by line) with a
Back button to the list. The fingerprint -- a radar of all the aspects -- shows on
the right, and an expandable "What each strip measures" panel
defines every aspect and how it is scored. A second tab, "Compare a poem", lets you paste any poem and ranks the corpus poems and poets that share the most distinctive vocabulary with it. To load your own data:

```bash
python3 export_viz.py       # writes outputs/atlas_data.js (and atlas.json)
```

Then open `atlas.html` beside `atlas_data.js` and it loads automatically. With no
data file it shows a small built-in sample. Note: proper line breaks in the poems
require rebuilding the corpus with the current fetchers -- re-run `fetch.py` ->
`combine.py` -> `export_viz.py`; an older `poems.csv` has the line breaks flattened
to spaces, so poems would read as one block.


### Limitations

Word lists are hand-built (hence `validate.py`); dating is by author floruit, not
composition date; the corpus is canonical and public-domain. All measures are
descriptive -- the study makes no claims about cause.

### Requirements

Python 3.9+ · numpy · matplotlib · certifi


#### Outputs
- **`poetryAnalytics_claims.png`**: one panel per claim, showing the measure across the
  eras with a shaded 95% band; the "before" era (gray line) and the era the claim
  is about (red line) are marked, and the verdict is in the title.
- **`poetryAnalytics_heatmap.png`**: every available measure across all eras in one grid, each
  cell coloured by how high or low that measure is relative to its own average
  (red = high, blue = low). The whole "shape of literary change" at a glance.
- **`poetryAnalytics_effects.png`**: one bar per claim showing how big the shift was from
  the "before" era to the claim era (in standard deviations), coloured by verdict
  (green = confirmed, orange = weakly supported, red = challenged).
- **`poetryAnalytics_counts.png`**: poems per era, so a reader can see exactly where the
  corpus is thick or thin before trusting any trend.
- **`results_poetryAnalytics.md`**: a scoreboard of every claim with its before/after
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
