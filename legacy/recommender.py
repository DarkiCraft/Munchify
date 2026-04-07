import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from models.baseline import PopularityRecommender, ContentBasedRecommender
from models.ncf import NCFModel, train_ncf
from config import (
    EMBEDDING_DIM,
    EPOCHS,
    LEARNING_RATE,
    NUM_USERS,
    NUM_ITEMS,
    PROCESSED_DATA_DIR,
    MODELS_DIR,
    RAW_DATA_DIR,
)
from data_loader import load_data
from utils import setup_logger

logger = setup_logger(__name__)


class RecommendationService:
    def __init__(self):
        # Ensure raw data dir exists
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.users_df, self.items_df, self.interactions_df = load_data()

        self.ncf_model = NCFModel(NUM_USERS, NUM_ITEMS, embedding_dim=EMBEDDING_DIM)
        self.pop_model = PopularityRecommender()
        self.cb_model = ContentBasedRecommender()

        # Load or Train (For prototype, we train on startup to keep it simple,
        # or load if exists - let's train for now as it's fast on small data)
        self._train_models()

    def reset_data(self):
        """Clears all interaction data."""
        logger.info("Resetting interaction data...")
        self.interactions_df = pd.DataFrame(
            columns=[
                "user_id",
                "item_id",
                "interaction_type",
                "timestamp",
                "rating",
                "weight",
            ]
        )

        # Clear file
        if (RAW_DATA_DIR / "interactions.csv").exists():
            # Keep header
            self.interactions_df.to_csv(RAW_DATA_DIR / "interactions.csv", index=False)

        # Clear processed
        if (PROCESSED_DATA_DIR / "dataset.pt").exists():
            (PROCESSED_DATA_DIR / "dataset.pt").unlink()

        logger.info("Data reset complete.")

    def retrain_model(self):
        """Triggers a full retraining of the model."""
        self._train_models(force_retrain=True)

    def _train_models(self, force_retrain=False):
        logger.info("Training models...")

        # Baseline (Fit on all for popularity/content as they are heuristic based,
        # but for proper ML evaluation we should use train set.
        # For this prototype, we'll fit baselines on ALL but NCF on TRAIN to demonstrate metrics validation)

        # Split Data for NCF Evaluation
        # Stratified split by user to ensure every user is in both sets if possible
        train_df, test_df = train_test_split(
            self.interactions_df,
            test_size=0.2,
            random_state=42,
            stratify=self.interactions_df["user_id"],
        )
        self.test_df = test_df  # Save for evaluation

        # Fit Baselines (Fast)
        self.pop_model.fit(train_df, self.items_df)
        self.cb_model.fit(self.items_df)  # Items don't change

        # NCF Training or Loading
        model_path = MODELS_DIR / "ncf_model.pth"

        if model_path.exists() and not force_retrain:
            logger.info(f"Loading saved model from {model_path}...")
            # Load state dict
            self.ncf_model.load_state_dict(torch.load(model_path))
            self.ncf_model.eval()  # Set to eval mode by default
            logger.info("Model loaded successfully.")
        else:
            logger.info("No saved model found. Training NCF...")
            from data_loader import get_interaction_dataset

            dataset = get_interaction_dataset(train_df)
            train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
            self.ncf_model = train_ncf(
                self.ncf_model, train_loader, epochs=EPOCHS, lr=LEARNING_RATE
            )

            # Save model
            torch.save(self.ncf_model.state_dict(), model_path)
            logger.info(f"Model saved to {model_path}")

        logger.info("Initialization/Training complete.")

    def get_recommendations(self, user_id, strategy="personalized", k=5):
        """
        Strategies: 'personalized' (NCF), 'popularity', 'content'
        """
        logger.info(f"Generating {strategy} recommendations for user {user_id}")

        if strategy == "popularity":
            recs = self.pop_model.recommend(k)
            return recs

        elif strategy == "content":
            # Identify user's favorite cuisine from history
            user_history = self.interactions_df[
                self.interactions_df["user_id"] == user_id
                ]
            if user_history.empty:
                # Fallback to popularity
                return self.pop_model.recommend(k)

            # Most frequent cuisine
            # Join with items to get cuisine
            history_details = user_history.merge(self.items_df, on="item_id")
            if history_details.empty:
                return self.pop_model.recommend(k)

            fav_cuisine = history_details["cuisine_type"].mode()[0]
            return self.cb_model.recommend(fav_cuisine, k)

        else:  # personalized (NCF)
            # Predict score for ALL items for this user
            self.ncf_model.eval()
            all_item_ids = torch.arange(NUM_ITEMS)
            user_tensor = torch.full((NUM_ITEMS,), user_id, dtype=torch.long)

            with torch.no_grad():
                predictions = self.ncf_model(user_tensor, all_item_ids)

            # Get top K*3 indices for diversification
            k_candidates = k * 3
            _, top_indices = torch.topk(predictions, k_candidates)
            candidate_ids = top_indices.numpy()

            # Fetch item details for candidates
            candidates_df = self.items_df[self.items_df["item_id"].isin(candidate_ids)]
            candidates_df = (
                candidates_df.set_index("item_id").loc[candidate_ids].reset_index()
            )

            # Forced Diversification (Simple Greedy Reranking)
            # Goal: No more than 2 items of same cuisine in Top 5 (if possible)
            final_recs = []
            cuisine_counts = {}
            max_per_cuisine = 2

            for _, item in candidates_df.iterrows():
                if len(final_recs) >= k:
                    break

                c = item["cuisine_type"]
                if cuisine_counts.get(c, 0) < max_per_cuisine:
                    final_recs.append(item)
                    cuisine_counts[c] = cuisine_counts.get(c, 0) + 1

            # Fallback if too strict (not enough unique cuisines)
            if len(final_recs) < k:
                remaining_k = k - len(final_recs)
                # Add remaining top candidates that weren't picked
                current_ids = {x["item_id"] for x in final_recs}
                for _, item in candidates_df.iterrows():
                    if len(final_recs) >= k:
                        break
                    if item["item_id"] not in current_ids:
                        final_recs.append(item)

            return pd.DataFrame(final_recs)

    def log_interaction(self, user_id, item_id, interaction_type, rating=None):
        logger.info(
            f"Logging interaction: User {user_id} -> Item {item_id} ({interaction_type})"
        )
        # In a real system, append to DB. Here we just log and maybe update DF temporarily
        new_row = {
            "user_id": user_id,
            "item_id": item_id,
            "interaction_type": interaction_type,
            "timestamp": pd.Timestamp.now(),
            "rating": rating,
            "weight": 3.0 if interaction_type == "order" else 1.0,
        }
        # Append to dataframe (inefficient but works for memory-only prototype)
        # Append to dataframe
        self.interactions_df = pd.concat(
            [self.interactions_df, pd.DataFrame([new_row])], ignore_index=True
        )

        # Persist to disk
        from config import RAW_DATA_DIR

        # Append mode 'a', header=False if file exists
        csv_path = RAW_DATA_DIR / "interactions.csv"
        pd.DataFrame([new_row]).to_csv(
            csv_path, mode="a", header=not csv_path.exists(), index=False
        )
        logger.info(f"Interaction persisted to {csv_path}")

    def get_system_stats(self):
        """Calculates RS-adjacent statistics for the Admin Dashboard."""
        stats = {}

        # 1. System Health
        # Use simple max to estimate, or union if we had user table updates.
        # For now, unique IDs in interactions + known users is safest.

        # Calculate actual dimensionality
        unique_users = set(self.users_df["user_id"].unique()) | set(
            self.interactions_df["user_id"].unique()
        )
        unique_items = set(self.items_df["item_id"].unique()) | set(
            self.interactions_df["item_id"].unique()
        )
        unique_interactions = self.interactions_df[
            ["user_id", "item_id"]
        ].drop_duplicates()

        num_users = len(unique_users)
        num_items = len(unique_items)
        total_interactions = len(unique_interactions)

        # Sparsity
        possible_interactions = num_users * num_items
        sparsity = (
            1.0 - (total_interactions / possible_interactions)
            if possible_interactions > 0
            else 0
        )
        stats["sparsity"] = sparsity

        # Catalog Coverage
        interacted_items = self.interactions_df["item_id"].nunique()
        catalog_coverage = interacted_items / num_items if num_items > 0 else 0
        stats["catalog_coverage"] = catalog_coverage

        # Interaction Distribution
        stats["interaction_distribution"] = (
            self.interactions_df["interaction_type"].value_counts().to_dict()
        )

        # 2. User Stats
        user_activity = self.interactions_df["user_id"].value_counts()
        stats["active_users"] = len(user_activity)
        stats["avg_interactions_per_user"] = user_activity.mean()

        return stats

    def calculate_metrics(self, k=5):
        """
        Calculates Precision, Recall, Accuracy (Hit Rate), F-measure, MAP@k, MAR@k
        on the test set.
        """
        logger.info("Calculating evaluation metrics...")

        # We need to generate Top-K recs for all users in test set
        test_users = self.test_df["user_id"].unique()

        precisions = []
        recalls = []
        average_precisions = []
        average_recalls = []
        hits = 0
        total_cases = 0

        # Pre-compute test items for faster lookup
        test_user_items = (
            self.test_df.groupby("user_id")["item_id"].apply(set).to_dict()
        )

        self.ncf_model.eval()

        # Optimization: Batch prediction could be faster but looping is fine for small N
        with torch.no_grad():
            for user_id in test_users:
                if user_id not in test_user_items:
                    continue

                actual_items = test_user_items[user_id]
                if not actual_items:
                    continue

                # Predict (using NCF logic directly to avoid overhead)
                all_item_ids = torch.arange(NUM_ITEMS)
                user_tensor = torch.full((NUM_ITEMS,), user_id, dtype=torch.long)
                predictions = self.ncf_model(user_tensor, all_item_ids)
                _, top_indices = torch.topk(predictions, k)
                train_recs = top_indices.numpy()

                # Metrics Calculation
                hits_k = len(set(train_recs) & actual_items)

                # Precision: TP / K
                p_k = hits_k / k
                precisions.append(p_k)

                # Recall: TP / len(Relevant)
                r_k = hits_k / len(actual_items)
                recalls.append(r_k)

                # F-measure (per user)
                if p_k + r_k > 0:
                    f1 = 2 * (p_k * r_k) / (p_k + r_k)
                else:
                    f1 = 0

                # MAP@K Calculation
                # Avg Precision for this user
                score = 0.0
                num_hits = 0.0
                for i, p in enumerate(train_recs):
                    if p in actual_items:
                        num_hits += 1.0
                        score += num_hits / (i + 1.0)

                ap = score / min(len(actual_items), k)  # Standard AP@K definition
                average_precisions.append(ap)

                # MAR@K Calculation (Mean Average Recall - less standard but requested)
                # Usually Recall@K is sufficient, but let's define AR as Recall at each rank average?
                # Or just use the Recall@K we calculated.
                # User asked for "Mean Average Recall at K".
                # In literature, MAR usually matches Mean Recall. Let's strictly calculate Mean Recall.
                average_recalls.append(r_k)

                # Accuracy (Hit Rate): Did we recommend at least one relevant item?
                if hits_k > 0:
                    hits += 1
                total_cases += 1

        metrics = {
            "precision": np.mean(precisions) if precisions else 0,
            "recall": np.mean(recalls) if recalls else 0,
            "f1": (
                2
                * (np.mean(precisions) * np.mean(recalls))
                / (np.mean(precisions) + np.mean(recalls))
                if (np.mean(precisions) + np.mean(recalls)) > 0
                else 0
            ),
            "accuracy": hits / total_cases if total_cases > 0 else 0,  # Hit Rate
            "map": np.mean(average_precisions) if average_precisions else 0,
            "mar": np.mean(average_recalls) if average_recalls else 0,
        }

        return metrics

    def get_user_stats(self, user_id):
        """Calculates specific stats for a single user."""
        user_history = self.interactions_df[self.interactions_df["user_id"] == user_id]
        if user_history.empty:
            return None

        stats = {}
        # Activity
        stats["total_interactions"] = len(user_history)

        # Cuisine Preference Profile
        # Join with items
        details = user_history.merge(self.items_df, on="item_id")
        if not details.empty:
            stats["top_cuisines"] = (
                details["cuisine_type"].value_counts().head(3).to_dict()
            )
        else:
            stats["top_cuisines"] = {}

        return stats
