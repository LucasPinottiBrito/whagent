import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-with-enough-length-32-bytes"
os.environ["INTERNAL_API_KEY"] = "test-internal-key"
os.environ["OPENAI_API_KEY"] = ""
os.environ["EVOLUTION_API_BASE_URL"] = ""
os.environ["EVOLUTION_API_KEY"] = ""

from app.api.deps import (  # noqa: E402
    get_agent_service,
    get_conversation_queue_service,
    get_db,
    get_evolution_service,
)
from app.core.database import Base  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    Conversation,
    Customer,
    Store,
    User,
    WhatsAppInstance,
)
from app.services.agent_service import AgentResult  # noqa: E402


class FakeQueueService:
    def __init__(self):
        self.scheduled = []

    def schedule_conversation(self, conversation_id: str) -> float:
        self.scheduled.append(conversation_id)
        return 123.0


class FakeAgentService:
    def __init__(self):
        self.calls = []
        self.fail = False

    def run(self, *, customer_input: str, context: dict | None = None, history: list[dict] | None = None) -> AgentResult:
        self.calls.append({"customer_input": customer_input, "context": context or {}, "history": history or []})
        if self.fail:
            raise RuntimeError("agent exploded")
        return AgentResult(
            reply_text="Encontrei um Toyota Corolla 2021. Voce pretende financiar?",
            intent="vehicle_search",
            lead_status="qualified",
            score=82,
            vehicle_interest="Toyota Corolla",
            budget_max=120000,
            payment_type="unknown",
            interest_summary="Cliente procura Corolla ate 120 mil.",
            tools_used=["search_vehicles"],
            raw_response={"mode": "test"},
            model="test-model",
        )


class FakeEvolutionService:
    def __init__(self):
        self.sent = []

    def send_text_message(self, instance_name: str, phone: str, text: str) -> dict:
        self.sent.append(
            {"instance_name": instance_name, "phone": phone, "text": text}
        )
        return {"dry_run": True}


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def fake_queue():
    return FakeQueueService()


@pytest.fixture()
def fake_agent():
    return FakeAgentService()


@pytest.fixture()
def fake_evolution():
    return FakeEvolutionService()


@pytest.fixture()
def client(db_session, fake_queue, fake_agent, fake_evolution):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_conversation_queue_service] = lambda: fake_queue
    app.dependency_overrides[get_agent_service] = lambda: fake_agent
    app.dependency_overrides[get_evolution_service] = lambda: fake_evolution
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def demo_data(db_session):
    store = Store(
        name="Loja Demo",
        slug="loja-demo",
        document="00000000000100",
        phone="5511999999999",
    )
    db_session.add(store)
    db_session.flush()

    admin = User(
        store_id=store.id,
        email="admin@example.com",
        full_name="Admin Demo",
        role="admin",
        hashed_password=hash_password("admin123"),
        is_active=True,
    )
    salesperson = User(
        store_id=store.id,
        email="seller@example.com",
        full_name="Vendedor Demo",
        role="salesperson",
        hashed_password=hash_password("seller123"),
        is_active=True,
    )
    instance = WhatsAppInstance(
        store_id=store.id,
        instance_name="demo-instance",
        phone="5511999999999",
        webhook_secret="secret-123",
        active=True,
    )
    customer = Customer(
        store_id=store.id,
        phone="5511977776666",
        name="Cliente Teste",
        last_seen_at=datetime.now(timezone.utc),
    )
    db_session.add_all([admin, salesperson, instance, customer])
    db_session.commit()
    return {
        "store": store,
        "admin": admin,
        "salesperson": salesperson,
        "instance": instance,
        "customer": customer,
    }


@pytest.fixture()
def auth_header(client, demo_data):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def make_conversation(db_session, demo_data, *, status="ai_active", ai_enabled=True):
    conversation = Conversation(
        store_id=demo_data["store"].id,
        customer_id=demo_data["customer"].id,
        whatsapp_instance_id=demo_data["instance"].id,
        status=status,
        ai_enabled=ai_enabled,
    )
    db_session.add(conversation)
    db_session.commit()
    return conversation
