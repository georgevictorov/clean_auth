from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserInfoResponse:
    user_id: UUID
    username: str
