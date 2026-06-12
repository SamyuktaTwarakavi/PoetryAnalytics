"""
Full-scale analysis for the Poetry Drift study.

A single word2vec run is noisy, so we train several and average the numbers
that come out of them. We put confidence intervals on everything by
resampling over *poets* (not poems, since a poet's poems aren't independent),
and we run the lexical TF-IDF trajectory alongside as an independent
cross-check. Finally we look for the period transition where practice moved
fastest -- the candidate "turning point".

Everything lands in outputs/:
    study_trajectory.png   one representative run, the period journey
    study_dimensions.png   each dimension over time, with confidence bands
    study_velocity.png     how far practice moved at each step
    results_summary.md     the numbers, formatted to drop into the paper

Run:  python run_study.py
(It trains several models, so give it a minute on the full corpus.)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from gensim.models import Word2Vec

import config
from corpus import poems, era_order
from poems_data import DIMENSION_SEEDS

# --- settings (turn N_SEEDS / N_BOOTSTRAP down if you just want a quick look) ---
N_SEEDS = 5            # word2vec models to average over (each is heavier on a big corpus)
N_BOOTSTRAP = 500     # total resamples over poets, split across the seeds
VECTOR_SIZE = 150
WINDOW = 5
MIN_COUNT = 10        # ignore rare words; sensible for a ~40k-poem corpus
EPOCHS = 10

rng = np.random.default_rng(0)


# ----------------------------------------------------------------------
# little numeric helpers
# ----------------------------------------------------------------------
def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def cosine_distance(a, b):
    return 1 - cosine(a, b)


def ci(samples):
    """2.5th / 97.5th percentiles, i.e. a 95% interval."""
    if not len(samples):
        return (float("nan"), float("nan"))
    return tuple(float(x) for x in np.percentile(samples, [2.5, 97.5]))


def centroids_from_rows(vectors, eras_arr, rows):
    """Mean vector per era, computed only over the given rows."""
    out, sub = {}, eras_arr[rows]
    for era in era_order:
        picked = rows[sub == era]
        if len(picked):
            out[era] = vectors[picked].mean(axis=0)
    return out


def movement(centroids):
    """Displacement between neighbouring eras, total path, and net drift."""
    steps = [cosine_distance(centroids[era_order[i]], centroids[era_order[i + 1]])
             for i in range(len(era_order) - 1)]
    return {
        "steps": steps,
        "path_length": float(sum(steps)),
        "net_drift": cosine_distance(centroids[era_order[0]], centroids[era_order[-1]]),
    }


def all_eras_present(centroids):
    return all(e in centroids for e in era_order)


# ----------------------------------------------------------------------
# building blocks
# ----------------------------------------------------------------------
def train_embedding(sentences, seed):
    return Word2Vec(sentences, vector_size=VECTOR_SIZE, window=WINDOW,
                    min_count=MIN_COUNT, sg=1, epochs=EPOCHS,
                    seed=seed, workers=1).wv


def poem_vector(tokens, wv):
    vecs = [wv[t] for t in tokens if t in wv]
    return np.mean(vecs, axis=0) if vecs else None


def build_axes(wv):
    """Each dimension is the average direction of its antonym pairs."""
    axes = {}
    for dim, pairs in DIMENSION_SEEDS.items():
        diffs = [wv[hi] - wv[lo] for hi, lo in pairs if hi in wv and lo in wv]
        if diffs:
            v = np.mean(diffs, axis=0)
            axes[dim] = v / (np.linalg.norm(v) + 1e-9)
    return axes


# ----------------------------------------------------------------------
# the semantic analysis (word2vec), averaged over seeds with bootstrap CIs
# ----------------------------------------------------------------------
def semantic_analysis():
    sentences = [p["text"].split() for p in poems]
    poets = np.array([p["poet"] for p in poems])
    eras = np.array([p["era"] for p in poems])
    unique_poets = sorted(set(poets))
    per_seed_boot = max(1, N_BOOTSTRAP // N_SEEDS)

    # collected across all seeds (and their bootstraps)
    seed_steps, seed_path, seed_net = [], [], []          # one value per seed
    boot_steps = [[] for _ in range(len(era_order) - 1)]  # pooled bootstrap
    boot_path, boot_net = [], []
    dim_means = {}      # dim -> era -> [seed means]
    dim_boot = {}       # dim -> era -> [bootstrap means]
    representative = None

    for s in range(N_SEEDS):
        wv = train_embedding(sentences, seed=s + 1)
        axes = build_axes(wv)

        vecs = [poem_vector(t, wv) for t in sentences]
        keep = np.array([i for i, v in enumerate(vecs) if v is not None])
        V = np.array([vecs[i] for i in keep])
        E = eras[keep]
        P = poets[keep]
        scores = {d: np.array([cosine(V[j], axes[d]) for j in range(len(V))]) for d in axes}
        poet_rows = {pt: np.where(P == pt)[0] for pt in unique_poets}

        # point estimate for this seed
        cents = centroids_from_rows(V, E, np.arange(len(V)))
        mv = movement(cents)
        seed_steps.append(mv["steps"])
        seed_path.append(mv["path_length"])
        seed_net.append(mv["net_drift"])
        for d in axes:
            dim_means.setdefault(d, {e: [] for e in era_order})
            for e in era_order:
                vals = scores[d][E == e]
                if len(vals):
                    dim_means[d][e].append(float(vals.mean()))

        if s == 0:
            representative = (V, E, cents)

        # bootstrap over poets, pooled into the shared collections
        for _ in range(per_seed_boot):
            chosen = rng.choice(unique_poets, size=len(unique_poets), replace=True)
            rows = np.concatenate([poet_rows[pt] for pt in chosen])
            cents_b = centroids_from_rows(V, E, rows)
            if not all_eras_present(cents_b):
                continue
            mv_b = movement(cents_b)
            for i, st in enumerate(mv_b["steps"]):
                boot_steps[i].append(st)
            boot_path.append(mv_b["path_length"])
            boot_net.append(mv_b["net_drift"])
            sub_e = E[rows]
            for d in axes:
                dim_boot.setdefault(d, {e: [] for e in era_order})
                for e in era_order:
                    vals = scores[d][rows[sub_e == e]]
                    if len(vals):
                        dim_boot[d][e].append(float(vals.mean()))

    return {
        "mean_steps": np.mean(seed_steps, axis=0).tolist(),
        "step_ci": [ci(boot_steps[i]) for i in range(len(boot_steps))],
        "path": float(np.mean(seed_path)), "path_ci": ci(boot_path),
        "net": float(np.mean(seed_net)), "net_ci": ci(boot_net),
        "dim_mean": {d: {e: float(np.mean(v)) if v else float("nan")
                         for e, v in ers.items()} for d, ers in dim_means.items()},
        "dim_ci": {d: {e: ci(dim_boot[d][e]) for e in era_order} for d in dim_boot},
        "representative": representative,
    }


# ----------------------------------------------------------------------
# the lexical analysis (TF-IDF) -- an independent cross-check
# ----------------------------------------------------------------------
def lexical_analysis():
    X = TfidfVectorizer(stop_words="english", max_features=5000).fit_transform(
        [p["text"] for p in poems]).toarray()
    eras = np.array([p["era"] for p in poems])
    poets = np.array([p["poet"] for p in poems])
    unique_poets = sorted(set(poets))
    poet_rows = {pt: np.where(poets == pt)[0] for pt in unique_poets}

    point = movement(centroids_from_rows(X, eras, np.arange(len(X))))
    boot_steps = [[] for _ in range(len(era_order) - 1)]
    boot_path, boot_net = [], []
    for _ in range(N_BOOTSTRAP):
        chosen = rng.choice(unique_poets, size=len(unique_poets), replace=True)
        rows = np.concatenate([poet_rows[pt] for pt in chosen])
        cents = centroids_from_rows(X, eras, rows)
        if not all_eras_present(cents):
            continue
        mv = movement(cents)
        for i, st in enumerate(mv["steps"]):
            boot_steps[i].append(st)
        boot_path.append(mv["path_length"])
        boot_net.append(mv["net_drift"])

    return {
        "steps": point["steps"], "step_ci": [ci(b) for b in boot_steps],
        "path": point["path_length"], "path_ci": ci(boot_path),
        "net": point["net_drift"], "net_ci": ci(boot_net),
    }


# ----------------------------------------------------------------------
# turning point: the transition that moved the most
# ----------------------------------------------------------------------
def turning_points(steps):
    try:
        import ruptures as rpt
        series = np.array(steps).reshape(-1, 1)
        breaks = rpt.Pelt(model="rbf").fit(series).predict(pen=1)
        idx = [b - 1 for b in breaks if 0 < b <= len(steps)]
        if idx:
            return idx
    except Exception:
        pass
    # fallback: just the single biggest jump
    return [int(np.argmax(steps))]


# ----------------------------------------------------------------------
# figures
# ----------------------------------------------------------------------
def save(name):
    import os
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUT_DIR, name)
    plt.savefig(path, dpi=140)
    plt.close()
    print("saved", os.path.join("outputs", name))


def plot_trajectory(rep):
    V, E, cents = rep
    pca = PCA(n_components=2).fit(V)
    pts = pca.transform(V)
    cxy = pca.transform(np.array([cents[e] for e in era_order]))
    colours = plt.cm.viridis(np.linspace(0, 1, len(era_order)))
    plt.figure(figsize=(8.5, 7))
    for i in range(len(V)):
        plt.scatter(*pts[i], s=30, alpha=0.25, color=colours[era_order.index(E[i])])
    for i, e in enumerate(era_order):
        plt.scatter(*cxy[i], s=320, color=colours[i], edgecolor="black", zorder=5)
        plt.annotate(e, cxy[i], fontsize=11, fontweight="bold",
                     xytext=(8, 8), textcoords="offset points")
        if i:
            plt.annotate("", xy=cxy[i], xytext=cxy[i - 1],
                         arrowprops=dict(arrowstyle="->", lw=2, color="gray"))
    plt.title("Trajectory of poetic practice (one representative word2vec run)")
    plt.xlabel("Direction 1"); plt.ylabel("Direction 2"); plt.tight_layout()
    save("study_trajectory.png")


def plot_dimensions(sem):
    dims = list(sem["dim_mean"].keys())
    if not dims:
        print("no dimensions built (seed words too rare in this corpus) -- skipping")
        return
    rows = (len(dims) + 1) // 2
    fig, axes = plt.subplots(rows, 2, figsize=(11, 4 * rows))
    axes = np.array(axes).flatten()
    for k, d in enumerate(dims):
        mean = [sem["dim_mean"][d][e] for e in era_order]
        lo = [sem["dim_ci"][d][e][0] for e in era_order]
        hi = [sem["dim_ci"][d][e][1] for e in era_order]
        axes[k].plot(era_order, mean, "o-", lw=2, color="tab:purple")
        axes[k].fill_between(range(len(era_order)), lo, hi, alpha=0.2, color="tab:purple")
        axes[k].set_title(d, fontsize=11)
        axes[k].tick_params(axis="x", labelrotation=25)
        axes[k].grid(alpha=0.3)
    for j in range(len(dims), len(axes)):
        axes[j].axis("off")
    fig.suptitle("Learned dimensions over time (mean and 95% interval)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save("study_dimensions.png")


def plot_velocity(sem, tps):
    labels = [f"{era_order[i]}\n->{era_order[i+1]}" for i in range(len(era_order) - 1)]
    mean = sem["mean_steps"]
    lo = [sem["step_ci"][i][0] for i in range(len(mean))]
    hi = [sem["step_ci"][i][1] for i in range(len(mean))]
    err = [[max(0.0, m - l) for m, l in zip(mean, lo)],
           [max(0.0, h - m) for h, m in zip(hi, mean)]]
    colours = ["tab:red" if i in tps else "tab:gray" for i in range(len(mean))]
    plt.figure(figsize=(9, 5))
    plt.bar(range(len(mean)), mean, yerr=err, color=colours, capsize=4)
    plt.xticks(range(len(mean)), labels, fontsize=9)
    plt.ylabel("displacement (cosine distance)")
    plt.title("How far poetic practice moved at each step (red = turning point)")
    plt.tight_layout()
    save("study_velocity.png")


# ----------------------------------------------------------------------
# results summary, formatted for the paper
# ----------------------------------------------------------------------
def write_summary(sem, lex, tps):
    import os
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUT_DIR, "results_summary.md")
    L = []
    L.append("# Results summary\n")
    L.append(f"Corpus: {len(poems)} poems across {len(era_order)} eras "
             f"({', '.join(era_order)}).")
    L.append(f"Settings: {N_SEEDS} embedding runs, {N_BOOTSTRAP} bootstrap "
             f"resamples over poets, vector size {VECTOR_SIZE}.\n")

    L.append("## Movement between eras (semantic, word2vec)\n")
    L.append("| transition | displacement | 95% CI |")
    L.append("|---|---|---|")
    for i in range(len(era_order) - 1):
        lo, hi = sem["step_ci"][i]
        L.append(f"| {era_order[i]} -> {era_order[i+1]} | "
                 f"{sem['mean_steps'][i]:.3f} | [{lo:.3f}, {hi:.3f}] |")
    L.append(f"\nPath length: {sem['path']:.3f} "
             f"(95% CI [{sem['path_ci'][0]:.3f}, {sem['path_ci'][1]:.3f}]). "
             f"Net drift: {sem['net']:.3f} "
             f"(95% CI [{sem['net_ci'][0]:.3f}, {sem['net_ci'][1]:.3f}]).")
    L.append(f"\nTurning point(s): "
             + ", ".join(f"{era_order[i]} -> {era_order[i+1]}" for i in tps) + "\n")

    L.append("## Movement between eras (lexical, TF-IDF cross-check)\n")
    L.append("| transition | displacement | 95% CI |")
    L.append("|---|---|---|")
    for i in range(len(era_order) - 1):
        lo, hi = lex["step_ci"][i]
        L.append(f"| {era_order[i]} -> {era_order[i+1]} | "
                 f"{lex['steps'][i]:.3f} | [{lo:.3f}, {hi:.3f}] |")
    L.append("")

    L.append("## Dimension scores by era (semantic, mean and 95% CI)\n")
    if not sem["dim_mean"]:
        L.append("_No dimension axes were built: the seed words are too rare in "
                 "this corpus. Lower MIN_COUNT or use a larger corpus._\n")
    for d in sem["dim_mean"]:
        L.append(f"### {d}\n")
        L.append("| era | mean | 95% CI |")
        L.append("|---|---|---|")
        for e in era_order:
            lo, hi = sem["dim_ci"][d][e]
            L.append(f"| {e} | {sem['dim_mean'][d][e]:.3f} | [{lo:.3f}, {hi:.3f}] |")
        L.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("saved", os.path.join("outputs", "results_summary.md"))


# ----------------------------------------------------------------------
def main():
    print(f"Semantic analysis: {N_SEEDS} word2vec runs ...")
    sem = semantic_analysis()
    print("Lexical cross-check ...")
    lex = lexical_analysis()
    tps = turning_points(sem["mean_steps"])

    plot_trajectory(sem["representative"])
    plot_dimensions(sem)
    plot_velocity(sem, tps)
    write_summary(sem, lex, tps)

    print("\nBiggest move:",
          f"{era_order[tps[0]]} -> {era_order[tps[0]+1]}")
    print("Everything written to outputs/. Paste results_summary.md into the paper.")


if __name__ == "__main__":
    main()
