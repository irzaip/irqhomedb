from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BoxPhoto(Base):
    __tablename__ = "box_photos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    box_id: Mapped[str] = mapped_column(
        ForeignKey("boxes.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    caption: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    box: Mapped["Box"] = relationship("Box", back_populates="photos")

    def __repr__(self):
        return f"<BoxPhoto {self.filename}>"