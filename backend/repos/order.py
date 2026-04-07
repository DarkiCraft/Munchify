from datetime import datetime

from sqlalchemy.orm import Session

from models.order import OrderModel


class OrderRepo:
    def __init__(self, db: Session):
        self.__db = db

    def create(self, order: OrderModel):
        self.__db.add(order)
        self.__db.commit()
        self.__db.refresh(order)
        return order

    def get_all(self):
        return self.__db.query(OrderModel).all()

    def get_by_id(self, order_id: int):
        return self.__db.get(OrderModel, order_id)

    def get_by_user(self, user_id: int):
        return self.__db.query(OrderModel).filter(OrderModel.user_id == user_id).all()

    def get_by_item(self, item_id: int):
        return self.__db.query(OrderModel).filter(OrderModel.item_id == item_id).all()

    def get_by_user_item(self, user_id: int, item_id: int):
        return self.__db.query(OrderModel).filter(
            OrderModel.user_id == user_id,
            OrderModel.item_id == item_id
        ).all()

    def get_by_timeframe(self, start_time: datetime = None, end_time: datetime = None):
        start = start_time or datetime(2000, 1, 1)
        end = end_time or datetime.now()

        return self.__db.query(OrderModel).filter(
            OrderModel.timestamp >= start,
            OrderModel.timestamp <= end
        ).all()
