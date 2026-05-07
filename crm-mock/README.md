# CRM Mock

API FastAPI em memória para simular estoque, lojas e vendedores.

## Execução local (sem Docker)

```bash
python -m pip install -e .[dev]
uvicorn app.main:app --reload --port 8001
```

## Execução com Docker Compose

A partir da raiz do projeto:

```bash
docker compose up --build -d crm-mock
```

Healthcheck:

```bash
curl http://localhost:8001/health
```

## Deploy com Swarm

```bash
docker build -t whagent-crm-mock:latest ./crm-mock
docker service update --force whagent_crm-mock
```

## Endpoints

- `GET /health`
- `GET /vehicles`
- `GET /stores`
- `GET /salespeople`
