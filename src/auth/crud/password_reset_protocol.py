from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import PasswordResetToken


class PasswordResetStorageProtocol(ABC):
    @abstractmethod
    async def create_or_update_token(
        self,
        session: AsyncSession,
        user_id: UUID,
        hashed_token: str,
    ) -> PasswordResetToken:
        pass

    @abstractmethod
    async def get_by_hashed_token(
        self,
        session: AsyncSession,
        hashed_token: str,
    ) -> Optional[PasswordResetToken]:
        pass

    @abstractmethod
    async def delete_token(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        pass
