# tools.py -- small shared helpers: a little math, and saving pictures.

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def cosine_distance(a, b):
    return 1 - cosine(a, b)


def era_average(poems, era, key):
    values = [p[key] for p in poems if p["era"] == era and key in p]
    return sum(values) / len(values) if values else 0.0


def _colours(n):
    cmap = plt.cm.viridis
    return [cmap(i / max(1, n - 1)) for i in range(n)]


def _save(name):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUT_DIR, name)
    plt.savefig(path, dpi=130)
    plt.close()
    print("saved", os.path.join("outputs", name))


def save_journey(poem_xy, poem_eras, centroid_xy, era_order, title, name):
    colours = _colours(len(era_order))
    plt.figure(figsize=(8.5, 7))
    for i in range(len(poem_xy)):
        plt.scatter(poem_xy[i, 0], poem_xy[i, 1], s=35, alpha=0.3,
                    color=colours[era_order.index(poem_eras[i])])
    for i, era in enumerate(era_order):
        plt.scatter(centroid_xy[i, 0], centroid_xy[i, 1], s=320, zorder=5,
                    color=colours[i], edgecolor="black", label=era)
        plt.annotate(era, (centroid_xy[i, 0], centroid_xy[i, 1]), fontsize=11,
                     fontweight="bold", xytext=(8, 8), textcoords="offset points")
        if i > 0:
            plt.annotate("", xy=centroid_xy[i], xytext=centroid_xy[i - 1],
                         arrowprops=dict(arrowstyle="->", lw=2, color="gray"))
    plt.title(title)
    plt.xlabel("Direction 1")
    plt.ylabel("Direction 2")
    if len(era_order) <= 8:
        plt.legend(title="Era")
    plt.tight_layout()
    _save(name)


def save_dimension_lines(era_order, scores, title, name):
    dims = list(scores.keys())
    rows = (len(dims) + 1) // 2
    fig, axes = plt.subplots(rows, 2, figsize=(11, 4 * rows))
    axes = np.array(axes).flatten()
    for i, dim in enumerate(dims):
        axes[i].plot(era_order, scores[dim], "o-", lw=2, color="tab:purple")
        axes[i].set_title(dim, fontsize=11)
        axes[i].tick_params(axis="x", labelrotation=25)
        axes[i].grid(alpha=0.3)
    for j in range(len(dims), len(axes)):
        axes[j].axis("off")
    fig.suptitle(title, fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(config.OUTPUT_DIR, name), dpi=130)
    plt.close(fig)
    print("saved", os.path.join("outputs", name))


def save_named_space(xs, ys, era_order, xlabel, ylabel, title, name):
    colours = _colours(len(era_order))
    plt.figure(figsize=(8.5, 7))
    for i, era in enumerate(era_order):
        plt.scatter(xs[i], ys[i], s=320, zorder=5, color=colours[i], edgecolor="black")
        plt.annotate(era, (xs[i], ys[i]), fontsize=11, fontweight="bold",
                     xytext=(8, 8), textcoords="offset points")
        if i > 0:
            plt.annotate("", xy=(xs[i], ys[i]), xytext=(xs[i - 1], ys[i - 1]),
                         arrowprops=dict(arrowstyle="->", lw=2, color="gray"))
    plt.axhline(0, color="black", lw=0.6)
    plt.axvline(0, color="black", lw=0.6)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    _save(name)
