from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TokenPairResponse:
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class TokenPayload:
    user_id: UUID
    session_id: UUID
