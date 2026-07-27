from datetime import datetime
from sqlite3 import Row
from uuid import UUID

from auth.domain.models import Session, User


class UserMapper:

    @staticmethod
    def to_domain(row: Row):
        return User(
            user_id=UUID(row["user_id"]),
            username=row["username"],
            password_hash=row["password_hash"],
            version=row["version"],
            _disabled=bool(row["disabled"])
        )

    @staticmethod
    def to_row(user: User) -> tuple:
        return (
            str(user.user_id),
            user.username,
            user.password_hash,
            user.version,
            int(user.disabled)
        )


class SessionMapper:

    @staticmethod
    def to_domain(row: Row) -> Session:
        return Session(
            session_id=UUID(row["session_id"]),
            user_id=UUID(row["user_id"]),
            token_hash=row["token_hash"],
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            version=row["version"],
            _revoked=bool(row["revoked"]),
        )

    @staticmethod
    def to_row(session: Session) -> tuple:
        return (
            str(session.session_id),
            str(session.user_id),
            session.token_hash,
            session.created_at.isoformat(),
            session.expires_at.isoformat(),
            session.version,
            int(session.revoked),
        )
