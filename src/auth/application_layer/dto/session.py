from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateSession:
    session_id: UUID
    username: str
    created_at: datetime
    expires_at: datetime
    revoked: bool


@dataclass(frozen=True)
class RefreshRequest:
    refresh_token: str
