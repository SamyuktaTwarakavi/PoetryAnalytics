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
