from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User

from .user_protocol import UserStorageProtocol


class SQLAlchemyUserStorage(UserStorageProtocol):
    async def get_user_by_id(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:
        result = await session.execute(select(User).where(User.id == user_id))

        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        result = await session.execute(select(User).where(User.email == email))

        return result.scalar_one_or_none()

    async def create_user(
        self,
        session: AsyncSession,
        **user_data: Any,
    ) -> User:
        new_user = User(**user_data)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user


def get_user_storage() -> UserStorageProtocol:
    return SQLAlchemyUserStorage()
