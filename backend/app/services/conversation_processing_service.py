from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AgentRun, Conversation, Lead, Message
from app.services.agent_service import AgentResult, AgentService
from app.services.evolution_service import EvolutionService
from app.services.runtime_state import runtime_state


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

        if not runtime_state.ai_runtime_enabled:
            conversation.pending_agent_processing = False
            self.db.commit()
            return {"status": "skipped", "reason": "ai_runtime_disabled"}
        if not conversation.ai_enabled or conversation.status != "ai_active":
            conversation.pending_agent_processing = False
            self.db.commit()
            return {"status": "skipped", "reason": "ai_disabled_or_not_active"}

        pending_messages = self._pending_inbound_messages(conversation)
        if not pending_messages:
            conversation.pending_agent_processing = False
            self.db.commit()
            return {"status": "skipped", "reason": "no_pending_messages"}

        input_text = "\n".join(message.content for message in pending_messages)
        last_message = pending_messages[-1]
        agent_run = AgentRun(
            conversation_id=conversation.id,
            input_text=input_text,
            status="running",
        )
        self.db.add(agent_run)
        self.db.flush()

        try:
            result = self.agent_service.run(
                customer_input=input_text,
                context={
                    "store_id": conversation.store_id,
                    "conversation_id": conversation.id,
                    "customer_phone": conversation.customer.phone,
                },
            )
            agent_run.output_text = result.reply_text
            agent_run.model = result.model
            agent_run.tools_used = result.tools_used
            agent_run.raw_response = result.raw_response
            agent_run.status = "success"

            self._upsert_lead(conversation, result)
            outbound = Message(
                conversation_id=conversation.id,
                direction="outbound",
                sender_type="agent",
                content=result.reply_text,
            )
            self.db.add(outbound)
            self.db.flush()

            self.evolution_service.send_text_message(
                conversation.whatsapp_instance.instance_name,
                conversation.customer.phone,
                result.reply_text,
            )

            conversation.last_intent = result.intent
            conversation.last_agent_processed_at = last_message.created_at
            conversation.last_agent_processed_message_id = last_message.id
            conversation.pending_agent_processing = False
            conversation.last_processing_error = None
            self.db.commit()
            return {
                "status": "processed",
                "conversation_id": conversation.id,
                "message_count": len(pending_messages),
                "agent_run_id": agent_run.id,
                "outbound_message_id": outbound.id,
            }
        except Exception as exc:
            agent_run.status = "error"
            agent_run.error = str(exc)
            conversation.processing_attempts = (conversation.processing_attempts or 0) + 1
            conversation.last_processing_error = str(exc)
            self.db.commit()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    def _pending_inbound_messages(self, conversation: Conversation) -> list[Message]:
        conditions = [
            Message.conversation_id == conversation.id,
            Message.direction == "inbound",
            Message.sender_type == "customer",
        ]
        marker = None
        if conversation.last_agent_processed_message_id:
            marker = self.db.get(Message, conversation.last_agent_processed_message_id)
        if marker is not None:
            conditions.append(Message.created_at > marker.created_at)
        return list(
            self.db.scalars(
                select(Message).where(*conditions).order_by(Message.created_at, Message.id)
            )
        )

    def _upsert_lead(self, conversation: Conversation, result: AgentResult) -> Lead:
        lead = self.db.scalar(select(Lead).where(Lead.conversation_id == conversation.id))
        if lead is None:
            lead = Lead(
                store_id=conversation.store_id,
                customer_id=conversation.customer_id,
                conversation_id=conversation.id,
                status=result.lead_status or "new",
                score=int(result.score or 0),
            )
            self.db.add(lead)
        lead.status = result.lead_status or lead.status
        lead.score = int(result.score or 0)
        lead.intent = result.intent
        lead.vehicle_interest = result.vehicle_interest
        lead.budget_min = _decimal_or_none(result.budget_min)
        lead.budget_max = _decimal_or_none(result.budget_max)
        lead.payment_type = result.payment_type
        lead.trade_in_vehicle = result.trade_in_vehicle
        lead.interest_summary = result.interest_summary
        self.db.flush()
        return lead


def _decimal_or_none(value) -> Decimal | None:
    if value in (None, ""):
        return None
    return Decimal(str(value))
