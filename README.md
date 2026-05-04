# WhatsApp Car Agent SaaS

Monorepo para uma plataforma SaaS simples de atendimento via WhatsApp para lojas de carros.

## Estrutura

```txt
/backend   API principal FastAPI
/crm-mock  API mockada de estoque/CRM
/frontend  base Next.js do painel
/docs      documentacao tecnica
/workers   processamento assincrono via Redis
```

## Rodar localmente

```bash
cp backend/.env.example backend/.env
cp crm-mock/.env.example crm-mock/.env
cp workers/.env.example workers/.env
docker compose up --build
```

Em outro terminal:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_demo_data.py
```

Servicos:

- Backend: `http://localhost:8000/health`
- CRM mock: `http://localhost:8001/health`
- Redis: `localhost:6379`
- PostgreSQL: `localhost:5432`

## Fluxo principal

1. Evolution API envia webhook para `POST /api/webhooks/evolution/{instance_name}`.
2. Backend valida, identifica instancia, cliente e conversa.
3. Backend salva mensagem inbound no PostgreSQL.
4. Backend marca `pending_agent_processing=true` e agenda a conversa no Redis.
5. Worker busca conversas prontas no sorted set e adquire lock por conversa.
6. Worker chama `POST /api/internal/conversations/{conversation_id}/process`.
7. Backend agrupa mensagens inbound pendentes, chama `AgentService`, atualiza lead, salva resposta e envia pela Evolution API.

O webhook nao chama OpenAI diretamente. O worker nao acessa o banco diretamente.

## Testes

```bash
cd backend && python -m pytest -q
cd ../crm-mock && python -m pytest -q
cd ../workers && python -m pytest -q
```
