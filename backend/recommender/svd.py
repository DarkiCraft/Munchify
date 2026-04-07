import numpy as np


class SVDRecommender:
    def __init__(self, n_factors: int = 20):
        self._n_factors = n_factors
        self._user_factors = None
        self._item_factors = None
        self._user_index = {}
        self._item_index = {}

    def fit(self, interactions: list) -> None:
        # Build index maps
        user_ids = sorted(set(i.user_id for i in interactions))
        item_ids = sorted(set(i.item_id for i in interactions))

        self._user_index = {uid: idx for idx, uid in enumerate(user_ids)}
        self._item_index = {iid: idx for idx, iid in enumerate(item_ids)}

        # Build user-item matrix
        matrix = np.zeros((len(user_ids), len(item_ids)))
        for i in interactions:
            u = self._user_index[i.user_id]
            it = self._item_index[i.item_id]
            matrix[u][it] += 1.0

        # SVD
        u, sigma, vt = np.linalg.svd(matrix, full_matrices=False)
        k = min(self._n_factors, len(sigma))
        self._user_factors = u[:, :k] * sigma[:k]
        self._item_factors = vt[:k, :].T

    def recommend(self, user_id: int, k: int = 5) -> list[int]:
        if user_id not in self._user_index:
            return []

        u = self._user_index[user_id]
        scores = self._item_factors @ self._user_factors[u]
        top_indices = np.argsort(scores)[::-1][:k]

        index_to_item = {idx: iid for iid, idx in self._item_index.items()}
        return [index_to_item[idx] for idx in top_indices]