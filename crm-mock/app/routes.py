from fastapi import APIRouter, HTTPException, Query

from app.data.salespeople import SALESPEOPLE
from app.data.stores import STORES
from app.data.vehicles import VEHICLES


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/vehicles")
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
        vehicles = [item for item in vehicles if item["brand"].lower() == brand.lower()]
    if model:
        vehicles = [item for item in vehicles if model.lower() in item["model"].lower()]
    if year_min is not None:
        vehicles = [item for item in vehicles if item["year"] >= year_min]
    if year_max is not None:
        vehicles = [item for item in vehicles if item["year"] <= year_max]
    if max_price is not None:
        vehicles = [item for item in vehicles if item["price"] <= max_price]
    if min_price is not None:
        vehicles = [item for item in vehicles if item["price"] >= min_price]
    if transmission:
        vehicles = [
            item
            for item in vehicles
            if item["transmission"].lower() == transmission.lower()
        ]
    if fuel:
        vehicles = [item for item in vehicles if item["fuel"].lower() == fuel.lower()]
    if status:
        vehicles = [item for item in vehicles if item["status"].lower() == status.lower()]
    return vehicles


@router.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: str):
    for vehicle in VEHICLES:
        if vehicle["id"] == vehicle_id:
            return vehicle
    raise HTTPException(status_code=404, detail="vehicle not found")


@router.get("/stores")
def list_stores():
    return STORES


@router.get("/stores/{store_id}")
def get_store(store_id: str):
    for store in STORES:
        if store["id"] == store_id:
            return store
    raise HTTPException(status_code=404, detail="store not found")


@router.get("/salespeople/suggest")
def suggest_salesperson(
    store_id: str | None = Query(default=None),
    specialty: str | None = Query(default=None),
):
    candidates = [item for item in SALESPEOPLE if item["active"]]
    if store_id:
        candidates = [item for item in candidates if item["store_id"] == store_id]
    if specialty:
        exact = [item for item in candidates if item["specialty"].lower() == specialty.lower()]
        if exact:
            candidates = exact
    if not candidates:
        raise HTTPException(status_code=404, detail="salesperson not found")
    return candidates[0]


@router.get("/salespeople")
def list_salespeople(
    store_id: str | None = None,
    specialty: str | None = None,
    active: bool | None = None,
):
    salespeople = SALESPEOPLE
    if store_id:
        salespeople = [item for item in salespeople if item["store_id"] == store_id]
    if specialty:
        salespeople = [
            item for item in salespeople if item["specialty"].lower() == specialty.lower()
        ]
    if active is not None:
        salespeople = [item for item in salespeople if item["active"] is active]
    return salespeople


@router.get("/salespeople/{salesperson_id}")
def get_salesperson(salesperson_id: str):
    for salesperson in SALESPEOPLE:
        if salesperson["id"] == salesperson_id:
            return salesperson
    raise HTTPException(status_code=404, detail="salesperson not found")
