from pydantic import BaseModel


class EvolutionWebhookResponse(BaseModel):
    status: str
    conversation_id: str | None = None
    message_id: str | None = None
    scheduled: bool = False
