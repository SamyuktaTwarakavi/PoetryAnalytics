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
