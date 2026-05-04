# Estrutura do Repositório - Plataforma de Agente IA para WhatsApp

## 1. Objetivo deste documento

Este documento define a estrutura base do repositório da plataforma de atendimento com agente de IA para lojas de carros.

A aplicação será organizada como um monorepo simples, separando claramente:

- backend principal da plataforma;
- API mockada de CRM;
- frontend da plataforma;
- documentações;
- workers futuros.

O objetivo é manter o projeto simples, extensível e fácil de evoluir para um SaaS real.

---

## 2. Estrutura obrigatória do repositório

A estrutura raiz do projeto deve respeitar o seguinte formato:

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
````

---

# 3. Diretório `/backend`

## 3.1 Responsabilidade

O diretório `/backend` será a API principal da plataforma.

Ele será responsável por:

* receber webhooks da Evolution API;
* processar mensagens recebidas do WhatsApp;
* centralizar a comunicação com a Evolution API;
* centralizar o acesso ao banco PostgreSQL;
* gerenciar autenticação dos usuários da plataforma;
* gerenciar lojas, usuários, conversas, mensagens e leads;
* chamar a OpenAI API;
* coordenar o agente de IA;
* consultar o `/crm-mock` quando precisar de dados fictícios de veículos, lojas ou vendedores;
* controlar quando a IA deve responder ou parar de responder;
* expor endpoints para o futuro frontend.

O `/backend` deve ser tratado como o núcleo real do SaaS.

---

## 3.2 Stack do backend

O backend deve ser desenvolvido com:

* Python 3.11+
* FastAPI
* PostgreSQL
* SQLAlchemy 2.x ou SQLModel
* Alembic
* Pydantic
* JWT local
* bcrypt/passlib para hash de senha
* OpenAI Python SDK
* httpx
* pytest
* Docker

Não usar:

* LangChain
* LangGraph
* autenticação terceirizada no MVP
* Firebase Auth
* Supabase Auth
* Auth0
* Clerk

A autenticação deve ser **JWT nativa e local**, implementada no próprio backend.

---

## 3.3 Autenticação

O backend deve implementar autenticação SaaS comum, sem complexidade desnecessária.

### Funcionalidades mínimas

* cadastro de usuário admin inicial via seed;
* login com e-mail e senha;
* geração de access token JWT;
* proteção de rotas privadas;
* hash seguro de senha;
* associação de usuário com uma loja;
* suporte básico a roles.

### Roles iniciais

```txt
admin
manager
salesperson
```

### Comportamento esperado

* `admin`: pode configurar loja, instâncias WhatsApp, usuários, leads e conversas.
* `manager`: pode ver leads, conversas e assumir atendimentos.
* `salesperson`: pode ver leads/conversas atribuídas a ele e assumir atendimentos.

---

## 3.4 Estrutura interna sugerida do `/backend`

```txt
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── jwt.py
│   │   └── logging.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── store.py
│   │   ├── whatsapp_instance.py
│   │   ├── customer.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── lead.py
│   │   ├── salesperson.py
│   │   ├── handoff_event.py
│   │   └── agent_run.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── store.py
│   │   ├── whatsapp_instance.py
│   │   ├── customer.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── lead.py
│   │   ├── salesperson.py
│   │   └── webhook.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── store_repository.py
│   │   ├── conversation_repository.py
│   │   ├── message_repository.py
│   │   ├── lead_repository.py
│   │   └── salesperson_repository.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── evolution_service.py
│   │   ├── webhook_parser.py
│   │   ├── conversation_service.py
│   │   ├── lead_service.py
│   │   ├── lead_scoring_service.py
│   │   ├── crm_mock_client.py
│   │   ├── handoff_service.py
│   │   └── agent_service.py
│   │
│   ├── agents/
│   │   ├── car_sales_agent.py
│   │   ├── prompts.py
│   │   └── tools.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── stores.py
│   │       ├── webhooks.py
│   │       ├── conversations.py
│   │       ├── leads.py
│   │       ├── salespeople.py
│   │       └── health.py
│   │
│   └── utils/
│       ├── datetime.py
│       └── phone.py
│
├── alembic/
├── tests/
├── scripts/
│   └── seed_demo_data.py
├── Dockerfile
├── pyproject.toml
├── alembic.ini
├── .env.example
└── README.md
```

