import pytest

from auth.application_layer.dto.auth import LoginRequest, LogoutRequest
from auth.application_layer.dto.session import RefreshRequest
from auth.domain.errors import InvalidCredentials
from auth.domain.models import User
from tests.unit.application.fakes import (FakeClock, FakeHasher,
                                          FakeTokenProvider)


def create_test_user(
        username="john",
        password="password"
):
    return User.create(
        username=username,
        password_hash=password
    )


def create_login_request(username="john", password="password"):
    return LoginRequest(
        username=username,
        password=password
    )


def create_refresh_request(refresh_token=""):
    return RefreshRequest(
        refresh_token=refresh_token
    )


def create_logout_request(refresh_token=""):
    return LogoutRequest(
        refresh_token=refresh_token
    )


def login(service, uow):
    user = create_test_user()
    uow.users.add(user)

    tokens = service.login(create_login_request())

    return user, tokens


class TestLogin:
    def test_creates_new_session(self, auth_context):
        service, uow = auth_context
        user, _ = login(service, uow)

        sessions = uow.sessions.list_by_user_id(user.user_id)

        assert len(sessions) == 1

        session = sessions[0]

        assert session.user_id == user.user_id
        assert session.refresh_token_hash is not None
        assert session.is_active(FakeClock.now())

    def test_raises_invalid_credentials_when_username_is_unknown(self, auth_context):
        service, _ = auth_context

        cmd = create_login_request(username="")

        with pytest.raises(InvalidCredentials):
            service.login(cmd)

    def test_raises_invalid_credentials_when_password_is_invalid(self, auth_context):
        service, uow = auth_context

        user = create_test_user(password="correct")
        uow.users.add(user)

        cmd = create_login_request(password="wrong")

        with pytest.raises(InvalidCredentials):
            service.login(cmd)


class TestRefresh:
    def test_rotates_refresh_token(self, auth_context):
        service, uow = auth_context
        _, old_tokens = login(service, uow)

        cmd = create_refresh_request(old_tokens.refresh_token)

        new_tokens = service.refresh(cmd)

        assert new_tokens.access_token != old_tokens.access_token
        assert new_tokens.refresh_token != old_tokens.refresh_token

    def test_rotates_refresh_token_hash(self, auth_context):
        service, uow = auth_context
        user, old_tokens = login(service, uow)

        cmd = create_refresh_request(old_tokens.refresh_token)

        new_tokens = service.refresh(cmd)

        session = uow.sessions.list_by_user_id(user.user_id)[0]

        assert FakeHasher.verify(
            new_tokens.refresh_token,
            session.refresh_token_hash,
        )

    def test_invalidates_previous_refresh_token(self, auth_context):
        service, uow = auth_context
        _, old_tokens = login(service, uow)

        cmd = create_refresh_request(old_tokens.refresh_token)

        service.refresh(cmd)

        with pytest.raises(InvalidCredentials):
            service.refresh(cmd)

    def test_allows_using_new_refresh_token(self, auth_context):
        service, uow = auth_context
        _, old_tokens = login(service, uow)

        cmd = create_refresh_request(old_tokens.refresh_token)

        new_tokens = service.refresh(cmd)

        again = service.refresh(
            create_refresh_request(new_tokens.refresh_token)
        )

        assert again.refresh_token != new_tokens.refresh_token
        assert again.access_token != new_tokens.access_token

    def test_raises_invalid_credentials_when_refresh_token_is_invalid(self, auth_context):
        service, uow = auth_context
        _, tokens = login(service, uow)

        with pytest.raises(InvalidCredentials):
            cmd = create_refresh_request(f"{tokens.refresh_token}-invalid")
            service.refresh(cmd)

    def test_raises_invalid_credentials_when_session_does_not_exist(self, auth_context):
        service, uow = auth_context
        _, old_tokens = login(service, uow)

        payload = FakeTokenProvider.verify_refresh(old_tokens.refresh_token)
        del uow.sessions.sessions[payload.session_id]

        with pytest.raises(InvalidCredentials):
            service.refresh(create_refresh_request(old_tokens.refresh_token))

    def test_raises_invalid_credentials_when_session_is_expired(self, auth_context):
        service, uow = auth_context
        user, old_tokens = login(service, uow)

        session = uow.sessions.list_by_user_id(user.user_id)[0]
        session.expires_at = FakeClock.now()

        with pytest.raises(InvalidCredentials):
            service.refresh(create_refresh_request(old_tokens.refresh_token))

    def test_raises_invalid_credentials_when_session_is_revoked(self, auth_context):
        service, uow = auth_context
        user, old_tokens = login(service, uow)

        session = uow.sessions.list_by_user_id(user.user_id)[0]
        session.revoke()

        with pytest.raises(InvalidCredentials):
            service.refresh(create_refresh_request(old_tokens.refresh_token))

    def test_raises_invalid_credentials_when_refresh_token_hash_does_not_match(self, auth_context):
        service, uow = auth_context
        user, old_tokens = login(service, uow)

        session = uow.sessions.list_by_user_id(user.user_id)[0]
        session.rotate_refresh_token(
            FakeHasher.hash(f"{old_tokens.refresh_token}-invalid")
        )

        with pytest.raises(InvalidCredentials):
            service.refresh(create_refresh_request(old_tokens.refresh_token))

    def test_commits_unit_of_work(self, auth_context):
        service, uow = auth_context
        _, old_tokens = login(service, uow)

        service.refresh(
            create_refresh_request(old_tokens.refresh_token)
        )

        assert uow.committed


class TestLogout:
    def test_revokes_user_sessions(self, auth_context):
        service, uow = auth_context
        user, token = login(service, uow)

        service.logout(create_logout_request(token.refresh_token))

        session = uow.sessions.list_by_user_id(user.user_id)[0]

        assert session.revoked is True
        assert session.is_active(FakeClock.now()) is False

    def test_commits_unit_of_work(self, auth_context):
        service, uow = auth_context

        _, tokens = login(service, uow)

        service.logout(
            create_logout_request(tokens.refresh_token)
        )

        assert uow.committed

    def test_logout_is_idempotent_for_revoked_session(self, auth_context):
        service, uow = auth_context

        _, tokens = login(service, uow)

        request = create_logout_request(tokens.refresh_token)

        service.logout(request)

        service.logout(request)

    def test_raises_invalid_credentials_when_refresh_token_is_invalid(self, auth_context):
        service, uow = auth_context

        with pytest.raises(InvalidCredentials):
            service.logout(
                create_logout_request("invalid-token")
            )

    def test_raises_invalid_credentials_when_session_does_not_exist(self, auth_context):
        service, uow = auth_context

        _, tokens = login(service, uow)

        payload = FakeTokenProvider.verify_refresh(
            tokens.refresh_token
        )

        del uow.sessions.sessions[payload.session_id]

        with pytest.raises(InvalidCredentials):
            service.logout(
                create_logout_request(tokens.refresh_token)
            )

    def test_does_not_revoke_other_sessions(self, auth_context):
        service, uow = auth_context

        user, first_tokens = login(service, uow)

        service.login(create_login_request())

        service.logout(create_logout_request(first_tokens.refresh_token))

        sessions = uow.sessions.list_by_user_id(user.user_id)

        revoked = [session.revoked for session in sessions]

        assert revoked == [True, False]
