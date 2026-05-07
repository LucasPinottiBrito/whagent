# Deploy com Docker Swarm

## 1) Build das imagens

```bash
./scripts/build-images.sh
```

Ou manualmente:

```bash
docker build -t whagent-backend:latest ./backend
docker build -t whagent-worker:latest ./workers
docker build -t whagent-frontend:latest ./frontend
docker build -t whagent-crm-mock:latest ./crm-mock
```

## 2) Inicializar o Swarm (uma vez por nó manager)

```bash
docker swarm init
```

## 2.1) Preparar variáveis de ambiente (obrigatório)

O deploy Swarm consome **apenas** o `.env` da raiz do repositório (referenciado por `env_file: .env` no `docker-stack.yml`).

```bash
cp .env.example .env
```

Edite o arquivo e ajuste segredos/URLs antes do deploy.

## 3) Deploy da stack

```bash
./scripts/deploy-stack.sh
```

## 3.1) Rodar migrações (serviço migrate)

Após o deploy, execute o serviço de migração:

```bash
docker service update --force whagent_migrate
```

Acompanhe o status:

```bash
docker service ps whagent_migrate
docker service logs -f whagent_migrate
```

## 4) Verificar serviços e tarefas

```bash
docker stack services whagent
docker stack ps whagent
```

## 5) Logs

```bash
docker service logs -f whagent_backend
docker service logs -f whagent_worker
docker service logs -f whagent_frontend
```

Atalho:

```bash
./scripts/logs.sh backend
./scripts/logs.sh worker
./scripts/logs.sh frontend
```

## 6) Atualização após mudanças

```bash
docker build -t whagent-backend:latest ./backend
docker build -t whagent-worker:latest ./workers
docker build -t whagent-frontend:latest ./frontend
docker service update --force whagent_backend
docker service update --force whagent_worker
docker service update --force whagent_frontend
```

## 7) Escalar worker

```bash
docker service scale whagent_worker=2
```

## 8) Remover stack

```bash
docker stack rm whagent
```

## 9) Debug de falhas comuns

- Rode `docker stack ps whagent` para verificar restart loop e motivo.
- Rode `docker service logs -f whagent_backend` para erros de app/migração/env.
- Verifique se as variáveis de conexão usam hosts internos (`postgres`, `redis`, `backend`, `crm-mock`) e não `localhost`.
- Valide arquivos antes do deploy:

```bash
docker compose config
docker stack config -c docker-stack.yml
```

## 10) Healthcheck backend

```bash
curl http://localhost:8000/health
```

A rota já existe no backend e retorna status da API.


## 11) Primeiro usuário admin (boas práticas)

Primeiro admin é criado automaticamente no startup do backend (usuário padrão `admin@whagent.local` / senha `admin123`) se não existir nenhum usuário admin.

Alternativa automatizada/CLI (idempotente):

```bash
docker service update --env-add BOOTSTRAP_STORE_NAME="Minha Loja" \
  --env-add BOOTSTRAP_STORE_SLUG="minha-loja" \
  --env-add BOOTSTRAP_ADMIN_EMAIL="admin@minhaloja.com" \
  --env-add BOOTSTRAP_ADMIN_PASSWORD="trocar-esta-senha" \
  --env-add BOOTSTRAP_ADMIN_FULL_NAME="Administrador" \
  --force whagent_backend

# Executar bootstrap manual no container backend
docker exec -it $(docker ps --filter name=whagent_backend -q | head -n1) \
  python scripts/bootstrap_admin.py
```

O script só cria admin se a tabela `users` estiver vazia.
