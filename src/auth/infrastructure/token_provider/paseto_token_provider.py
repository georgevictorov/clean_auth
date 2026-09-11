import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pyseto
from pyseto import Key, KeyInterface

from auth.application_layer.dto.token import TokenPairResponse, TokenPayload
from auth.application_layer.ports.key_pair_provider import (PrivateKeyProvider,
                                                            PublicKeyProvider)
from auth.domain.errors import TokenDecodeError

ACCESS_TTL = timedelta(minutes=15)


class PasetoTokenProvider:
    def __init__(
            self,
            private_key_provider: PrivateKeyProvider,
            public_key_provider: PublicKeyProvider,
    ):
        self._private_key_provider = private_key_provider
        self._public_key_provider = public_key_provider

    def _get_private_key(self) -> KeyInterface:
        return Key.new(
            version=4,
            purpose="public",
            key=self._private_key_provider.get_private_key(),
        )

    def _get_public_key(self) -> KeyInterface:
        return Key.new(
            version=4,
            purpose="public",
            key=self._public_key_provider.get_public_key(),
        )

    def issue(self, user_id: UUID, session_id: UUID) -> TokenPairResponse:
        now = datetime.now(UTC)

        # access token with timestamp for external services
        access_payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + ACCESS_TTL).timestamp()),
        }

        # refresh token without timestamp, expiration time is checked in DB
        refresh_payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": "refresh",
        }

        private_key = self._get_private_key()
        access_token = pyseto.encode(private_key, access_payload, serializer=json).decode()
        refresh_token = pyseto.encode(private_key, refresh_payload, serializer=json).decode()

        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def verify_refresh(self, token: str) -> TokenPayload:
        try:
            decoded = pyseto.decode(
                self._get_public_key(),
                token,
                deserializer=json,
            )
            payload = decoded.payload
        except Exception as e:
            raise TokenDecodeError("invalid token format or signature") from e

        if not isinstance(payload, dict):
            raise TokenDecodeError("invalid token payload")

        if payload.get("type") != "refresh":
            raise TokenDecodeError("invalid token type")

        try:
            user_id = UUID(payload["sub"])
            session_id = UUID(payload["sid"])
        except (KeyError, ValueError, TypeError) as e:
            raise TokenDecodeError("invalid payload structure") from e

        return TokenPayload(
            user_id=user_id,
            session_id=session_id,
        )
