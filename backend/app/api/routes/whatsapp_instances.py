import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_evolution_service
from app.core.config import get_settings
from app.models import User, WhatsAppInstance
from app.schemas.dashboard import WhatsAppInstanceCreateRequest
from app.services.evolution_service import EvolutionService


router = APIRouter(prefix="/whatsapp-instances", tags=["whatsapp instances"])


@router.get("")
def list_instances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(WhatsAppInstance).order_by(WhatsAppInstance.created_at.desc())
    if current_user.store_id:
        statement = statement.where(WhatsAppInstance.store_id == current_user.store_id)
    instances = list(db.scalars(statement))
    return {"items": [_instance_response(instance) for instance in instances]}


@router.post("")
def create_instance(
    payload: WhatsAppInstanceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    if not current_user.store_id:
        raise HTTPException(status_code=403, detail="user has no store")
    instance_name = payload.instance_name.strip()
    existing = db.scalar(
        select(WhatsAppInstance).where(
            WhatsAppInstance.instance_name == instance_name
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="instance already exists")

    webhook_secret = payload.webhook_secret or secrets.token_urlsafe(24)
    webhook_url = _webhook_url(instance_name, webhook_secret)
    instance = WhatsAppInstance(
        store_id=current_user.store_id,
        instance_name=instance_name,
        phone=payload.phone,
        webhook_secret=webhook_secret,
        active=True,
    )
    db.add(instance)
    db.flush()

    evolution = evolution_service.create_instance(
        instance_name=instance.instance_name,
        phone=instance.phone,
        webhook_url=webhook_url,
        webhook_secret=instance.webhook_secret,
    )
    instance.evolution_instance_id = _extract_evolution_instance_id(evolution)
    db.commit()
    db.refresh(instance)
    response = _instance_response(instance)
    response["evolution"] = evolution
    response["webhook_url"] = webhook_url
    return response


@router.get("/{instance_id}")
def get_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    instance = _get_instance_for_user(db, instance_id, current_user)
    response = _instance_response(instance)
    response["webhook_url"] = _webhook_url(
        instance.instance_name, instance.webhook_secret
    )
    return response


@router.post("/{instance_id}/connect")
def connect_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    instance = _get_instance_for_user(db, instance_id, current_user)
    return evolution_service.connect_instance(instance.instance_name, instance.phone)


@router.post("/{instance_id}/sync-status")
def sync_status(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    instance = _get_instance_for_user(db, instance_id, current_user)
    result = evolution_service.get_connection_state(instance.instance_name)
    state = _extract_connection_state(result)
    return {"state": state, "evolution": result}


@router.post("/{instance_id}/sync-webhook")
def sync_webhook(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    instance = _get_instance_for_user(db, instance_id, current_user)
    return evolution_service.configure_webhook(
        instance_name=instance.instance_name,
        webhook_url=_webhook_url(instance.instance_name, instance.webhook_secret),
        webhook_secret=instance.webhook_secret,
    )


@router.post("/{instance_id}/restart")
def restart_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    instance = _get_instance_for_user(db, instance_id, current_user)
    instance.active = True
    result = evolution_service.restart_instance(instance.instance_name)
    db.commit()
    return result


@router.post("/{instance_id}/logout")
def logout_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    instance = _get_instance_for_user(db, instance_id, current_user)
    result = evolution_service.logout_instance(instance.instance_name)
    instance.active = False
    db.commit()
    return result


def _get_instance_for_user(
    db: Session, instance_id: str, current_user: User
) -> WhatsAppInstance:
    instance = db.get(WhatsAppInstance, instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail="instance not found")
    if current_user.store_id and instance.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="instance belongs to another store")
    return instance


def _instance_response(instance: WhatsAppInstance) -> dict:
    return {
        "id": instance.id,
        "store_id": instance.store_id,
        "instance_name": instance.instance_name,
        "phone": instance.phone,
        "evolution_instance_id": instance.evolution_instance_id,
        "active": instance.active,
        "created_at": instance.created_at,
        "updated_at": instance.updated_at,
    }


def _webhook_url(instance_name: str, webhook_secret: str) -> str:
    settings = get_settings()
    base_url = settings.webhook_public_base_url.rstrip("/")
    return (
        f"{base_url}/api/webhooks/evolution/{instance_name}"
        f"?webhook_secret={webhook_secret}"
    )


def _extract_evolution_instance_id(payload: dict) -> str | None:
    instance = payload.get("instance") if isinstance(payload, dict) else None
    if isinstance(instance, dict):
        return instance.get("instanceId") or instance.get("id")
    return None


def _extract_connection_state(payload: dict) -> str | None:
    instance = payload.get("instance") if isinstance(payload, dict) else None
    if isinstance(instance, dict):
        return instance.get("state") or instance.get("connectionStatus")
    return payload.get("state") if isinstance(payload, dict) else None
