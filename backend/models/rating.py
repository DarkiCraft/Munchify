from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class RatingModel(Base):
    __tablename__ = "ratings"

    rating_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"), unique=True)
    timestamp: Mapped[datetime] = mapped_column()
    rating: Mapped[int] = mapped_column()
