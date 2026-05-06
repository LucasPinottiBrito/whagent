Você é um engenheiro de software sênior, especialista em Python, FastAPI, sistemas assíncronos, filas, Redis, PostgreSQL, integrações via webhook, agentes de IA e boas práticas de arquitetura backend.

Quero que você desenvolva o projeto Whagent, uma plataforma SaaS simples para atendimento via WhatsApp de lojas de carros usando agente de IA.

O objetivo deste prompt é implementar o projeto com foco em:

- código estável;
- arquitetura simples;
- comportamento previsível;
- boa separação de responsabilidades;
- facilidade de manutenção;
- testes isolados por componente;
- debug local do agente;
- documentação clara;
- sem overengineering;
- sem criar arquivos desnecessários ou não funcionais;
- sem inventar informações, bibliotecas, endpoints ou comportamentos não especificados.

Antes de implementar qualquer coisa:
1. Analise a estrutura atual do repositório.
2. Leia os arquivos existentes em `/docs`, se existirem.
3. Identifique o que já está implementado.
4. Não sobrescreva código funcional sem necessidade.
5. Apresente um plano curto de implementação dividido por fases.
6. Execute uma fase por vez.
7. Após cada fase, explique o que foi feito, quais arquivos foram criados/alterados e quais testes foram adicionados.
8. Quando houver dúvida sobre uma biblioteca, API, framework ou integração, pesquise a documentação oficial antes de implementar.
9. Nunca invente comportamento de APIs externas. Se a documentação não estiver clara, registre a dúvida e implemente uma abstração segura.

====================================================================
1. VISÃO GERAL DO PROJETO
====================================================================

O Whagent é uma plataforma para atendimento automatizado via WhatsApp para lojas de carros.

A plataforma deve:

- receber mensagens de clientes via Evolution API;
- salvar clientes, conversas, mensagens, leads, handoffs e execuções do agente;
- agrupar mensagens consecutivas do cliente usando Redis com debounce;
- processar conversas de forma assíncrona usando worker separado;
- chamar um agente de IA para responder em português do Brasil;
- consultar um CRM mock de veículos;
- qualificar leads;
- permitir takeover humano;
- permitir devolver a conversa para a IA;
- funcionar localmente mesmo sem chave OpenAI usando fallback determinístico;
- permitir debug isolado do agente via chat local.

A estrutura obrigatória do repositório é:

/
├── backend/
├── crm-mock/
├── frontend/
├── docs/
├── workers/
├── docker-compose.yml
├── README.md
└── .gitignore

Não crie outras pastas de primeiro nível sem necessidade real.

====================================================================
2. PRINCÍPIOS ARQUITETURAIS OBRIGATÓRIOS
====================================================================

A arquitetura deve seguir estas regras:

1. O `/backend` é o cérebro do sistema.
2. O `/workers` não deve acessar diretamente o banco de dados.
3. O `/workers` deve falar com Redis e chamar endpoints internos do backend.
4. O webhook da Evolution nunca deve chamar OpenAI diretamente.
5. O webhook deve retornar rápido.
6. Toda mensagem válida deve ser salva antes de qualquer processamento de IA.
7. Redis deve ser usado apenas para fila simples, debounce e lock.
8. O AgentService não deve salvar diretamente no banco.
9. O ConversationProcessingService deve orquestrar processamento, lead, agent_run e envio.
10. EvolutionService deve centralizar chamadas para Evolution API.
11. CrmMockClient deve centralizar chamadas para `/crm-mock`.
12. O frontend deve falar somente com o backend.
13. O frontend nunca deve acessar diretamente:
    - Redis;
    - Evolution API;
    - OpenAI;
    - CRM mock;
    - PostgreSQL.
14. O sistema deve ser simples antes de ser sofisticado.
15. Não implementar filas complexas, dead-letter, backoff sofisticado ou mensageria avançada no MVP.
16. Não usar LangChain.
17. Não usar LangGraph.
18. Não usar Celery no MVP.
19. Não usar autenticação externa.
20. Não usar Firebase Auth, Supabase Auth, Clerk ou Auth0.
21. Não criar módulos, factories, adapters ou abstrações genéricas sem necessidade real.
22. Não criar arquivos vazios ou quase vazios só para parecer arquitetura sofisticada.
23. Não criar CRUDs administrativos completos se não forem solicitados nesta fase.
24. Não implementar painel SaaS completo nesta primeira versão.
25. Manter o código legível, tipado, testável e documentado.

====================================================================
3. STACK PRINCIPAL
====================================================================

Backend:

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x ou SQLModel
- Alembic
- Pydantic v2
- JWT local
- passlib/bcrypt ou alternativa segura documentada
- httpx
- redis-py
- OpenAI Python SDK
- pytest
- pytest-asyncio, se necessário

Workers:

- Python 3.11+
- redis-py
- httpx
- pydantic-settings
- pytest

CRM mock:

- Python 3.11+
- FastAPI
- Pydantic
- dados em memória
- sem banco
- sem autenticação

Frontend:

- Next.js
- React
- TypeScript
- estrutura mínima
- health check do backend
- sem painel operacional completo no MVP

Infra local:

- Docker Compose
- PostgreSQL
- Redis
- backend
- crm-mock
- workers
- frontend opcional ou preparado

====================================================================
4. MODELO MENTAL DO PROCESSAMENTO DE MENSAGENS
====================================================================

O fluxo principal deve ser:

Cliente envia WhatsApp
↓
Evolution API chama webhook
↓
Backend valida, classifica e salva mensagem
↓
Backend agenda processamento no Redis
↓
Worker espera o debounce vencer
↓
Worker adquire lock
↓
Worker chama endpoint interno do backend
↓
Backend agrupa mensagens pendentes
↓
Backend chama AgentService
↓
Backend salva AgentRun
↓
Backend cria/atualiza Lead
↓
Backend salva mensagem outbound
↓
Backend envia resposta pela Evolution
↓
Worker remove a conversa da fila
↓
Worker libera lock

