from typing import Any, Dict
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

        return new_user

    async def update_user(
        self,
        session: AsyncSession,
        user: User,
        data: Dict[str, Any],
    ) -> User:
        for key, value in data.items():
            setattr(user, key, value)

        session.add(user)

        return user


def get_user_storage() -> UserStorageProtocol:
    return SQLAlchemyUserStorage()
