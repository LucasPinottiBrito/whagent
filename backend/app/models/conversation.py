from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin


class Conversation(IdMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id"), nullable=False, index=True
    )
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id"), nullable=False, index=True
    )
    whatsapp_instance_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("whatsapp_instances.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="ai_active")
    ai_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    assigned_salesperson_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("salespeople.id"), nullable=True, index=True
    )
    last_intent: Mapped[str | None] = mapped_column(String(120), nullable=True)
    pending_agent_processing: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    last_customer_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_agent_processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    store = relationship("Store", back_populates="conversations")
    customer = relationship("Customer", back_populates="conversations")
    whatsapp_instance = relationship("WhatsAppInstance", back_populates="conversations")
    assigned_salesperson = relationship("Salesperson", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    lead = relationship("Lead", back_populates="conversation", uselist=False)
    handoff_events = relationship("HandoffEvent", back_populates="conversation")
    agent_runs = relationship("AgentRun", back_populates="conversation")
