from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin


class WhatsAppInstance(IdMixin, TimestampMixin, Base):
    __tablename__ = "whatsapp_instances"

    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id"), nullable=False, index=True
    )
    instance_name: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    evolution_instance_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    webhook_secret: Mapped[str] = mapped_column(String(160), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    store = relationship("Store", back_populates="whatsapp_instances")
    conversations = relationship(
        "Conversation", back_populates="whatsapp_instance", passive_deletes=True
    )
