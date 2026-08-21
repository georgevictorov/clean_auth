from copy import deepcopy
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from auth.domain.errors import ConcurrencyError, InfrastructureError
from auth.domain.models import Session, User
from auth.infrastructure.repo.postgres.mapper import SessionMapper, UserMapper


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
            with self._conn.cursor(row_factory=dict_row) as cursor:
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


class PostgresSessionRepo:
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

        self._identity_map: dict[UUID, Session] = {}
        self._snapshot: dict[UUID, Session] = {}

    def add(self, session: Session) -> None:
        self._identity_map[session.session_id] = session

    def get(self, session_id: UUID) -> Session | None:
        if session_id in self._identity_map:
            return self._identity_map[session_id]

        try:
            with self._conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select
                        session_id,
                        user_id,
                        refresh_token_hash,
                        created_at,
                        expires_at,
                        version,
                        revoked
                    from sessions
                    where
                        session_id = %s
                    """, (session_id,),
                )

                session_row = cursor.fetchone()

                if session_row is None:
                    return None

                session = SessionMapper.to_domain(session_row)

                return self._track(session)

        except psycopg.Error as e:
            raise InfrastructureError from e

    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(
                    """
                    select 
                        session_id,
                        user_id,
                        refresh_token_hash,
                        created_at,
                        expires_at,
                        version,
                        revoked
                    from sessions
                    where
                        user_id = %s
                    """, (user_id,),
                )

                sessions = []

                for row in cursor.fetchall():
                    session_id = row[0]

                    if session_id in self._identity_map:
                        session = self._identity_map[session_id]
                    else:
                        session = SessionMapper.to_domain(row)
                        self._track(session)

                    sessions.append(session)

                return sessions

        except psycopg.Error as e:
            raise InfrastructureError from e

    def flush(self):
        try:
            for session_id, session in self._identity_map.items():
                snapshot = self._snapshot.get(session_id)

                if snapshot is None:
                    self._insert(session)
                    self._track(session)
                elif snapshot != session:
                    self._update(session)
                    self._track(session)

        except psycopg.Error as e:
            raise InfrastructureError from e

    def _track(self, session: Session) -> Session:
        self._identity_map[session.session_id] = session
        self._snapshot[session.session_id] = deepcopy(session)
        return session

    def _insert(self, session: Session):
        with self._conn.cursor() as cursor:
            cursor.execute(
                """
                insert into sessions(
                    session_id,
                    user_id,
                    refresh_token_hash,
                    created_at,
                    expires_at,
                    version,
                    revoked
                )
                values (%s, %s, %s, %s, %s, %s, %s)
                """,
                SessionMapper.to_row(session),
            )

    def _update(self, session: Session):
        with self._conn.cursor() as cursor:
            cursor.execute(
                """
                update sessions
                set
                    refresh_token_hash = %s,
                    created_at = %s,
                    expires_at = %s,
                    version = version + 1,
                    revoked = %s
                where
                    session_id = %s and
                    version = %s
                """,
                (
                    session.refresh_token_hash,
                    session.created_at,
                    session.expires_at,
                    session.revoked,
                    session.session_id,
                    session.version,

                ),
            )

            if cursor.rowcount != 1:
                raise ConcurrencyError

        session.version += 1