Regra de ouro:

Webhook registra evento.
Redis controla tempo.
Worker dispara processamento.
Backend executa regra de negócio.
AgentService gera resposta.
EvolutionService envia mensagem.
CRM mock fornece dados fictícios.

====================================================================
5. FASES DE DESENVOLVIMENTO
====================================================================

Implemente em fases. Não tente fazer tudo em um único bloco.

--------------------------------------------------------------------
FASE 0 — Análise inicial do repositório
--------------------------------------------------------------------

Objetivo:
Entender o estado atual antes de alterar código.

Tarefas:
1. Listar estrutura atual do repositório.
2. Identificar se já existem `/backend`, `/workers`, `/crm-mock`, `/frontend` e `/docs`.
3. Identificar arquivos relevantes já existentes.
4. Identificar dependências já usadas.
5. Identificar se há código funcional que deve ser preservado.
6. Apresentar plano curto antes de alterar arquivos.

Critérios de aceite:
- Nenhum arquivo alterado antes da análise.
- Plano de implementação apresentado.
- Riscos ou dúvidas listados.

--------------------------------------------------------------------
FASE 1 — Estrutura base do monorepo e Docker Compose
--------------------------------------------------------------------

Objetivo:
Criar a estrutura mínima funcional sem poluir o projeto.

Criar ou ajustar:

/
├── backend/
├── crm-mock/
├── frontend/
├── docs/
├── workers/
├── docker-compose.yml
├── README.md
└── .gitignore

Docker Compose deve conter:

- postgres
- redis
- backend
- crm-mock
- workers

Frontend pode ficar configurado ou documentado como etapa inicial, sem obrigatoriedade de painel completo.

Não criar serviços extras.

Critérios de aceite:
- `docker-compose.yml` legível.
- Variáveis de ambiente documentadas.
- README com instruções locais.
- Nenhum arquivo inútil criado.

--------------------------------------------------------------------
FASE 2 — Backend base, configurações e health check
--------------------------------------------------------------------

Objetivo:
Criar API backend mínima e estável.

Implementar:

- FastAPI app.
- Configuração com pydantic-settings.
- Logging simples.
- Banco PostgreSQL.
- Sessão SQLAlchemy.
- Alembic.
- Rota `GET /health`.

Estrutura sugerida:

backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── api/
│   │   └── routes/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── tests/
├── alembic/
├── pyproject.toml
├── Dockerfile
├── .env.example
└── README.md

Não criar subpastas vazias desnecessárias.

Critérios de aceite:
- Backend sobe localmente.
- `GET /health` responde.
- Teste isolado para `/health`.
- README do backend explica como rodar.

--------------------------------------------------------------------
FASE 3 — Modelos de banco e migrations
--------------------------------------------------------------------

Objetivo:
Criar o modelo de dados mínimo para o fluxo central.

Entidades obrigatórias:

1. Store
2. User
3. WhatsAppInstance
4. Customer
5. Conversation
6. Message
7. Lead
8. HandoffEvent
9. AgentRun

Campos mínimos:

Store:
- id
- name
- slug
- document
- phone
- created_at
- updated_at

User:
- id
- store_id nullable
- email unique
- full_name
- role
- hashed_password
- is_active
- created_at
- updated_at

WhatsAppInstance:
- id
- store_id
- instance_name unique
- phone
- evolution_instance_id nullable
- webhook_secret
- active
- created_at
- updated_at

Customer:
- id
- store_id
- phone
- name nullable
- last_seen_at
- created_at
- updated_at

Regras:
- único por `store_id + phone`.

Conversation:
- id
- store_id
- customer_id
- whatsapp_instance_id
- status
- ai_enabled
- assigned_salesperson_id nullable
- last_intent nullable
- pending_agent_processing
- last_customer_message_at nullable
- last_agent_processed_at nullable
- last_agent_processed_message_id nullable, se viável
- last_processing_error nullable
- processing_attempts
- created_at
- updated_at

Status permitidos:
- ai_active
- human_active
- ai_disabled
- closed

Não implementar `handoff_requested`, pois não faz parte da lógica atual.

Message:
- id
- conversation_id
- direction
- sender_type
- content
- evolution_message_id nullable
- raw_payload JSON nullable
- created_at

Direction:
- inbound
- outbound

Sender type:
- customer
- agent
- human
- system

Importante:
- Criar deduplicação por `evolution_message_id` quando ele existir.
- A constraint precisa ser pensada com cuidado para permitir mensagens sem id externo.
- Se usar PostgreSQL, pode usar índice único parcial para `evolution_message_id IS NOT NULL`.

Lead:
- id
- store_id
- customer_id
- conversation_id unique
- status
- score
- intent nullable
- vehicle_interest nullable
- budget_min nullable
- budget_max nullable
- payment_type nullable
- trade_in_vehicle nullable
- interest_summary nullable
- created_at
- updated_at

HandoffEvent:
- id
- conversation_id
- salesperson_id nullable
- event_type
- reason nullable
- metadata JSON nullable
- created_at

AgentRun:
- id
- conversation_id
- input_text
- output_text nullable
- model nullable
- tools_used JSON nullable
- raw_response JSON nullable
- status
- error nullable
- created_at
- updated_at

Critérios de aceite:
- Migration criada.
- Banco sobe e aplica migration.
- Testes simples de criação das entidades principais.
- Constraints importantes testadas, principalmente cliente único e message id duplicado.

--------------------------------------------------------------------
FASE 4 — Autenticação JWT local
--------------------------------------------------------------------

