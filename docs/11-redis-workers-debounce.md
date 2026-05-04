Perfeito. Então a arquitetura já deve nascer com **Redis para debounce e fila simples de processamento**, respeitando sua estrutura:

```txt
/backend
/crm-mock
/frontend
/docs
/workers
```

A ideia principal fica assim:

```txt
Evolution API
  ↓
/backend recebe webhook
  ↓
/backend salva mensagem no PostgreSQL
  ↓
/backend agenda processamento no Redis
  ↓
/workers consome/processa conversas pendentes
  ↓
/workers chama AgentService/OpenAI pelo código compartilhado ou por endpoint interno do backend
  ↓
/backend ou worker envia resposta via Evolution API
```

Para manter a arquitetura limpa, minha recomendação é:

```txt
/backend = API principal, banco, auth, EvolutionService, AgentService e regras de domínio
/workers = processos assíncronos que reutilizam serviços do backend ou chamam endpoints internos
/redis = fila, debounce, lock e controle de processamento
```

---

# Documentação complementar: Redis e Workers

Use este trecho como novo arquivo em:

```txt
/docs/11-redis-workers-debounce.md
```

````md
# Redis, Workers e Debounce de Mensagens

## 1. Objetivo

Este documento define como o projeto deve usar Redis e workers para lidar com mensagens consecutivas recebidas pelo WhatsApp.

No WhatsApp é comum que um cliente envie várias mensagens em sequência, por exemplo:

```txt
Oi
Queria ver um Corolla
Automático
Até uns 120 mil
````

O agente de IA não deve responder cada mensagem separadamente.

O sistema deve aguardar alguns segundos após a última mensagem recebida, agrupar as mensagens e responder como se fossem uma única entrada.

---

## 2. Estrutura respeitada do repositório

O projeto deve manter a seguinte estrutura:

```txt
/
├── backend/
├── crm-mock/
├── frontend/
├── docs/
├── workers/
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 3. Responsabilidade de cada módulo

## 3.1 `/backend`

O `/backend` continua sendo a API principal da plataforma.

Responsabilidades:

* receber webhooks da Evolution API;
* salvar mensagens no PostgreSQL;
* gerenciar usuários, lojas, conversas, leads e mensagens;
* autenticação JWT local;
* comunicação com Evolution API;
* comunicação com OpenAI;
* comunicação com `/crm-mock`;
* regras principais de domínio;
* endpoints usados pelo frontend;
* endpoints internos usados pelos workers.

O webhook da Evolution não deve chamar a OpenAI diretamente.

Ele deve apenas:

1. receber a mensagem;
2. validar o payload;
3. identificar instância, loja, cliente e conversa;
4. salvar a mensagem no banco;
5. publicar/agendar processamento no Redis;
6. retornar 200 rapidamente para a Evolution API.

---

## 3.2 `/workers`

O `/workers` será responsável pelos processos assíncronos do projeto.

No MVP, o principal worker será o worker de processamento de conversas.

Responsabilidades:

* consumir eventos do Redis;
* aplicar debounce por conversa;
* evitar processamento duplicado;
* agrupar mensagens recentes;
* chamar o agente de IA;
* salvar resposta;
* enviar resposta pela Evolution API;
* atualizar lead;
* registrar execução do agente.

---

## 3.3 `/crm-mock`

O `/crm-mock` continua sendo uma API fictícia, sem autenticação e sem banco.

Ele deve simular:

* veículos;
* lojas;
* vendedores;
* disponibilidade;
* sugestões de vendedor.

O worker ou o backend poderão consultar o `/crm-mock` através do backend, preferencialmente centralizando essa comunicação no backend.

---

## 3.4 `/frontend`

O `/frontend` deve se comunicar apenas com o `/backend`.

Ele não deve falar diretamente com:

* Redis;
* Evolution API;
* OpenAI API;
* `/crm-mock`;
* banco de dados.

---

# 4. Redis no projeto

## 4.1 Usos do Redis

O Redis será usado para:

* debounce de mensagens;
* fila simples de conversas pendentes;
* lock de processamento por conversa;
* evitar chamadas duplicadas à OpenAI;
* possível retry futuro.

---

## 4.2 Estratégia recomendada

Usaremos Redis com dois conceitos:

### Chave de debounce por conversa

```txt
debounce:conversation:{conversation_id}
```

Essa chave terá TTL em segundos.

Sempre que uma nova mensagem do cliente chegar, o backend renova essa chave.

