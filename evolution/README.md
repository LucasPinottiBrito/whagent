# Evolution API local

Stack local da Evolution API para desenvolvimento do WhatsApp Agent SaaS.

## Subir no Windows

Pre-requisito: Docker Desktop rodando com engine Linux.

```powershell
cd C:\Users\User\Documents\projects-freelancer\whatsapp_agent_saas\evolution
Copy-Item .env.example .env
docker compose up -d
```

Servicos:

- API: `http://localhost:8080`
- Manager: `http://localhost:8080/manager`
- Postgres da Evolution: `localhost:5433`
- Redis da Evolution: `localhost:6380`

## Configurar webhook para o backend local

Use a instancia `demo-instance`, que tambem existe no seed do backend.

URL do webhook quando o backend roda no Windows via `uvicorn`:

```txt
http://host.docker.internal:8000/api/webhooks/evolution/demo-instance?webhook_secret=dev-evolution-webhook-secret-change-me
```

Eventos minimos:

- `MESSAGES_UPSERT`
- `SEND_MESSAGE`
- `CONNECTION_UPDATE`

Use a API key de desenvolvimento no header `apikey`:

```txt
dev-evolution-api-key-change-me
```

## Parar

```powershell
docker compose down
```

Para apagar dados locais da Evolution:

```powershell
docker compose down -v
```
