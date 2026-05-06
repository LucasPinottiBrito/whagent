# Frontend

Dashboard operacional do Whagent em Next.js.

O frontend fala apenas com o backend via `NEXT_PUBLIC_API_BASE_URL`.
Ele nao acessa diretamente Redis, Evolution API, OpenAI, CRM mock ou banco.

## Rotas

- `/setup`: cria a primeira empresa e usuario admin quando o banco nao tem usuarios.
- `/login`: login JWT local.
- `/app/overview`: resumo da operacao.
- `/app/inbox`: conversas, timeline, envio humano, IA on/off e processar agora.
- `/app/instances`: cria e controla instancias Evolution pelo backend.
- `/app/leads`: leads qualificados.
- `/app/company`: dados da empresa.
- `/app/debug`: simulacao inbound e runtime local fora de producao.

## Rodar

Requer Node.js 20.9+.

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

Acesse `http://localhost:3000`.