---

## 3.5 Banco de dados do backend

O backend será o único serviço com acesso direto ao banco PostgreSQL principal.

O `/crm-mock` não deve usar o banco principal no MVP.

O frontend também não deve acessar o banco diretamente.

A comunicação correta deve ser:

```txt
frontend -> backend -> PostgreSQL
Evolution API -> backend -> PostgreSQL
backend -> crm-mock
backend -> OpenAI API
backend -> Evolution API
```

---

## 3.6 Entidades principais do backend

O backend deve gerenciar:

* users
* stores
* whatsapp_instances
* customers
* conversations
* messages
* leads
* salespeople
* handoff_events
* agent_runs

A entidade `vehicles` não deve ficar no backend principal no MVP, pois os veículos serão simulados no `/crm-mock`.

O backend pode armazenar apenas referências ou resumos de interesse do cliente, como:

```txt
vehicle_interest
interest_summary
budget_min
budget_max
payment_type
trade_in_vehicle
```

---

## 3.7 Comunicação com Evolution API

A comunicação com a Evolution API deve ficar centralizada em:

```txt
backend/app/services/evolution_service.py
```

Esse serviço deve expor métodos como:

```python
send_text_message(instance_name: str, phone: str, text: str)
```

Nenhum outro módulo deve chamar a Evolution API diretamente.

---

## 3.8 Webhooks da Evolution API

Os webhooks devem entrar por:

```txt
POST /api/webhooks/evolution/{instance_name}
```

O fluxo esperado é:

```txt
1. Recebe payload da Evolution
2. Identifica instância
3. Faz parse do payload
4. Identifica telefone do cliente
5. Identifica se é mensagem recebida ou enviada
6. Cria ou atualiza customer
7. Cria ou atualiza conversation
8. Salva message
9. Verifica se IA está ativa
10. Se IA ativa, chama AgentService
11. Salva resposta
12. Envia resposta pela Evolution API
```

O parser do payload da Evolution deve ficar separado em:

```txt
backend/app/services/webhook_parser.py
```

Isso facilita ajustes futuros caso o formato do webhook mude.

---

## 3.9 Comunicação com OpenAI

A comunicação com a OpenAI deve ficar centralizada em:

```txt
backend/app/services/agent_service.py
backend/app/agents/
```

O backend deve usar a lib oficial da OpenAI em Python.

O agente deve ser implementado usando:

* OpenAI Python SDK;
* Responses API;
* tools/function calling;
* retorno estruturado;
* prompts versionados no código.

---

# 4. Diretório `/crm-mock`

## 4.1 Responsabilidade

O `/crm-mock` será uma API fictícia que simula um CRM ou sistema de estoque de veículos.

Ela deve ser separada do backend principal para simular uma integração real com sistemas externos.

Essa API será usada para testar o agente sem depender de um CRM real.

---

## 4.2 Características do `/crm-mock`

O `/crm-mock` deve:

* ser uma API simples;
* usar FastAPI;
* não exigir autenticação;
* não usar banco de dados no MVP;
* ter dados fixos/chumbados no código;
* simular veículos, lojas e vendedores;
* responder rapidamente;
* ser fácil de substituir futuramente por um CRM real.

---

## 4.3 Estrutura sugerida do `/crm-mock`

