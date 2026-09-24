def test_refresh(client, api_url, user):
    login_response = client.post(
        f"{api_url}/login",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    old_refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        f"{api_url}/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != old_refresh_token


def test_refresh_with_invalid_token(client, api_url):
    response = client.post(
        f"{api_url}/refresh",
        json={
            "refresh_token": "invalid-token",
        },
    )

    assert response.status_code == 401


def test_refresh_requires_refresh_token(client, api_url):
    response = client.post(
        f"{api_url}/refresh",
        json={},
    )

    assert response.status_code == 400


def test_refresh_token_cannot_be_reused(client, api_url, user):
    login_response = client.post(
        f"{api_url}/login",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        f"{api_url}/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200

    response = client.post(
        f"{api_url}/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401
