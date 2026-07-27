from abc import ABC, abstractmethod

from auth.application_layer.ports.repository import (SessionRepository,
                                                     UserRepository)


class AbstractUnitOfWork(ABC):
    users: UserRepository
    sessions: SessionRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError
