# Handoff Humano

Rotas:

- `POST /api/conversations/{conversation_id}/takeover`
- `POST /api/conversations/{conversation_id}/release-to-ai`

Takeover:

- define `ai_enabled=false`;
- define `status=human_active`;
- registra `handoff_event`.

Release:

- define `ai_enabled=true`;
- define `status=ai_active`.

Mensagens manuais detectadas com `fromMe=true` tambem geram takeover automatico quando nao forem marcadas como envio do agente.
