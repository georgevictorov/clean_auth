from copy import deepcopy
from uuid import UUID

import psycopg

from auth.domain.errors import ConcurrencyError, InfrastructureError
from auth.domain.models import Session, User
from auth.infrastructure.repo.postgres.mapper import UserMapper


class PostgresUserRepo:
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

        self._identity_map: dict[UUID, User] = {}
        self._snapshot: dict[UUID, User] = {}
        self._username_map: dict[str, User] = {}

    def add(self, user: User) -> None:
        self._identity_map[user.user_id] = user
        self._username_map[user.username] = user

    def get(self, user_id: UUID) -> User | None:
        if user_id in self._identity_map:
            return self._identity_map[user_id]

        try:
            with self._conn.cursor() as cursor:
                cursor.execute(
                    """
                    select 
                        user_id, 
                        username,  
                        password_hash,
                        version,
                        disabled
                    from users 
                        where user_id = %s
                    """, (user_id,),
                )

                user_row = cursor.fetchone()

                if user_row is None:
                    return None

                user = UserMapper.to_domain(user_row)

                return self._track(user)

        except psycopg.Error as e:
            raise InfrastructureError from e

    def get_by_username(self, username: str) -> User | None:
        if username in self._username_map:
            return self._username_map[username]
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(
                    """
                    select
                        user_id,
                        username,
                        password_hash,
                        version,
                        disabled
                    from users
                        where username = %s
                    """,
                    (username,),
                )

                user_row = cursor.fetchone()

                if user_row is None:
                    return None

                user = UserMapper.to_domain(user_row)

                if user.user_id in self._identity_map:
                    return self._identity_map[user.user_id]

                return self._track(user)

        except psycopg.Error as e:
            raise InfrastructureError from e

    def flush(self):
        try:
            for user_id, user in self._identity_map.items():

                snapshot = self._snapshot.get(user_id)

                if snapshot is None:
                    self._insert(user)
                    self._track(user)

                elif snapshot != user:
                    self._update(user)
                    self._track(user)

        except psycopg.Error as e:
            raise InfrastructureError from e

    def _track(self, user: User) -> User:
        old = self._snapshot.get(user.user_id)
        if old is not None and old.username != user.username:
            self._username_map.pop(old.username, None)

        self._identity_map[user.user_id] = user
        self._snapshot[user.user_id] = deepcopy(user)
        self._username_map[user.username] = user
        return user

    def _insert(self, user: User):
        with self._conn.cursor() as cursor:
            cursor.execute(
                """
                insert into users(
                    user_id,
                    username,
                    password_hash,
                    version,
                    disabled
                )
                values (%s, %s, %s, %s, %s)
                """,
                UserMapper.to_row(user),
            )

    def _update(self, user: User):
        with self._conn.cursor() as cursor:
            cursor.execute(
                """
                update users
                set
                    username = %s,
                    password_hash = %s,
                    version = version + 1,
                    disabled = %s
                where
                    user_id = %s and
                    version = %s
                """,
                (
                    user.username,
                    user.password_hash,
                    user.is_active,
                    user.user_id,
                    user.version,
                ),
            )

            if cursor.rowcount != 1:
                raise ConcurrencyError

        user.version += 1
