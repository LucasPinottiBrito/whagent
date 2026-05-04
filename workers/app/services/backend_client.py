import httpx


class BackendClient:
    def __init__(self, *, base_url: str, internal_api_key: str):
        self.base_url = base_url.rstrip("/")
        self.internal_api_key = internal_api_key

    def process_conversation(self, conversation_id: str) -> httpx.Response:
        return httpx.post(
            f"{self.base_url}/api/internal/conversations/{conversation_id}/process",
            headers={"X-Internal-Api-Key": self.internal_api_key},
            timeout=60,
        )
