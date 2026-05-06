# Workers

Worker simples que observa Redis e chama o endpoint interno do backend.

Ele nao acessa PostgreSQL, OpenAI, Evolution API nem CRM mock.

```powershell
Copy-Item .env.example .env
python -m pip install -e .[dev]
python -m app.main
```