Objetivo:
Criar autenticação simples e local.

Implementar:

- `POST /api/auth/login`
- `GET /api/auth/me`

Roles:
- admin
- manager
- salesperson

JWT deve conter:
- sub
- role
- store_id
- exp

Regras:
- Login por email e senha.
- Negar usuário inexistente.
- Negar usuário inativo.
- Hash de senha seguro.
- Criar seed local com:
  - loja demo;
  - usuário admin;
  - instância WhatsApp demo;
  - vendedor demo, se houver tabela ou mock necessário.

Critérios de aceite:
- Teste de login válido.
- Teste de login inválido.
- Teste de `/me` com token válido.
- Teste de `/me` sem token.

--------------------------------------------------------------------
FASE 5 — CRM mock
--------------------------------------------------------------------

Objetivo:
Criar API mock separada para simular estoque e vendedores.

Estrutura:

crm-mock/
├── app/
│   ├── main.py
│   ├── data/
│   │   ├── vehicles.py
│   │   ├── stores.py
│   │   └── salespeople.py
│   ├── schemas.py
│   └── routes.py
├── pyproject.toml
├── Dockerfile
├── .env.example
└── README.md

Endpoints:

- GET /health
- GET /vehicles
- GET /vehicles/{vehicle_id}
- GET /stores
- GET /stores/{store_id}
- GET /salespeople
- GET /salespeople/{salesperson_id}
- GET /salespeople/suggest

Filtros em `/vehicles`:

- brand
- model
- year_min
- year_max
- max_price
- min_price
- transmission
- fuel
- status

Dados mínimos:
- Toyota Corolla 2021 automático flex disponível.
- Honda Civic 2020 automático flex disponível.
- Jeep Compass 2022 automático flex disponível.

Não usar banco.
Não usar auth.
Não complicar.

Critérios de aceite:
- CRM mock sobe.
- `/health` funciona.
- `/vehicles` retorna dados.
- Filtros básicos testados.

--------------------------------------------------------------------
FASE 6 — Clients externos no backend
--------------------------------------------------------------------

Objetivo:
Criar clientes internos para APIs externas.

Implementar:

1. `EvolutionService`
2. `CrmMockClient`
3. `AgentService`

EvolutionService:
- arquivo sugerido: `backend/app/services/evolution_service.py`
- método mínimo:
  - `send_text_message(instance_name: str, phone: str, text: str)`

Regras:
- Se `EVOLUTION_API_BASE_URL` ou `EVOLUTION_API_KEY` não estiverem configurados, usar `dry_run`.
- O dry_run deve salvar a mensagem no banco normalmente, mas indicar que não houve envio real.
- Não quebrar fluxo local sem Evolution configurada.

CrmMockClient:
- arquivo sugerido: `backend/app/services/crm_mock_client.py`
- métodos mínimos:
  - `search_vehicles(...)`
  - `get_vehicle(vehicle_id)`
  - `suggest_salesperson(...)`, se simples

AgentService:
- arquivo sugerido: `backend/app/services/agent_service.py`
- não deve salvar no banco.
- recebe texto consolidado e contexto mínimo.
- retorna objeto estruturado.

Formato de retorno esperado:

{
  "reply_text": "...",
  "intent": "...",
  "lead_status": "...",
  "score": 0,
  "vehicle_interest": "...",
  "budget_min": null,
  "budget_max": null,
  "payment_type": null,
  "trade_in_vehicle": null,
  "interest_summary": "..."
}

Com OpenAI configurado:
- Usar SDK oficial da OpenAI.
- Usar Responses API se for a API atual recomendada pela documentação oficial.
- Se houver dúvida sobre parâmetros, consultar documentação oficial da OpenAI.
- Não inventar formato de tool calling.
- Criar implementação clara, simples e testável.

Sem OpenAI configurado:
- Usar fallback determinístico.
- Buscar veículos disponíveis no CRM mock.
- Oferecer o primeiro veículo disponível.
- Perguntar sobre pagamento, orçamento ou troca.
- Não quebrar o fluxo local.

Critérios de aceite:
- Testes do CrmMockClient com mock HTTP.
- Teste do EvolutionService em dry_run.
- Teste do AgentService fallback.
- Código com docstrings curtas onde necessário.

--------------------------------------------------------------------
FASE 7 — Parser e política de origem do webhook Evolution
--------------------------------------------------------------------

Objetivo:
Isolar parsing e classificação de mensagens.

Criar componentes:

- `EvolutionWebhookParser`
- `MessageOriginPolicy`

O parser deve extrair:

- remoteJid
- phone normalizado
- text
- fromMe
- message_id
- pushName
- sent_by_agent
- source
- is_group
- raw_payload

Formatos textuais suportados:

- conversation
- text
- extendedTextMessage.text
- imageMessage.caption
- videoMessage.caption
- message aninhado, se existir no payload

Se não houver `remoteJid`, ignorar.
Se não houver texto reconhecível, ignorar.

A política de origem deve retornar uma decisão clara:

- customer_inbound
- human_outbound_takeover
- agent_echo_ignore
- ignored_from_me
- ignored_invalid
- duplicate

Regras:

1. Se `sent_by_agent=true` ou `source=agent`:
   - classificar como `agent_echo_ignore`;
   - não acionar handoff;
   - não agendar processamento.

2. Se `fromMe=true` e runtime permitir tratar fromMe como inbound:
   - classificar como `customer_inbound`.
   - usado apenas em debug/self-group.

3. Se `fromMe=true` e handoff humano estiver habilitado:
   - classificar como `human_outbound_takeover`;
   - salvar mensagem outbound humana;
   - desativar IA;
   - mudar conversa para `human_active`;
   - registrar handoff_event.

