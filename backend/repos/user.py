from sqlalchemy.orm import Session

from models.user import UserModel


class UserRepo:
    def __init__(self, db: Session):
        self.__db = db

    def create(self, user: UserModel) -> UserModel:
        self.__db.add(user)
        self.__db.commit()
        self.__db.refresh(user)
        return user

    def get_all(self):
        return self.__db.query(UserModel).all()

    def get_by_id(self, user_id: int):
        return self.__db.get(UserModel, user_id)

    def get_by_username(self, username: str):
        return self.__db.query(UserModel).filter(UserModel.user_name == username).first()

    def get_by_email(self, email: str):
        return self.__db.query(UserModel).filter(UserModel.email == email).first()
