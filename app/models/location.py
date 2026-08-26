from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=True)
    room: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    children: Mapped[list["Location"]] = relationship(
        "Location", backref="parent", remote_side="Location.id", lazy="selectin"
    )
    photos: Mapped[list["LocationPhoto"]] = relationship(
        "LocationPhoto", back_populates="location", lazy="selectin",
        cascade="all, delete-orphan", order_by="LocationPhoto.sort_order"
    )
    boxes: Mapped[list["Box"]] = relationship(
        "Box", back_populates="location", lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Location {self.name}>"