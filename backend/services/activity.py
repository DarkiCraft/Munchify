from datetime import datetime

from models.interaction import InteractionModel, InteractionType
from models.order import OrderModel
from models.rating import RatingModel
from repos.interaction import InteractionRepo
from repos.item import ItemRepo
from repos.order import OrderRepo
from repos.rating import RatingRepo
from schemas.activity import ClickRequest, OrderRequest, OrderResponse, RateRequest


class ActivityService:
    def __init__(
            self,
            interaction_repo: InteractionRepo,
            item_repo: ItemRepo,
            order_repo: OrderRepo,
            rating_repo: RatingRepo
    ):
        self.__interaction_repo = interaction_repo
        self.__item_repo = item_repo
        self.__order_repo = order_repo
        self.__rating_repo = rating_repo

    def click(self, request: ClickRequest, user_id: int):
        if self.__item_repo.get_by_id(request.item_id) is None:
            raise ValueError("Item not found")

        self.__interaction_repo.create(
            InteractionModel(
                user_id=user_id,
                item_id=request.item_id,
                interaction_type=InteractionType.CLICK,
                timestamp=datetime.now()
            )
        )

    def order(self, request: OrderRequest, user_id: int):
        if self.__item_repo.get_by_id(request.item_id) is None:
            raise ValueError("Item not found")

        timestamp = datetime.now()

        order = self.__order_repo.create(
            OrderModel(
                user_id=user_id,
                item_id=request.item_id,
                timestamp=timestamp
            )
        )

        self.__interaction_repo.create(
            InteractionModel(
                user_id=user_id,
                item_id=request.item_id,
                interaction_type=InteractionType.ORDER,
                timestamp=timestamp
            )
        )

        return OrderResponse(
            order_id=order.order_id,
            item_id=order.item_id,
            timestamp=order.timestamp
        )

    def rate(self, request: RateRequest, user_id: int):
        order = self.__order_repo.get_by_id(request.order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.user_id != user_id:
            raise ValueError("User not found")

        self.__rating_repo.create(
            RatingModel(
                order_id=order.order_id,
                timestamp=datetime.now(),
                rating=request.rating
            )
        )