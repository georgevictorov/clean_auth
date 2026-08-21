from auth.domain.models import Session, User


class UserMapper:

    @staticmethod
    def to_domain(row) -> User:
        return User(
            user_id=row["user_id"],
            username=row["username"],
            password_hash=row["password_hash"],
            version=row["version"],
            _disabled=row["disabled"],
        )

    @staticmethod
    def to_row(user: User) -> tuple:
        return (
            user.user_id,
            user.username,
            user.password_hash,
            user.version,
            user.is_disabled,
        )


class SessionMapper:

    @staticmethod
    def to_domain(row) -> Session:
        return Session(
            session_id=row["session_id"],
            user_id=row["user_id"],
            refresh_token_hash=row["refresh_token_hash"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
            version=row["version"],
            _revoked=row["revoked"],
        )

    @staticmethod
    def to_row(session: Session) -> tuple:
        return (
            session.session_id,
            session.user_id,
            session.refresh_token_hash,
            session.created_at,
            session.expires_at,
            session.version,
            session.revoked,
        )
