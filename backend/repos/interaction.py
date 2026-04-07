from datetime import datetime

from sqlalchemy.orm import Session

from models.interaction import InteractionModel, InteractionType


class InteractionRepo:
    def __init__(self, db: Session):
        self.__db = db

    def create(self, interaction: InteractionModel):
        self.__db.add(interaction)
        self.__db.commit()
        self.__db.refresh(interaction)
        return interaction

    def get_all(self):
        return self.__db.query(InteractionModel).all()

    def get_by_id(self, interaction_id: int):
        return self.__db.get(InteractionModel, interaction_id)

    def get_by_user(self, user_id: int):
        return self.__db.query(InteractionModel).filter(InteractionModel.user_id == user_id).all()

    def get_by_item(self, item_id: int):
        return self.__db.query(InteractionModel).filter(InteractionModel.item_id == item_id).all()

    def get_by_user_item(self, user_id: int, item_id: int):
        return self.__db.query(InteractionModel).filter(
            InteractionModel.user_id == user_id,
            InteractionModel.item_id == item_id,
        ).all()

    def get_by_type(self, interaction_type: InteractionType):
        return (self.__db.query(InteractionModel).filter(
            InteractionModel.interaction_type == interaction_type
        ).all())

    def get_by_timeframe(self, start_time: datetime = None, end_time: datetime = None):
        start = start_time or datetime(2000, 1, 1)
        end = end_time or datetime.now()

        return self.__db.query(InteractionModel).filter(
            InteractionModel.timestamp >= start,
            InteractionModel.timestamp <= end
        ).all()
