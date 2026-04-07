from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class InteractionType(Enum):
    CLICK = "click"
    ORDER = "order"


class InteractionModel(Base):
    __tablename__ = "interactions"

    interaction_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.item_id"))
    interaction_type: Mapped[InteractionType] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column()
