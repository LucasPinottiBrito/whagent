from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_agent_service, get_db, get_evolution_service
from app.core.config import get_settings
from app.services.agent_service import AgentService
from app.services.conversation_processing_service import ConversationProcessingService
from app.services.evolution_service import EvolutionService


router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/conversations/{conversation_id}/process")
def process_conversation(
    conversation_id: str,
    x_internal_api_key: str | None = Header(default=None, alias="X-Internal-Api-Key"),
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    if x_internal_api_key != get_settings().internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid internal api key",
        )
    return ConversationProcessingService(
        db=db,
        agent_service=agent_service,
        evolution_service=evolution_service,
    ).process(conversation_id)
