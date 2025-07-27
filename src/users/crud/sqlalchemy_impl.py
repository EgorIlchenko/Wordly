from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from users.schemas import UserCreate
from users.crud.base import UserStorageProtocol


class SQLAlchemyUserStorage(UserStorageProtocol):
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
        user: UserCreate,
        hashed_password: str,
    ) -> User:
        new_user = User(
            email=str(user.email),
            full_name=user.full_name,
            hashed_password=hashed_password,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
