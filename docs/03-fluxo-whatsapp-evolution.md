# Fluxo WhatsApp Evolution

Entrada:

```txt
POST /api/webhooks/evolution/{instance_name}
```

Ao receber mensagem inbound:

1. validar payload;
2. identificar instancia WhatsApp;
3. identificar ou criar cliente;
4. identificar ou criar conversa;
5. salvar mensagem inbound;
6. atualizar `last_customer_message_at`;
7. marcar `pending_agent_processing=true`;
8. agendar `conversation_id` no Redis;
9. retornar 200 rapidamente.

O webhook nao chama OpenAI diretamente.

Se `fromMe=true` e a mensagem nao foi marcada como enviada pelo agente, o backend considera takeover humano, salva mensagem outbound `human`, desativa IA e registra `handoff_event`.
