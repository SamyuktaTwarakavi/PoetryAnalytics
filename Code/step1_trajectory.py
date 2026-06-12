# step1_trajectory.py -- turn poems into vectors and draw the era journey.
# Run:  python step1_trajectory.py

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

from corpus import poems, era_order
import tools

# each poem -> a vector of word weights
X = TfidfVectorizer(stop_words="english", max_features=5000).fit_transform(
    [p["text"] for p in poems]).toarray()

# the centre of each era
centroids = {}
for era in era_order:
    rows = [i for i in range(len(poems)) if poems[i]["era"] == era]
    centroids[era] = X[rows].mean(axis=0)

# how far did poetry move between eras?
print("\nmovement between eras")
for i in range(len(era_order) - 1):
    d = tools.cosine_distance(centroids[era_order[i]], centroids[era_order[i + 1]])
    print(f"  {era_order[i]} -> {era_order[i + 1]}: {d:.3f}")

# squish to 2D and draw the journey
pca = PCA(n_components=2).fit(X)
tools.save_journey(
    pca.transform(X),
    [p["era"] for p in poems],
    pca.transform(np.array([centroids[e] for e in era_order])),
    era_order,
    "Journey through word space (TF-IDF + PCA)",
    "step1_trajectory.png",
)
