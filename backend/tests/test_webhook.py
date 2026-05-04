from sqlalchemy import select

from app.models import Conversation, HandoffEvent, Message


def inbound_payload(text: str, message_id: str = "msg-1"):
    return {
        "event": "messages.upsert",
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


def test_evolution_webhook_saves_inbound_message_and_schedules_processing(
    client, db_session, demo_data, fake_queue
):
    response = client.post(
        "/api/webhooks/evolution/demo-instance",
        json=inbound_payload("Oi, quero ver um Corolla"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "scheduled"
    assert body["scheduled"] is True

    message = db_session.scalar(select(Message))
    conversation = db_session.scalar(select(Conversation))

    assert message.direction == "inbound"
    assert message.sender_type == "customer"
    assert message.content == "Oi, quero ver um Corolla"
    assert conversation.pending_agent_processing is True
    assert conversation.last_customer_message_at is not None
    assert fake_queue.scheduled == [conversation.id]


def test_manual_from_me_message_triggers_human_takeover(
    client, db_session, demo_data
):
    payload = inbound_payload("Eu assumo daqui", message_id="manual-1")
    payload["data"]["key"]["fromMe"] = True

    response = client.post("/api/webhooks/evolution/demo-instance", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "human_takeover"

    conversation = db_session.scalar(select(Conversation))
    handoff_event = db_session.scalar(select(HandoffEvent))
    message = db_session.scalar(select(Message))

    assert conversation.ai_enabled is False
    assert conversation.status == "human_active"
    assert handoff_event.event_type == "manual_from_me"
    assert message.direction == "outbound"
    assert message.sender_type == "human"
