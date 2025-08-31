from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserCreateWithPassword
from auth.utils import hash_password
from core.service import BaseService
from users.crud import UserStorageProtocol

from .verification_service import VerificationService


class RegistrationService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        user_storage: UserStorageProtocol,
        code_service: VerificationService,
    ):
        super().__init__(session=session)
        self.user_storage = user_storage
        self.code_service = code_service

    async def register_user(self, user_data: UserCreateWithPassword) -> None:
        user = await self.user_storage.get_user_by_email(
            session=self.session,
            email=user_data.email,  # noqa
        )
        if user:
            if user.is_google_account:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Этот email уже используется для входа через Google. "
                    "Пожалуйста, войдите через Google.",
                )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует",
            )

        hashed_password = hash_password(
            password=user_data.password,
        )

        db_user_data = user_data.model_dump()
        del db_user_data["password"]
        db_user_data["hashed_password"] = hashed_password

        new_user = await self.user_storage.create_user(
            session=self.session,
            **db_user_data,
        )

        await self.session.commit()
        await self.session.refresh(new_user)

        await self.code_service.send_code(email=new_user.email)
