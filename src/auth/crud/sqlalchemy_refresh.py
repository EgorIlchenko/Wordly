from typing import Any, Optional
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from auth.models import RefreshSession
from auth.schemas import RefreshSessionCreate

from .refresh_session_protocol import RefreshSessionStorageProtocol


class SQLAlchemyRefreshSessionStorage(RefreshSessionStorageProtocol):
    async def save_token(
        self,
        session: AsyncSession,
        refresh_token_data: RefreshSessionCreate,
    ) -> None:
        new_refresh_session = RefreshSession(
            id=refresh_token_data.session_id,
            user_id=refresh_token_data.user_id,
            refresh_token=refresh_token_data.refresh_token,
            expires_at=refresh_token_data.expires_at,
            verifier_hash=refresh_token_data.verifier_hash,
        )
        session.add(new_refresh_session)

    async def get_token_by_session_id(
        self,
        session: AsyncSession,
        session_id: UUID,
    ) -> Optional[RefreshSession]:
        stmt = (
            select(RefreshSession)
            .where(RefreshSession.id == session_id)
            .options(joinedload(RefreshSession.user))
        )
        result = await session.execute(stmt)
        session_obj = result.scalar_one_or_none()

        if session_obj and not session_obj.is_expired() and not session_obj.is_revoked:
            return session_obj
        return None

    async def update_token(
        self,
        session: AsyncSession,
        session_id: UUID,
        new_data: dict[str, Any],
    ) -> None:
        stmt = update(RefreshSession).where(RefreshSession.id == session_id).values(**new_data)
        await session.execute(stmt)

    async def delete_refresh_token(
        self,
        session: AsyncSession,
        refresh_token: str,
    ) -> None:
        stmt = delete(RefreshSession).where(
            RefreshSession.refresh_token == refresh_token,
        )
        await session.execute(stmt)

    async def revoke_all_user_sessions(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        stmt = (
            update(RefreshSession).where(RefreshSession.user_id == user_id).values(is_revoked=True)
        )
        await session.execute(stmt)