4. Se `fromMe=true` sem regra especial:
   - ignorar.

5. Se `fromMe=false`:
   - classificar como `customer_inbound`.

Critérios de aceite:
- Teste para payload sem remoteJid.
- Teste para payload sem texto.
- Teste para mensagem normal do cliente.
- Teste para eco do agente.
- Teste para fromMe humano.
- Teste para fromMe em modo debug/self-group.
- Teste para normalização de telefone.

--------------------------------------------------------------------
FASE 8 — Webhook da Evolution
--------------------------------------------------------------------

Objetivo:
Implementar o endpoint real de entrada.

Endpoint:

POST /api/webhooks/evolution/{instance_name}

Segurança:
- aceitar segredo por header `X-Evolution-Webhook-Secret`;
- aceitar segredo por query param `webhook_secret`;
- rejeitar segredo inválido com 401.

Fluxo:

1. Validar segredo.
2. Buscar WhatsAppInstance ativa por `instance_name`.
3. Parsear payload.
4. Deduplicar por `evolution_message_id`, se existir.
5. Localizar ou criar Customer por `store_id + phone`.
6. Atualizar `customer.last_seen_at`.
7. Preencher nome do cliente se vier no webhook e estiver vazio.
8. Localizar conversa aberta mais recente por:
   - store_id;
   - customer_id;
   - whatsapp_instance_id;
   - status != closed.
9. Criar conversa se não existir:
   - status=ai_active;
   - ai_enabled=true.
10. Classificar origem.
11. Se customer_inbound:
   - salvar Message direction=inbound sender_type=customer;
   - atualizar `last_customer_message_at`;
   - se IA ativa, marcar `pending_agent_processing=true`;
   - agendar conversa no Redis.
12. Se human_outbound_takeover:
   - salvar Message direction=outbound sender_type=human;
   - executar takeover;
   - não agendar Redis.
13. Se agent_echo_ignore:
   - não acionar handoff;
   - não agendar Redis.
14. Retornar rápido.

O webhook não deve chamar AgentService.
O webhook não deve chamar OpenAI.
O webhook não deve enviar mensagem outbound.

Critérios de aceite:
- Teste de segredo inválido.
- Teste de instância inexistente.
- Teste de inbound de cliente.
- Teste de criação de cliente.
- Teste de reuso de conversa.
- Teste de agendamento Redis.
- Teste de eco do agente.
- Teste de takeover por fromMe.
- Teste de deduplicação por evolution_message_id.

--------------------------------------------------------------------
FASE 9 — Redis, fila e debounce
--------------------------------------------------------------------

Objetivo:
Implementar fila simples com Redis Sorted Set.

Variáveis:

REDIS_URL=redis://redis:6379/0
AGENT_DEBOUNCE_SECONDS=8
CONVERSATION_LOCK_SECONDS=60
WORKER_POLL_INTERVAL_SECONDS=1
WORKER_BATCH_SIZE=10

Chaves:

Sorted Set:
queue:conversation-processing

Debounce:
debounce:conversation:{conversation_id}

Lock:
lock:conversation:{conversation_id}

Ao receber mensagem inbound processável:

process_at = now + AGENT_DEBOUNCE_SECONDS

Executar:

ZADD queue:conversation-processing process_at conversation_id
SET debounce:conversation:{conversation_id} 1 EX AGENT_DEBOUNCE_SECONDS

Se outra mensagem chegar antes do tempo vencer:
- atualizar o score do mesmo conversation_id;
- o processamento será empurrado para frente.

Criar serviço:

backend/app/services/conversation_queue_service.py

Responsabilidades:
- schedule_conversation(conversation_id)
- opcionalmente expose helpers simples para teste

Não colocar regra de negócio complexa nesse serviço.

Critérios de aceite:
- Teste isolado de cálculo de process_at.
- Teste de reagendamento do mesmo conversation_id.
- Teste de escrita no sorted set.
- Teste de TTL da chave de debounce, se viável.

--------------------------------------------------------------------
FASE 10 — Worker de processamento
--------------------------------------------------------------------

Objetivo:
Criar worker simples e confiável.

Estrutura:

workers/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── services/
│   │   ├── backend_client.py
│   │   └── redis_queue.py
│   └── worker.py
├── pyproject.toml
├── Dockerfile
├── .env.example
└── README.md

O worker deve:

1. Conectar no Redis.
2. Em loop, buscar conversas prontas:

ZRANGEBYSCORE queue:conversation-processing -inf now LIMIT 0 WORKER_BATCH_SIZE

3. Para cada conversation_id:
   - criar token único de lock;
   - tentar lock:

SET lock:conversation:{conversation_id} token NX EX CONVERSATION_LOCK_SECONDS

4. Se não conseguir lock:
   - ignorar e continuar.

5. Se conseguir lock:
   - chamar backend:

POST {BACKEND_INTERNAL_API_URL}/api/internal/conversations/{conversation_id}/process
Header: X-Internal-Api-Key: {BACKEND_INTERNAL_API_KEY}

6. Se backend responder 2xx:
   - remover da fila:

ZREM queue:conversation-processing conversation_id

7. Se backend responder não-2xx:
   - manter na fila;
   - logar erro;
   - não remover.

8. Liberar lock de forma segura:
   - só deletar o lock se o valor atual for igual ao token criado pelo worker.
   - usar Lua script ou operação equivalente segura.

O worker NÃO deve:
- acessar banco;
- importar models do backend;
- chamar OpenAI;
- chamar Evolution;
- chamar CRM mock;
- decidir se IA está ativa;
- decidir lead;
- agrupar mensagens.

O worker é apenas um disparador confiável.

