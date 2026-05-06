from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_conversation_queue_service, get_db
from app.schemas.webhook import EvolutionWebhookResponse
from app.services.conversation_queue_service import ConversationQueueService
from app.services.evolution_webhook_service import (
    EvolutionWebhookService,
    WebhookAuthError,
    WhatsAppInstanceNotFoundError,
)


router = APIRouter(prefix="/webhooks/evolution", tags=["webhooks"])


@router.post("/{instance_name}", response_model=EvolutionWebhookResponse)
def receive_evolution_webhook(
    instance_name: str,
    payload: dict,
    db: Session = Depends(get_db),
    queue: ConversationQueueService = Depends(get_conversation_queue_service),
    header_secret: str | None = Header(
        default=None, alias="X-Evolution-Webhook-Secret"
    ),
    query_secret: str | None = Query(default=None, alias="webhook_secret"),
):
    try:
        result = EvolutionWebhookService(db=db, queue=queue).handle(
            instance_name=instance_name,
            payload=payload,
            webhook_secret=header_secret or query_secret,
        )
    except WebhookAuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except WhatsAppInstanceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return EvolutionWebhookResponse(**result)
