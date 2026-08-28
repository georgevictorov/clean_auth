import threading
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

import pytest

from auth.domain.errors import ConcurrencyError, InfrastructureError
from auth.domain.models import Session, User
from auth.infrastructure.uow.postgres.postgres_uow import PostgresUnitOfWork

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def add_new_user(db_pool):
    with PostgresUnitOfWork(db_pool) as uow:
        user = User.create(
            "username",
            "password-super-hash"
        )

        uow.users.add(user)
        uow.commit()


def get_user_by_username_from_db(username, db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            select
                user_id,
                username,
                password_hash,
                disabled
            from users
            where
                username = %s
            """, (username,),
        )
        return cursor.fetchone()


def get_session_id_by_user_id_from_db(user_id, db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            select
                session_id,
                revoked
            from sessions
            where
                user_id = %s
            """, (user_id,),
        )

        return cursor.fetchone()


def test_add_user(db_pool, db_connection, clean_db):
    add_new_user(db_pool)

    row = get_user_by_username_from_db("username", db_connection)

    assert row is not None
    assert isinstance(row[0], UUID)
    assert row[1] == "username"
    assert row[2] == "password-super-hash"


def test_add_session(db_pool, db_connection, clean_db):
    add_new_user(db_pool)

    user = get_user_by_username_from_db("username", db_connection)

    with PostgresUnitOfWork(db_pool) as uow:
        session = Session.create(
            user_id=user[0],
            created_at=NOW,
            lifetime=timedelta(days=30),
        )

        uow.sessions.add(session)
        uow.commit()

    session = get_session_id_by_user_id_from_db(user[0], db_connection)

    assert session is not None
    assert isinstance(session[0], UUID)


def test_rollback_discards_new_user(db_pool, db_connection, clean_db):
    with pytest.raises(RuntimeError):
        with PostgresUnitOfWork(db_pool) as uow:
            user = User.create(
                "username",
                "password-super-hash"
            )

            uow.users.add(user)

            raise RuntimeError

    row = get_user_by_username_from_db("username", db_connection)

    assert row is None


def test_rollback_discards_new_session(db_pool, db_connection, clean_db):
    add_new_user(db_pool)

    user = get_user_by_username_from_db("username", db_connection)
    with pytest.raises(RuntimeError):
        with PostgresUnitOfWork(db_pool) as uow:
            session = Session.create(
                user_id=user[0],
                created_at=NOW,
                lifetime=timedelta(days=30),
            )
            uow.sessions.add(session)

            raise RuntimeError

    row = get_session_id_by_user_id_from_db(user[0], db_connection)

    assert row is None


def test_commit_updates_existing_user(db_pool, db_connection, clean_db):
    add_new_user(db_pool)
    row = get_user_by_username_from_db("username", db_connection)
    with PostgresUnitOfWork(db_pool) as uow:
        user = uow.users.get(row[0])
        user.disable()  # noqa
        uow.commit()

    row = get_user_by_username_from_db("username", db_connection)

    assert row[3] is False


def test_commit_updates_existing_session(db_pool, db_connection, clean_db):
    add_new_user(db_pool)
    user = get_user_by_username_from_db("username", db_connection)
    with PostgresUnitOfWork(db_pool) as uow:
        session = Session.create(
            user_id=user[0],
            created_at=NOW,
            lifetime=timedelta(days=30),
        )
        uow.sessions.add(session)
        uow.commit()

    row = get_session_id_by_user_id_from_db(user[0], db_connection)
    with PostgresUnitOfWork(db_pool) as uow:
        session = uow.sessions.get(row[0])
        session.revoke()  # noqa
        uow.commit()

    row = get_session_id_by_user_id_from_db(user[0], db_connection)

    assert row[1] is True


def test_rollback_discards_user_update(db_pool, db_connection, clean_db):
    add_new_user(db_pool)

    with pytest.raises(RuntimeError):
        with PostgresUnitOfWork(db_pool) as uow:
            row = get_user_by_username_from_db("username", db_connection)

            user = uow.users.get(row[0])
            user.disable()  # noqa

            raise RuntimeError

    row = get_user_by_username_from_db("username", db_connection)

    assert row[3] is False


def test_rollback_discards_session_update(db_pool, db_connection, clean_db):
    add_new_user(db_pool)
    user = get_user_by_username_from_db("username", db_connection)

    with PostgresUnitOfWork(db_pool) as uow:
        session = Session.create(
            user_id=user[0],
            created_at=NOW,
            lifetime=timedelta(days=30),
        )

        uow.sessions.add(session)
        uow.commit()

    with pytest.raises(RuntimeError):
        with PostgresUnitOfWork(db_pool) as uow:
            row = get_session_id_by_user_id_from_db(user[0], db_connection)
            session = uow.sessions.get(row[0])
            session.revoke()  # noqa

            raise RuntimeError

    row = get_session_id_by_user_id_from_db(user[0], db_connection)

    assert row[1] is False


