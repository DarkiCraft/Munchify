from datetime import datetime

from sqlalchemy.orm import Session

from models.rating import RatingModel


class RatingRepo:
    def __init__(self, db: Session):
        self.__db = db

    def create(self, rating: RatingModel):
        self.__db.add(rating)
        self.__db.commit()
        self.__db.refresh(rating)
        return rating

    def get_all(self):
        return self.__db.query(RatingModel).all()

    def get_by_id(self, rating_id: int):
        return self.__db.get(RatingModel, rating_id)

    def get_by_order(self, order_id: int):
        return self.__db.query(RatingModel).filter(RatingModel.order_id == order_id).first()

    def get_by_timeframe(self, start_time: datetime = None, end_time: datetime = None):
        start = start_time or datetime(2000, 1, 1)
        end = end_time or datetime.now()

        return self.__db.query(RatingModel).filter(
            RatingModel.timestamp >= start,
            RatingModel.timestamp <= end
        ).all()
