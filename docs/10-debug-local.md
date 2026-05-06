# Debug Local

Rotas `/api/debug/*` so existem fora de `APP_ENV=prod` ou `APP_ENV=production`.

O frontend tambem expoe `/app/debug` para usar essas rotas sem terminal.

Endpoints:

- `GET /api/debug/runtime`
- `PATCH /api/debug/runtime`
- `POST /api/debug/runtime/reset`
- `POST /api/debug/modes/self-group`
- `POST /api/debug/modes/external-tester`
- `POST /api/debug/evolution/simulate-inbound`
- `GET /api/debug/conversations/{conversation_id}`
- `POST /api/debug/conversations/{conversation_id}/ai/disable`
- `POST /api/debug/conversations/{conversation_id}/ai/enable`
- `POST /api/debug/conversations/{conversation_id}/human/takeover`
- `POST /api/debug/conversations/{conversation_id}/human/release`

Exemplo:

```powershell
curl -X POST http://localhost:8000/api/debug/evolution/simulate-inbound ^
  -H "Content-Type: application/json" ^
  -d "{\"instance_name\":\"demo-instance\",\"webhook_secret\":\"dev-evolution-webhook-secret\",\"phone\":\"5511977776666\",\"text\":\"Quero um Corolla\",\"process_now\":true}"
```

Pelo painel:

1. Entre em `/app/debug`.
2. Escolha a instancia e informe o telefone do cliente.
3. Marque `Processar com IA imediatamente` para chamar o processamento no mesmo fluxo.
