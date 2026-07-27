from uuid import UUID

from auth.domain.models import Session, User


class InMemoryUserRepository:
    def __init__(self):
        self.users: dict[UUID, User] = {}

    def add(self, user: User):
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

    def add(self, session: Session):
        self.sessions[session.session_id] = session

    def get(self, session_id: UUID) -> Session | None:
        return self.sessions.get(session_id)

    def list_by_user_id(self, user_id: UUID) -> list[Session]:
        return [session for session in self.sessions.values() if session.user_id == user_id]

    def remove(self, session: Session):
        self.sessions.pop(session.user_id)
