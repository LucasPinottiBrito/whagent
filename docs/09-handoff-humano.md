# Handoff Humano

Rotas autenticadas:

- `POST /api/conversations/{conversation_id}/takeover`
- `POST /api/conversations/{conversation_id}/release-to-ai`

Takeover:

- `status=human_active`
- `ai_enabled=false`
- registra `handoff_events.event_type=takeover`

Release:

- `status=ai_active`
- `ai_enabled=true`
- registra `handoff_events.event_type=release_to_ai`

Mensagem Evolution `fromMe=true` que nao seja eco do agente vira takeover automatico com `event_type=manual_from_me`.
