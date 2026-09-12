from psycopg_pool import ConnectionPool

from auth.application_layer.use_cases import auth, key, user
from auth.config import get_postgres_uri
from auth.infrastructure.clock.system_clock import SystemClock
from auth.infrastructure.hasher.argon2.hasher import Argon2PasswordHasher
from auth.infrastructure.key_provider.file_key_pair_provider import \
    FileKeysPairProvider
from auth.infrastructure.public_key_provider.paserk_provider import \
    PaserkPublicKeyProvider
from auth.infrastructure.token_provider.paseto_token_provider import \
    PasetoTokenProvider
from auth.infrastructure.uow.postgres.postgres_uow import PostgresUnitOfWork

# composition root

def create_pool() -> ConnectionPool:
    return ConnectionPool(
        conninfo=get_postgres_uri(),
        min_size=1,
        max_size=5,
    )


class CLIContainer:
    def __init__(self):
        self._pool = create_pool()

        self.user_service = user.UserService(
            uow=PostgresUnitOfWork(pool=self._pool),
            hasher=Argon2PasswordHasher()
        )

    def close(self):
        self._pool.close()


class FlaskContainer:
    def __init__(self):
        self._pool = create_pool()
        self._key_provider = FileKeysPairProvider()

        self.auth_service = auth.AuthService(
            uow=PostgresUnitOfWork(pool=self._pool),
            hasher=Argon2PasswordHasher(),
            token_provider=PasetoTokenProvider(private_key_provider=self._key_provider,
                                               public_key_provider=self._key_provider),
            clock=SystemClock(),
        )

        self.key_service = key.KeyService(
            key_provider=PaserkPublicKeyProvider(public_key_provider=self._key_provider),
        )

    def close(self):
        self._pool.close()

# register_auth_routes(app, container.auth_service)
# register_key_routes(app, container.key_service)
