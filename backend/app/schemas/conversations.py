from pydantic import BaseModel


class TakeoverRequest(BaseModel):
    reason: str | None = None
