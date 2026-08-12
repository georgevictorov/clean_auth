from datetime import timedelta

import pytest

from auth.application_layer.dto.user import (ChangePasswordRequest,
                                             CreateUserRequest,
                                             DisableUserRequest)
from auth.domain.errors import (InvalidCredentials, UserAlreadyExists,
                                UserNotFound)
from auth.domain.models import Session, User
from tests.unit.application.fakes import FakeClock

NOW = FakeClock.now()
SESSION_LIFETIME = timedelta(days=15)


def create_user_request(username='john', password='password'):
    return CreateUserRequest(username=username, password=password)


class TestCreateUser:
    def test_creates_new_user(self, user_context):
        service, uow = user_context
        cmd = create_user_request()

        result = service.create_user(cmd)

        user = uow.users.get_by_username(cmd.username)

        assert result.user_id == user.user_id
        assert result.username == user.username
        assert service.hasher.verify(cmd.password, user.password_hash)

    def test_raises_user_already_exists(self, user_context):
        service, uow = user_context

        uow.users.add(User.create("john", "password"))
        cmd = create_user_request()

        with pytest.raises(UserAlreadyExists):
            service.create_user(cmd)


class TestDisableUser:
    def test_disables_user(self, user_context):
        service, uow = user_context
        user = User.create("john", "password")
        uow.users.add(user)

        cmd = DisableUserRequest(user.username)

        service.disable_user(cmd)

        assert user.is_active is False

    def test_raises_user_not_found(self, user_context):
        service, _ = user_context

        with pytest.raises(UserNotFound):
            service.disable_user(DisableUserRequest("john"))

    def test_revokes_all_sessions(self, user_context):
        service, uow = user_context
        user = User.create("john", "password")
        uow.users.add(user)

        session_1 = Session.create(
            user.user_id,
            NOW,
            SESSION_LIFETIME,
        )
        session_2 = Session.create(
            user.user_id,
            NOW,
            SESSION_LIFETIME,
        )

        uow.sessions.add(session_1)
        uow.sessions.add(session_2)

        assert session_1.is_active(NOW) is True
        assert session_2.is_active(NOW) is True

        service.disable_user(DisableUserRequest(user.username))

        assert session_1.is_active(NOW) is False
        assert session_2.is_active(NOW) is False


class TestChangePassword:
    def test_changes_password(self, user_context):
        service, uow = user_context

        user = User.create("john", "old-password")
        uow.users.add(user)

        old_hash = user.password_hash

        service.change_password(
            ChangePasswordRequest(
                username=user.username,
                old_password="old-password",
                new_password="new-password",
            )
        )

        assert user.password_hash != old_hash
        assert service.hasher.verify(
            "new-password",
            user.password_hash,
        )

    def test_raises_if_user_not_found(self, user_context):
        service, _ = user_context

        with pytest.raises(UserNotFound):
            service.change_password(
                ChangePasswordRequest(
                    username="unknown",
                    old_password="old-password",
                    new_password="new-password",
                )
            )

    def test_raises_if_old_password_invalid(self, user_context):
        service, uow = user_context

        user = User.create("john", "password")
        uow.users.add(user)

        old_password_hash = user.password_hash

        with pytest.raises(InvalidCredentials):
            service.change_password(
                ChangePasswordRequest(
                    username=user.username,
                    old_password="wrong-password",
                    new_password="new-password",
                )
            )

        assert user.password_hash == old_password_hash
