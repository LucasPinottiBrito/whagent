# CRM Mock

O `crm-mock` e uma API FastAPI separada, sem auth e sem banco.

Endpoints:

- `GET /health`
- `GET /vehicles`
- `GET /vehicles/{vehicle_id}`
- `GET /stores`
- `GET /stores/{store_id}`
- `GET /salespeople`
- `GET /salespeople/{salesperson_id}`
- `GET /salespeople/suggest`

Dados estaticos:

- `crm-mock/app/data/vehicles.py`
- `crm-mock/app/data/stores.py`
- `crm-mock/app/data/salespeople.py`
