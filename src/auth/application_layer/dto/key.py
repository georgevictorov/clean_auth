from dataclasses import dataclass


@dataclass(frozen=True)
class PublicKey:
    kid: str
    paserk: str


@dataclass(frozen=True)
class PublicKeyResponse:
    keys: tuple[PublicKey, ...]
