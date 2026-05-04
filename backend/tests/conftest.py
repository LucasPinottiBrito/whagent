import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-with-at-least-32-bytes"
os.environ["INTERNAL_API_KEY"] = "test-internal-key"
os.environ["OPENAI_API_KEY"] = ""

from app.api.deps import (  # noqa: E402
    get_agent_service,
    get_conversation_queue,
    get_db,
    get_evolution_service,
)
from app.core.database import Base  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    Customer,
    Salesperson,
    Store,
    User,
    WhatsAppInstance,
)
from app.services.agent_service import AgentResult  # noqa: E402


class FakeQueue:
    def __init__(self):
        self.scheduled = []

    def schedule_conversation(self, conversation_id: str) -> float:
        self.scheduled.append(conversation_id)
        return 123.0


class FakeAgentService:
    def __init__(self):
        self.calls = []

    def run(self, *, conversation, customer_input: str) -> AgentResult:
        self.calls.append(customer_input)
        return AgentResult(
            reply_text="Encontrei um Corolla XEi 2021 por R$ 119.900. Voce pretende financiar?",
            intent="vehicle_search",
            lead_status="qualified",
            score=82,
            vehicle_interest="Toyota Corolla",
            budget_min=None,
            budget_max=120000,
            payment_type="unknown",
            trade_in_vehicle=None,
            interest_summary="Cliente procura Corolla automatico ate 120 mil.",
            tools_used=["search_vehicles"],
            raw_response={"mode": "test"},
        )


class FakeEvolutionService:
    def __init__(self):
        self.sent = []

    def send_text_message(self, instance_name: str, phone: str, text: str):
        self.sent.append(
            {"instance_name": instance_name, "phone": phone, "text": text}
        )
        return {"sent": True}


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def fake_queue():
    return FakeQueue()


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
    app.dependency_overrides[get_conversation_queue] = lambda: fake_queue
    app.dependency_overrides[get_agent_service] = lambda: fake_agent
    app.dependency_overrides[get_evolution_service] = lambda: fake_evolution

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def demo_data(db_session):
    store = Store(name="Loja Demo", slug="loja-demo", phone="5511999999999")
    db_session.add(store)
    db_session.flush()

    user = User(
        store_id=store.id,
        email="admin@example.com",
        full_name="Admin Demo",
        role="admin",
        hashed_password=hash_password("admin123"),
        is_active=True,
    )
    instance = WhatsAppInstance(
        store_id=store.id,
        instance_name="demo-instance",
        phone="5511999999999",
        active=True,
    )
    salesperson = Salesperson(
        store_id=store.id,
        name="Ana Vendedora",
        email="ana@example.com",
        phone="5511988887777",
        active=True,
        specialty="sedans",
    )
    customer = Customer(
        store_id=store.id,
        phone="5511977776666",
        name="Cliente Teste",
        last_seen_at=datetime.now(timezone.utc),
    )
    db_session.add_all([user, instance, salesperson, customer])
    db_session.commit()
    return {
        "store": store,
        "user": user,
        "instance": instance,
        "salesperson": salesperson,
        "customer": customer,
    }
