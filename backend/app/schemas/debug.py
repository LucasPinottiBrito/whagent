from pydantic import BaseModel


class DebugRuntimePatch(BaseModel):
    ai_runtime_enabled: bool | None = None
    allow_from_me_as_inbound: bool | None = None


class SimulateInboundRequest(BaseModel):
    instance_name: str
    webhook_secret: str | None = None
    phone: str
    text: str
    push_name: str | None = "Cliente Debug"
    message_id: str | None = None
    process_now: bool = False
