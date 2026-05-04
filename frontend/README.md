# Frontend

Base Next.js, React e TypeScript para o painel da plataforma.

Regra arquitetural: o frontend fala apenas com o backend via `NEXT_PUBLIC_API_BASE_URL`.

Ele nao deve acessar diretamente:

- Redis;
- Evolution API;
- OpenAI;
- crm-mock;
- banco de dados.

## Rodar

```bash
cp frontend/.env.example frontend/.env.local
cd frontend
npm install
npm run dev
```
