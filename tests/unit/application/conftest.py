import pytest

from auth.application_layer.use_cases.auth import AuthService
from tests.unit.application.fakes import (FakeClock, FakeHasher,
                                          FakeTokenProvider,
                                          InMemoryUnitOfWork)


@pytest.fixture
def auth_context():
    uow = InMemoryUnitOfWork()

    service = AuthService(
        uow=uow,
        hasher=FakeHasher(),
        token_provider=FakeTokenProvider(),
        clock=FakeClock()
    )

    return service, uow
