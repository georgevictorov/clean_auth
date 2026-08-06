from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import pytest

from auth.domain.errors import (InvalidCreationTime, InvalidExpirationTime,
                                InvalidUserID)
from auth.domain.models import Session

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def make_session(**kwargs) -> Session:
    defaults = {
        "user_id": uuid7(),
        "created_at": NOW,
        "lifetime": timedelta(days=30),
    }

    defaults.update(kwargs)

    return Session.create(**defaults)


def make_raw_session(**kwargs) -> Session:
    defaults = {
        "session_id": uuid7(),
        "user_id": uuid7(),
        "refresh_token_hash": None,
        "created_at": NOW,
        "expires_at": NOW + timedelta(days=30),
    }

    defaults.update(kwargs)

    return Session(**defaults)


# Creation


def test_create_initializes_session():
    user_id = uuid7()

    session = make_session(user_id=user_id)

    assert isinstance(session.session_id, UUID)
    assert session.user_id == user_id
    assert session.created_at == NOW
    assert session.expires_at == NOW + timedelta(days=30)
    assert session.refresh_token_hash is None
    assert session.version == 1
    assert session.revoked is False
    assert session.is_active(NOW) is True


def test_create_calculates_expiration_time():
    session = make_session(
        lifetime=timedelta(days=30),
    )

    assert session.expires_at == NOW + timedelta(days=30)


def test_session_can_be_created_with_specific_version():
    session = make_raw_session(version=10)

    assert session.version == 10


# Validation


def test_empty_user_id_is_invalid():
    with pytest.raises(InvalidUserID):
        make_session(user_id="")


def test_created_at_must_be_timezone_aware():
    created_at = datetime(2026, 1, 1, 12, 0)

    with pytest.raises(InvalidCreationTime):
        make_session(
            created_at=created_at,
            lifetime=timedelta(days=1),
        )


def test_expires_at_must_be_timezone_aware():
    expires_at = datetime(2026, 1, 2, 12, 0)

    with pytest.raises(InvalidExpirationTime):
        make_raw_session(
            expires_at=expires_at,
        )


def test_expires_at_must_be_after_created_at():
    with pytest.raises(InvalidExpirationTime):
        make_session(
            created_at=NOW,
            lifetime=-timedelta(seconds=1),
        )


# Revocation


def test_session_is_not_revoked_by_default():
    session = make_session()

    assert session.revoked is False


def test_revoke_marks_session_as_revoked():
    session = make_session()

    session.revoke()

    assert session.revoked is True
    assert session.is_active(NOW) is False


def test_revoke_is_idempotent():
    session = make_session()

    session.revoke()
    session.revoke()

    assert session.revoked is True
    assert session.is_active(NOW) is False


# Expiration / Activity


def test_is_active_returns_true_for_active_session():
    session = make_session(
        created_at=NOW,
        lifetime=timedelta(hours=1),
    )

    assert session.is_active(NOW) is True


def test_is_active_returns_false_for_revoked_session():
    session = make_session(
        created_at=NOW,
        lifetime=timedelta(hours=1),
    )

    session.revoke()

    assert session.is_active(NOW) is False


def test_is_active_returns_false_for_expired_session():
    session = make_session(
        created_at=NOW - timedelta(hours=1),
        lifetime=timedelta(microseconds=1),
    )

    expired_now = NOW + timedelta(seconds=1)

    assert session.is_active(expired_now) is False


def test_is_expired_returns_true_after_expiration():
    session = make_session(
        created_at=NOW,
        lifetime=timedelta(microseconds=1),
    )

    after_expiration = NOW + timedelta(seconds=1)

    assert session.is_expired(after_expiration) is True


def test_is_expired_returns_false_before_expiration():
    session = make_session(
        created_at=NOW,
        lifetime=timedelta(seconds=1),
    )

    assert session.is_expired(NOW) is False


# Refresh token


def test_refresh_token_is_empty_by_default():
    session = make_session()

    assert session.refresh_token_hash is None


def test_attach_refresh_token_stores_hash():
    session = make_session()

    session.rotate_refresh_token("hash")

    assert session.refresh_token_hash == "hash"
