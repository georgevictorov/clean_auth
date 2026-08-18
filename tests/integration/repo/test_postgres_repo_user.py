import pytest

from auth.domain.errors import ConcurrencyError, InfrastructureError
from auth.domain.models import User
from auth.infrastructure.repo.postgres.postgres_repo import PostgresUserRepo


def test_add_and_get_user(db_connection, clean_db):
    repo = PostgresUserRepo(db_connection)

    user = User.create(
        "username",
        "password-super-hash"
    )

    repo.add(user)
    repo.flush()

    result = repo.get(user.user_id)

    assert result == user


def test_get_by_username(db_connection, clean_db):
    repo = PostgresUserRepo(db_connection)

    user = User.create(
        "username",
        "password-super-hash"
    )

    repo.add(user)
    repo.flush()

    result = repo.get_by_username("username")

    assert result == user


def test_get_raises_error_if_conn_closed(db_connection, clean_db):
    repo = PostgresUserRepo(db_connection)
    db_connection.close()
    with pytest.raises(InfrastructureError):
        repo.get_by_username("username")


def test_flush_raises_error_if_conn_closed(db_connection, clean_db):
    repo = PostgresUserRepo(db_connection)

    user = User.create(
        "username",
        "password-super-hash"
    )

    repo.add(user)

    db_connection.close()

    with pytest.raises(InfrastructureError):
        repo.flush()


def test_flush_raises_concurrency_error_if_version_changed(db_connection, clean_db):
    repo = PostgresUserRepo(db_connection)

    user = User.create(
        "username",
        "password-super-hash"
    )

    repo.add(user)
    repo.flush()
    db_connection.commit()

    user = repo.get(user.user_id)

    user.disable()  # noqa

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            update users
                set version = version + 1
            where
                user_id = %s
            """,
            (user.user_id,),  # noqa
        )
    db_connection.commit()

    with pytest.raises(ConcurrencyError):
        repo.flush()
