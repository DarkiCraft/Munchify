from collections import Counter

class ContentBasedRecommender:
    def __init__(self):
        self._items = []

    def fit(self, items: list) -> None:
        self._items = items

    def recommend(self, interactions: list, k: int = 5) -> list[int]:
        if not interactions:
            return []

        # Find favourite cuisine from interaction history
        item_map = {item.item_id: item for item in self._items}
        cuisine_counts = Counter(
            item_map[i.item_id].cuisine
            for i in interactions
            if i.item_id in item_map
        )

        if not cuisine_counts:
            return []

        favourite_cuisine = cuisine_counts.most_common(1)[0][0]

        matches = [
            item.item_id for item in self._items
            if item.cuisine == favourite_cuisine
        ]

        return matches[:k]