Critérios de aceite:
- Teste do RedisQueue buscando conversas prontas.
- Teste de lock adquirido.
- Teste de lock não adquirido.
- Teste de unlock seguro por token.
- Teste de chamada ao backend.
- Teste: remove da fila apenas em 2xx.
- Teste: mantém na fila em erro.

--------------------------------------------------------------------
FASE 11 — Endpoint interno de processamento
--------------------------------------------------------------------

Objetivo:
Criar endpoint interno protegido usado pelo worker.

Endpoint:

POST /api/internal/conversations/{conversation_id}/process

Header obrigatório:

X-Internal-Api-Key

Fluxo:

1. Validar chave interna.
2. Se chave inválida, retornar 401.
3. Buscar conversa.
4. Se não existir, retornar 404.
5. Se runtime de IA estiver desabilitado, retornar skipped.
6. Se `conversation.ai_enabled=false`, retornar skipped.
7. Se `conversation.status != ai_active`, retornar skipped.
8. Buscar mensagens inbound pendentes:
   - direction=inbound;
   - sender_type=customer;
   - conversation_id correto;
   - criadas depois do último marcador processado.

Importante:
- Preferir usar `last_agent_processed_message_id` ou algum marcador seguro.
- Evitar usar apenas `now()` como marcador final, pois uma nova mensagem pode chegar durante o processamento.
- Se implementar apenas `last_agent_processed_at`, garantir que ele represente a última mensagem efetivamente incluída no input, e não simplesmente o horário atual após o processamento.

9. Se não houver mensagens pendentes:
   - marcar `pending_agent_processing=false`;
   - retornar skipped.

10. Agrupar mensagens em ordem cronológica com quebra de linha.
11. Criar AgentRun com status `running`.
12. Chamar AgentService.
13. Atualizar AgentRun com:
   - output_text;
   - model;
   - tools_used;
   - raw_response;
   - status=success.
14. Criar ou atualizar Lead.
15. Salvar Message outbound:
   - direction=outbound;
   - sender_type=agent;
   - content=reply_text.
16. Enviar resposta pela EvolutionService.
17. Atualizar Conversation:
   - last_intent;
   - last_agent_processed_at;
   - last_agent_processed_message_id, se implementado;
   - pending_agent_processing=false;
   - last_processing_error=null.
18. Retornar processed.

Em caso de erro:
- atualizar AgentRun com status=error, se existir;
- atualizar Conversation.last_processing_error;
- incrementar processing_attempts;
- retornar erro adequado;
- não mascarar exceções silenciosamente.

Critérios de aceite:
- Teste de chave inválida.
- Teste de conversa inexistente.
- Teste de IA desligada.
- Teste de status human_active.
- Teste sem mensagens pendentes.
- Teste com múltiplas mensagens agrupadas.
- Teste de criação de AgentRun.
- Teste de criação/atualização de Lead.
- Teste de Message outbound salva antes do envio.
- Teste de EvolutionService dry_run.
- Teste de erro do AgentService.

--------------------------------------------------------------------
FASE 12 — AgentService e prompt do agente
--------------------------------------------------------------------

Objetivo:
Criar agente de atendimento simples, controlado e depurável.

O agente deve:

- responder em português do Brasil;
- agir como atendente de loja de carros;
- qualificar lead;
- perguntar informações faltantes;
- consultar veículos via CRM mock quando fizer sentido;
- nunca inventar veículos;
- nunca prometer disponibilidade fora do retorno do CRM;
- retornar dados estruturados;
- funcionar com fallback determinístico sem OpenAI.

Campos estruturados esperados:

- reply_text
- intent
- lead_status
- score
- vehicle_interest
- budget_min
- budget_max
- payment_type
- trade_in_vehicle
- interest_summary

Tool mínima:
- search_vehicles

Regras:
1. Se o cliente pedir modelo, marca, faixa de preço, câmbio, ano ou disponibilidade, consultar CRM.
2. Se não houver dados suficientes, perguntar de forma objetiva.
3. Se encontrar veículo compatível, oferecer no máximo 1 ou 2 opções.
4. Não transformar a resposta em texto longo.
5. Não usar tom robótico.
6. Não pressionar o cliente.
7. Não inventar preço, modelo, ano ou disponibilidade.
8. Não mencionar detalhes internos do sistema.
9. Não mencionar OpenAI, ferramenta, CRM mock ou backend.
10. Sempre produzir resposta final compatível com WhatsApp.

Debug:
- Criar forma de testar o AgentService isoladamente, sem webhook e sem Evolution.
- Implementar um script CLI simples:

backend/scripts/agent_chat.py

Esse script deve permitir uma conversa local no terminal:

Usuário digita mensagem
↓
Script chama AgentService
↓
Mostra reply_text e dados estruturados
↓
Mantém contexto mínimo em memória durante a sessão

Regras do script:
- Não acessar Evolution.
- Não salvar mensagem real no banco, a menos que seja explicitamente configurado como modo persistente.
- Por padrão, ser modo local/ephemeral.
- Permitir testar com fallback sem OpenAI.
- Permitir testar com OpenAI se `OPENAI_API_KEY` estiver configurada.
- Exibir, quando possível:
  - input enviado;
  - resposta;
  - intent;
  - score;
  - vehicle_interest;
  - tools usadas.

Não criar interface web para isso no MVP, a menos que já exista infraestrutura simples. O CLI é suficiente.

Critérios de aceite:
- Teste do fallback determinístico.
- Teste com busca de veículos mockada.
- Teste validando que o agente não inventa veículo.
- Script `agent_chat.py` documentado no README.
- Instrução de uso clara.

--------------------------------------------------------------------
FASE 13 — Handoff humano
--------------------------------------------------------------------

Objetivo:
Implementar takeover e release.

Endpoints:

