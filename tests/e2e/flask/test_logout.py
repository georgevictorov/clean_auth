def test_logout(client, api_url, user):
    login_response = client.post(
        f"{api_url}/login",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        f"{api_url}/logout",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 204


def test_logout_revokes_refresh_token(client, api_url, user):
    login_response = client.post(
        f"{api_url}/login",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post(
        f"{api_url}/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert logout_response.status_code == 204

    refresh_response = client.post(
        f"{api_url}/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == 401


def test_logout_with_invalid_token(client, api_url):
    response = client.post(
        f"{api_url}/logout",
        json={
            "refresh_token": "invalid-token",
        },
    )

    assert response.status_code == 401


def test_logout_requires_refresh_token(client, api_url):
    response = client.post(
        f"{api_url}/logout",
        json={},
    )

    assert response.status_code == 400
