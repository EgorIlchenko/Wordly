from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from .verification import EmailVerificationService
from core.service import BaseService
from auth.schemas import UserCreate, UserRead
from users.crud import UserStorageProtocol

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        storage: UserStorageProtocol,
    ):
        super().__init__(session)
        self.storage = storage
        self.verification = EmailVerificationService(session)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    async def create_user(self, user_data: UserCreate) -> UserRead:
        existing = await self.storage.get_user_by_email(
            session=self.session,
            email=str(user_data.email),
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует",
            )

        hashed_pw = self.hash_password(password=user_data.password)

        user = await self.storage.create_user(
            session=self.session,
            user=user_data,
            hashed_password=hashed_pw,
        )

        await self.verification.send_code(email=user.email)

        return UserRead.model_validate(user)

    async def verify_email(self, email: str, code: str) -> None:
        valid = await self.verification.validate_code(email=email, code=code)
        if not valid:
            raise HTTPException(status_code=400, detail="Код недействителен или истёк")

        user = await self.storage.get_user_by_email(session=self.session, email=email)
        user.is_verified = True
        await self.session.commit()
