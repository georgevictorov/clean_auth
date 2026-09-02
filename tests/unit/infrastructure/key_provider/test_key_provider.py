import hashlib

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from auth.infrastructure.key_provider.file_key_provider import FileKeyProvider


@pytest.fixture
def public_key_file(tmp_path):
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    path = tmp_path / "public.pem"
    path.write_bytes(public_key_pem)

    return path, public_key_pem


def test_get_public_keys(public_key_file):
    path, public_key_pem = public_key_file

    provider = FileKeyProvider(str(path))

    result = provider.get_public_keys()

    assert len(result.keys) == 1

    key = result.keys[0]

    expected_kid = hashlib.sha256(public_key_pem).hexdigest()[:16]

    assert key.kid == expected_kid
    assert key.paserk.startswith("k4.public.")


def test_get_public_keys_generates_stable_kid(public_key_file):
    path, _ = public_key_file

    provider = FileKeyProvider(str(path))

    first = provider.get_public_keys()
    second = provider.get_public_keys()

    assert first.keys[0].kid == second.keys[0].kid


def test_get_public_keys_raises_when_file_does_not_exist(tmp_path):
    provider = FileKeyProvider(
        str(tmp_path / "public.pem")
    )

    with pytest.raises(FileNotFoundError):
        provider.get_public_keys()
