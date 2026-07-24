from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from auth.domain.errors import (InvalidCreationTime, InvalidExpirationTime,
                                InvalidPasswordHash, InvalidUsername, InvalidUserID)


@dataclass
class User:
    user_id: UUID
    username: str
    password_hash: str
    version: int = 1
    _disabled: bool = False

    def __post_init__(self) -> None:
        if not self.username:
            raise InvalidUsername('username is required')

        if not self.password_hash:
            raise InvalidPasswordHash('password hash is required')

    @property
    def is_active(self) -> bool:
        return not self._disabled

    def enable(self) -> None:
        self._disabled = False

    def disable(self) -> None:
        self._disabled = True


@dataclass
class Session:
    session_id: UUID
    user_id: UUID
    token_hash: str
    created_at: datetime
    expires_at: datetime
    version: int = 1
    _revoked: bool = False

    def __post_init__(self) -> None:
        if not self.user_id:
            raise InvalidUserID('user_id is required')

        if self.created_at.tzinfo is None:
            raise InvalidCreationTime("created_at must be timezone-aware")

        if self.expires_at.tzinfo is None:
            raise InvalidExpirationTime("expires_at must be timezone-aware")

        if self.expires_at <= self.created_at:
            raise InvalidExpirationTime("expires_at must be later than created_at")

    def revoke(self) -> None:
        self._revoked = True

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at <= now

    def is_active(self, now: datetime) -> bool:
        return (
                not self._revoked and
                not self.is_expired(now)
        )
