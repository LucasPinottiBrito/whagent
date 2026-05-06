from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_vehicle_filters_and_details():
    response = client.get(
        "/vehicles",
        params={"brand": "Toyota", "max_price": 130000, "status": "available"},
    )

    assert response.status_code == 200
    vehicles = response.json()
    assert len(vehicles) == 1
    assert vehicles[0]["model"] == "Corolla"

    detail = client.get(f"/vehicles/{vehicles[0]['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == vehicles[0]["id"]


def test_salespeople_and_stores_endpoints():
    assert client.get("/stores").status_code == 200
    assert client.get("/stores/store_001").status_code == 200
    assert client.get("/salespeople").status_code == 200
    suggest = client.get("/salespeople/suggest", params={"store_id": "store_001"})
    assert suggest.status_code == 200
    assert suggest.json()["store_id"] == "store_001"
