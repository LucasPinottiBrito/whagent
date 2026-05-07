# Arquitetura

```txt
Evolution API -> Backend -> PostgreSQL
Backend -> Redis
Worker -> Redis
Worker -> Backend endpoint interno
Backend -> AgentService
Backend -> CRM Mock
Backend -> Evolution API
Frontend -> Backend
```

Regras implementadas:

- webhook salva mensagem e retorna rapido;
- webhook nao chama OpenAI;
- worker nao acessa banco;
- worker nao chama OpenAI, Evolution ou CRM mock;
- AgentService nao salva no banco;
- ConversationProcessingService orquestra agent_run, lead, mensagem outbound e envio;
- frontend fala somente com backend.

O painel do cliente usa apenas rotas do backend:

- login;
- dados da empresa;
- overview operacional;
- controle de instancias WhatsApp/Evolution;
- inbox com timeline e envio humano;
- controles de IA por conversa;
- leads;
- debug local fora de producao.

O frontend nao acessa Redis, Evolution, PostgreSQL, OpenAI ou CRM mock diretamente.
