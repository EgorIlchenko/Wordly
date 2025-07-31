from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import EmailVerificationCode
from auth.schemas import EmailVerificationCodeCreate


class EmailVerificationStorageProtocol(ABC):
    @abstractmethod
    async def save_code(
        self,
        session: AsyncSession,
        code: EmailVerificationCodeCreate,
    ) -> None:
        pass

    @abstractmethod
    async def get_valid_code(
        self,
        session: AsyncSession,
        email: str,
    ) -> Optional[EmailVerificationCode]:
        pass

    @abstractmethod
    async def delete_code(
        self,
        session: AsyncSession,
        email: str,
    ) -> None:
        pass
