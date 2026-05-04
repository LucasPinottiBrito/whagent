# CRM Mock

API FastAPI sem autenticacao e sem banco. Simula estoque, lojas e vendedores para o agente consultar durante o MVP.

## Endpoints

- `GET /health`
- `GET /vehicles`
- `GET /vehicles/{vehicle_id}`
- `GET /stores`
- `GET /stores/{store_id}`
- `GET /salespeople`
- `GET /salespeople/{salesperson_id}`
- `GET /salespeople/suggest`

Os dados ficam em `app/data/vehicles.py`, `app/data/stores.py` e `app/data/salespeople.py`.
