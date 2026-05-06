# CRM Mock

API FastAPI em memoria para simular estoque, lojas e vendedores.

```powershell
python -m pip install -e .[dev]
uvicorn app.main:app --reload --port 8001
```

Endpoints:

- `GET /health`
- `GET /vehicles`
- `GET /vehicles/{vehicle_id}`
- `GET /stores`
- `GET /stores/{store_id}`
- `GET /salespeople`
- `GET /salespeople/{salesperson_id}`
- `GET /salespeople/suggest`
