from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_vehicle_filters_and_details():
    response = client.get("/vehicles", params={"brand": "Toyota", "max_price": 130000})
    assert response.status_code == 200
    assert response.json()
    assert response.json()[0]["brand"] == "Toyota"

    detail_response = client.get(f"/vehicles/{response.json()[0]['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == response.json()[0]["id"]


def test_salespeople_suggest():
    response = client.get("/salespeople/suggest", params={"store_id": "store_001"})
    assert response.status_code == 200
    assert response.json()["id"].startswith("sales_")
