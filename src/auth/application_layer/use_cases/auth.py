from datetime import timedelta

from auth.application_layer.dto.auth import LoginRequest, LogoutRequest
from auth.application_layer.dto.session import RefreshRequest
from auth.application_layer.dto.token import TokenPairResponse
from auth.application_layer.ports.clock import Clock
from auth.application_layer.ports.hasher import PasswordHasher
from auth.application_layer.ports.token_provider import TokenProvider
from auth.application_layer.ports.unit_of_work import AbstractUnitOfWork
from auth.domain.errors import InvalidCredentials, TokenDecodeError
from auth.domain.models import Session

SESSION_LIFETIME = timedelta(days=15)


class AuthService:
    def __init__(
            self,
            uow: AbstractUnitOfWork,
            hasher: PasswordHasher,
            token_provider: TokenProvider,
            clock: Clock,
    ):
        self.uow = uow
        self.hasher = hasher
        self.token_provider = token_provider
        self.clock = clock

    def login(self, data: LoginRequest) -> TokenPairResponse:
        with self.uow:
            user = self.uow.users.get_by_username(data.username)
            if user is None:
                raise InvalidCredentials('invalid credentials')

            if not self.hasher.verify(data.password, user.password_hash):
                raise InvalidCredentials('invalid credentials')

            now = self.clock.now()

            session = Session.create(
                user.user_id,
                now,
                SESSION_LIFETIME
            )

            tokens = self.token_provider.issue(user.user_id, session.session_id)

            refresh_hash = self.hasher.hash(tokens.refresh_token)
            session.rotate_refresh_token(refresh_hash)

            self.uow.sessions.add(session)
            self.uow.commit()

            return tokens

    def refresh(self, data: RefreshRequest) -> TokenPairResponse:
        with self.uow:
            session = self._get_session_from_refresh_token(data.refresh_token)

            now = self.clock.now()

            if not session.is_active(now):
                raise InvalidCredentials('invalid credentials')

            if session.refresh_token_hash is None:
                raise InvalidCredentials('invalid credentials')

            if not self.hasher.verify(data.refresh_token, session.refresh_token_hash):
                raise InvalidCredentials('invalid credentials')

            tokens = self.token_provider.issue(session.user_id, session.session_id)

            refresh_hash = self.hasher.hash(tokens.refresh_token)
            session.rotate_refresh_token(refresh_hash)

            self.uow.commit()

            return tokens

    def logout(self, data: LogoutRequest):
        with self.uow:
            session = self._get_session_from_refresh_token(data.refresh_token)

            session.revoke()

            self.uow.commit()

    def _get_session_from_refresh_token(self, refresh_token: str) -> Session:
        try:
            payload = self.token_provider.verify_refresh(refresh_token)
        except TokenDecodeError:
            raise InvalidCredentials('invalid credentials')

        session = self.uow.sessions.get(payload.session_id)

        if session is None:
            raise InvalidCredentials('invalid credentials')

        if session.user_id != payload.user_id:
            raise InvalidCredentials('invalid credentials')

        return session
