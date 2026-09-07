from auth.infrastructure.key_provider.file_key_pair_provider import \
    FileKeysPairProvider
from auth.infrastructure.public_key_provider.paserk_provider import \
    PaserkPublicKeyProvider


def test_get_public_key_from_docker_secrets():
    path = "/run/secrets/public_key"

    public_key_provider = FileKeysPairProvider(public_key_path=path)

    paserk_provider = PaserkPublicKeyProvider(public_key_provider)
    result = paserk_provider.get_public_keys()

    assert len(result.keys) == 1

    key = result.keys[0]

    assert key.kid
    assert key.paserk
