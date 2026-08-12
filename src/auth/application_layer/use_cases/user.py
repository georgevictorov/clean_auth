from auth.application_layer.dto.user import (ChangePasswordRequest,
                                             CreateUserRequest,
                                             DisableUserRequest,
                                             UserInfoResponse)
from auth.application_layer.ports.hasher import PasswordHasher
from auth.application_layer.ports.unit_of_work import AbstractUnitOfWork
from auth.domain.errors import (InvalidCredentials, UserAlreadyExists,
                                UserNotFound)
from auth.domain.models import User


class UserService:
    def __init__(
            self,
            uow: AbstractUnitOfWork,
            hasher: PasswordHasher
    ):
        self.uow = uow
        self.hasher = hasher

    def create_user(self, data: CreateUserRequest) -> UserInfoResponse:
        with self.uow:
            user = self.uow.users.get_by_username(data.username)
            if user:
                raise UserAlreadyExists('user with that username already exists')

            password_hash = self.hasher.hash(data.password)
            user = User.create(username=data.username, password_hash=password_hash)

            self.uow.users.add(user)
            self.uow.commit()

            return UserInfoResponse(user_id=user.user_id, username=user.username)

    def disable_user(self, data: DisableUserRequest):
        with self.uow:
            user = self.uow.users.get_by_username(data.username)
            if not user:
                raise UserNotFound('user does not exist')

            user.disable()

            for session in self.uow.sessions.list_by_user_id(user.user_id):
                session.revoke()

            self.uow.commit()

    def change_password(self, data: ChangePasswordRequest):
        with self.uow:
            user = self.uow.users.get_by_username(data.username)
            if not user:
                raise UserNotFound('user does not exist')

            if not self.hasher.verify(data.old_password, user.password_hash):
                raise InvalidCredentials('invalid credentials')

            new_password_hash = self.hasher.hash(data.new_password)

            user.change_password(new_password_hash)

            self.uow.commit()
