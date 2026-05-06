from pydantic import BaseModel


class BootstrapRequest(BaseModel):
    store_name: str
    store_slug: str
    store_document: str | None = None
    store_phone: str | None = None
    admin_email: str
    admin_full_name: str
    admin_password: str


class StoreUpdateRequest(BaseModel):
    name: str | None = None
    document: str | None = None
    phone: str | None = None


class WhatsAppInstanceCreateRequest(BaseModel):
    instance_name: str
    phone: str | None = None
    webhook_secret: str | None = None


class HumanMessageRequest(BaseModel):
    content: str
