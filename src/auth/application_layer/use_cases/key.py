from auth.application_layer.dto.key import PublicKeyResponse
from auth.application_layer.ports.public_key_provider import PublicKeyProvider


class KeyService:
    def __init__(self, key_provider: PublicKeyProvider):
        self.key_provider = key_provider

    def get_public_keys(self) -> PublicKeyResponse:
        return self.key_provider.get_public_keys()
