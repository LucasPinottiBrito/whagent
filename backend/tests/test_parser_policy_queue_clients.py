from app.services.agent_service import AgentService
from app.services.conversation_queue_service import ConversationQueueService
from app.services.evolution_service import EvolutionService
from app.services.message_origin_policy import (
    MessageOrigin,
    MessageOriginPolicy,
    RuntimeOriginConfig,
)
from app.services.webhook_parser import EvolutionWebhookParser, WebhookParseError


class FakeRedis:
    def __init__(self):
        self.sorted_sets = {}
        self.values = {}
        self.expirations = {}

    def zadd(self, key, mapping):
        self.sorted_sets.setdefault(key, {}).update(mapping)

    def set(self, key, value, ex=None):
        self.values[key] = value
        self.expirations[key] = ex
        return True


class FakeCrmClient:
    def search_vehicles(self, **params):
        return [
            {
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2021,
                "price": 119900,
                "status": "available",
            }
        ]


def test_parser_ignores_payload_without_remote_jid_or_text():
    parser = EvolutionWebhookParser()

    try:
        parser.parse({"data": {"message": {"conversation": "Oi"}}})
    except WebhookParseError as exc:
        assert "remoteJid" in str(exc)

    try:
        parser.parse({"data": {"key": {"remoteJid": "5511@s.whatsapp.net"}}})
    except WebhookParseError as exc:
        assert "texto" in str(exc)


def test_parser_extracts_nested_text_and_normalizes_phone():
    parsed = EvolutionWebhookParser().parse(
        {
            "data": {
                "key": {
                    "id": "msg-1",
                    "remoteJid": "55 11 97777-6666@s.whatsapp.net",
                    "fromMe": False,
                },
                "pushName": "Cliente",
                "message": {"extendedTextMessage": {"text": "Quero um Corolla"}},
            }
        }
    )

    assert parsed.phone == "5511977776666"
    assert parsed.text == "Quero um Corolla"
    assert parsed.message_id == "msg-1"
    assert parsed.push_name == "Cliente"
    assert parsed.is_group is False


def test_origin_policy_classifies_agent_echo_human_and_debug_from_me():
    policy = MessageOriginPolicy(RuntimeOriginConfig())

    assert (
        policy.classify(from_me=False, sent_by_agent=False, source=None)
        == MessageOrigin.CUSTOMER_INBOUND
    )
    assert (
        policy.classify(from_me=True, sent_by_agent=True, source="agent")
        == MessageOrigin.AGENT_ECHO_IGNORE
    )
    assert (
        policy.classify(from_me=True, sent_by_agent=False, source=None)
        == MessageOrigin.HUMAN_OUTBOUND_TAKEOVER
    )

    debug_policy = MessageOriginPolicy(RuntimeOriginConfig(allow_from_me_as_inbound=True))
    assert (
        debug_policy.classify(from_me=True, sent_by_agent=False, source=None)
        == MessageOrigin.CUSTOMER_INBOUND
    )


def test_queue_service_schedules_and_reschedules_conversation():
    redis = FakeRedis()
    queue = ConversationQueueService(
        redis_client=redis,
        debounce_seconds=8,
        now_func=lambda: 100.0,
    )

    process_at = queue.schedule_conversation("conv-1")

    assert process_at == 108.0
    assert redis.sorted_sets["queue:conversation-processing"]["conv-1"] == 108.0
    assert redis.values["debounce:conversation:conv-1"] == "1"
    assert redis.expirations["debounce:conversation:conv-1"] == 8


def test_evolution_service_dry_run_without_credentials():
    service = EvolutionService(base_url="", api_key="")

    result = service.send_text_message("demo", "5511999999999", "Oi")

    assert result["dry_run"] is True


def test_agent_fallback_uses_available_vehicle_without_openai():
    service = AgentService(openai_api_key="", crm_client=FakeCrmClient())

    result = service.run(customer_input="Quero um Corolla automatico", context={})

    assert "Corolla" in result.reply_text
    assert result.intent == "vehicle_search"
    assert result.vehicle_interest == "Toyota Corolla"
    assert result.tools_used == ["search_vehicles"]