```txt
crm-mock/
├── app/
│   ├── main.py
│   ├── data/
│   │   ├── vehicles.py
│   │   ├── stores.py
│   │   └── salespeople.py
│   │
│   ├── schemas/
│   │   ├── vehicle.py
│   │   ├── store.py
│   │   └── salesperson.py
│   │
│   ├── services/
│   │   ├── vehicle_service.py
│   │   ├── store_service.py
│   │   └── salesperson_service.py
│   │
│   └── api/
│       └── routes/
│           ├── vehicles.py
│           ├── stores.py
│           ├── salespeople.py
│           └── health.py
│
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 4.4 Endpoints do `/crm-mock`

### Health

```txt
GET /health
```

### Veículos

```txt
GET /vehicles
GET /vehicles/{vehicle_id}
```

Filtros opcionais:

```txt
brand
model
year_min
year_max
max_price
min_price
transmission
fuel
status
```

### Lojas

```txt
GET /stores
GET /stores/{store_id}
```

### Vendedores

```txt
GET /salespeople
GET /salespeople/{salesperson_id}
GET /salespeople/suggest
```

Filtros opcionais:

```txt
store_id
specialty
active
```

---

## 4.5 Dados mockados

Os dados devem estar em arquivos Python simples.

Exemplo:

```txt
crm-mock/app/data/vehicles.py
```

Deve conter uma lista fixa de veículos, por exemplo:

```python
VEHICLES = [
    {
        "id": "veh_001",
        "store_id": "store_001",
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2021,
        "version": "XEi 2.0 Flex",
        "price": 119900,
        "mileage": 42000,
        "color": "Prata",
        "transmission": "Automático",
        "fuel": "Flex",
        "status": "available",
        "description": "Veículo completo, único dono, revisões em dia."
    }
]
```

O `/crm-mock` não deve ter login, JWT ou controle de permissão no MVP.

---

# 5. Diretório `/frontend`

## 5.1 Responsabilidade

O `/frontend` será usado para o painel da plataforma.

No MVP inicial, o frontend pode ser simples ou até ficar para uma segunda etapa, mas a estrutura deve existir desde o início.

O frontend será responsável por:

* login;
* visualização de conversas;
* visualização de leads;
* assumir atendimento humano;
* reativar IA;
* visualizar dados básicos do cliente;
* visualizar histórico de mensagens;
* gerenciar vendedores;
* visualizar status da instância WhatsApp.

---

## 5.2 Stack sugerida

Usar:

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui, se desejado
* Axios ou fetch nativo
* JWT salvo de forma segura no client

---

## 5.3 Estrutura sugerida do `/frontend`

```txt
frontend/
├── app/
│   ├── login/
│   ├── dashboard/
│   ├── conversations/
│   ├── leads/
│   ├── settings/
│   └── layout.tsx
│
├── components/
│   ├── layout/
│   ├── conversations/
│   ├── leads/
│   └── ui/
│
├── services/
│   ├── api.ts
│   ├── auth.ts
│   ├── conversations.ts
│   └── leads.ts
│
├── types/
│   ├── conversation.ts
│   ├── lead.ts
│   └── user.ts
│
├── public/
├── package.json
├── .env.example
└── README.md
```

---

## 5.4 Telas mínimas futuras

### Login

* e-mail
* senha
* botão de entrar

### Dashboard

* total de conversas
* leads novos
* leads quentes
* conversas aguardando humano

### Conversas

* lista de conversas
* status da conversa
* cliente
* última mensagem
* botão para abrir conversa

### Detalhe da conversa

* histórico de mensagens
* dados do cliente
* dados do lead
* botão "Assumir atendimento"
* botão "Reativar IA"

### Leads

* lista de leads
* filtro por status
* filtro por score
* filtro por intenção

---

# 6. Diretório `/docs`

## 6.1 Responsabilidade

O diretório `/docs` deve armazenar toda a documentação do projeto.

Ele deve ser usado para manter decisões, arquitetura, integrações e planejamento técnico.

---

## 6.2 Estrutura sugerida do `/docs`

```txt
docs/
├── 01-visao-geral.md
├── 02-arquitetura.md
├── 03-fluxo-whatsapp-evolution.md
├── 04-agente-ia.md
├── 05-crm-mock.md
├── 06-modelo-dados.md
├── 07-auth-jwt.md
├── 08-handoff-humano.md
├── 09-deploy-vps.md
├── 10-roadmap.md
└── prompts/
    ├── codex-setup-inicial.md
    ├── codex-backend.md
    ├── codex-crm-mock.md
    └── codex-frontend.md
```

---

# 7. Diretório `/workers`

## 7.1 Responsabilidade

O diretório `/workers` será reservado para processos assíncronos futuros.

No MVP, ele pode ficar vazio ou conter apenas um README.

Ele será usado futuramente para:

* processamento de filas;
* retries de mensagens;
* análise posterior de conversas;
* geração de relatórios;
* sincronização com CRMs reais;
* envio de notificações;
* rotinas agendadas;
* classificação assíncrona de leads;
* tarefas pesadas fora do fluxo do webhook.

---

## 7.2 Estrutura inicial

```txt
workers/
└── README.md
```

Conteúdo sugerido:

```md
# Workers

