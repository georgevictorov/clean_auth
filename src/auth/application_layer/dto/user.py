from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateUserRequest:
    username: str
    password: str


@dataclass(frozen=True)
class DisableUserRequest:
    username: str


@dataclass(frozen=True)
class ChangePasswordRequest:
    username: str
    old_password: str
    new_password: str


@dataclass(frozen=True)
class UserInfoResponse:
    user_id: UUID
    username: str
