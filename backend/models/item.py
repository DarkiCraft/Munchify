from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ItemModel(Base):
    __tablename__ = "items"

    item_id: Mapped[int] = mapped_column(primary_key=True)
    item_name: Mapped[str] = mapped_column()
    cuisine: Mapped[str] = mapped_column()
