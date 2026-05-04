from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AgentRun, Conversation, Lead, Message
from app.services.agent_service import AgentService, AgentResult
from app.services.evolution_service import EvolutionService
from app.utils.datetime import utcnow


class ConversationProcessingService:
    def __init__(
        self,
        *,
        db: Session,
        agent_service: AgentService,
        evolution_service: EvolutionService,
    ):
        self.db = db
        self.agent_service = agent_service
        self.evolution_service = evolution_service

    def process(self, conversation_id: str) -> dict:
        conversation = self.db.get(Conversation, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="conversation not found")

        if not conversation.ai_enabled or conversation.status != "ai_active":
            conversation.pending_agent_processing = False
            self.db.commit()
            return {"status": "skipped", "reason": "ai_disabled_or_not_active"}

        inbound_messages = self._pending_inbound_messages(conversation)
        if not inbound_messages:
            conversation.pending_agent_processing = False
            self.db.commit()
            return {"status": "skipped", "reason": "no_pending_messages"}

        customer_input = "\n".join(message.content for message in inbound_messages)
        conversation.processing_attempts = (conversation.processing_attempts or 0) + 1

        try:
            agent_result = self.agent_service.run(
                conversation=conversation, customer_input=customer_input
            )
            agent_run = self._save_agent_run(conversation, customer_input, agent_result)
            self._upsert_lead(conversation, agent_result)
            outbound = self._save_outbound_message(conversation, agent_result.reply_text)
            self.evolution_service.send_text_message(
                conversation.whatsapp_instance.instance_name,
                conversation.customer.phone,
                agent_result.reply_text,
            )

            now = utcnow()
            conversation.last_intent = agent_result.intent
            conversation.last_agent_processed_at = now
            conversation.pending_agent_processing = False
            conversation.last_processing_error = None
            self.db.commit()
            return {
                "status": "processed",
                "conversation_id": conversation.id,
                "message_count": len(inbound_messages),
                "agent_run_id": agent_run.id,
                "outbound_message_id": outbound.id,
            }
        except Exception as exc:
            self.db.rollback()
            conversation = self.db.get(Conversation, conversation_id)
            if conversation is not None:
                conversation.processing_attempts = (
                    conversation.processing_attempts or 0
                ) + 1
                conversation.last_processing_error = str(exc)
                self.db.commit()
            raise

    def _pending_inbound_messages(self, conversation: Conversation) -> list[Message]:
        conditions = [
            Message.conversation_id == conversation.id,
            Message.direction == "inbound",
            Message.sender_type == "customer",
        ]
        if conversation.last_agent_processed_at is not None:
            conditions.append(Message.created_at > conversation.last_agent_processed_at)
        return list(
            self.db.scalars(select(Message).where(*conditions).order_by(Message.created_at))
        )

    def _save_agent_run(
        self,
        conversation: Conversation,
        customer_input: str,
        agent_result: AgentResult,
    ) -> AgentRun:
        settings = get_settings()
        agent_run = AgentRun(
            conversation_id=conversation.id,
            input_text=customer_input,
            output_text=agent_result.reply_text,
            model=settings.default_openai_model,
            tools_used=agent_result.tools_used,
            raw_response=agent_result.raw_response,
            status="succeeded",
        )
        self.db.add(agent_run)
        self.db.flush()
        return agent_run

    def _upsert_lead(
        self, conversation: Conversation, agent_result: AgentResult
    ) -> Lead:
        lead = self.db.scalar(
            select(Lead).where(Lead.conversation_id == conversation.id)
        )
        if lead is None:
            lead = Lead(
                store_id=conversation.store_id,
                customer_id=conversation.customer_id,
                conversation_id=conversation.id,
            )
            self.db.add(lead)
        lead.status = agent_result.lead_status or lead.status
        lead.score = int(agent_result.score or 0)
        lead.intent = agent_result.intent
        lead.vehicle_interest = agent_result.vehicle_interest
        lead.budget_min = _decimal_or_none(agent_result.budget_min)
        lead.budget_max = _decimal_or_none(agent_result.budget_max)
        lead.payment_type = agent_result.payment_type
        lead.trade_in_vehicle = agent_result.trade_in_vehicle
        lead.interest_summary = agent_result.interest_summary
        self.db.flush()
        return lead

    def _save_outbound_message(
        self, conversation: Conversation, reply_text: str
    ) -> Message:
        message = Message(
            conversation_id=conversation.id,
            direction="outbound",
            sender_type="agent",
            content=reply_text,
        )
        self.db.add(message)
        self.db.flush()
        return message


def _decimal_or_none(value) -> Decimal | None:
    if value in (None, ""):
        return None
    return Decimal(str(value))
