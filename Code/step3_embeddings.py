# step3_embeddings.py -- learn the dimensions with word2vec (the real method).
# Run:  python step3_embeddings.py
# Needs a real corpus (run the fetchers + combine.py first).

import numpy as np
from sklearn.decomposition import PCA
from gensim.models import Word2Vec

from corpus import poems, era_order
from poems_data import DIMENSION_SEEDS
import tools

# train word2vec on the poems
model = Word2Vec([p["text"].split() for p in poems], vector_size=50, window=5,
                 min_count=1, sg=1, epochs=50, seed=1, workers=1)
wv = model.wv
print(f"learned vectors for {len(wv.index_to_key)} words")

# each poem -> average of its word vectors
good = []
for p in poems:
    vecs = [wv[w] for w in p["text"].split() if w in wv]
    if vecs:
        p["vec"] = np.mean(vecs, axis=0)
        good.append(p)

# each dimension -> a direction from its word pairs
axes = {}
for dim, pairs in DIMENSION_SEEDS.items():
    diffs = [wv[h] - wv[l] for h, l in pairs if h in wv and l in wv]
    if diffs:
        v = np.mean(diffs, axis=0)
        axes[dim] = v / (np.linalg.norm(v) + 1e-9)

# score each poem on each dimension
for p in good:
    for dim, axis in axes.items():
        p[dim] = tools.cosine(p["vec"], axis)

scores = {d: [tools.era_average(good, e, d) for e in era_order] for d in axes}
tools.save_dimension_lines(era_order, scores,
                           "Learned dimensions across the eras (word2vec)",
                           "step3_dimensions.png")

# the journey through the learned space
centroids = {e: np.mean([p["vec"] for p in good if p["era"] == e], axis=0)
             for e in era_order}
V = np.array([p["vec"] for p in good])
pca = PCA(n_components=2).fit(V)
tools.save_journey(
    pca.transform(V),
    [p["era"] for p in good],
    pca.transform(np.array([centroids[e] for e in era_order])),
    era_order,
    "Journey through learned semantic space (word2vec + PCA)",
    "step3_trajectory.png",
)
