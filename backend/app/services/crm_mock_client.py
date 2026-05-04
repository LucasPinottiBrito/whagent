import httpx


class CrmMockClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def search_vehicles(self, **params) -> list[dict]:
        clean_params = {key: value for key, value in params.items() if value not in (None, "")}
        response = httpx.get(f"{self.base_url}/vehicles", params=clean_params, timeout=10)
        response.raise_for_status()
        return response.json()

    def suggest_salesperson(self, **params) -> dict | None:
        clean_params = {key: value for key, value in params.items() if value not in (None, "")}
        response = httpx.get(
            f"{self.base_url}/salespeople/suggest", params=clean_params, timeout=10
        )
        response.raise_for_status()
        return response.json()
