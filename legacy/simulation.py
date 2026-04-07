import random

import numpy as np
import pandas as pd

from utils import setup_logger

logger = setup_logger(__name__)


class UserSimulator:
    def __init__(self, items_df):
        self.items_df = items_df
        self.items_df["price_range"] = self.items_df["price_range"].astype(int)

    def generate_persona(self, user_id):
        """
        Creates a latent persona for a user.
        Traits:
        - fav_cuisines: List of cuisines they are likely to click/order.
        - price_sensitivity: 1 (low) to 4 (high). High means avoids expensive.
        - adventurousness: 0.0 to 1.0. Chance to interact with random stuff.
        """
        all_cuisines = self.items_df["cuisine_type"].unique()

        # Pick 1-3 favorite cuisines
        num_favs = random.randint(1, 3)
        fav_cuisines = np.random.choice(all_cuisines, num_favs, replace=False).tolist()

        return {
            "user_id": user_id,
            "fav_cuisines": fav_cuisines,
            "price_sensitivity": random.randint(1, 4),
            "adventurousness": random.uniform(0.1, 0.3),
        }

    def simulate_interaction_probability(self, persona, item):
        """
        Calculates probability of interaction based on persona vs item.
        """
        score = 0.0

        # 1. Cuisine Match (The biggest factor)
        if item["cuisine_type"] in persona["fav_cuisines"]:
            score += 0.6  # Huge boost

        # 2. Price match
        # If user price sensitivity is high (4) and item is expensive (4), penalty.
        # If user is rich (1) and item is expensive (4), no penalty.
        item_price = item["price_range"]
        user_sens = persona["price_sensitivity"]

        if user_sens >= 3 and item_price >= 3:
            score -= 0.3  # Cannot afford / won't pay
        elif user_sens == 1:
            score += 0.1  # Likes premium

        # 3. Random noise / Adventurousness
        if random.random() < persona["adventurousness"]:
            score += 0.2

        return score

    def simulate_session(self, user_id, num_views=20):
        """
        Simulates a user scrolling through 'num_views' random items.
        Returns list of interactions.
        """
        persona = self.generate_persona(user_id)
        interactions = []

        # Pick random items to view
        # In a real sim, this would be the output of a recommender, but for bootstrapping
        # we treat it as "organic discovery" (random feed).
        # Pick random items to view
        # We allow replacement because in food ordering, users often view/order the same things multiple times over time.
        # Also needed if num_views > num_items.
        viewed_items = self.items_df.sample(n=num_views, replace=True)

        for _, item in viewed_items.iterrows():
            prob = self.simulate_interaction_probability(persona, item)

            # Action logic
            # Thresholds
            if prob > 0.4:  # Click
                interactions.append(
                    {
                        "user_id": user_id,
                        "item_id": item["item_id"],
                        "interaction_type": "click",
                        "timestamp": pd.Timestamp.now(),
                        "rating": None,
                        "weight": 1.0,
                    }
                )

                if prob > 0.7:  # Order
                    # Rating logic: Based on item quality + personal match
                    # Base rating is item's avg_rating
                    base_rating = item["avg_rating"]
                    # Add noise based on match
                    personal_rating = min(
                        5, max(1, round(np.random.normal(base_rating, 0.5)))
                    )

                    interactions.append(
                        {
                            "user_id": user_id,
                            "item_id": item["item_id"],
                            "interaction_type": "order",
                            "timestamp": pd.Timestamp.now(),
                            "rating": personal_rating,
                            "weight": 3.0 + (personal_rating - 3) * 0.5,
                        }
                    )

        return interactions


def run_simulation(items_df, num_users=50, views_per_user=30):
    sim = UserSimulator(items_df)
    all_interactions = []

    logger.info(f"Simulating {num_users} users...")
    for uid in range(num_users):
        # We use IDs 1000+ to distinguish from "real" users if needed,
        # but for bootstrapping let's just use 0-N
        ints = sim.simulate_session(uid, num_views=views_per_user)
        all_interactions.extend(ints)

    logger.info(f"Generated {len(all_interactions)} interactions.")
    return pd.DataFrame(all_interactions)
