from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud.password_reset_protocol import PasswordResetStorageProtocol
from auth.models import PasswordResetToken


class SQLAlchemyPasswordResetStorage(PasswordResetStorageProtocol):
    async def create_or_update_token(
        self,
        session: AsyncSession,
        user_id: UUID,
        hashed_token: str,
    ) -> PasswordResetToken:
        stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        result = await session.execute(stmt)
        existing_token = result.scalar_one_or_none()

        if existing_token:
            existing_token.hashed_token = hashed_token
            existing_token.created_at = datetime.now(timezone.utc)
            existing_token.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            token_obj = existing_token
        else:
            token_obj = PasswordResetToken(
                user_id=user_id,
                hashed_token=hashed_token,
            )

        session.add(token_obj)

        return token_obj

    async def get_by_hashed_token(
        self,
        session: AsyncSession,
        hashed_token: str,
    ) -> Optional[PasswordResetToken]:
        stmt = select(PasswordResetToken).where(PasswordResetToken.hashed_token == hashed_token)
        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def delete_token(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        stmt = delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        await session.execute(stmt)
