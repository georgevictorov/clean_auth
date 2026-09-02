from auth.infrastructure.key_provider.file_key_provider import FileKeyProvider


def test_get_public_key_from_docker_secrets():
    path = "/run/secrets/public_key"

    provider = FileKeyProvider(
        public_key_path=path
    )

    result = provider.get_public_keys()

    assert len(result.keys) == 1

    key = result.keys[0]

    assert key.kid
    assert key.paserk
