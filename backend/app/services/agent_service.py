import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

from app.core.config import get_settings
from app.services.crm_mock_client import CrmMockClient


AGENT_PROMPT = """\
Você é o assistente virtual de vendas da loja. Atende clientes pelo WhatsApp de forma profissional, educada e consultiva.

## Identidade e Tom
- Trate o cliente por "você" e mantenha um tom amigável, porém profissional.
- Use português brasileiro correto, com acentos e pontuação.
- Mensagens curtas e objetivas (máximo 3 parágrafos). Evite textos longos demais.
- Nunca use gírias excessivas, linguagem técnica de TI nem jargão interno.
- Utilize emojis com moderação (máximo 1-2 por mensagem) para criar proximidade.

## Fluxo de Qualificação
1. **Saudação**: Cumprimente o cliente, pergunte o nome dele e como pode ajudar.
2. **Descoberta**: Identifique o interesse — pergunte sobre modelo, faixa de preço, forma de pagamento (à vista, financiamento, consórcio) e se possui veículo para troca.
3. **Apresentação**: Use a ferramenta `search_vehicles` para buscar opções reais no estoque. Apresente até 3 veículos que mais se encaixam no perfil. Informe modelo, ano, versão, quilometragem, cor e preço.
4. **Negociação leve**: Responda dúvidas sobre condições, mas NÃO ofereça descontos nem faça promessas de preço. Diga que um consultor pode detalhar as melhores condições.
5. **Encaminhamento**: Quando o cliente demonstrar interesse real (quiser agendar visita, test-drive, proposta formal, ou tratar valores com mais detalhe), encaminhe para atendimento humano.

## Regras de Encaminhamento para Atendimento Humano
Direcione o cliente para um consultor humano nas seguintes situações:
- Cliente pede explicitamente para falar com uma pessoa / gerente / vendedor.
- Negociação de preço ou desconto específico.
- Solicitação de agendamento de visita ou test-drive.
- Reclamação, insatisfação ou problema pós-venda.
- Perguntas sobre financiamento detalhado (taxas, parcelas exatas, documentação).
- Assuntos fora do escopo de vendas de veículos.

Quando encaminhar, diga algo como:
"Vou transferir você para um dos nossos consultores que poderá dar continuidade com mais detalhes. Um momento! 😊"

Ao encaminhar, defina no JSON: `"intent": "handoff"` e `"lead_status": "qualified"`.

## Regras Estritas
- NUNCA invente veículos, preços, anos, quilometragem ou disponibilidade. Use SOMENTE dados retornados pela ferramenta `search_vehicles`.
- Se não houver veículos no estoque que atendam ao perfil, informe com transparência e sugira que o cliente deixe o contato para ser avisado quando chegar algo similar.
- Não forneça informações sobre financiamento que não tenha recebido do sistema.
- Sempre retorne a resposta no formato JSON solicitado.
"""

SEARCH_VEHICLES_TOOL = {
    "type": "function",
    "name": "search_vehicles",
    "description": "Consulta veiculos disponiveis no CRM mock.",
    "parameters": {
        "type": "object",
        "properties": {
            "brand": {"type": "string"},
            "model": {"type": "string"},
            "year_min": {"type": "integer"},
            "year_max": {"type": "integer"},
            "min_price": {"type": "number"},
            "max_price": {"type": "number"},
            "transmission": {"type": "string"},
            "fuel": {"type": "string"},
            "status": {"type": "string"},
        },
        "additionalProperties": False,
    },
}

AGENT_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "whagent_agent_response",
    "strict": False,
    "schema": {
        "type": "object",
        "properties": {
            "reply_text": {"type": "string"},
            "intent": {"type": "string"},
            "lead_status": {"type": "string"},
            "score": {"type": "integer"},
            "vehicle_interest": {"type": ["string", "null"]},
            "budget_min": {"type": ["number", "null"]},
            "budget_max": {"type": ["number", "null"]},
            "payment_type": {"type": ["string", "null"]},
            "trade_in_vehicle": {"type": ["string", "null"]},
            "interest_summary": {"type": ["string", "null"]},
        },
        "required": ["reply_text"],
        "additionalProperties": True,
    },
}


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
    model: str | None = None


class AgentService:
    def __init__(
        self,
        *,
        openai_api_key: str | None = None,
        model: str | None = None,
        crm_client: CrmMockClient | None = None,
    ):
        settings = get_settings()
        self.openai_api_key = openai_api_key if openai_api_key is not None else settings.openai_api_key
        self.model = model or settings.default_openai_model
        self.crm_client = crm_client or CrmMockClient(settings.crm_mock_base_url)
        self.client = (
            OpenAI(api_key=self.openai_api_key)
            if OpenAI is not None and self.openai_api_key
            else None
        )

    def run(self, *, customer_input: str, context: dict | None = None, history: list[dict] | None = None) -> AgentResult:
        if self.client is None:
            return self._fallback_response(customer_input)
        return self._openai_response(customer_input, context or {}, history or [])

    def _openai_response(self, customer_input: str, context: dict, history: list[dict]) -> AgentResult:
        messages = [{"role": "developer", "content": json.dumps(context, ensure_ascii=True)}]
        messages.extend(history)
        messages.append({"role": "user", "content": customer_input})

        response = self.client.responses.create(
            model=self.model,
            instructions=AGENT_PROMPT,
            input=messages,
            tools=[SEARCH_VEHICLES_TOOL],
            text={"format": AGENT_RESPONSE_FORMAT},
        )
        tools_used: list[str] = []
        tool_outputs: list[dict] = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", None) != "function_call":
                continue
            if getattr(item, "name", None) != "search_vehicles":
                continue
            tools_used.append("search_vehicles")
            args = json.loads(getattr(item, "arguments", "{}") or "{}")
            args.setdefault("status", "available")
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
                model=self.model,
                instructions=AGENT_PROMPT,
                previous_response_id=response.id,
                input=tool_outputs,
                text={"format": AGENT_RESPONSE_FORMAT},
            )

        payload = self._parse_payload(getattr(response, "output_text", ""))
        payload["tools_used"] = tools_used
        payload["raw_response"] = {"id": getattr(response, "id", None)}
        payload["model"] = self.model
        return self._result_from_payload(payload)

    def _fallback_response(self, customer_input: str) -> AgentResult:
        vehicles: list[dict] = []
        try:
            vehicles = self.crm_client.search_vehicles(status="available")
        except Exception:
            vehicles = []

        vehicle = vehicles[0] if vehicles else None
        if vehicle:
            vehicle_name = f"{vehicle['brand']} {vehicle['model']}"
            reply = (
                f"Temos um {vehicle_name} {vehicle['year']} disponivel. "
                "Voce pretende pagar a vista, financiar ou tem carro para troca?"
            )
            return AgentResult(
                reply_text=reply,
                intent="vehicle_search",
                lead_status="new",
                score=50,
                vehicle_interest=vehicle_name,
                interest_summary=customer_input,
                tools_used=["search_vehicles"],
                raw_response={"mode": "fallback"},
                model="fallback",
            )

        return AgentResult(
            reply_text=(
                "Posso te ajudar a encontrar o carro ideal. "
                "Qual modelo, faixa de preco e forma de pagamento voce prefere?"
            ),
            intent="qualification",
            lead_status="new",
            score=20,
            interest_summary=customer_input,
            raw_response={"mode": "fallback"},
            model="fallback",
        )

    def _parse_payload(self, output_text: str) -> dict[str, Any]:
        if not output_text:
            return {"reply_text": "Pode me dizer qual modelo e faixa de preco voce procura?"}
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
            model=payload.get("model") or self.model,
        )
