from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import RefreshSession
from auth.schemas import RefreshSessionCreate


class RefreshSessionStorageProtocol(ABC):
    @abstractmethod
    async def save_token(
        self,
        session: AsyncSession,
        refresh_token_data: RefreshSessionCreate,
    ) -> None:
        pass

    @abstractmethod
    async def get_token_by_session_id(
        self,
        session: AsyncSession,
        session_id: UUID,
    ) -> Optional[RefreshSession]:
        pass

    @abstractmethod
    async def update_token(
        self,
        session: AsyncSession,
        session_id: UUID,
        new_data: dict[str, Any],
    ) -> None:
        pass

    @abstractmethod
    async def delete_refresh_token(
        self,
        session: AsyncSession,
        refresh_token: str,
    ) -> None:
        pass

    @abstractmethod
    async def revoke_all_user_sessions(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        pass
