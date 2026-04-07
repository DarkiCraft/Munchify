import os
import torch

from recommender.ncf import NCFModel, train_ncf, predict_ncf
from recommender.svd import SVDRecommender
from recommender.popularity import PopularityRecommender
from recommender.content import ContentBasedRecommender
from repos.interaction import InteractionRepo
from repos.item import ItemRepo
from repos.user import UserRepo
from schemas.recommend import RecommendRequest, RecommendResponse

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
NCF_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "ncf_model.pth")

EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 32))
EPOCHS = int(os.getenv("EPOCHS", 5))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", 0.001))
W_NCF = float(os.getenv("W_NCF", 0.5))
W_SVD = float(os.getenv("W_SVD", 0.3))
W_CONTENT = float(os.getenv("W_CONTENT", 0.1))
W_POPULARITY = float(os.getenv("W_POPULARITY", 0.1))


class RecommendationService:
    def __init__(
            self,
            interaction_repo: InteractionRepo,
            item_repo: ItemRepo,
            user_repo: UserRepo
    ):
        self.__interaction_repo = interaction_repo
        self.__item_repo = item_repo
        self.__user_repo = user_repo

        self.__popularity = PopularityRecommender()
        self.__content = ContentBasedRecommender()
        self.__svd = SVDRecommender()
        self.__ncf: NCFModel | None = None

        self.__num_users = 0
        self.__num_items = 0

        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        self.__load_or_train()

    def __load_or_train(self):
        interactions = self.__interaction_repo.get_all()
        items = self.__item_repo.get_all()
        users = self.__user_repo.get_all()

        self.__num_users = len(users)
        self.__num_items = len(items)

        # Fit lightweight models
        self.__popularity.fit(interactions)
        self.__content.fit(items)
        self.__svd.fit(interactions)

        # NCF — load if exists, else train
        self.__ncf = NCFModel(self.__num_users, self.__num_items, EMBEDDING_DIM)
        if os.path.exists(NCF_MODEL_PATH):
            self.__ncf.load_state_dict(torch.load(NCF_MODEL_PATH))
            self.__ncf.eval()
        else:
            self.__train_ncf(interactions)

    def __train_ncf(self, interactions: list):
        self.__ncf = train_ncf(
            self.__ncf,
            interactions,
            self.__num_items,
            epochs=EPOCHS,
            lr=LEARNING_RATE
        )
        torch.save(self.__ncf.state_dict(), NCF_MODEL_PATH)

    def retrain(self):
        interactions = self.__interaction_repo.get_all()
        items = self.__item_repo.get_all()
        users = self.__user_repo.get_all()

        self.__num_users = len(users)
        self.__num_items = len(items)

        self.__popularity.fit(interactions)
        self.__content.fit(items)
        self.__svd.fit(interactions)

        self.__ncf = NCFModel(self.__num_users, self.__num_items, EMBEDDING_DIM)
        self.__train_ncf(interactions)

    def recommend(self, request: RecommendRequest, user_id: int):
        interactions = self.__interaction_repo.get_by_user(user_id)

        # Cold start — no history
        if not interactions:
            return self.__popularity.recommend(request.k)

        all_item_ids = [item.item_id for item in self.__item_repo.get_all()]
        scores = {item_id: 0.0 for item_id in all_item_ids}

        # NCF scores
        if self.__ncf and user_id < self.__num_users:
            ncf_scores = predict_ncf(self.__ncf, user_id, self.__num_items)
            for item_id in all_item_ids:
                if item_id < len(ncf_scores):
                    scores[item_id] += W_NCF * float(ncf_scores[item_id])

        # SVD scores
        svd_recs = self.__svd.recommend(user_id, k=len(all_item_ids))
        for rank, item_id in enumerate(svd_recs):
            if item_id in scores:
                scores[item_id] += W_SVD * (1.0 / (rank + 1))

        # Content boost
        content_recs = self.__content.recommend(interactions, k=len(all_item_ids))
        for rank, item_id in enumerate(content_recs):
            if item_id in scores:
                scores[item_id] += W_CONTENT * (1.0 / (rank + 1))

        # Popularity boost
        pop_recs = self.__popularity.recommend(k=len(all_item_ids))
        for rank, item_id in enumerate(pop_recs):
            if item_id in scores:
                scores[item_id] += W_POPULARITY * (1.0 / (rank + 1))

        # Sort and return top k
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return RecommendResponse(
            recommendations=[item_id for item_id, _ in ranked[:request.k]]
        )