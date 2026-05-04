# Redis, Workers e Debounce

Variaveis:

```env
AGENT_DEBOUNCE_SECONDS=8
REDIS_URL=redis://redis:6379/0
CONVERSATION_LOCK_SECONDS=60
WORKER_POLL_INTERVAL_SECONDS=1
WORKER_BATCH_SIZE=10
```

Ao receber inbound:

```txt
process_at = now + AGENT_DEBOUNCE_SECONDS
ZADD queue:conversation-processing process_at conversation_id
SET debounce:conversation:{conversation_id} 1 EX AGENT_DEBOUNCE_SECONDS
```

Worker:

```txt
ZRANGEBYSCORE queue:conversation-processing -inf now LIMIT 0 WORKER_BATCH_SIZE
SET lock:conversation:{conversation_id} 1 NX EX CONVERSATION_LOCK_SECONDS
POST /api/internal/conversations/{conversation_id}/process
ZREM queue:conversation-processing conversation_id
DEL lock:conversation:{conversation_id}
```

O worker nao acessa o banco. A regra de negocio continua no backend.
