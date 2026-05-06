from sqlalchemy import JSON, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin


class Message(IdMixin, TimestampMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index(
            "uq_messages_evolution_message_id_not_null",
            "evolution_message_id",
            unique=True,
            sqlite_where=text("evolution_message_id IS NOT NULL"),
            postgresql_where=text("evolution_message_id IS NOT NULL"),
        ),
    )

    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, index=True
    )
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    evolution_message_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
