import pytest

from auth.application_layer.use_cases.auth import AuthService
from auth.application_layer.use_cases.user import UserService
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


@pytest.fixture
def user_context():
    uow = InMemoryUnitOfWork()

    service = UserService(
        uow=uow,
        hasher=FakeHasher()
    )

    return service, uow
