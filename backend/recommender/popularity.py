from collections import Counter

class PopularityRecommender:
    def __init__(self):
        self._popular_item_ids = []

    def fit(self, interactions: list) -> None:
        counts = Counter(i.item_id for i in interactions)
        self._popular_item_ids = [item_id for item_id, _ in counts.most_common()]

    def recommend(self, k: int = 5) -> list[int]:
        return self._popular_item_ids[:k]