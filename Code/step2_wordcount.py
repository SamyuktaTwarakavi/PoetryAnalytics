# step2_wordcount.py -- score poems on named dimensions by counting words.
# Run:  python step2_wordcount.py

from corpus import poems, era_order
import poems_data as words
import tools


def polarity(text, high, low):
    w = text.split()
    h = sum(1 for x in w if x in high)
    l = sum(1 for x in w if x in low)
    return (h - l) / (h + l) if (h + l) else 0.0


def rate(text, word_list):
    w = text.split()
    return 100.0 * sum(1 for x in w if x in word_list) / len(w)


for p in poems:
    p["valence"] = polarity(p["text"], words.POSITIVE, words.NEGATIVE)
    p["concreteness"] = polarity(p["text"], words.CONCRETE, words.ABSTRACT)
    p["nature"] = rate(p["text"], words.NATURE)
    p["industrial"] = rate(p["text"], words.INDUSTRIAL)
    p["religious"] = rate(p["text"], words.RELIGIOUS)

dims = ["valence", "concreteness", "nature", "industrial", "religious"]
scores = {d: [tools.era_average(poems, e, d) for e in era_order] for d in dims}

tools.save_dimension_lines(era_order, scores,
                           "Word-count dimensions across the eras",
                           "step2_dimensions.png")
tools.save_named_space(scores["concreteness"], scores["valence"], era_order,
                       "abstract  <-  Concreteness  ->  concrete",
                       "negative  <-  Valence  ->  positive",
                       "A space we can name", "step2_named_space.png")
