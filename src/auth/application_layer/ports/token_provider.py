from typing import Protocol
from uuid import UUID

from auth.application_layer.dto.token import TokenPairDTO


class TokenProvider(Protocol):

    def issue(self, user_id: UUID, session_id: UUID) -> TokenPairDTO:
        ...

    def verify_access(self, token: str):
        ...

    def verify_refresh(self, token: str):
        ...
