# Arquitetura

```txt
Frontend -> Backend -> PostgreSQL
Evolution API -> Backend -> PostgreSQL
Backend -> Redis
Worker -> Redis
Worker -> Backend endpoint interno
Backend -> OpenAI
Backend -> CRM Mock
Backend -> Evolution API
```

Responsabilidades:

- `backend`: regra de negocio, dados, auth, IA e integracoes;
- `workers`: debounce, lock e chamada ao endpoint interno;
- `crm-mock`: dados ficticios de estoque/CRM;
- `frontend`: painel, sempre via backend;
- `docs`: decisoes e guias tecnicos.
