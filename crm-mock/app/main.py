from fastapi import FastAPI, HTTPException, Query

from app.data.salespeople import SALESPEOPLE
from app.data.stores import STORES
from app.data.vehicles import VEHICLES


app = FastAPI(title="CRM Mock")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/vehicles")
def list_vehicles(
    brand: str | None = None,
    model: str | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    transmission: str | None = None,
    fuel: str | None = None,
    status: str | None = None,
):
    vehicles = VEHICLES
    if brand:
        vehicles = [v for v in vehicles if v["brand"].lower() == brand.lower()]
    if model:
        vehicles = [v for v in vehicles if model.lower() in v["model"].lower()]
    if year_min is not None:
        vehicles = [v for v in vehicles if v["year"] >= year_min]
    if year_max is not None:
        vehicles = [v for v in vehicles if v["year"] <= year_max]
    if max_price is not None:
        vehicles = [v for v in vehicles if v["price"] <= max_price]
    if min_price is not None:
        vehicles = [v for v in vehicles if v["price"] >= min_price]
    if transmission:
        vehicles = [
            v for v in vehicles if v["transmission"].lower() == transmission.lower()
        ]
    if fuel:
        vehicles = [v for v in vehicles if v["fuel"].lower() == fuel.lower()]
    if status:
        vehicles = [v for v in vehicles if v["status"].lower() == status.lower()]
    return vehicles


@app.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: str):
    for vehicle in VEHICLES:
        if vehicle["id"] == vehicle_id:
            return vehicle
    raise HTTPException(status_code=404, detail="vehicle not found")


@app.get("/stores")
def list_stores():
    return STORES


@app.get("/stores/{store_id}")
def get_store(store_id: str):
    for store in STORES:
        if store["id"] == store_id:
            return store
    raise HTTPException(status_code=404, detail="store not found")


@app.get("/salespeople/suggest")
def suggest_salesperson(
    store_id: str | None = Query(default=None),
    specialty: str | None = Query(default=None),
):
    candidates = [
        salesperson for salesperson in SALESPEOPLE if salesperson["active"] is True
    ]
    if store_id:
        candidates = [s for s in candidates if s["store_id"] == store_id]
    if specialty:
        exact = [s for s in candidates if s["specialty"].lower() == specialty.lower()]
        if exact:
            candidates = exact
    if not candidates:
        raise HTTPException(status_code=404, detail="salesperson not found")
    return candidates[0]


@app.get("/salespeople")
def list_salespeople(
    store_id: str | None = None,
    specialty: str | None = None,
    active: bool | None = None,
):
    salespeople = SALESPEOPLE
    if store_id:
        salespeople = [s for s in salespeople if s["store_id"] == store_id]
    if specialty:
        salespeople = [s for s in salespeople if s["specialty"].lower() == specialty.lower()]
    if active is not None:
        salespeople = [s for s in salespeople if s["active"] is active]
    return salespeople


@app.get("/salespeople/{salesperson_id}")
def get_salesperson(salesperson_id: str):
    for salesperson in SALESPEOPLE:
        if salesperson["id"] == salesperson_id:
            return salesperson
    raise HTTPException(status_code=404, detail="salesperson not found")
