from sqlalchemy import select

from app.models import Conversation, Lead, Message, Store, User, WhatsAppInstance
from conftest import make_conversation


class FakeEvolutionControlService:
    def __init__(self):
        self.created = []
        self.webhooks = []
        self.connected = []
        self.status_checked = []
        self.sent = []

    def create_instance(self, *, instance_name, phone, webhook_url, webhook_secret):
        self.created.append(
            {
                "instance_name": instance_name,
                "phone": phone,
                "webhook_url": webhook_url,
                "webhook_secret": webhook_secret,
            }
        )
        return {
            "dry_run": True,
            "instance": {
                "instanceName": instance_name,
                "instanceId": f"evo-{instance_name}",
                "status": "created",
            },
        }

    def connect_instance(self, instance_name: str, phone: str | None = None):
        self.connected.append({"instance_name": instance_name, "phone": phone})
        return {"dry_run": True, "pairingCode": "12345678", "code": "QR-CODE"}

    def get_connection_state(self, instance_name: str):
        self.status_checked.append(instance_name)
        return {"dry_run": True, "instance": {"instanceName": instance_name, "state": "open"}}

    def configure_webhook(self, *, instance_name, webhook_url, webhook_secret):
        self.webhooks.append(
            {
                "instance_name": instance_name,
                "webhook_url": webhook_url,
                "webhook_secret": webhook_secret,
            }
        )
        return {"dry_run": True, "webhook": {"enabled": True, "url": webhook_url}}

    def restart_instance(self, instance_name: str):
        return {"dry_run": True, "instance": {"instanceName": instance_name, "state": "open"}}

    def logout_instance(self, instance_name: str):
        return {"dry_run": True, "status": "SUCCESS"}

    def delete_instance(self, instance_name: str):
        return {"dry_run": True, "status": "SUCCESS"}

    def send_text_message(self, instance_name: str, phone: str, text: str):
        self.sent.append({"instance_name": instance_name, "phone": phone, "text": text})
        return {"dry_run": True}


def test_store_me_can_read_and_update(client, demo_data, auth_header):
    response = client.get("/api/store/me", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["slug"] == "loja-demo"

    update = client.patch(
        "/api/store/me",
        headers=auth_header,
        json={"name": "Loja Demo Atualizada", "phone": "5511000000000"},
    )

    assert update.status_code == 200
    assert update.json()["name"] == "Loja Demo Atualizada"


def test_whatsapp_instance_lifecycle_uses_evolution_service(
    client, db_session, demo_data, auth_header
):
    fake_evolution = FakeEvolutionControlService()
    from app.api.deps import get_evolution_service
    from app.main import app

    app.dependency_overrides[get_evolution_service] = lambda: fake_evolution
    try:
        response = client.post(
            "/api/whatsapp-instances",
            headers=auth_header,
            json={
                "instance_name": "nova-instancia",
                "phone": "551188887777",
                "webhook_secret": "secret-nova",
            },
        )
    finally:
        app.dependency_overrides.pop(get_evolution_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["instance_name"] == "nova-instancia"
    assert body["evolution"]["dry_run"] is True
    assert db_session.scalar(
        select(WhatsAppInstance).where(
            WhatsAppInstance.instance_name == "nova-instancia"
        )
    )
    assert fake_evolution.created[0]["instance_name"] == "nova-instancia"


def test_instance_connect_status_and_webhook_sync(client, demo_data, auth_header):
    fake_evolution = FakeEvolutionControlService()
    from app.api.deps import get_evolution_service
    from app.main import app

    instance_id = demo_data["instance"].id
    app.dependency_overrides[get_evolution_service] = lambda: fake_evolution
    try:
        connect = client.post(
            f"/api/whatsapp-instances/{instance_id}/connect",
            headers=auth_header,
        )
        status = client.post(
            f"/api/whatsapp-instances/{instance_id}/sync-status",
            headers=auth_header,
        )
        webhook = client.post(
            f"/api/whatsapp-instances/{instance_id}/sync-webhook",
            headers=auth_header,
        )
    finally:
        app.dependency_overrides.pop(get_evolution_service, None)

    assert connect.status_code == 200
    assert connect.json()["pairingCode"] == "12345678"
    assert status.json()["state"] == "open"
    assert webhook.json()["webhook"]["enabled"] is True


def test_dashboard_overview_counts_records(client, db_session, demo_data, auth_header):
    conversation = make_conversation(db_session, demo_data)
    db_session.add(
        Lead(
            store_id=demo_data["store"].id,
            customer_id=demo_data["customer"].id,
            conversation_id=conversation.id,
            status="qualified",
            score=80,
        )
    )
    db_session.commit()

    response = client.get("/api/dashboard/overview", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["conversations_total"] == 1
    assert response.json()["leads_total"] == 1
    assert response.json()["instances_total"] == 1


def test_conversation_list_detail_human_send_and_ai_controls(
    client, db_session, demo_data, auth_header
):
    conversation = make_conversation(db_session, demo_data)
    inbound = Message(
        conversation_id=conversation.id,
        direction="inbound",
        sender_type="customer",
        content="Oi",
    )
    db_session.add(inbound)
    db_session.commit()

    fake_evolution = FakeEvolutionControlService()
    from app.api.deps import get_evolution_service
    from app.main import app

    app.dependency_overrides[get_evolution_service] = lambda: fake_evolution
    try:
        listing = client.get("/api/conversations", headers=auth_header)
        detail = client.get(f"/api/conversations/{conversation.id}", headers=auth_header)
        disable = client.post(
            f"/api/conversations/{conversation.id}/ai/disable", headers=auth_header
        )
        human = client.post(
            f"/api/conversations/{conversation.id}/messages/human",
            headers=auth_header,
            json={"content": "Vou te atender por aqui."},
        )
        enable = client.post(
            f"/api/conversations/{conversation.id}/ai/enable", headers=auth_header
        )
    finally:
        app.dependency_overrides.pop(get_evolution_service, None)

    assert listing.status_code == 200
    assert listing.json()["items"][0]["id"] == conversation.id
    assert detail.json()["messages"][0]["content"] == "Oi"
    assert disable.json()["ai_enabled"] is False
    assert human.status_code == 200
    assert fake_evolution.sent[0]["text"] == "Vou te atender por aqui."
    assert enable.json()["ai_enabled"] is True
    assert db_session.query(Message).count() == 2


def test_process_now_and_leads_api(client, db_session, demo_data, auth_header):
    conversation = make_conversation(db_session, demo_data)
    db_session.add(
        Message(
            conversation_id=conversation.id,
            direction="inbound",
            sender_type="customer",
            content="Quero um Corolla",
        )
    )
    db_session.commit()

    processed = client.post(
        f"/api/conversations/{conversation.id}/process-now", headers=auth_header
    )
    leads = client.get("/api/leads", headers=auth_header)

    assert processed.status_code == 200
    assert processed.json()["status"] == "processed"
    assert leads.status_code == 200
    assert leads.json()["items"][0]["conversation_id"] == conversation.id