def test_commit_rolls_back_all_repositories_on_flush_error(db_pool, db_connection, clean_db):
    with pytest.raises(InfrastructureError):
        with PostgresUnitOfWork(db_pool) as uow:
            user = User.create(
                "username",
                "password-super-hash",
            )

            session = Session.create(
                user_id=uuid7(),  # non-existing user_id
                created_at=NOW,
                lifetime=timedelta(days=30),
            )

            uow.users.add(user)
            uow.sessions.add(session)

            uow.commit()

    assert get_user_by_username_from_db("username", db_connection) is None


def test_returns_none_for_nonexistent_user(db_pool, clean_db):
    with PostgresUnitOfWork(db_pool) as uow:
        user = uow.users.get(uuid7())

    assert user is None


def test_returns_none_for_nonexistent_session(db_pool, clean_db):
    with PostgresUnitOfWork(db_pool) as uow:
        session = uow.sessions.get(uuid7())

    assert session is None


def test_optimistic_locking_user(db_pool, db_connection, clean_db):
    add_new_user(db_pool)
    row = get_user_by_username_from_db("username", db_connection)

    uow1 = PostgresUnitOfWork(db_pool)
    uow2 = PostgresUnitOfWork(db_pool)

    with uow1:
        with uow2:
            user1 = uow1.users.get(row[0])
            user2 = uow2.users.get(row[0])

            user1.disable()  # noqa
            uow1.commit()

            user2.disable()  # noqa
            with pytest.raises(ConcurrencyError):
                uow2.commit()


def test_optimistic_locking_session(db_pool, db_connection, clean_db):
    add_new_user(db_pool)

    user = get_user_by_username_from_db("username", db_connection)

    with PostgresUnitOfWork(db_pool) as uow:
        session = Session.create(
            user_id=user[0],
            created_at=NOW,
            lifetime=timedelta(days=30),
        )

        uow.sessions.add(session)
        uow.commit()

    row = get_session_id_by_user_id_from_db(user[0], db_connection)

    uow1 = PostgresUnitOfWork(db_pool)
    uow2 = PostgresUnitOfWork(db_pool)

    with uow1:
        with uow2:
            session1 = uow1.sessions.get(row[0])
            session2 = uow2.sessions.get(row[0])

            session1.revoke()  # noqa
            uow1.commit()

            session2.revoke()  # noqa

            with pytest.raises(ConcurrencyError):
                uow2.commit()


def test_optimistic_locking_threads_user(db_pool, db_connection, clean_db):
    add_new_user(db_pool)
    row = get_user_by_username_from_db("username", db_connection)

    barrier = threading.Barrier(2)
    result = []

    def worker(user_id: UUID):
        try:
            with PostgresUnitOfWork(db_pool) as uow:
                user = uow.users.get(user_id)
                user.disable()  # noqa

                barrier.wait()

                uow.commit()

            result.append("ok")

        except ConcurrencyError:
            result.append("error")

    t1 = threading.Thread(target=worker, args=(row[0],))
    t2 = threading.Thread(target=worker, args=(row[0],))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(result) == 2
    assert result.count("ok") == 1
    assert result.count("error") == 1


def test_optimistic_locking_threads_session(db_pool, db_connection, clean_db):
    add_new_user(db_pool)
    user_row = get_user_by_username_from_db("username", db_connection)
    with PostgresUnitOfWork(db_pool) as unit_of_work:
        s = Session.create(
            user_id=user_row[0],
            created_at=NOW,
            lifetime=timedelta(days=30),
        )
        unit_of_work.sessions.add(s)
        unit_of_work.commit()

    session_row = get_session_id_by_user_id_from_db(user_row[0], db_connection)

    barrier = threading.Barrier(2)
    result = []

    def worker(session_id: UUID):
        try:
            with PostgresUnitOfWork(db_pool) as uow:
                session = uow.sessions.get(session_id)
                session.revoke()  # noqa

                barrier.wait()

                uow.commit()

            result.append("ok")

        except ConcurrencyError:
            result.append("error")

    t1 = threading.Thread(target=worker, args=(session_row[0],))
    t2 = threading.Thread(target=worker, args=(session_row[0],))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(result) == 2
    assert result.count("ok") == 1
    assert result.count("error") == 1
