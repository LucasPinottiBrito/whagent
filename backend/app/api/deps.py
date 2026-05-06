import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import decode_access_token
from app.models import Conversation, User
from app.services.agent_service import AgentService
from app.services.conversation_queue_service import ConversationQueueService
from app.services.evolution_service import EvolutionService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    yield from get_session()


def get_conversation_queue_service() -> ConversationQueueService:
    settings = get_settings()
    return ConversationQueueService.from_url(
        redis_url=settings.redis_url,
        debounce_seconds=settings.agent_debounce_seconds,
    )


def get_agent_service() -> AgentService:
    settings = get_settings()
    return AgentService(
        openai_api_key=settings.openai_api_key,
        model=settings.default_openai_model,
    )


def get_evolution_service() -> EvolutionService:
    settings = get_settings()
    return EvolutionService(
        base_url=settings.evolution_api_base_url,
        api_key=settings.evolution_api_key,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_error
    except jwt.PyJWTError as exc:
        raise credentials_error from exc

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_error
    return user


def require_conversation_access(
    conversation: Conversation, current_user: User
) -> None:
    allowed_roles = {"admin", "manager", "salesperson"}
    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="role not allowed")
    if current_user.store_id and current_user.store_id != conversation.store_id:
        raise HTTPException(status_code=403, detail="conversation belongs to another store")
