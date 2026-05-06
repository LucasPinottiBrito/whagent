from pydantic import BaseModel


class Vehicle(BaseModel):
    id: str
    store_id: str
    brand: str
    model: str
    year: int
    version: str
    price: float
    mileage: int
    color: str
    transmission: str
    fuel: str
    status: str
