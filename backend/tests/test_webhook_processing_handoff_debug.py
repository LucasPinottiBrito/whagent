from sqlalchemy import select

from app.models import AgentRun, Conversation, HandoffEvent, Lead, Message
from conftest import make_conversation


def inbound_payload(text: str = "Oi", message_id: str = "msg-1"):
    return {
        "event": "MESSAGES_UPSERT",
        "data": {
            "key": {
                "id": message_id,
                "remoteJid": "5511977776666@s.whatsapp.net",
                "fromMe": False,
            },
            "pushName": "Cliente Teste",
            "message": {"conversation": text},
        },
    }


def test_webhook_requires_valid_secret(client, demo_data):
    response = client.post(
        "/api/webhooks/evolution/demo-instance",
        json=inbound_payload(),
        headers={"X-Evolution-Webhook-Secret": "wrong"},
    )

    assert response.status_code == 401


def test_webhook_creates_customer_conversation_message_and_schedules(
    client, db_session, demo_data, fake_queue
):
    response = client.post(
        "/api/webhooks/evolution/demo-instance?webhook_secret=secret-123",
        json=inbound_payload("Quero um Corolla"),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "scheduled"
    conversation = db_session.scalar(select(Conversation))
    message = db_session.scalar(select(Message))
    assert conversation.pending_agent_processing is True
    assert message.direction == "inbound"
    assert message.sender_type == "customer"
    assert fake_queue.scheduled == [conversation.id]


def test_webhook_deduplicates_evolution_message_id(client, db_session, demo_data):
    for _ in range(2):
        response = client.post(
            "/api/webhooks/evolution/demo-instance?webhook_secret=secret-123",
            json=inbound_payload("Duplicada", message_id="same-id"),
        )
        assert response.status_code == 200

    assert db_session.query(Message).count() == 1


def test_webhook_agent_echo_is_ignored_without_handoff(client, db_session, demo_data):
    payload = inbound_payload("Eco", message_id="echo-1")
    payload["data"]["key"]["fromMe"] = True
    payload["data"]["source"] = "agent"

    response = client.post(
        "/api/webhooks/evolution/demo-instance?webhook_secret=secret-123",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ignored_agent_echo"
    assert db_session.query(HandoffEvent).count() == 0


def test_webhook_from_me_human_message_triggers_takeover(client, db_session, demo_data):
    payload = inbound_payload("Eu assumo", message_id="manual-1")
    payload["data"]["key"]["fromMe"] = True

    response = client.post(
        "/api/webhooks/evolution/demo-instance?webhook_secret=secret-123",
        json=payload,
    )

    assert response.status_code == 200
    conversation = db_session.scalar(select(Conversation))
    handoff = db_session.scalar(select(HandoffEvent))
    message = db_session.scalar(select(Message))
    assert conversation.status == "human_active"
    assert conversation.ai_enabled is False
    assert handoff.event_type == "manual_from_me"
    assert message.sender_type == "human"


def test_internal_processing_groups_pending_messages_and_updates_lead(
    client, db_session, demo_data, fake_agent, fake_evolution
):
    conversation = make_conversation(db_session, demo_data)
    db_session.add_all(
        [
            Message(
                conversation_id=conversation.id,
                direction="inbound",
                sender_type="customer",
                content="Oi",
            ),
            Message(
                conversation_id=conversation.id,
                direction="inbound",
                sender_type="customer",
                content="Quero Corolla ate 120 mil",
            ),
        ]
    )
    db_session.commit()

    response = client.post(
        f"/api/internal/conversations/{conversation.id}/process",
        headers={"X-Internal-Api-Key": "test-internal-key"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert fake_agent.calls[0]["customer_input"] == "Oi\nQuero Corolla ate 120 mil"
    assert fake_evolution.sent[0]["instance_name"] == "demo-instance"
    assert db_session.scalar(select(AgentRun)).status == "success"
    assert db_session.scalar(select(Lead)).status == "qualified"
    assert db_session.scalars(select(Message).where(Message.direction == "outbound")).one()
    db_session.refresh(conversation)
    assert conversation.pending_agent_processing is False
    assert conversation.last_agent_processed_message_id is not None


def test_internal_processing_skips_without_ai_or_pending_messages(
    client, db_session, demo_data
):
    conversation = make_conversation(
        db_session, demo_data, status="human_active", ai_enabled=False
    )

    response = client.post(
        f"/api/internal/conversations/{conversation.id}/process",
        headers={"X-Internal-Api-Key": "test-internal-key"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "skipped"


def test_internal_processing_records_agent_error(
    client, db_session, demo_data, fake_agent
):
    fake_agent.fail = True
    conversation = make_conversation(db_session, demo_data)
    db_session.add(
        Message(
            conversation_id=conversation.id,
            direction="inbound",
            sender_type="customer",
            content="Oi",
        )
    )
    db_session.commit()

    response = client.post(
        f"/api/internal/conversations/{conversation.id}/process",
        headers={"X-Internal-Api-Key": "test-internal-key"},
    )

    assert response.status_code == 500
    db_session.refresh(conversation)
    assert "agent exploded" in conversation.last_processing_error
    assert db_session.scalar(select(AgentRun)).status == "error"


def test_takeover_release_require_auth_and_record_events(
    client, db_session, demo_data, auth_header
):
    conversation = make_conversation(db_session, demo_data)

    unauthenticated = client.post(f"/api/conversations/{conversation.id}/takeover")
    assert unauthenticated.status_code == 401

    takeover = client.post(
        f"/api/conversations/{conversation.id}/takeover",
        json={"reason": "Cliente pediu humano"},
        headers=auth_header,
    )
    assert takeover.status_code == 200
    db_session.refresh(conversation)
    assert conversation.status == "human_active"

    release = client.post(
        f"/api/conversations/{conversation.id}/release-to-ai",
        headers=auth_header,
    )
    assert release.status_code == 200
    db_session.refresh(conversation)
    assert conversation.status == "ai_active"
    assert db_session.query(HandoffEvent).count() == 2


def test_debug_simulate_inbound_can_process_now(client, db_session, demo_data):
    response = client.post(
        "/api/debug/evolution/simulate-inbound",
        json={
            "instance_name": "demo-instance",
            "webhook_secret": "secret-123",
            "phone": "5511977776666",
            "text": "Quero um Civic",
            "process_now": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["processing"]["status"] == "processed"
    assert db_session.query(Message).count() == 2
