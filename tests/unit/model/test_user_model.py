from uuid import uuid7

import pytest

from auth.domain.errors import InvalidPasswordHash, InvalidUsername
from auth.domain.models import User


def create_user(
        username='test-user',
        password='hash-password'
) -> User:
    return User.create(
        username=username,
        password_hash=password,
    )


def test_create_user():
    user = create_user()

    assert user.username == 'test-user'
    assert user.password_hash == 'hash-password'
    assert user.is_active


def test_user_is_enabled_by_default():
    user = create_user()

    assert user.is_active is True


def test_create_user_no_username():
    with pytest.raises(InvalidUsername):
        create_user(username='', password='<PASSWORD>')


def test_create_user_no_password_hash():
    with pytest.raises(InvalidPasswordHash):
        create_user(username='test-user', password='')


def test_disable_user():
    user = create_user()
    user.disable()

    assert not user.is_active


def test_disable_disabled_user():
    user = create_user()

    user.disable()
    user.disable()

    assert not user.is_active


def test_enable_user():
    user = create_user()
    user.disable()
    assert not user.is_active

    user.enable()
    assert user.is_active


def test_enable_enabled_user():
    user = create_user()

    user.enable()

    assert user.is_active


def test_user_default_version_is_one():
    user = create_user()

    assert user.version == 1


def test_user_disabled_property_returns_true_after_disable():
    user = create_user()

    user.disable()

    assert user.is_active is False


def test_user_can_be_created_with_specific_version():
    user = User(
        user_id=uuid7(),
        username="test-user",
        password_hash="hash-password",
        version=5,
    )

    assert user.version == 5


def test_user_change_password():
    user = create_user()
    user.change_password('new-password')

    assert user.password_hash == 'new-password'


def test_user_change_password_empty_password_hash():
    user = create_user()

    with pytest.raises(InvalidPasswordHash):
        user.change_password('')
