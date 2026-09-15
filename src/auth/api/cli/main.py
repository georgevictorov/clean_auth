import argparse
import getpass
import sys

from auth.application_layer.dto.user import (ChangePasswordRequest,
                                             CreateUserRequest,
                                             DisableUserRequest)
from auth.bootstrap import CLIContainer
from auth.domain import errors


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='auth')
    subparsers = parser.add_subparsers(
        dest='command',
        required=True,
    )

    create_user_parser = subparsers.add_parser(
        "create-user",
        help="create a new user",
    )
    create_user_parser.add_argument("username", type=str, help="username")

    disable_user_parser = subparsers.add_parser(
        "disable-user",
        help="disable a user",
    )
    disable_user_parser.add_argument("username", type=str, help="username")

    change_password_parser = subparsers.add_parser(
        "change-password",
        help="change a user's password",
    )
    change_password_parser.add_argument("username", type=str, help="username")

    return parser


def create_user_cli(container: CLIContainer, username: str) -> int:
    password = getpass.getpass(prompt="password: ")
    password_confirm = getpass.getpass(prompt="confirm password: ")
    if password != password_confirm:
        print("passwords do not match", file=sys.stderr)
        return 1

    try:
        cmd = CreateUserRequest(
            username=username,
            password=password,
        )
        user_info = container.user_service.create_user(cmd)
    except errors.UserAlreadyExists:
        print("user already exists", file=sys.stderr)
        return 1
    except errors.ValidationError:
        print("incorrect data", file=sys.stderr)
        return 1

    print(f"user: {user_info.username} created with id: {user_info.user_id}1")
    return 0


def disable_user_cli(container: CLIContainer, username: str) -> int:
    try:
        cmd = DisableUserRequest(username=username)
        container.user_service.disable_user(cmd)
    except errors.UserNotFound:
        print("user does not exist", file=sys.stderr)
        return 1

    print(f"user: {username} disabled")
    return 0


def change_password_cli(container: CLIContainer, username: str) -> int:
    old_password = getpass.getpass(prompt="enter old password: ")

    new_password = getpass.getpass(prompt="enter new password: ")
    new_password_confirm = getpass.getpass(prompt="confirm new password: ")
    if new_password != new_password_confirm:
        print("passwords do not match", file=sys.stderr)
        return 1

    try:
        cmd = ChangePasswordRequest(
            username=username,
            old_password=old_password,
            new_password=new_password,
        )
        container.user_service.change_password(cmd)
    except errors.UserNotFound:
        print("user does not exist", file=sys.stderr)
        return 1
    except errors.InvalidCredentials:
        print("invalid credentials", file=sys.stderr)
        return 1

    print(f"user: {username} changed password")
    return 0


def main():
    parser = create_parser()
    args = parser.parse_args()

    container = CLIContainer()

    try:
        match args.command:
            case "create-user":
                return create_user_cli(container, args.username)
            case "disable-user":
                return disable_user_cli(container, args.username)
            case "change-password":
                return change_password_cli(container, args.username)
    finally:
        container.close()


if __name__ == "__main__":
    raise SystemExit(main())
