import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Box(Base):
    __tablename__ = "boxes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    status: Mapped[str] = mapped_column(String(20), default="unidentified", index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=True, index=True
    )
    upload_session_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    location: Mapped["Location"] = relationship("Location", back_populates="boxes", lazy="selectin")
    photos: Mapped[list["BoxPhoto"]] = relationship(
        "BoxPhoto", back_populates="box", lazy="selectin",
        cascade="all, delete-orphan", order_by="BoxPhoto.sort_order"
    )
    items: Mapped[list["Item"]] = relationship(
        "Item", back_populates="box", lazy="selectin",
        cascade="all, delete-orphan"
    )
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], lazy="selectin")

    def __repr__(self):
        return f"<Box {self.name or 'unnamed'} [{self.status}]>"