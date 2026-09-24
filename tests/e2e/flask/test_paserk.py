def test_get_public_keys(client, api_url):
    response = client.get(
        f"{api_url}/.well-known/paserk.json",
    )

    assert response.status_code == 200

    data = response.json()

    assert "keys" in data
    assert len(data["keys"]) >= 1

    key = data["keys"][0]

    assert "kid" in key
    assert "paserk" in key
