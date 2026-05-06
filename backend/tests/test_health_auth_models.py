import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import decode_access_token
from app.models import Customer, Message
from conftest import make_conversation


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_and_me_with_valid_token(client, demo_data):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    claims = decode_access_token(token)
    assert claims["role"] == "admin"
    assert claims["store_id"] == demo_data["store"].id

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "admin@example.com"


def test_login_rejects_invalid_or_inactive_user(client, db_session, demo_data):
    bad_password = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "wrong"},
    )
    assert bad_password.status_code == 401

    demo_data["admin"].is_active = False
    db_session.commit()
    inactive = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    assert inactive.status_code == 401


def test_me_requires_token(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_customer_is_unique_per_store_and_phone(db_session, demo_data):
    duplicate = Customer(
        store_id=demo_data["store"].id,
        phone="5511977776666",
        name="Outro Nome",
    )
    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_evolution_message_id_deduplicates_only_when_present(db_session, demo_data):
    conversation = make_conversation(db_session, demo_data)
    first = Message(
        conversation_id=conversation.id,
        direction="inbound",
        sender_type="customer",
        content="Oi",
        evolution_message_id="external-1",
    )
    second = Message(
        conversation_id=conversation.id,
        direction="inbound",
        sender_type="customer",
        content="Duplicada",
        evolution_message_id="external-1",
    )
    db_session.add(first)
    db_session.commit()
    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
    db_session.add_all(
        [
            Message(
                conversation_id=conversation.id,
                direction="inbound",
                sender_type="customer",
                content="Sem id 1",
            ),
            Message(
                conversation_id=conversation.id,
                direction="inbound",
                sender_type="customer",
                content="Sem id 2",
            ),
        ]
    )
    db_session.commit()
    assert len(db_session.scalars(select(Message)).all()) == 3
