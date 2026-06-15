"""
Close reading -- the poems at each extreme.

For every measure, list the highest- and lowest-scoring poems (author, era,
score, and the opening words) so you can check that the numbers match what is
on the page. If the most-concrete poems really are full of physical images and
the least are all abstractions, the measure means something.

Uses the same scoring as poetryAnalytics.py: the lexicons if they are in
data/lexicons/, otherwise the word lists.

Run:  python closeread.py
Writes outputs/closeread.md and prints a short version to the screen.
"""

import os

import config
from corpus import poems
from poetryAnalytics import build_measures

TOP_N = 5
MIN_WORDS = 40          # skip very short poems -- their rates swing wildly


def snippet(text, n=24):
    w = text.split()
    return " ".join(w[:n]) + (" ..." if len(w) > n else "")


def line(score, p):
    return (f"- **{score:.3f}**  {p['poet']}  ({p['era']})  \n"
            f"  > {snippet(p['text'])}")


def main():
    order, scorers, scoring = build_measures()

    long_poems = [p for p in poems if len(p["text"].split()) >= MIN_WORDS]
    print(f"ranking {len(long_poems)} poems (>= {MIN_WORDS} words) of {len(poems)} total")
    print("measures:", ", ".join(order))

    out = ["# Close reading: the poems at each extreme\n"]
    out.append(f"For each measure, the {TOP_N} highest- and lowest-scoring poems "
               f"(length >= {MIN_WORDS} words). The text shown is the cleaned, "
               f"lowercased version used for scoring -- look up the original to "
               f"read it properly.\n")

    for m in order:
        scored = [(scorers[m](p["text"]), p) for p in long_poems]
        scored = [(s, p) for s, p in scored if s is not None]
        scored.sort(key=lambda sp: sp[0])
        low = scored[:TOP_N]
        high = scored[-TOP_N:][::-1]

        out.append(f"## {m}  ({scoring[m]})\n")
        out.append(f"### Highest {m}\n")
        out += [line(s, p) for s, p in high]
        out.append(f"\n### Lowest {m}\n")
        out += [line(s, p) for s, p in low]
        out.append("")

        print(f"\n{m}  ({scoring[m]})")
        print("  highest: " + ", ".join(f"{p['poet']} {s:.2f}" for s, p in high))
        print("  lowest:  " + ", ".join(f"{p['poet']} {s:.2f}" for s, p in low))

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUT_DIR, "closeread.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("\nsaved", os.path.join("outputs", "closeread.md"))


if __name__ == "__main__":
    main()
