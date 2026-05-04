import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import decode_access_token
from app.models import User
from app.services.agent_service import AgentService
from app.services.conversation_queue import ConversationQueue
from app.services.evolution_service import EvolutionService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    yield from get_session()


def get_conversation_queue() -> ConversationQueue:
    settings = get_settings()
    return ConversationQueue.from_url(
        settings.redis_url, debounce_seconds=settings.agent_debounce_seconds
    )


def get_agent_service() -> AgentService:
    return AgentService(settings=get_settings())


def get_evolution_service() -> EvolutionService:
    settings = get_settings()
    return EvolutionService(
        base_url=settings.evolution_api_base_url,
        api_key=settings.evolution_api_key,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception
    return user
