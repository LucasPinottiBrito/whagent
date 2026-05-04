from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin


class HandoffEvent(IdMixin, TimestampMixin, Base):
    __tablename__ = "handoff_events"

    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, index=True
    )
    salesperson_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("salespeople.id"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    conversation = relationship("Conversation", back_populates="handoff_events")
    salesperson = relationship("Salesperson", back_populates="handoff_events")
