from typing import Protocol
from uuid import UUID

from auth.domain.models import Session, User


class UserRepository(Protocol):
    def add(self, user: User) -> None:
        ...

    def get(self, user_id: UUID) -> User | None:
        ...

    def get_by_username(self, username: str) -> User | None:
        ...


class SessionRepository(Protocol):
    def add(self, session: Session) -> None:
        ...

    def get(self, session_id: UUID) -> Session | None:
        ...

    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        ...

    def remove(self, session: Session) -> None:
        ...
