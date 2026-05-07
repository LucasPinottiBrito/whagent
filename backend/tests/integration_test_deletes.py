from sqlalchemy import text
from sqlalchemy import select

from app.models import AgentRun, Conversation, HandoffEvent, Lead, Message, WhatsAppInstance


def _seed_full_relational_graph(db_session, demo_data):
    db_session.execute(text("PRAGMA foreign_keys=ON"))
    instance = demo_data["instance"]
    store = demo_data["store"]
    customer = demo_data["customer"]
    salesperson = demo_data["salesperson"]

    conv1 = Conversation(
        store_id=store.id,
        customer_id=customer.id,
        whatsapp_instance_id=instance.id,
        status="ai_active",
        ai_enabled=True,
        assigned_salesperson_id=salesperson.id,
    )
    conv2 = Conversation(
        store_id=store.id,
        customer_id=customer.id,
        whatsapp_instance_id=instance.id,
        status="human_active",
        ai_enabled=False,
        assigned_salesperson_id=salesperson.id,
    )
    db_session.add_all([conv1, conv2])
    db_session.flush()

    db_session.add_all(
        [
            Message(
                conversation_id=conv1.id,
                direction="inbound",
                sender_type="customer",
                content="Mensagem conv1",
            ),
            Message(
                conversation_id=conv2.id,
                direction="inbound",
                sender_type="customer",
                content="Mensagem conv2",
            ),
            Lead(
                store_id=store.id,
                customer_id=customer.id,
                conversation_id=conv1.id,
                status="qualified",
                score=88,
            ),
            Lead(
                store_id=store.id,
                customer_id=customer.id,
                conversation_id=conv2.id,
                status="new",
                score=10,
            ),
            HandoffEvent(
                conversation_id=conv1.id,
                salesperson_id=salesperson.id,
                event_type="manual_panel",
                reason="Teste conv1",
            ),
            HandoffEvent(
                conversation_id=conv2.id,
                salesperson_id=salesperson.id,
                event_type="takeover",
                reason="Teste conv2",
            ),
            AgentRun(
                conversation_id=conv1.id,
                input_text="Oi",
                output_text="Resposta",
                status="success",
                model="test-model",
            ),
            AgentRun(
                conversation_id=conv2.id,
                input_text="Tudo bem?",
                output_text="Tudo certo",
                status="success",
                model="test-model",
            ),
        ]
    )
    db_session.commit()
    return {"instance": instance, "conv1": conv1, "conv2": conv2}


def test_delete_whatsapp_instance_removes_instance_and_all_related_rows(
    client, db_session, demo_data, auth_header, fake_evolution
):
    seeded = _seed_full_relational_graph(db_session, demo_data)
    fake_evolution.delete_instance = lambda _instance_name: {"status": "ok"}

    response = client.delete(
        f"/api/whatsapp-instances/{seeded['instance'].id}", headers=auth_header
    )

    # Se houver IntegrityError (NOT NULL/FK), a API retornaria 500.
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    assert db_session.get(WhatsAppInstance, seeded["instance"].id) is None
    assert db_session.scalars(select(Conversation)).all() == []
    assert db_session.scalars(select(Message)).all() == []
    assert db_session.scalars(select(Lead)).all() == []
    assert db_session.scalars(select(HandoffEvent)).all() == []
    assert db_session.scalars(select(AgentRun)).all() == []


def test_delete_single_conversation_removes_only_its_children_and_keeps_siblings(
    client, db_session, demo_data, auth_header, fake_evolution
):
    seeded = _seed_full_relational_graph(db_session, demo_data)
    fake_evolution.delete_instance = lambda _instance_name: {"status": "ok"}

    response = client.delete(f"/api/conversations/{seeded['conv1'].id}", headers=auth_header)

    # Se houver IntegrityError (NOT NULL/FK), a API retornaria 500.
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    assert db_session.get(Conversation, seeded["conv1"].id) is None
    assert db_session.get(Conversation, seeded["conv2"].id) is not None

    remaining_messages = db_session.scalars(select(Message)).all()
    remaining_leads = db_session.scalars(select(Lead)).all()
    remaining_handoffs = db_session.scalars(select(HandoffEvent)).all()
    remaining_runs = db_session.scalars(select(AgentRun)).all()

    assert {row.conversation_id for row in remaining_messages} == {seeded["conv2"].id}
    assert {row.conversation_id for row in remaining_leads} == {seeded["conv2"].id}
    assert {row.conversation_id for row in remaining_handoffs} == {seeded["conv2"].id}
    assert {row.conversation_id for row in remaining_runs} == {seeded["conv2"].id}
