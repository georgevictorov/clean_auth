from typing import Protocol


class PrivateKeyProvider(Protocol):
    def get_private_key(self) -> bytes:
        ...


class PublicKeyProvider(Protocol):
    def get_public_key(self) -> bytes:
        ...
