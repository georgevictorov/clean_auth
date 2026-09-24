def test_login(client, api_url, user):
    response = client.post(
        f"{api_url}/login",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data


def test_login_with_invalid_password(client, api_url, user):
    response = client.post(
        f"{api_url}/login",
        json={
            "username": user["username"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["msg"] == "invalid credentials"


def test_login_with_unknown_user(client, api_url):
    response = client.post(
        f"{api_url}/login",
        json={
            "username": "unknown",
            "password": "password123",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["msg"] == "invalid credentials"


def test_login_requires_fields(client, api_url):
    response = client.post(
        f"{api_url}/login",
        json=[
            {"username": "unknown", "password": "password123"},
            {}
        ],
    )

    assert response.status_code == 400


def test_login_with_invalid_json(client, api_url):
    response = client.post(
        f"{api_url}/login",
        data="not json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
