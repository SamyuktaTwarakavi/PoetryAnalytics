# Ruler validation

## 1. Word-list rulers vs published lexicons

Concreteness and valence are the only measures with both a homemade word list and a lexicon, so we can correlate the two. Higher means our word list agrees with the experts; the era-level number is the one that matters, since the claims are about era averages.

| our measure | lexicon | poem-level r | era-level r | poems |
|---|---|---|---|---|
| concreteness | Brysbaert concreteness | 0.34 | 0.84 | 33753 |
| valence | NRC-VAD valence | 0.44 | 0.41 | 33753 |

## 2. Lexicon coverage

Share of the corpus's words each lexicon actually scores. A measure built on a low-coverage lexicon is noisier and should be read with more caution.

| lexicon (measure) | corpus words covered | lexicon size |
|---|---|---|
| concreteness (Brysbaert) | 85.4% | 39954 |
| valence (NRC-VAD) | 68.9% | 54801 |
| arousal (NRC-VAD) | 68.9% | 54801 |
| dominance (NRC-VAD) | 68.9% | 54801 |
| visual (Lancaster) | 85.4% | 39707 |
| auditory (Lancaster) | 85.4% | 39707 |
| emotion words (EmoLex joy/sad/fear) | 7.1% | 2614 |

## 3. Convergent validity (lexicon-only measures)

Arousal, dominance, visual, auditory and the emotions have no second independent ruler, so instead we check they relate to trusted measures in the expected direction. A matching sign is evidence the measure is capturing something real; an UNEXPECTED sign is a red flag worth investigating.

| measure | vs | expected | r | result | poems |
|---|---|---|---|---|---|
| sadness | valence | - | -0.40 | as expected | 33753 |
| joy | valence | + | +0.53 | as expected | 33753 |
| fear | valence | - | -0.40 | as expected | 33753 |
| fear | arousal | + | +0.38 | as expected | 33753 |
| visual | concreteness | + | +0.73 | as expected | 33753 |
| joy | sadness | - | +0.07 | UNEXPECTED | 33753 |

Expected directions: sadness vs valence (sad-word poems should score lower valence); joy vs valence (joy-word poems should score higher valence); fear vs valence (fear-word poems should score lower valence); fear vs arousal (fear-word poems should score higher arousal); visual vs concreteness (visual imagery should track concreteness); joy vs sadness (joy and sadness should pull opposite ways).
