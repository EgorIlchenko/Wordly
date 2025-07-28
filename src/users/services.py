from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from .crud.base import UserStorageProtocol
from .schemas import UserCreate, UserRead

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def create_user(
    session: AsyncSession,
    user_data: UserCreate,
    storage: UserStorageProtocol,
) -> UserRead:
    existing_user = await storage.get_user_by_email(
        session=session,
        email=str(user_data.email),
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_pw = hash_password(password=user_data.password)

    new_user = await storage.create_user(
        session=session,
        user=user_data,
        hashed_password=hashed_pw,
    )

    return UserRead.model_validate(new_user)
