# Backend

API principal do Whagent.

## Rodar local

```powershell
Copy-Item .env.example .env
python -m pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

Para iniciar sem seed, abra o frontend em `/setup`. O endpoint publico de bootstrap
fica bloqueado automaticamente depois que existir qualquer usuario.

Seed demo opcional:

```powershell
python scripts/seed_demo_data.py
```

## Endpoints principais

- `GET /health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/setup/status`
- `POST /api/setup/bootstrap`
- `GET/PATCH /api/store/me`
- `GET /api/dashboard/overview`
- `GET/POST /api/whatsapp-instances`
- `POST /api/whatsapp-instances/{id}/connect`
- `POST /api/whatsapp-instances/{id}/sync-status`
- `POST /api/whatsapp-instances/{id}/sync-webhook`
- `POST /api/whatsapp-instances/{id}/restart`
- `POST /api/whatsapp-instances/{id}/logout`
- `GET /api/conversations`
- `GET /api/conversations/{conversation_id}`
- `POST /api/conversations/{conversation_id}/messages/human`
- `POST /api/conversations/{conversation_id}/ai/enable`
- `POST /api/conversations/{conversation_id}/ai/disable`
- `POST /api/conversations/{conversation_id}/process-now`
- `GET /api/leads`
- `POST /api/webhooks/evolution/{instance_name}`
- `POST /api/internal/conversations/{conversation_id}/process`
- `POST /api/conversations/{conversation_id}/takeover`
- `POST /api/conversations/{conversation_id}/release-to-ai`

## Evolution

Se `EVOLUTION_API_BASE_URL` ou `EVOLUTION_API_KEY` estiverem vazios, o
`EvolutionService` retorna `dry_run` e o fluxo local continua funcionando.
Configure `WEBHOOK_PUBLIC_BASE_URL` com a URL publica do backend para sincronizar
webhooks reais pela Evolution.

## Chat local do agente

```powershell
python scripts/agent_chat.py
```
