import httpx


class EvolutionService:
    def __init__(self, *, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def send_text_message(self, instance_name: str, phone: str, text: str) -> dict:
        if not self.base_url or not self.api_key:
            return {"dry_run": True, "instance_name": instance_name, "phone": phone}

        response = httpx.post(
            f"{self.base_url}/message/sendText/{instance_name}",
            headers={"apikey": self.api_key},
            json={"number": phone, "text": text},
            timeout=20,
        )
        response.raise_for_status()
        if not response.content:
            return {"sent": True}
        return response.json()
