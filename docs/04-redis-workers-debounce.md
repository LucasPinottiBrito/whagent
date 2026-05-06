# Redis, Workers e Debounce

Chaves:

- sorted set: `queue:conversation-processing`
- debounce: `debounce:conversation:{conversation_id}`
- lock: `lock:conversation:{conversation_id}`

Ao receber inbound processavel:

```txt
process_at = now + AGENT_DEBOUNCE_SECONDS
ZADD queue:conversation-processing process_at conversation_id
SET debounce:conversation:{conversation_id} 1 EX AGENT_DEBOUNCE_SECONDS
```

O worker busca itens prontos com `ZRANGEBYSCORE`, tenta lock com token unico e chama:

```txt
POST /api/internal/conversations/{conversation_id}/process
X-Internal-Api-Key: ...
```

O item sai da fila somente se o backend responder 2xx. O unlock compara token via Lua script.
