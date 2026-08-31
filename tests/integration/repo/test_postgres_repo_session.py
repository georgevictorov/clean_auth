from datetime import UTC, datetime, timedelta
from uuid import uuid7

import pytest

from auth.domain.errors import ConcurrencyError, InfrastructureError
from auth.domain.models import Session, User
from auth.infrastructure.repo.postgres.postgres_repo import (
    SessionRepository, UserRepository)

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def create_user(db_connection):
    user = User(
        user_id=uuid7(),
        username=f"user-{uuid7()}",
        password_hash="hash",
    )

    repo = UserRepository(db_connection)
    repo.add(user)
    repo.flush()

    return user


def make_session(**kwargs) -> Session:
    defaults = {
        "user_id": uuid7(),
        "created_at": NOW,
        "lifetime": timedelta(days=30),
    }

    defaults.update(kwargs)

    return Session.create(**defaults)


def test_add_and_get__session(db_connection, clean_db):
    user = create_user(db_connection)
    session = make_session(user_id=user.user_id)
    repo = SessionRepository(db_connection)

    repo.add(session)
    repo.flush()

    result = repo.get(session.session_id)

    assert result == session


def test_get_loads_session_from_database(db_connection, clean_db):
    user = create_user(db_connection)
    session = make_session(user_id=user.user_id)

    repo = SessionRepository(db_connection)
    repo.add(session)
    repo.flush()
    db_connection.commit()

    repo = SessionRepository(db_connection)

    result = repo.get(session.session_id)

    assert result == session
    assert result is not session


def test_list_by_user_id(db_connection, clean_db):
    user1 = create_user(db_connection)
    user2 = create_user(db_connection)

    session1 = make_session(user_id=user1.user_id)
    session2 = make_session(user_id=user2.user_id)
    repo = SessionRepository(db_connection)

    repo.add(session1)
    repo.add(session2)
    repo.flush()
    db_connection.commit()

    sessions = repo.list_by_user_id(user1.user_id)

    assert len(sessions) == 1
    assert sessions[0] is session1


def test_list_by_user_id_returns_empty_list_for_user_without_sessions(db_connection, clean_db):
    repo = SessionRepository(db_connection)

    sessions = repo.list_by_user_id(uuid7())

    assert sessions == []


def test_get_raises_error_if_conn_closed(db_connection, clean_db):
    repo = SessionRepository(db_connection)
    db_connection.close()
    with pytest.raises(InfrastructureError):
        repo.get(uuid7())


def test_flush_raises_error_if_conn_closed(db_connection, clean_db):
    repo = SessionRepository(db_connection)
    session = make_session()

    repo.add(session)

    db_connection.close()

    with pytest.raises(InfrastructureError):
        repo.flush()


def test_update_session(db_connection, clean_db):
    user = create_user(db_connection)
    repo = SessionRepository(db_connection)
    session = make_session(user_id=user.user_id)

    repo.add(session)
    repo.flush()
    db_connection.commit()

    session.revoke()

    repo.flush()
    db_connection.commit()

    assert session.version == 2

    result = repo.get(session.session_id)

    assert result == session
    assert result.revoked is True  # noqa


def test_update_raises_concurrency_error(db_connection, clean_db):
    user = create_user(db_connection)
    repo = SessionRepository(db_connection)
    session = make_session(user_id=user.user_id)
    repo.add(session)
    repo.flush()
    db_connection.commit()

    session = repo.get(session.session_id)
    session.revoke()  # noqa

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            update sessions
                set version = version + 1
            where
                session_id = %s
            """, (session.session_id,),  # noqa
        )

    db_connection.commit()

    with pytest.raises(ConcurrencyError):
        repo.flush()
