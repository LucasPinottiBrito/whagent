# Workers

Processos assincronos da plataforma. No MVP existe um worker de processamento de conversas pendentes.

## Responsabilidade

- consultar Redis em loop;
- buscar conversas cujo debounce expirou;
- adquirir lock por `conversation_id`;
- chamar `POST /api/internal/conversations/{conversation_id}/process`;
- remover da fila em caso de resposta 2xx;
- liberar lock;
- nao acessar o banco diretamente.

## Rodar

```bash
cp workers/.env.example workers/.env
python -m app.main
```
