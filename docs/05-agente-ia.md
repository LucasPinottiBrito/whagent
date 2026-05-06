# Agente de IA

O `AgentService` fica no backend e retorna dados estruturados:

- `reply_text`
- `intent`
- `lead_status`
- `score`
- `vehicle_interest`
- `budget_min`
- `budget_max`
- `payment_type`
- `trade_in_vehicle`
- `interest_summary`

Com `OPENAI_API_KEY`, usa o SDK oficial da OpenAI e Responses API. Sem chave, usa fallback deterministico:

1. consulta veiculos disponiveis no CRM mock;
2. oferece o primeiro veiculo retornado;
3. pergunta sobre pagamento, financiamento ou troca.

O fallback nao inventa veiculos.

Debug local:

```powershell
cd backend
python scripts/agent_chat.py
```
