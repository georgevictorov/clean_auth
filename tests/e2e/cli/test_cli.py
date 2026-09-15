import sys
from typing import Any

import pexpect


def run_cli(*args: str) -> pexpect.spawn:
    child = pexpect.spawn(
        sys.executable,
        ["-m", "auth.api.cli.main", *args],
        encoding="utf-8",
    )
    return child


def enter_password_pair(
        child: pexpect.spawn,
        password: str,
        password_confirm: str | None = None,
) -> None:
    if password_confirm is None:
        password_confirm = password

    child.expect("password: ")
    child.sendline(password)

    child.expect("confirm password: ")
    child.sendline(password_confirm)


def enter_change_password(
        child: pexpect.spawn,
        old_password: str,
        new_password: str,
        new_password_confirm: str | None = None,
) -> None:
    if new_password_confirm is None:
        new_password_confirm = new_password

    child.expect("enter old password: ")
    child.sendline(old_password)

    child.expect("enter new password: ")
    child.sendline(new_password)

    child.expect("confirm new password: ")
    child.sendline(new_password_confirm)


def finish_cli(child: pexpect.spawn) -> tuple[int | None, Any | None]:
    child.expect(pexpect.EOF)
    child.close()

    return child.exitstatus, child.before


def test_create_user(clean_db):
    child = run_cli("create-user", "george")

    enter_password_pair(child, "password123")

    exitstatus, output = finish_cli(child)

    assert exitstatus == 0
    assert "user: george created with id:" in output


def test_create_user_already_exists(clean_db):
    child = run_cli("create-user", "george")
    enter_password_pair(child, "password123")

    exitstatus, _ = finish_cli(child)

    assert exitstatus == 0

    child = run_cli("create-user", "george")
    enter_password_pair(child, "password123")

    exitstatus, output = finish_cli(child)

    assert exitstatus == 1
    assert "user already exists" in output


def test_create_user_passwords_do_not_match(clean_db):
    child = run_cli("create-user", "george")

    enter_password_pair(
        child,
        password="password123",
        password_confirm="different",
    )

    exitstatus, output = finish_cli(child)

    assert exitstatus == 1
    assert "passwords do not match" in output


def test_disable_user(clean_db):
    child = run_cli("create-user", "george")
    enter_password_pair(child, "password123")

    exitstatus, _ = finish_cli(child)

    assert exitstatus == 0

    child = run_cli("disable-user", "george")

    exitstatus, output = finish_cli(child)

    assert exitstatus == 0
    assert "user: george disabled" in output


def test_disable_user_not_found(clean_db):
    child = run_cli("disable-user", "george")

    exitstatus, output = finish_cli(child)

    assert exitstatus == 1
    assert "user does not exist" in output


def test_change_password(clean_db):
    child = run_cli("create-user", "george")
    enter_password_pair(child, "old-password")

    exitstatus, _ = finish_cli(child)

    assert exitstatus == 0

    child = run_cli("change-password", "george")

    enter_change_password(
        child,
        old_password="old-password",
        new_password="new-password",
    )

    exitstatus, output = finish_cli(child)

    assert exitstatus == 0
    assert "user: george changed password" in output


def test_change_password_user_not_found(clean_db):
    child = run_cli("change-password", "george")

    enter_change_password(
        child,
        old_password="old-password",
        new_password="new-password",
    )

    exitstatus, output = finish_cli(child)

    assert exitstatus == 1
    assert "user does not exist" in output


def test_change_password_invalid_old_password(clean_db):
    child = run_cli("create-user", "george")
    enter_password_pair(child, "old-password")

    exitstatus, _ = finish_cli(child)

    assert exitstatus == 0

    child = run_cli("change-password", "george")

    enter_change_password(
        child,
        old_password="wrong-password",
        new_password="new-password",
    )

    exitstatus, output = finish_cli(child)

    assert exitstatus == 1
    assert "invalid credentials" in output


def test_change_password_passwords_do_not_match(clean_db):
    child = run_cli("create-user", "george")
    enter_password_pair(child, "old-password")

    exitstatus, _ = finish_cli(child)

    assert exitstatus == 0

    child = run_cli("change-password", "george")

    enter_change_password(
        child,
        old_password="old-password",
        new_password="new-password",
        new_password_confirm="different",
    )

    exitstatus, output = finish_cli(child)

    assert exitstatus == 1
    assert "passwords do not match" in output
