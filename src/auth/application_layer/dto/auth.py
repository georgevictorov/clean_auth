from dataclasses import dataclass


@dataclass(frozen=True)
class LoginRequest:
    username: str
    password: str


@dataclass(frozen=True)
class LogoutRequest:
    refresh_token: str
