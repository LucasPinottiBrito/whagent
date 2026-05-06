# Modelo de Dados

Tabelas:

- `stores`
- `users`
- `whatsapp_instances`
- `customers`
- `conversations`
- `messages`
- `leads`
- `handoff_events`
- `agent_runs`

Status de conversa:

- `ai_active`
- `human_active`
- `ai_disabled`
- `closed`

Mensagens:

- direction: `inbound`, `outbound`
- sender_type: `customer`, `agent`, `human`, `system`

Constraints principais:

- customer unico por `store_id + phone`;
- `conversation_id` unico em lead;
- `evolution_message_id` unico somente quando nao nulo.