Este diretório será usado futuramente para processos assíncronos da plataforma.

No MVP, o processamento será feito diretamente no backend.

Possíveis usos futuros:

- filas de mensagens;
- retentativas;
- análise assíncrona de leads;
- sincronização com CRMs;
- notificações;
- relatórios agendados.
```

---

# 8. Docker Compose raiz

O projeto deve possuir um `docker-compose.yml` na raiz para desenvolvimento local.

Serviços sugeridos:

```txt
backend
crm-mock
postgres
```

Opcionalmente, no futuro:

```txt
frontend
redis
workers
```

Exemplo conceitual: (lembre-se que já temos um postgres rodando, que deve ser usado)

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

  backend:
    build: ./backend
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - crm-mock
    ports:
      - "8000:8000"

  crm-mock:
    build: ./crm-mock
    ports:
      - "8001:8001"

volumes:
  postgres_data:
```

---

# 9. Comunicação entre serviços

## 9.1 Fluxo principal

```txt
WhatsApp
  ↓
Evolution API
  ↓
/backend
  ↓
OpenAI API
  ↓
/backend
  ↓
/crm-mock
  ↓
/backend
  ↓
Evolution API
  ↓
WhatsApp
```

---

## 9.2 O frontend nunca fala com o `/crm-mock`

O frontend deve se comunicar apenas com o backend.

Correto:

```txt
frontend -> backend -> crm-mock
```

Errado:

```txt
frontend -> crm-mock
```

O backend deve ser o ponto central de regra de negócio.

---

# 10. Variáveis de ambiente

## 10.1 Backend

Arquivo:

```txt
backend/.env.example
```

Variáveis:

```env
APP_NAME=Car Agent Platform
APP_ENV=development
APP_DEBUG=true

DATABASE_URL=postgresql+psycopg://car_agent_user:car_agent_password@postgres:5432/car_agent_db

JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

OPENAI_API_KEY=
DEFAULT_OPENAI_MODEL=gpt-4.1-mini

EVOLUTION_API_BASE_URL=
EVOLUTION_API_KEY=

CRM_MOCK_BASE_URL=http://crm-mock:8001

CORS_ORIGINS=http://localhost:3000
```

---

## 10.2 CRM Mock

Arquivo:

```txt
crm-mock/.env.example
```

Variáveis:

```env
APP_NAME=CRM Mock
APP_ENV=development
APP_DEBUG=true
PORT=8001
```

---

## 10.3 Frontend

Arquivo:

```txt
frontend/.env.example
```

Variáveis:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

# 11. Princípios de arquitetura

## 11.1 Backend centraliza tudo

O backend deve centralizar:

* banco de dados;
* autenticação;
* autorização;
* comunicação com Evolution API;
* comunicação com OpenAI;
* comunicação com CRM mock;
* regras de conversa;
* regras de lead;
* regras de handoff.

---

## 11.2 CRM mock simula integração externa

O `/crm-mock` deve existir para que o agente consulte uma API externa simulada.

Isso deixa o MVP mais próximo de um cenário real, onde uma loja poderia ter:

* CRM próprio;
* sistema de estoque;
* ERP;
* plataforma de veículos;
* sistema de leads.

---

## 11.3 Workers ficam para depois

No MVP, evitar complexidade com filas.

O fluxo pode ser síncrono inicialmente.

Depois, se necessário, evoluir para:

```txt
Evolution webhook -> backend -> fila -> worker -> OpenAI -> Evolution
```

Possíveis tecnologias futuras:

* Redis
* Celery
* RQ
* Dramatiq
* Arq


---

# 13. Decisão importante para o MVP

A divisão correta será:

```txt
/backend     = produto real, banco real, auth real, agente real
/crm-mock    = simulação de sistema externo
/frontend    = painel da plataforma
/docs        = documentação e prompts
/workers     = futuro
```

Essa separação deixa o projeto mais profissional e evita misturar responsabilidades.

O ponto mais importante: **o backend é o cérebro do sistema**. O `/crm-mock` é apenas uma simulação externa para o agente consultar dados de veículos.
