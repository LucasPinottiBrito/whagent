# Data lifecycle e regras de ownership

Este documento descreve **ownership entre tabelas** e o comportamento de **deleção em cascata** usado no backend.
A fonte de verdade deve permanecer nos modelos em `backend/app/models/`.

## 1) `whatsapp_instances -> conversations` (CASCADE)

- A FK `conversations.whatsapp_instance_id` referencia `whatsapp_instances.id` com `ondelete="CASCADE"`.
- Consequência: ao deletar uma linha em `whatsapp_instances`, o banco remove automaticamente as `conversations` filhas relacionadas.
- Alinhamento ORM: o relacionamento `WhatsAppInstance.conversations` usa `passive_deletes=True`, delegando a deleção ao banco.

## 2) `conversations -> messages/leads/handoff_events/agent_runs` (CASCADE)

A tabela `conversations` é dona do ciclo de vida das entidades abaixo:

- `messages.conversation_id -> conversations.id` com `ondelete="CASCADE"`
- `leads.conversation_id -> conversations.id` com `ondelete="CASCADE"`
- `handoff_events.conversation_id -> conversations.id` com `ondelete="CASCADE"`
- `agent_runs.conversation_id -> conversations.id` com `ondelete="CASCADE"`

Consequências:

- Ao deletar uma `conversation`, o banco remove automaticamente `messages`, `lead`, `handoff_events` e `agent_runs` associados.
- No ORM, `Conversation.messages`, `Conversation.lead`, `Conversation.handoff_events` e `Conversation.agent_runs` estão com `passive_deletes=True` para reforçar que o banco executa a cascata.

## 3) Regra para rotas HTTP: proibição de delete manual de filhos

Quando houver FK com `ondelete="CASCADE"`:

- **Não implementar deleção manual de filhos em rotas HTTP** (ex.: apagar `messages`, `leads`, `handoff_events`, `agent_runs` antes da `conversation`).
- A rota deve deletar apenas a entidade pai e deixar o banco aplicar a cascata.
- Isso evita divergência entre código e schema, reduz risco de inconsistência e elimina duplicação de lógica.

## Referências de modelo (fonte de verdade)

- `backend/app/models/whatsapp_instance.py`
- `backend/app/models/conversation.py`
- `backend/app/models/message.py`
- `backend/app/models/lead.py`
- `backend/app/models/handoff_event.py`
- `backend/app/models/agent_run.py`
