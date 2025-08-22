from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserCreate
from users.models import User


class UserStorageProtocol(ABC):
    @abstractmethod
    async def get_user_by_id(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:
        pass

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
