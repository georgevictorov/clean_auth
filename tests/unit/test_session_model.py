from datetime import UTC, datetime, timedelta
from uuid import uuid7

import pytest

from auth.domain.errors import (InvalidCreationTime, InvalidExpirationTime,
                                InvalidUserID)
from auth.domain.models import Session

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def make_session(**kwargs) -> Session:
    defaults = {
        "session_id": uuid7(),
        "user_id": uuid7(),
        "token_hash": "hash",
        "created_at": NOW,
        "expires_at": NOW + timedelta(days=30),
    }

    defaults.update(kwargs)

    return Session(**defaults)


def test_create_valid_session():
    user_id = uuid7()
    session = make_session(user_id=user_id)

    assert session.user_id == user_id
    assert session.is_active(NOW) is True


def test_empty_username_is_invalid():
    with pytest.raises(InvalidUserID):
        make_session(user_id="")


def test_created_at_must_be_timezone_aware():
    created_at = datetime(2026, 1, 1, 12, 0)

    with pytest.raises(InvalidCreationTime):
        make_session(
            created_at=created_at,
            expires_at=created_at + timedelta(days=1),
        )


def test_expires_at_must_be_timezone_aware():
    expires_at = datetime(2026, 1, 2, 12, 0)

    with pytest.raises(InvalidExpirationTime):
        make_session(
            expires_at=expires_at,
        )


def test_expires_at_must_be_after_created_at():
    with pytest.raises(InvalidExpirationTime):
        make_session(
            created_at=NOW,
            expires_at=NOW - timedelta(seconds=1),
        )


def test_session_can_be_revoked():
    session = make_session()

    assert session.is_active(NOW) is True

    session.revoke()

    assert session.is_active(NOW) is False


def test_revoke_is_idempotent():
    session = make_session()

    session.revoke()
    session.revoke()

    assert session.is_active(NOW) is False


def test_active_session_returns_true():
    session = make_session(
        created_at=NOW,
        expires_at=NOW + timedelta(hours=1),
    )

    assert session.is_active(NOW) is True


def test_revoked_session_is_not_active():
    session = make_session(
        created_at=NOW,
        expires_at=NOW + timedelta(hours=1),
    )

    session.revoke()

    assert session.is_active(NOW) is False


def test_expired_session_is_not_active():
    session = make_session(
        created_at=NOW - timedelta(hours=1),
        expires_at=NOW - timedelta(seconds=1),
    )

    assert session.is_active(NOW) is False


def test_is_expired_returns_true_after_expiration():
    session = make_session(
        created_at=NOW - timedelta(hours=1),
        expires_at=NOW - timedelta(seconds=1),
    )

    assert session.is_expired(NOW) is True


def test_is_expired_returns_false_before_expiration():
    session = make_session(
        created_at=NOW,
        expires_at=NOW + timedelta(seconds=1),
    )

    assert session.is_expired(NOW) is False


def test_session_default_version_is_one():
    session = make_session()

    assert session.version == 1


def test_session_can_be_created_with_specific_version():
    session = make_session(version=10)

    assert session.version == 10
