from psycopg_pool import ConnectionPool

from auth.application_layer.ports.unit_of_work import AbstractUnitOfWork
from auth.infrastructure.repo.postgres.postgres_repo import (
    PostgresSessionRepo, PostgresUserRepo)


class PostgresUnitOfWork(AbstractUnitOfWork):
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def __enter__(self):
        self._conn = self._pool.getconn()

        self.users = PostgresUserRepo(self._conn)
        self.sessions = PostgresSessionRepo(self._conn)

        self._repositories = (
            self.users,
            self.sessions
        )

        return self

    def commit(self):
        for repository in self._repositories:
            repository.flush()  # noqa

        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            super().__exit__(exc_type, exc_value, traceback)
        finally:
            self._pool.putconn(self._conn)
