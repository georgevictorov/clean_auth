from typing import Protocol
from uuid import UUID

from auth.application_layer.dto.token import TokenPairResponse, TokenPayload


class TokenProvider(Protocol):

    def issue(self, user_id: UUID, session_id: UUID) -> TokenPairResponse:
        ...

    def verify_refresh(self, token: str) -> TokenPayload:
        ...
