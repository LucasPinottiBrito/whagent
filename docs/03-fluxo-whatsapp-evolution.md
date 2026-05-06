# Fluxo WhatsApp Evolution

Endpoint:

```txt
POST /api/webhooks/evolution/{instance_name}
```

Seguranca:

- header `X-Evolution-Webhook-Secret`; ou
- query param `webhook_secret`.

Fluxo:

1. backend localiza a instancia ativa;
2. valida o segredo;
3. parseia `remoteJid`, texto, `fromMe`, id externo e nome;
4. deduplica por `evolution_message_id` quando existir;
5. cria ou reutiliza customer e conversation;
6. salva mensagem inbound ou outbound humana;
7. agenda Redis apenas quando a IA esta ativa;
8. retorna status sem chamar o agente.

Eco do agente com `source=agent` ou `sent_by_agent=true` e ignorado.