Exemplo:

```txt
SET debounce:conversation:abc123 1 EX 8
```

### Fila de conversas para processamento

```txt
queue:conversation-processing
```

Quando uma mensagem chega, o backend adiciona a conversa em uma estrutura de controle para processamento.

Para MVP, pode ser uma lista, stream ou sorted set.

A recomendação inicial é usar Redis Sorted Set, pois facilita controlar quando a conversa estará pronta para processamento.

Exemplo:

```txt
ZADD queue:conversation-processing <timestamp_process_at> <conversation_id>
```

Onde `timestamp_process_at` será:

```txt
agora + AGENT_DEBOUNCE_SECONDS
```

Sempre que uma nova mensagem chegar, o score da conversa no sorted set é atualizado para alguns segundos no futuro.

---

# 5. Fluxo com Redis

## 5.1 Quando chega mensagem do cliente

```txt
Cliente envia mensagem
  ↓
Evolution API envia webhook
  ↓
backend recebe webhook
  ↓
backend salva mensagem no PostgreSQL
  ↓
backend atualiza conversa
  ↓
backend agenda conversa no Redis
  ↓
backend retorna 200
```

O backend não chama OpenAI nesse momento.

---

## 5.2 Agendamento no Redis

Ao receber mensagem inbound:

```txt
conversation_id = conversa identificada
process_at = now + AGENT_DEBOUNCE_SECONDS
```

O backend executa:

```txt
ZADD queue:conversation-processing process_at conversation_id
SET debounce:conversation:{conversation_id} 1 EX AGENT_DEBOUNCE_SECONDS
```

Se o cliente mandar outra mensagem antes do tempo acabar, o backend atualiza o score no sorted set:

```txt
ZADD queue:conversation-processing novo_process_at conversation_id
```

Assim, o processamento é empurrado para frente.

---

## 5.3 Worker processando fila

O worker roda em loop.

A cada ciclo:

1. Busca conversas com score menor ou igual a `now`:

```txt
ZRANGEBYSCORE queue:conversation-processing -inf now LIMIT 0 10
```

2. Para cada conversa, tenta adquirir lock:

```txt
SET lock:conversation:{conversation_id} 1 NX EX 60
```

3. Se não conseguir lock, ignora.

4. Verifica no banco se:

```txt
conversation.ai_enabled = true
conversation.status = "ai_active"
```

5. Busca mensagens inbound não processadas desde `last_agent_processed_at`.

6. Agrupa mensagens em uma única entrada.

7. Chama o agente.

8. Salva resposta no PostgreSQL.

9. Envia resposta pela Evolution API.

10. Atualiza:

```txt
conversation.last_agent_processed_at = now
conversation.pending_agent_processing = false
```

11. Remove da fila Redis:

```txt
ZREM queue:conversation-processing conversation_id
```

12. Remove lock:

```txt
DEL lock:conversation:{conversation_id}
```

---

# 6. Campos adicionais no banco

A tabela `conversations` deve incluir:

```txt
pending_agent_processing boolean default false
last_customer_message_at datetime nullable
last_agent_processed_at datetime nullable
last_processing_error text nullable
processing_attempts int default 0
```

Mesmo usando Redis, esses campos são úteis para auditoria, fallback e debug.

---

# 7. Variáveis de ambiente

## 7.1 Backend

Adicionar ao `backend/.env.example`:

```env
REDIS_URL=redis://redis:6379/0
AGENT_DEBOUNCE_SECONDS=8
CONVERSATION_LOCK_SECONDS=60
```

## 7.2 Workers

Criar `workers/.env.example`:

```env
APP_ENV=development

BACKEND_INTERNAL_API_URL=http://backend:8000
BACKEND_INTERNAL_API_KEY=change-me

REDIS_URL=redis://redis:6379/0

AGENT_DEBOUNCE_SECONDS=8
CONVERSATION_LOCK_SECONDS=60
WORKER_POLL_INTERVAL_SECONDS=1
WORKER_BATCH_SIZE=10
```

---

# 8. Docker Compose

O `docker-compose.yml` raiz deve incluir:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: car_agent_db
      POSTGRES_USER: car_agent_user
      POSTGRES_PASSWORD: car_agent_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis
      - crm-mock
    ports:
      - "8000:8000"

  crm-mock:
    build: ./crm-mock
    ports:
      - "8001:8001"

  workers:
    build: ./workers
    env_file:
      - ./workers/.env
    depends_on:
      - backend
      - redis
      - postgres
      - crm-mock

