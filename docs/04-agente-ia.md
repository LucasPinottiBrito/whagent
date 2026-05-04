# Agente de IA

O `AgentService` fica em `backend/app/services/agent_service.py`.

Caracteristicas:

- usa a lib oficial `openai`;
- usa `client.responses.create`;
- declara tool `search_vehicles`;
- usa retorno estruturado em JSON;
- mantem prompt em `backend/app/agents/prompts.py`;
- nao usa LangChain nem LangGraph.

Quando `OPENAI_API_KEY` nao esta configurada, o servico usa fallback deterministico para manter o ambiente local executavel.
