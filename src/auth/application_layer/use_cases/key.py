from auth.application_layer.dto.key import PublicKeyResponse
from auth.application_layer.ports.key_provider import KeyProvider


class KeyService:
    def __init__(self, key_provider: KeyProvider):
        self.key_provider = key_provider

    def get_public_keys(self) -> PublicKeyResponse:
        return self.key_provider.get_public_keys()
