class PopularityRecommender:
    def __init__(self):
        self.popular_items = []

    def fit(self, interactions_df, items_df):
        # Count frequency of interactions per item
        item_counts = interactions_df["item_id"].value_counts().reset_index()
        item_counts.columns = ["item_id", "count"]

        # Merge with item details
        self.popular_items = item_counts.merge(items_df, on="item_id").sort_values(
            "count", ascending=False
        )

    def recommend(self, k=5):
        return self.popular_items.head(k)


class ContentBasedRecommender:
    def __init__(self):
        self.items_df = None

    def fit(self, items_df):
        self.items_df = items_df

    def recommend(self, user_preferred_cuisine, k=5):
        # Very simple content filtering: Filter by cuisine, sort by rating
        if self.items_df is None:
            return []

        matches = self.items_df[self.items_df["cuisine_type"] == user_preferred_cuisine]
        if matches.empty:
            return self.items_df.sort_values("avg_rating", ascending=False).head(k)

        return matches.sort_values("avg_rating", ascending=False).head(k)
