def test_login_returns_jwt_and_me_returns_current_user(client, demo_data):
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "admin@example.com"
    assert me_response.json()["role"] == "admin"
