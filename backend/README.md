# Backend

API principal da plataforma. Centraliza banco, auth JWT local, webhooks da Evolution API, Redis, OpenAI, CRM mock, regras de conversa, leads e handoff humano.

## Rodar localmente

```bash
cp backend/.env.example backend/.env
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_data.py
```

Credenciais seed:

```txt
admin@example.com
admin123
```

## Endpoints principais

- `GET /health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/webhooks/evolution/{instance_name}`
- `POST /api/internal/conversations/{conversation_id}/process`
- `POST /api/conversations/{conversation_id}/takeover`
- `POST /api/conversations/{conversation_id}/release-to-ai`

O webhook apenas salva a mensagem e agenda a conversa no Redis. A chamada ao agente acontece somente no endpoint interno usado pelo worker.
