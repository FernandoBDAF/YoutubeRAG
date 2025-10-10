from typing import List

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer


class HashingEmbedder:
    def __init__(self, n_features: int = 1024) -> None:
        self.n_features = int(n_features)
        # alternate_sign=False to keep values non-negative (optional)
        self.vectorizer = HashingVectorizer(
            n_features=self.n_features,
            alternate_sign=False,
            norm="l2",
            stop_words="english",
        )

    def embed(self, text: str) -> List[float]:
        mat = self.vectorizer.transform([text])  # sparse row
        dense = mat.toarray()[0]
        return dense.astype(float).tolist()

