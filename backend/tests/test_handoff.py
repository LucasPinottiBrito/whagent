from app.models import Conversation, HandoffEvent


def test_takeover_and_release_to_ai_toggle_conversation_state(
    client, db_session, demo_data
):
    conversation = Conversation(
        store_id=demo_data["store"].id,
        customer_id=demo_data["customer"].id,
        whatsapp_instance_id=demo_data["instance"].id,
        status="ai_active",
        ai_enabled=True,
    )
    db_session.add(conversation)
    db_session.commit()

    takeover_response = client.post(f"/api/conversations/{conversation.id}/takeover")

    assert takeover_response.status_code == 200
    db_session.refresh(conversation)
    assert conversation.ai_enabled is False
    assert conversation.status == "human_active"
    assert db_session.query(HandoffEvent).count() == 1

    release_response = client.post(
        f"/api/conversations/{conversation.id}/release-to-ai"
    )

    assert release_response.status_code == 200
    db_session.refresh(conversation)
    assert conversation.ai_enabled is True
    assert conversation.status == "ai_active"
