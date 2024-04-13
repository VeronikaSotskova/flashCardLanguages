from abc import ABC, abstractmethod
from typing import Any

from src.db import async_session_maker
from src.repository.card import CardRepository
from src.repository.file import FileRepository
from src.repository.language import LanguageRepository
from src.repository.user import UserRepository


class BaseUnitOfWork(ABC):
    cards: Any
    files: Any
    languages: Any
    users: Any

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class SqlAlchemyUnitOfWork(BaseUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        self.cards = CardRepository(self.session)
        self.files = FileRepository(self.session)
        self.languages = LanguageRepository(self.session)
        self.users = UserRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
