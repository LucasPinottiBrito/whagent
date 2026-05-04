from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin


class Salesperson(IdMixin, TimestampMixin, Base):
    __tablename__ = "salespeople"

    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    specialty: Mapped[str | None] = mapped_column(String(80), nullable=True)

    store = relationship("Store", back_populates="salespeople")
    conversations = relationship("Conversation", back_populates="assigned_salesperson")
    handoff_events = relationship("HandoffEvent", back_populates="salesperson")
