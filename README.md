# Whagent

Plataforma SaaS simples para atendimento via WhatsApp de lojas de carros com agente de IA.

## Estrutura

```txt
/backend   API FastAPI principal, banco, auth, webhooks, agente e integracoes
/crm-mock  API FastAPI em memoria para estoque e vendedores ficticios
/frontend  Dashboard Next.js para setup, instancias, inbox, leads e debug
/docs      documentacao curta e fiel ao MVP
/workers   worker Redis que chama endpoint interno do backend
```

## Rodar localmente

Requisitos: Python 3.11+, Docker Desktop e Node.js 20.9+ para o frontend.

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item crm-mock/.env.example crm-mock/.env
Copy-Item workers/.env.example workers/.env
docker compose up --build
```

Em outro terminal, aplique as migrations:

```powershell
docker compose exec backend alembic upgrade head
```

Depois acesse o painel em `http://localhost:3000`.

Primeiro uso:

- se o banco nao tiver usuarios, abra `/setup` e crie a empresa/admin;
- se preferir dados demo via terminal, rode `docker compose exec backend python scripts/seed_demo_data.py`;
- apos login, use `/app/instances` para criar/conectar a instancia Evolution;
- use `/app/debug` para simular inbound sem WhatsApp real.

Servicos:

- Backend: `http://localhost:8000/health`
- CRM mock: `http://localhost:8001/health`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Testes

```powershell
python -m pip install -r requirements-dev.txt
cd backend; python -m pytest -q; cd ..
cd crm-mock; python -m pytest -q; cd ..
cd workers; python -m pytest -q; cd ..
```

## Debug do agente

```powershell
cd backend
python scripts/agent_chat.py
```

O chat local nao envia mensagens para a Evolution e, por padrao, nao grava conversas no banco.

## Simular inbound

Com backend e banco prontos, use:

```powershell
curl -X POST http://localhost:8000/api/debug/evolution/simulate-inbound ^
  -H "Content-Type: application/json" ^
  -d "{\"instance_name\":\"demo-instance\",\"webhook_secret\":\"dev-evolution-webhook-secret\",\"phone\":\"5511977776666\",\"text\":\"Quero um Corolla automatico\",\"process_now\":true}"
```

Rotas `/api/debug/*` nao sao carregadas quando `APP_ENV` for `prod` ou `production`.
