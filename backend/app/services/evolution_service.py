import httpx


WEBHOOK_EVENTS = [
    "MESSAGES_UPSERT",
    "SEND_MESSAGE",
    "CONNECTION_UPDATE",
    "QRCODE_UPDATED",
]


class EvolutionConfigError(Exception):
    """Raised when Evolution API credentials are not configured."""

    def __init__(self) -> None:
        super().__init__(
            "Evolution API não configurada. "
            "Preencha EVOLUTION_API_BASE_URL e EVOLUTION_API_KEY no .env do backend."
        )


class EvolutionApiError(Exception):
    """Wraps httpx errors with a user-friendly message."""

    def __init__(self, action: str, cause: Exception) -> None:
        detail = str(cause)
        if isinstance(cause, httpx.HTTPStatusError):
            try:
                body = cause.response.json()
                detail = body.get("message") or body.get("error") or detail
            except Exception:
                detail = cause.response.text or detail
        super().__init__(f"Evolution API error ({action}): {detail}")
        self.action = action
        self.cause = cause


class EvolutionService:
    def __init__(self, *, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.api_key = api_key or ""

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    def _require_config(self) -> None:
        if not self.is_configured:
            raise EvolutionConfigError()

    def send_text_message(self, instance_name: str, phone: str, text: str) -> dict:
        if not self.is_configured:
            return {
                "dry_run": True,
                "instance_name": instance_name,
                "phone": phone,
            }

        try:
            response = httpx.post(
                f"{self.base_url}/message/sendText/{instance_name}",
                headers={"apikey": self.api_key},
                json={"number": phone, "text": text},
                timeout=20,
            )
            response.raise_for_status()
            return response.json() if response.content else {"sent": True}
        except httpx.HTTPError as exc:
            raise EvolutionApiError("send_text_message", exc) from exc

    def create_instance(
        self,
        *,
        instance_name: str,
        phone: str | None,
        webhook_url: str,
        webhook_secret: str,
    ) -> dict:
        self._require_config()
        try:
            response = httpx.post(
                f"{self.base_url}/instance/create",
                headers=self._headers(),
                json={
                    "instanceName": instance_name,
                    "integration": "WHATSAPP-BAILEYS",
                    "qrcode": True,
                    "number": phone or "",
                    "groupsIgnore": True,
                    "alwaysOnline": True,
                    "readMessages": True,
                    "readStatus": False,
                    "syncFullHistory": False,
                    "webhook": {
                        "url": webhook_url,
                        "byEvents": False,
                        "base64": False,
                        "headers": {
                            "X-Evolution-Webhook-Secret": webhook_secret,
                            "Content-Type": "application/json",
                        },
                        "events": WEBHOOK_EVENTS,
                    },
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise EvolutionApiError("create_instance", exc) from exc

    def fetch_instances(
        self, *, instance_name: str | None = None, instance_id: str | None = None
    ) -> dict | list:
        self._require_config()
        try:
            params = {
                key: value
                for key, value in {
                    "instanceName": instance_name,
                    "instanceId": instance_id,
                }.items()
                if value
            }
            response = httpx.get(
                f"{self.base_url}/instance/fetchInstances",
                headers={"apikey": self.api_key},
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise EvolutionApiError("fetch_instances", exc) from exc

    def connect_instance(self, instance_name: str, phone: str | None = None) -> dict:
        self._require_config()
        try:
            params = {"number": phone} if phone else None
            response = httpx.get(
                f"{self.base_url}/instance/connect/{instance_name}",
                headers={"apikey": self.api_key},
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise EvolutionApiError("connect_instance", exc) from exc

    def get_connection_state(self, instance_name: str) -> dict:
        self._require_config()
        try:
            response = httpx.get(
                f"{self.base_url}/instance/connectionState/{instance_name}",
                headers={"apikey": self.api_key},
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise EvolutionApiError("get_connection_state", exc) from exc

    def configure_webhook(
        self,
        *,
        instance_name: str,
        webhook_url: str,
        webhook_secret: str,
    ) -> dict:
        self._require_config()
        try:
            response = httpx.post(
                f"{self.base_url}/webhook/set/{instance_name}",
                headers=self._headers(),
                json={
                    "enabled": True,
                    "url": webhook_url,
                    "events": WEBHOOK_EVENTS,
                    "webhook_by_events": False,
                    "webhook_base64": False,
                    "headers": {
                        "X-Evolution-Webhook-Secret": webhook_secret,
                        "Content-Type": "application/json",
                    },
                },
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise EvolutionApiError("configure_webhook", exc) from exc

    def restart_instance(self, instance_name: str) -> dict:
        self._require_config()
        try:
            response = httpx.put(
                f"{self.base_url}/instance/restart/{instance_name}",
                headers={"apikey": self.api_key},
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise EvolutionApiError("restart_instance", exc) from exc

    def logout_instance(self, instance_name: str) -> dict:
        self._require_config()
        try:
            response = httpx.delete(
                f"{self.base_url}/instance/logout/{instance_name}",
                headers={"apikey": self.api_key},
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise EvolutionApiError("logout_instance", exc) from exc

    def delete_instance(self, instance_name: str) -> dict:
        self._require_config()
        try:
            response = httpx.delete(
                f"{self.base_url}/instance/delete/{instance_name}",
                headers={"apikey": self.api_key},
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise EvolutionApiError("delete_instance", exc) from exc

    def _headers(self) -> dict[str, str]:
        return {"apikey": self.api_key, "Content-Type": "application/json"}
