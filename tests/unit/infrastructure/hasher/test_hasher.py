import pytest

from auth.infrastructure.hasher.argon2.hasher import Argon2PasswordHasher


@pytest.fixture
def hasher():
    return Argon2PasswordHasher()


def test_hash_and_verify_ok(hasher):
    password = "super-secret-2026-password"
    password_hash = hasher.hash(password)

    assert hasher.verify(password, password_hash) is True


def test_verify_wrong_password(hasher):
    password = "super-secret-2026-password"
    password_hash = hasher.hash(password)

    assert hasher.verify("not-super-secret-2026-password", password_hash) is False


def test_verify_invalid_hash(hasher):
    password = "super-secret-2026-password"
    broken_hash = "-2713272525206225125"

    assert hasher.verify(password, broken_hash) is False


def test_hash_unique_salt(hasher):
    password = "super-secret-2026-password"
    hash1 = hasher.hash(password)
    hash2 = hasher.hash(password)

    assert hash1 != hash2

    assert hasher.verify(password, hash1) is True
    assert hasher.verify(password, hash2) is True
