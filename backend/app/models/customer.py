from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin


class Customer(IdMixin, TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("store_id", "phone", name="uq_customer_store_phone"),)

    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id"), nullable=False, index=True
    )
    phone: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    store = relationship("Store", back_populates="customers")
    conversations = relationship("Conversation", back_populates="customer")
    leads = relationship("Lead", back_populates="customer")
