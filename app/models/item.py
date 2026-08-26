import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    status: Mapped[str] = mapped_column(String(20), default="unidentified")
    name: Mapped[str] = mapped_column(String(200), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    box_id: Mapped[str] = mapped_column(ForeignKey("boxes.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    min_quantity: Mapped[int] = mapped_column(Integer, default=0)
    unit: Mapped[str] = mapped_column(String(20), default="pcs")
    tags: Mapped[str] = mapped_column(Text, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    upload_session_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    box: Mapped["Box"] = relationship("Box", back_populates="items", lazy="selectin")
    photos: Mapped[list["ItemPhoto"]] = relationship(
        "ItemPhoto", back_populates="item", lazy="selectin",
        cascade="all, delete-orphan", order_by="ItemPhoto.sort_order"
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category", secondary="item_categories", lazy="selectin"
    )
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], lazy="selectin")

    def __repr__(self):
        return f"<Item {self.name or 'unnamed'} [{self.status}]>"