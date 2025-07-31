from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from auth.schemas import UserCreate


class UserStorageProtocol(ABC):
    @abstractmethod
    async def get_user_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        pass

    @abstractmethod
    async def create_user(
        self,
        session: AsyncSession,
        user: UserCreate,
        hashed_password: str,
    ) -> User:
        pass
