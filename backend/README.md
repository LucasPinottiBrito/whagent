# Backend

API FastAPI principal do Whagent.

## Execução local (sem Docker)

```bash
python -m pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Execução com Docker Compose

A partir da raiz do projeto:

```bash
docker compose up --build -d backend postgres redis crm-mock
docker compose exec backend alembic upgrade head
```

Healthcheck:

```bash
curl http://localhost:8000/health
```

## Deploy com Swarm

Backend usa imagem `whagent-backend:latest` no `docker-stack.yml`.

```bash
docker build -t whagent-backend:latest ./backend
docker service update --force whagent_backend
```

## Endpoints principais

- `GET /health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/login/status`
- `POST /api/login/bootstrap`
- `GET/PATCH /api/store/me`
- `GET /api/dashboard/overview`
- `GET/POST /api/whatsapp-instances`
- `POST /api/webhooks/evolution/{instance_name}`
- `POST /api/internal/conversations/{conversation_id}/process`


## Bootstrap de admin (opcional via CLI)

Se quiser criar o primeiro admin sem UI, use o script idempotente:

```bash
export BOOTSTRAP_STORE_NAME="Minha Loja"
export BOOTSTRAP_STORE_SLUG="minha-loja"
export BOOTSTRAP_ADMIN_EMAIL="admin@minhaloja.com"
export BOOTSTRAP_ADMIN_PASSWORD="trocar-esta-senha"
python scripts/bootstrap_admin.py
```

O script só cria o admin se ainda não existir usuário no banco.
