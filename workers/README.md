# Workers

Worker que observa Redis e chama endpoint interno do backend.

## Execução local (sem Docker)

```bash
python -m pip install -e .[dev]
python -m app.main
```

## Execução com Docker Compose

A partir da raiz do projeto:

```bash
docker compose up --build -d worker redis backend
```

Logs:

```bash
docker compose logs -f worker
```

## Deploy com Swarm

Worker usa imagem `whagent-worker:latest` e comando `python -m app.main`.

```bash
docker build -t whagent-worker:latest ./workers
docker service update --force whagent_worker
```

## Escalar workers

```bash
docker service scale whagent_worker=2
```
