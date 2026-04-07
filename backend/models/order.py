from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class OrderModel(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.item_id"))
    timestamp: Mapped[datetime] = mapped_column()
