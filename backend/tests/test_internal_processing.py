from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models import Conversation, Lead, Message


def create_conversation_with_messages(db_session, demo_data):
    conversation = Conversation(
        store_id=demo_data["store"].id,
        customer_id=demo_data["customer"].id,
        whatsapp_instance_id=demo_data["instance"].id,
        status="ai_active",
        ai_enabled=True,
        pending_agent_processing=True,
    )
    db_session.add(conversation)
    db_session.flush()
    first = Message(
        conversation_id=conversation.id,
        direction="inbound",
        sender_type="customer",
        content="Oi",
        created_at=datetime.now(timezone.utc) - timedelta(seconds=4),
    )
    second = Message(
        conversation_id=conversation.id,
        direction="inbound",
        sender_type="customer",
        content="Quero um Corolla automatico ate 120 mil",
    )
    db_session.add_all([first, second])
    db_session.commit()
    return conversation


def test_internal_processing_groups_messages_runs_agent_and_sends_reply(
    client, db_session, demo_data, fake_agent, fake_evolution
):
    conversation = create_conversation_with_messages(db_session, demo_data)

    response = client.post(
        f"/api/internal/conversations/{conversation.id}/process",
        headers={"X-Internal-Api-Key": "test-internal-key"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert fake_agent.calls == ["Oi\nQuero um Corolla automatico ate 120 mil"]
    assert fake_evolution.sent[0]["instance_name"] == "demo-instance"
    assert fake_evolution.sent[0]["phone"] == "5511977776666"

    db_session.refresh(conversation)
    outbound = db_session.scalars(
        select(Message).where(Message.direction == "outbound")
    ).one()
    lead = db_session.scalar(select(Lead))

    assert outbound.sender_type == "agent"
    assert "Corolla" in outbound.content
    assert lead.status == "qualified"
    assert lead.score == 82
    assert conversation.pending_agent_processing is False
    assert conversation.last_agent_processed_at is not None


def test_internal_processing_skips_when_ai_disabled(
    client, db_session, demo_data, fake_agent, fake_evolution
):
    conversation = create_conversation_with_messages(db_session, demo_data)
    conversation.ai_enabled = False
    conversation.status = "human_active"
    db_session.commit()

    response = client.post(
        f"/api/internal/conversations/{conversation.id}/process",
        headers={"X-Internal-Api-Key": "test-internal-key"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "skipped"
    assert fake_agent.calls == []
    assert fake_evolution.sent == []