POST /api/conversations/{conversation_id}/takeover
POST /api/conversations/{conversation_id}/release-to-ai

Ambos exigem JWT.

Roles permitidas:
- admin
- manager
- salesperson

Regras de loja:
- Se usuário tiver `store_id`, só pode atuar em conversas da mesma loja.
- Admin sem store_id pode atuar em qualquer conversa, se esse padrão for adotado.

Takeover:
- status=human_active
- ai_enabled=false
- registrar HandoffEvent:
  - event_type=takeover
  - reason, se informado

Release:
- status=ai_active
- ai_enabled=true
- registrar HandoffEvent também, mesmo que a implementação antiga não fizesse isso, pois é melhor para auditoria.
- event_type=release_to_ai

Takeover automático:
- Quando webhook receber `fromMe=true` e a mensagem não for do agente:
  - salvar mensagem outbound humana;
  - status=human_active;
  - ai_enabled=false;
  - registrar HandoffEvent event_type=manual_from_me;
  - não agendar Redis.

Critérios de aceite:
- Teste de takeover autenticado.
- Teste de release autenticado.
- Teste de bloqueio por role inválida.
- Teste de bloqueio por loja diferente.
- Teste de takeover automático via webhook.

--------------------------------------------------------------------
FASE 14 — Debug local e simulação de fluxo
--------------------------------------------------------------------

Objetivo:
Facilitar desenvolvimento sem depender de WhatsApp real.

Implementar rotas de debug apenas fora de produção.

As rotas `/api/debug/*` só devem existir se APP_ENV não for:
- prod
- production

Endpoints úteis:

GET /api/debug/runtime
PATCH /api/debug/runtime
POST /api/debug/runtime/reset
POST /api/debug/modes/self-group
POST /api/debug/modes/external-tester
POST /api/debug/evolution/simulate-inbound
GET /api/debug/conversations/{conversation_id}
POST /api/debug/conversations/{conversation_id}/ai/disable
POST /api/debug/conversations/{conversation_id}/ai/enable
POST /api/debug/conversations/{conversation_id}/human/takeover
POST /api/debug/conversations/{conversation_id}/human/release

Não gastar tempo criando dashboard de debug.

A timeline da conversa deve retornar:
- conversa;
- cliente;
- mensagens;
- lead;
- agent_runs;
- handoff_events;
- estado atual;
- pendências de processamento, se simples consultar.

Simulação inbound:
- deve montar payload semelhante ao Evolution;
- deve chamar a mesma lógica do webhook real;
- opcionalmente permitir `process_now=true` para chamar o processamento interno no mesmo request.

Critérios de aceite:
- Rotas não aparecem em produção.
- Simulação cria cliente/conversa/mensagem.
- Simulação pode agendar Redis.
- Simulação pode processar imediatamente quando solicitado.
- Timeline mostra mensagens, lead e agent_runs.

--------------------------------------------------------------------
FASE 15 — Frontend mínimo
--------------------------------------------------------------------

Objetivo:
Manter frontend simples no MVP.

Implementar apenas:

- página inicial;
- chamada ao `GET /health` do backend;
- exibição de status online/offline;
- README explicando que painel operacional completo será fase futura.

Não implementar:
- dashboard completo;
- listagem de conversas;
- CRUD de loja;
- CRUD de usuários;
- tela de leads;
- envio manual de mensagens;
- gráficos;
- relatórios.

Critérios de aceite:
- Frontend sobe.
- Mostra health do backend.
- Não fala com CRM mock, Redis, Evolution ou banco.

--------------------------------------------------------------------
FASE 16 — Documentação
--------------------------------------------------------------------

Objetivo:
Criar documentação útil, curta e verdadeira.

Criar ou atualizar:

docs/
├── 01-visao-geral.md
├── 02-arquitetura.md
├── 03-fluxo-whatsapp-evolution.md
├── 04-redis-workers-debounce.md
├── 05-agente-ia.md
├── 06-crm-mock.md
├── 07-modelo-dados.md
├── 08-auth-jwt.md
├── 09-handoff-humano.md
├── 10-debug-local.md
└── 11-roadmap.md

Regras:
- Documentar apenas o que existe ou o que é explicitamente roadmap.
- Não dizer que existe painel operacional se ele não existir.
- Não dizer que existe CRM real se só existe mock.
- Não dizer que existe retry/backoff/dead-letter se não foi implementado.
- Cada documento deve ser objetivo.
- Não criar documentação enorme e genérica.
- Incluir exemplos de comandos locais.

Critérios de aceite:
- Docs refletem o código real.
- README principal explica como rodar tudo.
- README explica como testar o AgentService via chat CLI.
- README explica como simular inbound.

--------------------------------------------------------------------
FASE 17 — Testes e qualidade
--------------------------------------------------------------------

Objetivo:
Garantir estabilidade do MVP.

Criar testes isolados por ponto.

Testes mínimos:

Backend:
- health
- auth login
- auth me
- criação/reuso de customer
- criação/reuso de conversation
- parser Evolution
- política de origem
- webhook inbound
- webhook agent echo
- webhook human takeover
- deduplicação por evolution_message_id
- Redis schedule service
- endpoint interno com chave inválida
- endpoint interno sem mensagens pendentes
- endpoint interno com mensagens agrupadas
- AgentService fallback
- Lead update
- EvolutionService dry_run
- takeover autenticado
- release autenticado

Worker:
- busca conversas prontas
- lock adquirido
- lock recusado
- unlock seguro por token
- chamada backend
- remove da fila apenas em 2xx
- mantém na fila em erro

CRM mock:
- health
- listagem vehicles
- filtros principais

Frontend:
- health call, se houver setup de teste simples