volumes:
  postgres_data:
  redis_data:
```

---

# 9. Organização do `/workers`

Estrutura sugerida:

```txt
workers/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── redis.py
│   │   └── logging.py
│   │
│   ├── services/
│   │   ├── backend_client.py
│   │   └── conversation_queue.py
│   │
│   └── workers/
│       └── conversation_processor.py
│
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

# 10. Como o worker chama o backend

Para evitar duplicar regras de negócio no `/workers`, o caminho mais limpo para o MVP é:

```txt
worker -> backend endpoint interno -> backend processa conversa
```

Criar no backend:

```txt
POST /api/internal/conversations/{conversation_id}/process
```

Esse endpoint deve:

* exigir uma chave interna;
* verificar se a conversa pode ser processada;
* agrupar mensagens;
* chamar AgentService;
* salvar resposta;
* enviar mensagem pela Evolution;
* atualizar lead;
* retornar status do processamento.

O worker fica responsável por:

* Redis;
* debounce;
* lock;
* decidir quando chamar o backend.

O backend fica responsável por:

* regra de negócio;
* banco;
* agente;
* Evolution;
* lead.

Essa separação evita que o worker tenha que importar diretamente modelos, repositories e services do backend.

---

# 11. Segurança dos endpoints internos

Criar variável no backend:

```env
INTERNAL_API_KEY=change-me
```

O worker deve enviar header:

```txt
X-Internal-Api-Key: change-me
```

Endpoints internos devem validar essa chave.

---

# 12. Fluxo final recomendado

```txt
1. Cliente manda uma ou várias mensagens no WhatsApp.

2. Evolution envia webhook para:
   POST /api/webhooks/evolution/{instance_name}

3. Backend:
   - salva mensagem;
   - atualiza conversa;
   - marca pending_agent_processing=true;
   - agenda conversation_id no Redis;
   - retorna 200.

4. Worker:
   - monitora Redis;
   - espera passar o debounce;
   - adquire lock da conversa;
   - chama endpoint interno do backend.

5. Backend:
   - busca mensagens novas;
   - junta mensagens em um único texto;
   - chama OpenAI;
   - consulta crm-mock se necessário;
   - salva agent_run;
   - salva mensagem outbound;
   - envia resposta pela Evolution;
   - atualiza lead;
   - marca conversa como processada.

6. Worker:
   - remove conversa da fila Redis;
   - libera lock.
```

---

# 13. Exemplo prático de debounce

Cliente manda:

```txt
T+00s: Oi
T+02s: Queria ver um Corolla
T+04s: Automático
T+06s: Até uns 120 mil
```

Com:

```env
AGENT_DEBOUNCE_SECONDS=8
```

O Redis será atualizado assim:

```txt
T+00s: processar em T+08s
T+02s: processar em T+10s
T+04s: processar em T+12s
T+06s: processar em T+14s
```

O worker só processa em T+14s.

Entrada consolidada enviada para o agente:

```txt
Oi
Queria ver um Corolla
Automático
Até uns 120 mil
```

Resposta única:

```txt
Olá! Temos algumas opções de Corolla automático nessa faixa. Encontrei um Corolla XEi 2021 por R$119.900. Você pretende comprar à vista, financiar ou tem veículo para troca?
```

---

# 14. Critérios de aceite

O Redis/workers estarão corretos quando:

1. O webhook não chamar OpenAI diretamente.
2. Cada mensagem recebida for salva imediatamente no banco.
3. Várias mensagens seguidas forem agrupadas.
4. O agente responder apenas uma vez após o período de debounce.
5. O worker conseguir processar conversas pendentes.
6. O lock impedir processamento duplicado da mesma conversa.
7. O backend continuar centralizando banco, Evolution, OpenAI e CRM mock.
8. O `/workers` não acessar diretamente o banco no MVP.
9. O `/frontend` não acessar Redis, Evolution ou CRM mock diretamente.
10. O sistema continuar funcionando mesmo se o worker reiniciar.

---

# 15. Evoluções futuras

Depois do MVP, o Redis também poderá ser usado para:

* retry de envio de mensagem;
* fila de mensagens outbound;
* controle de rate limit;
* cache de dados do CRM;
* cache de contexto curto de conversa;
* jobs de análise de leads;
* notificações para vendedores;
* relatórios assíncronos.
