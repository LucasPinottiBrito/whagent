# Frontend

Dashboard Next.js do Whagent.

## Execução local (sem Docker)

```bash
npm install
npm run dev
```

Acesse `http://localhost:3000`.

## Execução com Docker Compose

A partir da raiz do projeto:

```bash
docker compose up --build -d frontend backend
```

## Deploy com Swarm

Frontend usa imagem `whagent-frontend:latest`.

```bash
docker build -t whagent-frontend:latest ./frontend
docker service update --force whagent_frontend
```

## Variáveis públicas

O frontend deve consumir somente variáveis públicas (ex.: `NEXT_PUBLIC_*`).
Não exponha secrets de backend/frontend build.
