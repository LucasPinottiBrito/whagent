from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import Conversation, Customer, Message, WhatsAppInstance
from app.utils.datetime import utcnow


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_customer(
        self, *, store_id: str, phone: str, name: str | None
    ) -> Customer:
        customer = self.db.scalar(
            select(Customer).where(Customer.store_id == store_id, Customer.phone == phone)
        )
        if customer is None:
            customer = Customer(store_id=store_id, phone=phone, name=name)
            self.db.add(customer)
            self.db.flush()
        elif name and not customer.name:
            customer.name = name
        customer.last_seen_at = utcnow()
        return customer

    def get_or_create_conversation(
        self, *, customer: Customer, instance: WhatsAppInstance
    ) -> Conversation:
        conversation = self.db.scalar(
            select(Conversation)
            .where(
                Conversation.store_id == instance.store_id,
                Conversation.customer_id == customer.id,
                Conversation.whatsapp_instance_id == instance.id,
                Conversation.status != "closed",
            )
            .order_by(desc(Conversation.created_at))
        )
        if conversation is None:
            conversation = Conversation(
                store_id=instance.store_id,
                customer_id=customer.id,
                whatsapp_instance_id=instance.id,
                status="ai_active",
                ai_enabled=True,
            )
            self.db.add(conversation)
            self.db.flush()
        return conversation

    def add_message(
        self,
        *,
        conversation: Conversation,
        direction: str,
        sender_type: str,
        content: str,
        evolution_message_id: str | None = None,
        raw_payload: dict | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation.id,
            direction=direction,
            sender_type=sender_type,
            content=content,
            evolution_message_id=evolution_message_id,
            raw_payload=raw_payload,
        )
        self.db.add(message)
        self.db.flush()
        return message
