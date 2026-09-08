from pathlib import Path


class FileKeysPairProvider:
    def __init__(self,
                 private_key_path: str = "/run/secrets/private_key",
                 public_key_path: str = "/run/secrets/public_key"):
        self._private_key_path = Path(private_key_path)
        self._public_key_path = Path(public_key_path)

    def get_private_key(self) -> bytes:
        return self._private_key_path.read_bytes()

    def get_public_key(self) -> bytes:
        return self._public_key_path.read_bytes()
