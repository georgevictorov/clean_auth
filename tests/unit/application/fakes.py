from datetime import UTC, datetime
from uuid import UUID

from auth.application_layer.dto.key import PublicKeyResponse
from auth.application_layer.dto.token import TokenPairResponse, TokenPayload
from auth.application_layer.ports.unit_of_work import AbstractUnitOfWork
from auth.domain.errors import TokenDecodeError
from auth.domain.models import Session, User


class InMemoryUserRepository:
    def __init__(self):
        self.users: dict[UUID, User] = {}

    def add(self, user: User) -> None:
        self.users[user.user_id] = user

    def get(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        for user in self.users.values():
            if user.username == username:
                return user
        return None


class InMemorySessionRepository:
    def __init__(self):
        self.sessions: dict[UUID, Session] = {}

    def add(self, session: Session) -> None:
        self.sessions[session.session_id] = session

    def get(self, session_id: UUID) -> Session | None:
        return self.sessions.get(session_id)

    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        return [session for session in self.sessions.values() if session.user_id == user_id]


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.users = InMemoryUserRepository()
        self.sessions = InMemorySessionRepository()

        self.committed = False

    def __enter__(self):
        return self

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeHasher:
    @staticmethod
    def hash(password: str) -> str:
        return password

    @staticmethod
    def verify(password: str, password_hash: str) -> bool:
        return password == password_hash


class FakeTokenProvider:
    def __init__(self):
        self.counter = 0

    def issue(self, user_id, session_id):
        self.counter += 1

        return TokenPairResponse(
            access_token=f"{user_id}:{session_id}:a{self.counter}",
            refresh_token=f"{user_id}:{session_id}:r{self.counter}",
        )

    @staticmethod
    def verify_refresh(token: str):
        try:
            user_id, session_id, _ = token.split(":")

            return TokenPayload(
                user_id=UUID(user_id),
                session_id=UUID(session_id)
            )
        except Exception as e:
            raise TokenDecodeError from e


class FakeClock:
    NOW = datetime(
        2026, 1, 1,
        tzinfo=UTC
    )

    @staticmethod
    def now():
        return FakeClock.NOW


class FakeKeyProvider:
    def __init__(self, response: PublicKeyResponse) -> None:
        self.response = response
        self.counter = 0

    def get_public_keys(self) -> PublicKeyResponse:
        self.counter += 1
        return self.response
