from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ItemCategory(Base):
    __tablename__ = "item_categories"

    item_id: Mapped[str] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True, index=True
    )

    __table_args__ = (
        UniqueConstraint("item_id", "category_id", name="uq_item_category"),
    )

    def __repr__(self):
        return f"<ItemCategory item={self.item_id} cat={self.category_id}>"