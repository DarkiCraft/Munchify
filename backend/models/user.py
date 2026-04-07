from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes] = mapped_column()
    signup_date: Mapped[datetime] = mapped_column()
