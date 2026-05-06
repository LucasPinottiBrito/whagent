import httpx


class CrmMockClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def search_vehicles(self, **params) -> list[dict]:
        clean = {key: value for key, value in params.items() if value not in (None, "")}
        response = httpx.get(f"{self.base_url}/vehicles", params=clean, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_vehicle(self, vehicle_id: str) -> dict:
        response = httpx.get(f"{self.base_url}/vehicles/{vehicle_id}", timeout=10)
        response.raise_for_status()
        return response.json()

    def suggest_salesperson(self, **params) -> dict | None:
        clean = {key: value for key, value in params.items() if value not in (None, "")}
        response = httpx.get(
            f"{self.base_url}/salespeople/suggest", params=clean, timeout=10
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
