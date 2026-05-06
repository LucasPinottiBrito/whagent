import httpx


WEBHOOK_EVENTS = [
    "MESSAGES_UPSERT",
    "SEND_MESSAGE",
    "CONNECTION_UPDATE",
    "QRCODE_UPDATED",
]


class EvolutionService:
    def __init__(self, *, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def send_text_message(self, instance_name: str, phone: str, text: str) -> dict:
        # dry_run keeps local development usable without a real Evolution API.
        if not self.base_url or not self.api_key:
            return {
                "dry_run": True,
                "instance_name": instance_name,
                "phone": phone,
            }

        response = httpx.post(
            f"{self.base_url}/message/sendText/{instance_name}",
            headers={"apikey": self.api_key},
            json={"number": phone, "text": text},
            timeout=20,
        )
        response.raise_for_status()
        return response.json() if response.content else {"sent": True}

    def create_instance(
        self,
        *,
        instance_name: str,
        phone: str | None,
        webhook_url: str,
        webhook_secret: str,
    ) -> dict:
        if not self.base_url or not self.api_key:
            return {
                "dry_run": True,
                "instance": {
                    "instanceName": instance_name,
                    "instanceId": None,
                    "status": "dry_run",
                },
            }
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

    def fetch_instances(
        self, *, instance_name: str | None = None, instance_id: str | None = None
    ) -> dict | list:
        if not self.base_url or not self.api_key:
            return {"dry_run": True, "instances": []}
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

    def connect_instance(self, instance_name: str, phone: str | None = None) -> dict:
        if not self.base_url or not self.api_key:
            return {"dry_run": True, "pairingCode": None, "code": None, "count": 0}
        params = {"number": phone} if phone else None
        response = httpx.get(
            f"{self.base_url}/instance/connect/{instance_name}",
            headers={"apikey": self.api_key},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_connection_state(self, instance_name: str) -> dict:
        if not self.base_url or not self.api_key:
            return {
                "dry_run": True,
                "instance": {"instanceName": instance_name, "state": "dry_run"},
            }
        response = httpx.get(
            f"{self.base_url}/instance/connectionState/{instance_name}",
            headers={"apikey": self.api_key},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def configure_webhook(
        self,
        *,
        instance_name: str,
        webhook_url: str,
        webhook_secret: str,
    ) -> dict:
        if not self.base_url or not self.api_key:
            return {"dry_run": True, "webhook": {"enabled": True, "url": webhook_url}}
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

    def restart_instance(self, instance_name: str) -> dict:
        if not self.base_url or not self.api_key:
            return {"dry_run": True, "instance": {"instanceName": instance_name}}
        response = httpx.put(
            f"{self.base_url}/instance/restart/{instance_name}",
            headers={"apikey": self.api_key},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def logout_instance(self, instance_name: str) -> dict:
        if not self.base_url or not self.api_key:
            return {"dry_run": True, "status": "SUCCESS"}
        response = httpx.delete(
            f"{self.base_url}/instance/logout/{instance_name}",
            headers={"apikey": self.api_key},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def delete_instance(self, instance_name: str) -> dict:
        if not self.base_url or not self.api_key:
            return {"dry_run": True, "status": "SUCCESS"}
        response = httpx.delete(
            f"{self.base_url}/instance/delete/{instance_name}",
            headers={"apikey": self.api_key},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def _headers(self) -> dict[str, str]:
        return {"apikey": self.api_key, "Content-Type": "application/json"}
