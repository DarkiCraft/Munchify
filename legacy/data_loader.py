import random

import pandas as pd
import torch
from faker import Faker
from torch.utils.data import Dataset

from config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    NUM_USERS,
    NUM_ITEMS,
    NUM_INTERACTIONS,
)
from utils import setup_logger

logger = setup_logger(__name__)
fake = Faker()


def generate_synthetic_data():
    """Generates synthetic users, items, and interactions."""
    logger.info("Starting synthetic data generation...")

    # 1. Users
    users = []
    for i in range(NUM_USERS):
        users.append(
            {
                "user_id": i,
                "signup_date": fake.date_between(start_date="-1y", end_date="today"),
            }
        )
    users_df = pd.DataFrame(users)
    users_df.to_csv(RAW_DATA_DIR / "users.csv", index=False)

    # 2. Items (Food/Restaurants)
    cuisines = [
        "Italian",
        "Chinese",
        "Indian",
        "Mexican",
        "American",
        "Japanese",
        "Mediterranean",
    ]

    # Define some specific dishes per cuisine for realism
    dishes = {
        "Italian": [
            "Margherita Pizza",
            "Pasta Carbonara",
            "Lasagna",
            "Risotto",
            "Tiramisu",
        ],
        "Chinese": [
            "Kung Pao Chicken",
            "Sweet and Sour Pork",
            "Dim Sum",
            "Chow Mein",
            "Peking Duck",
        ],
        "Indian": [
            "Butter Chicken",
            "Chicken Biryani",
            "Paneer Tikka",
            "Naan",
            "Samosa",
        ],
        "Mexican": ["Tacos", "Burrito", "Quesadilla", "Guacamole", "Enchiladas"],
        "American": [
            "Cheeseburger",
            "Hot Dog",
            "BBQ Ribs",
            "Fried Chicken",
            "Apple Pie",
        ],
        "Japanese": ["Sushi Roll", "Ramen", "Tempura", "Udon", "Miso Soup"],
        "Mediterranean": ["Falafel", "Hummus", "Gyro", "Greek Salad", "Baklava"],
    }

    # Fake restaurant names
    restaurant_names = [fake.company() + " Kitchen" for _ in range(15)]

    items = []
    for i in range(NUM_ITEMS):
        cuisine = random.choice(cuisines)
        rest_id = random.randint(1, 10)  # Keeping generic ID but mapping to a name

        # Consistent name for ID
        # Let's just assign a random restaurant name from our list to this "ID" (conceptually)
        # To be consistent, let's just use the index rest_id-1
        r_name = (
            restaurant_names[rest_id - 1]
            if rest_id <= len(restaurant_names)
            else "General Food Co."
        )

        items.append(
            {
                "item_id": i,
                "restaurant_id": rest_id,
                "restaurant_name": r_name,
                "item_name": random.choice(dishes[cuisine]),
                "cuisine_type": cuisine,
                "price_range": random.randint(1, 4),  # 1: $, 4: $$$$
                "avg_rating": round(random.uniform(3.0, 5.0), 1),
                "availability": 1,  # Available
            }
        )
    items_df = pd.DataFrame(items)
    items_df.to_csv(RAW_DATA_DIR / "items.csv", index=False)

    # 3. Interactions
    interactions = []
    # Generate some organic patterns
    for _ in range(NUM_INTERACTIONS):
        u = random.randint(0, NUM_USERS - 1)
        i = random.randint(0, NUM_ITEMS - 1)

        # Simulate simple preference: Users might stick to 1-2 cuisines
        # For simplicity, we just use random here, but could be smarter

        interaction_type = random.choices(["click", "order"], weights=[0.7, 0.3])[0]
        timestamp = fake.date_time_between(start_date="-1y", end_date="now")

        interactions.append(
            {
                "user_id": u,
                "item_id": i,
                "interaction_type": interaction_type,
                "timestamp": timestamp,
                "rating": (
                    random.randint(1, 5)
                    if interaction_type == "order" and random.random() > 0.6
                    else None
                ),
            }
        )

    interactions_df = pd.DataFrame(interactions)
    interactions_df["weight"] = interactions_df["interaction_type"].apply(
        lambda x: 3.0 if x == "order" else 1.0
    )

    # Add rating bonus
    interactions_df["weight"] = interactions_df.apply(
        lambda x: (
            x["weight"] + (x["rating"] - 3.0) * 0.5
            if pd.notnull(x["rating"])
            else x["weight"]
        ),
        axis=1,
    )

    interactions_df.to_csv(RAW_DATA_DIR / "interactions.csv", index=False)
    logger.info("Data generation complete.")
    return users_df, items_df, interactions_df


