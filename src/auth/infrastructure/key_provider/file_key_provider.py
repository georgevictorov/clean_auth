from hashlib import sha256
from pathlib import Path

import pyseto

from auth.application_layer.dto.key import PublicKey, PublicKeyResponse
from auth.application_layer.ports.key_provider import KeyProvider


class FileKeyProvider(KeyProvider):
    def __init__(self, public_key_path: str):
        self._public_key_path = Path(public_key_path)

    def get_public_keys(self) -> PublicKeyResponse:
        public_key_pem = self._public_key_path.read_bytes()

        public_key = pyseto.Key.new(
            version=4,
            purpose="public",
            key=public_key_pem,
        )

        paserk = public_key.to_paserk()
        kid = sha256(public_key_pem).hexdigest()[:16]

        return PublicKeyResponse(
            keys=(
                PublicKey(
                    kid=kid,
                    paserk=paserk,
                ),
            )
        )
