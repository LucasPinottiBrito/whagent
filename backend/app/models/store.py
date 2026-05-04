from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import IdMixin, TimestampMixin


class Store(IdMixin, TimestampMixin, Base):
    __tablename__ = "stores"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    document: Mapped[str | None] = mapped_column(String(40), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)

    users = relationship("User", back_populates="store")
    whatsapp_instances = relationship("WhatsAppInstance", back_populates="store")
    customers = relationship("Customer", back_populates="store")
    conversations = relationship("Conversation", back_populates="store")
    salespeople = relationship("Salesperson", back_populates="store")
