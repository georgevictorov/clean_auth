from hashlib import sha256

from pyseto import Key

from auth.application_layer.dto.key import PublicKey, PublicKeyResponse
from auth.application_layer.ports.key_pair_provider import PublicKeyProvider


class PaserkPublicKeyProvider:
    def __init__(self, public_key_provider: PublicKeyProvider):
        self.public_key_provider = public_key_provider

    def get_public_keys(self) -> PublicKeyResponse:
        pem = self.public_key_provider.get_public_key()

        key = Key.new(
            version=4,
            purpose="public",
            key=pem
        ).to_paserk()

        kid = sha256(pem).hexdigest()[:16]

        return PublicKeyResponse(
            (
                PublicKey(
                    kid=kid,
                    paserk=key
                ),
            )
        )
