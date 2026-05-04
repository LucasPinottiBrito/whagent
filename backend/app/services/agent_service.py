import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - dependency exists in container images
    OpenAI = None

from app.agents.prompts import CAR_SALES_AGENT_PROMPT
from app.agents.tools import AGENT_RESPONSE_FORMAT, SEARCH_VEHICLES_TOOL
from app.core.config import Settings, get_settings
from app.models import Conversation
from app.services.crm_mock_client import CrmMockClient


@dataclass
class AgentResult:
    reply_text: str
    intent: str = "unknown"
    lead_status: str = "new"
    score: int = 0
    vehicle_interest: str | None = None
    budget_min: Decimal | float | int | None = None
    budget_max: Decimal | float | int | None = None
    payment_type: str | None = None
    trade_in_vehicle: str | None = None
    interest_summary: str | None = None
    tools_used: list[str] = field(default_factory=list)
    raw_response: dict[str, Any] = field(default_factory=dict)


class AgentService:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        crm_client: CrmMockClient | None = None,
    ):
        self.settings = settings or get_settings()
        self.crm_client = crm_client or CrmMockClient(self.settings.crm_mock_base_url)
        self.client = (
            OpenAI(api_key=self.settings.openai_api_key)
            if OpenAI and self.settings.openai_api_key
            else None
        )

    def run(self, *, conversation: Conversation, customer_input: str) -> AgentResult:
        if not self.client:
            return self._fallback_response(customer_input)

        response = self.client.responses.create(
            model=self.settings.default_openai_model,
            instructions=CAR_SALES_AGENT_PROMPT,
            input=customer_input,
            tools=[SEARCH_VEHICLES_TOOL],
            text={"format": AGENT_RESPONSE_FORMAT},
        )
        tools_used = []

        tool_outputs = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", None) != "function_call":
                continue
            if item.name != "search_vehicles":
                continue
            tools_used.append("search_vehicles")
            args = json.loads(item.arguments or "{}")
            result = self.crm_client.search_vehicles(**args)
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result, ensure_ascii=True),
                }
            )

        if tool_outputs:
            response = self.client.responses.create(
                model=self.settings.default_openai_model,
                instructions=CAR_SALES_AGENT_PROMPT,
                previous_response_id=response.id,
                input=tool_outputs,
                text={"format": AGENT_RESPONSE_FORMAT},
            )

        payload = self._parse_output_text(getattr(response, "output_text", ""))
        payload.setdefault("tools_used", tools_used)
        payload.setdefault("raw_response", {"id": getattr(response, "id", None)})
        return self._result_from_payload(payload)

    def _fallback_response(self, customer_input: str) -> AgentResult:
        vehicles: list[dict] = []
        try:
            vehicles = self.crm_client.search_vehicles(status="available")
        except Exception:
            vehicles = []

        vehicle = vehicles[0] if vehicles else None
        if vehicle:
            reply = (
                f"Encontrei um {vehicle['brand']} {vehicle['model']} "
                f"{vehicle['year']} por R$ {vehicle['price']}. "
                "Voce pretende comprar a vista, financiar ou tem veiculo para troca?"
            )
            vehicle_interest = f"{vehicle['brand']} {vehicle['model']}"
        else:
            reply = (
                "Posso te ajudar a encontrar o carro ideal. "
                "Qual modelo, faixa de preco e forma de pagamento voce prefere?"
            )
            vehicle_interest = None

        return AgentResult(
            reply_text=reply,
            intent="vehicle_search" if vehicle else "qualification",
            lead_status="new",
            score=50,
            vehicle_interest=vehicle_interest,
            interest_summary=customer_input,
            tools_used=["search_vehicles"] if vehicle else [],
            raw_response={"mode": "fallback"},
        )

    def _parse_output_text(self, output_text: str) -> dict[str, Any]:
        if not output_text:
            return {
                "reply_text": (
                    "Recebi sua mensagem. Pode me dizer qual modelo e faixa de preco "
                    "voce procura?"
                )
            }
        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            return {"reply_text": output_text}

    def _result_from_payload(self, payload: dict[str, Any]) -> AgentResult:
        return AgentResult(
            reply_text=payload.get("reply_text") or "",
            intent=payload.get("intent") or "unknown",
            lead_status=payload.get("lead_status") or "new",
            score=int(payload.get("score") or 0),
            vehicle_interest=payload.get("vehicle_interest"),
            budget_min=payload.get("budget_min"),
            budget_max=payload.get("budget_max"),
            payment_type=payload.get("payment_type"),
            trade_in_vehicle=payload.get("trade_in_vehicle"),
            interest_summary=payload.get("interest_summary"),
            tools_used=payload.get("tools_used") or [],
            raw_response=payload.get("raw_response") or {},
        )