class InteractionDataset(Dataset):
    def __init__(self, data):
        self.users = torch.tensor(data["user_id"].values, dtype=torch.long)
        self.items = torch.tensor(data["item_id"].values, dtype=torch.long)
        self.labels = torch.tensor(data["weight"].values, dtype=torch.float32)

    def __len__(self):
        return len(self.users)

    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.labels[idx]


def load_data():
    """Loads data, generating it if it doesn't exist."""
    u_path = RAW_DATA_DIR / "users.csv"
    i_path = RAW_DATA_DIR / "items.csv"
    int_path = RAW_DATA_DIR / "interactions.csv"

    if not (u_path.exists() and i_path.exists() and int_path.exists()):
        users, items, interactions = generate_synthetic_data()
    else:
        logger.info("Loading existing data...")
        users = pd.read_csv(u_path)
        items = pd.read_csv(i_path)
        interactions = pd.read_csv(int_path)

    return users, items, interactions


def get_interaction_dataset(interactions_df):
    """
    Gets InteractionDataset with Negative Sampling.
    Implements Hard Negative Sampling heuristic:
    - Mix of Random Negatives
    - Mix of "Hard" Negatives (Items in user's preferred cuisines but not interacted)
    """
    logger.info("Generating Training Data with Negative Sampling...")

    # 1. Identify Positives
    # Set of (u, i) tuples
    positives = set(zip(interactions_df["user_id"], interactions_df["item_id"]))
    all_items = set(range(NUM_ITEMS))

    # 2. User Profiles for Hard Negatives
    # Map User -> Visited Cuisines (to find items in same cuisine they missed)
    # We need items_df for this. We'll load it.
    from data_loader import load_data  # Circular import avoidance

    _, items_df, _ = load_data()
    item_to_cuisine = items_df.set_index("item_id")["cuisine_type"].to_dict()
    cuisine_to_items = items_df.groupby("cuisine_type")["item_id"].apply(list).to_dict()

    user_cuisines = (
        interactions_df.merge(items_df, on="item_id")
        .groupby("user_id")["cuisine_type"]
        .apply(set)
        .to_dict()
    )

    training_data = []

    # Add Positives
    for _, row in interactions_df.iterrows():
        training_data.append(
            {
                "user_id": row["user_id"],
                "item_id": row["item_id"],
                "weight": row["weight"],  # High weight for positives
            }
        )

        # Add Negatives (Ratio 1:4)
        u_id = row["user_id"]

        # 3 Random Negatives
        for _ in range(3):
            # Try 10 times to find a true negative
            for _ in range(10):
                neg_item = random.randint(0, NUM_ITEMS - 1)
                if (u_id, neg_item) not in positives:
                    training_data.append(
                        {
                            "user_id": u_id,
                            "item_id": neg_item,
                            "weight": 0.0,  # Zero weight for negatives
                        }
                    )
                    break

        # 1 "Hard" Negative (Same Schema/Cuisine but not clicked)
        # If user likes Italian, pick an unclicked Italian item.
        if u_id in user_cuisines:
            fav_cuisines = list(user_cuisines[u_id])
            if fav_cuisines:
                target_c = random.choice(fav_cuisines)
                candidates = cuisine_to_items.get(target_c, [])
                for _ in range(5):
                    if not candidates:
                        break
                    neg_item = random.choice(candidates)
                    if (u_id, neg_item) not in positives:
                        training_data.append(
                            {
                                "user_id": u_id,
                                "item_id": neg_item,
                                "weight": 0.1,  # Small non-zero weight for "hard" negatives? Or 0?
                                # Usually 0, but maybe 0.1 implies "close miss". Let's use 0 for BCELoss.
                            }
                        )
                        break

    train_df = pd.DataFrame(training_data)
    dataset = InteractionDataset(train_df)

    cache_path = PROCESSED_DATA_DIR / "dataset.pt"
    torch.save(dataset, cache_path)
    logger.info(
        f"Generated {len(train_df)} training samples (Pos+Neg). Saved to {cache_path}"
    )

    return dataset
