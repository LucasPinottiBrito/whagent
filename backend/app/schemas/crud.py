from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = "salesperson"


class UserUpdateRequest(BaseModel):
    email: str | None = None
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class CustomerUpdateRequest(BaseModel):
    name: str | None = None
    phone: str | None = None


class LeadUpdateRequest(BaseModel):
    status: str | None = None
    score: int | None = None
    intent: str | None = None
    vehicle_interest: str | None = None
    budget_min: float | None = None
    budget_max: float | None = None
    payment_type: str | None = None
    trade_in_vehicle: str | None = None
    interest_summary: str | None = None
