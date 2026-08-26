from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    icon: Mapped[str] = mapped_column(String(20), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    children: Mapped[list["Category"]] = relationship(
        "Category", backref="parent", remote_side="Category.id", lazy="selectin"
    )

    def __repr__(self):
        return f"<Category {self.name}>"
