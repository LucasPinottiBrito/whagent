# Visao Geral

Whagent e um MVP para atendimento automatizado via WhatsApp em lojas de carros.

O sistema recebe webhooks da Evolution API, salva mensagens e conversas no PostgreSQL, agenda processamento com Redis, usa um worker separado para acionar o backend e gera resposta por um agente de IA. Em ambiente local, o agente funciona sem OpenAI usando fallback deterministico.

Componentes:

- `backend`: API principal, banco, auth, webhooks, agente, leads e handoff.
- `workers`: polling Redis, lock e chamada ao endpoint interno do backend.
- `crm-mock`: estoque e vendedores ficticios em memoria.
- `frontend`: dashboard operacional para setup, login, instancias Evolution, inbox, leads, empresa e debug local.

No primeiro acesso, o painel chama `GET /api/setup/status`. Se nao houver usuarios, `/setup` cria a primeira loja e o primeiro admin. Depois disso, o bootstrap publico passa a retornar conflito e o acesso normal ocorre via login JWT local.