Boas práticas:
- Testes devem ser pequenos e isolados.
- Não depender de OpenAI real nos testes.
- Não depender de Evolution real nos testes.
- Usar mocks/fakes para HTTP externo.
- Não criar testes frágeis baseados em horário real sem controlar o tempo.
- Priorizar testes de regra de negócio.

Critérios de aceite:
- Testes rodam localmente.
- Instrução clara no README.
- Nenhum teste depende de serviço externo pago.

====================================================================
6. DETALHAMENTO DA FILA DE PROCESSAMENTO
====================================================================

A fila deve usar Redis Sorted Set.

Nome:

queue:conversation-processing

Cada item:
- member: conversation_id
- score: timestamp Unix de quando a conversa deve ser processada

Ao chegar inbound processável:

process_at = now + AGENT_DEBOUNCE_SECONDS

Executar:

ZADD queue:conversation-processing process_at conversation_id
SET debounce:conversation:{conversation_id} 1 EX AGENT_DEBOUNCE_SECONDS

Motivo:
- se o cliente mandar várias mensagens seguidas, o mesmo conversation_id é reagendado;
- o agente só responde depois que o cliente parar de digitar por alguns segundos.

Exemplo:

T+00s: "Oi"
T+02s: "Queria ver um Corolla"
T+04s: "Automático"
T+06s: "Até 120 mil"

Com debounce de 8 segundos:

T+00s -> processar T+08s
T+02s -> processar T+10s
T+04s -> processar T+12s
T+06s -> processar T+14s

O agente recebe uma entrada única:

"Oi
Queria ver um Corolla
Automático
Até 120 mil"

E gera uma única resposta.

====================================================================
7. DETALHAMENTO DO WORKER
====================================================================

O worker deve ser simples.

Pseudo fluxo:

while True:
    now = current_timestamp()
    conversation_ids = redis.zrangebyscore(
        "queue:conversation-processing",
        "-inf",
        now,
        start=0,
        num=WORKER_BATCH_SIZE
    )

    for conversation_id in conversation_ids:
        token = uuid4()
        lock_key = f"lock:conversation:{conversation_id}"

        acquired = redis.set(
            lock_key,
            token,
            nx=True,
            ex=CONVERSATION_LOCK_SECONDS
        )

        if not acquired:
            continue

        try:
            response = backend_client.process_conversation(conversation_id)

            if response.status_code >= 200 and response.status_code < 300:
                redis.zrem("queue:conversation-processing", conversation_id)
            else:
                log error and keep in queue

        finally:
            release lock only if current value == token

    sleep(WORKER_POLL_INTERVAL_SECONDS)

Regras importantes:

- Não remover da fila se o backend falhar.
- Não remover da fila se receber 500.
- Não remover da fila se timeout.
- Não acessar banco.
- Não processar a conversa localmente no worker.
- Não chamar AgentService diretamente.
- Não chamar OpenAI diretamente.
- Não chamar Evolution diretamente.
- Liberar lock de forma atômica comparando token.
- Usar logs claros.

====================================================================
8. DETALHAMENTO DO PROCESSAMENTO INTERNO
====================================================================

O backend deve agrupar mensagens pendentes.

Mensagens pendentes:

- conversation_id igual;
- direction=inbound;
- sender_type=customer;
- ainda não processadas.

Preferência:
- usar `last_agent_processed_message_id` como marcador.
- Se isso complicar muito, usar `last_agent_processed_at`, mas com cuidado para marcar o timestamp da última mensagem realmente processada, não o horário final da execução.

Não incluir no input:
- mensagens outbound do agente;
- mensagens outbound humanas;
- mensagens system;
- mensagens antigas já processadas.

O texto enviado ao agente deve preservar a ordem cronológica.

Exemplo:

Mensagem 1: Oi
Mensagem 2: Quero um Corolla
Mensagem 3: Até 120 mil

Input:

Oi
Quero um Corolla
Até 120 mil

====================================================================
9. BOAS PRÁTICAS DE CÓDIGO
====================================================================

Siga obrigatoriamente:

1. Código simples e direto.
2. Funções pequenas.
3. Nomes claros.
4. Tipagem sempre que possível.
5. Validação com Pydantic.
6. Serviços com responsabilidade única.
7. Evitar classes abstratas desnecessárias.
8. Evitar herança sem necessidade.
9. Evitar padrões complexos sem motivo.
10. Não duplicar regra de negócio.
11. Não deixar regra de negócio no router.
12. Não deixar regra de negócio no worker.
13. Não deixar regra de negócio no AgentService.
14. Não capturar exceções silenciosamente.
15. Logs úteis, sem poluição excessiva.
16. Comentários apenas onde ajudam.
17. Docstrings curtas em funções importantes.
18. Arquivos README curtos e práticos.
19. Testes próximos dos comportamentos críticos.
20. Não criar código morto.

====================================================================
10. DOCUMENTAÇÃO NO CÓDIGO
====================================================================

O código deve ser bem documentado, mas sem exagero.

Use comentários para explicar:

- decisões de fila;
- motivo do debounce;
- motivo do lock com token;
- motivo do webhook não chamar OpenAI;
- política de origem da mensagem;
- fallback do agente;
- dry_run da Evolution;
- cuidados com marcador de mensagens processadas.

Não comentar o óbvio.

Exemplo ruim:

# incrementa contador
counter += 1

Exemplo bom:

# O lock usa token para impedir que um worker antigo remova
# acidentalmente o lock renovado por outro worker.
release_lock_if_token_matches(...)

====================================================================
11. DEBUG ISOLADO DO AGENTE VIA CHAT
====================================================================

Implementar ferramenta simples para conversar com o agente sem WhatsApp.

Arquivo sugerido:

backend/scripts/agent_chat.py

Comportamento:

