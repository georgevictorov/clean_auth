from typing import Protocol

from auth.application_layer.dto.key import PublicKeyResponse


class PublicKeyProvider(Protocol):
    def get_public_keys(self) -> PublicKeyResponse:
        ...
