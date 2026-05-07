# Whagent

Plataforma SaaS para atendimento via WhatsApp de lojas de carros com agente de IA.

## Estrutura do projeto

```txt
/backend   API FastAPI principal, banco, auth, webhooks, agente e integrações
/crm-mock  API FastAPI em memória para estoque e vendedores fictícios
/frontend  Dashboard Next.js para setup, instâncias, inbox, leads e debug
/docs      documentação complementar
/workers   worker Redis que chama endpoint interno do backend
/scripts   scripts auxiliares de build/deploy/logs Docker
```

## Passo a passo completo (clone -> execução)

## 1) Pré-requisitos

- Git
- Docker e Docker Compose plugin
- (Opcional local sem Docker) Python 3.11+ e Node.js 20+

## 2) Clonar repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd whagent
```

## 3) Criar arquivo `.env` na raiz

O projeto usa um `.env` já preenchido com as variáveis da aplicação.
Garanta que esse arquivo exista em `./.env` antes de subir os containers.

## 4) Rodar local com Docker Compose (desenvolvimento)

```bash
docker compose up --build -d
```

Aplicar migrations do backend:

```bash
docker compose exec backend alembic upgrade head
```

Acessos:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- CRM mock health: `http://localhost:8001/health`

## 5) Primeiro uso

- Se o banco não tiver usuários, abra `/setup` no frontend.
- Opcional: popular dados demo:

```bash
docker compose exec backend python scripts/seed_demo_data.py
```

## 6) Deploy em Docker Swarm (produção)

Build de imagens:

```bash
./scripts/build-images.sh
```

Inicializar swarm (uma vez no manager):

```bash
docker swarm init
```

Deploy da stack:

```bash
./scripts/deploy-stack.sh
```

Verificar serviços e tarefas:

```bash
docker stack services whagent
docker stack ps whagent
```

Logs:

```bash
./scripts/logs.sh backend
./scripts/logs.sh worker
./scripts/logs.sh frontend
```

## 7) Atualização em produção

Após alterar código:

```bash
./scripts/build-images.sh
docker service update --force whagent_backend
docker service update --force whagent_worker
docker service update --force whagent_frontend
```

## 8) Remoção da stack

```bash
docker stack rm whagent
```

## Documentação detalhada

- Swarm: `docs/docker-swarm.md`
- Backend: `backend/README.md`
- Worker: `workers/README.md`
- Frontend: `frontend/README.md`
- CRM Mock: `crm-mock/README.md`

## Testes

```bash
python -m pip install -r requirements-dev.txt
cd backend && python -m pytest -q && cd ..
cd crm-mock && python -m pytest -q && cd ..
cd workers && python -m pytest -q && cd ..
```