- inicia sessão no terminal;
- aceita mensagens digitadas pelo desenvolvedor;
- chama AgentService;
- mostra resposta final;
- mostra dados estruturados;
- mostra tools usadas, se houver;
- permite sair com `exit` ou `quit`.

Exemplo de uso:

cd backend
python scripts/agent_chat.py

Exemplo de interação:

Você: Quero um Corolla automático até 120 mil
Agente: Temos uma opção interessante...
Intent: vehicle_search
Score: 75
Vehicle interest: Toyota Corolla
Tools used: search_vehicles

Regras:

- Por padrão, não salva conversa no banco.
- Por padrão, não envia nada para Evolution.
- Pode usar CRM mock.
- Pode usar fallback sem OpenAI.
- Se OpenAI estiver configurado, pode usar OpenAI.
- Deve ser documentado no README.
- Não criar interface complexa para isso.

====================================================================
12. O QUE NÃO IMPLEMENTAR NO MVP
====================================================================

Não implementar agora:

- painel SaaS completo;
- CRUD completo de lojas;
- CRUD completo de usuários;
- CRUD completo de instâncias;
- dashboards;
- relatórios;
- atribuição automática sofisticada de vendedores;
- CRM real;
- integração com múltiplos CRMs;
- fila com dead-letter;
- retry com backoff sofisticado;
- rate limit avançado;
- sistema de permissões complexo;
- refresh token;
- recuperação de senha;
- logout com blacklist;
- mensageria outbound humana via painel;
- envio de mídia;
- áudio;
- transcrição;
- múltiplos agentes especializados;
- LangChain;
- LangGraph;
- Celery;
- Kafka;
- RabbitMQ;
- Kubernetes;
- observabilidade complexa.

Se algo parecer necessário, documente como roadmap antes de implementar.

====================================================================
13. PESQUISA EM DOCUMENTAÇÕES
====================================================================

Nunca invente informações.

Quando houver dúvida, consulte a documentação oficial de:

- FastAPI;
- SQLAlchemy;
- Alembic;
- Pydantic;
- Redis;
- redis-py;
- OpenAI Python SDK;
- OpenAI Responses API;
- Evolution API;
- Next.js;
- Docker Compose.

Se a documentação oficial não for suficiente:
- registre a dúvida;
- implemente a menor abstração segura;
- deixe TODO explícito e justificado;
- não invente payloads externos como se fossem verdade.

Para Evolution API:
- não assumir formato de payload sem confirmar.
- criar parser tolerante.
- preservar raw_payload.
- documentar campos suportados.

Para OpenAI:
- não inventar formato de chamada.
- usar SDK oficial.
- se a API tiver mudado, ajustar conforme documentação oficial.
- evitar APIs legadas se a documentação atual recomendar outro caminho.

====================================================================
14. CRITÉRIOS FINAIS DE ACEITE
====================================================================

O MVP estará correto quando:

1. Docker Compose sobe PostgreSQL, Redis, backend, crm-mock e worker.
2. Backend responde `GET /health`.
3. CRM mock responde `GET /health`.
4. Backend possui login JWT local.
5. Migrations criam tabelas principais.
6. Seed cria dados demo mínimos.
7. Webhook Evolution recebe mensagem inbound.
8. Webhook valida segredo.
9. Webhook ignora payload inválido.
10. Webhook deduplica por `evolution_message_id`.
11. Webhook salva mensagem inbound.
12. Webhook não chama OpenAI.
13. Webhook agenda conversa no Redis.
14. Redis reagenda mesma conversa em mensagens consecutivas.
15. Worker busca conversas prontas pelo score.
16. Worker adquire lock por conversa.
17. Worker chama endpoint interno do backend.
18. Worker não acessa banco.
19. Worker remove da fila apenas se backend responder 2xx.
20. Worker libera lock comparando token.
21. Endpoint interno valida `X-Internal-Api-Key`.
22. Endpoint interno ignora conversa com IA desligada.
23. Endpoint interno ignora conversa em `human_active`.
24. Endpoint interno agrupa mensagens pendentes.
25. AgentService gera resposta estruturada.
26. AgentService funciona sem OpenAI usando fallback.
27. AgentService consulta CRM mock quando adequado.
28. Agente não inventa veículos.
29. Backend salva AgentRun.
30. Backend cria ou atualiza Lead.
31. Backend salva mensagem outbound antes de enviar.
32. EvolutionService suporta dry_run.
33. Takeover humano desativa IA.
34. Release para IA reativa IA.
35. Mensagem `fromMe=true` humana aciona takeover.
36. Eco do agente não aciona takeover.
37. Debug local permite simular inbound.
38. Debug local permite testar agente via chat CLI.
39. Frontend mínimo mostra status do backend.
40. README explica como rodar, testar e debugar.
41. Testes isolados cobrem os principais fluxos.
42. Código não contém arquivos inúteis ou placeholders excessivos.
43. Documentação não promete funcionalidades inexistentes.
44. O sistema permanece simples, estável e fácil de evoluir.

====================================================================
15. FORMA DE TRABALHO ESPERADA
====================================================================

Trabalhe de forma incremental.

Para cada fase:

1. Explique rapidamente o objetivo.
2. Liste arquivos que pretende criar/alterar.
3. Implemente.
4. Rode ou descreva os testes aplicáveis.
5. Explique como validar manualmente.
6. Não avance para a próxima fase se a fase atual estiver quebrada.
7. Se encontrar inconsistência no escopo, pare e explique.
8. Se precisar consultar documentação, consulte antes de codar.
9. Se algo for incerto, não invente: documente a decisão e implemente de forma segura.

Prioridade máxima:
- estabilidade;
- clareza;
- simplicidade;
- testes;
- manutenção futura.

Não tente impressionar com complexidade.
Implemente um MVP sólido.