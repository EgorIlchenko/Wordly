import hashlib
import secrets

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud.password_reset_protocol import PasswordResetStorageProtocol
from auth.services import JWTService, VerificationService
from auth.utils import hash_password
from core.celery_tasks import send_password_reset_email
from users.crud import UserStorageProtocol


class PasswordResetService:
    def __init__(
        self,
        session: AsyncSession,
        user_storage: UserStorageProtocol,
        reset_token_storage: PasswordResetStorageProtocol,
        jwt_service: JWTService,
        code_service: VerificationService,
    ):
        self.session = session
        self.user_storage = user_storage
        self.reset_token_storage = reset_token_storage
        self.jwt_service = jwt_service
        self.code_service = code_service

    async def request_password_reset(self, email: str) -> None:
        user = await self.user_storage.get_user_by_email(
            session=self.session,
            email=email,
        )

        if user and user.is_active and not user.is_google_account:
            token = secrets.token_urlsafe(32)
            hashed_token = hashlib.sha256(token.encode()).hexdigest()

            await self.reset_token_storage.create_or_update_token(
                session=self.session,
                user_id=user.id,  # noqa
                hashed_token=hashed_token,
            )
            await self.session.commit()

            send_password_reset_email.delay(email=email, token=token)

    async def reset_password(self, token: str, new_password: str) -> None:
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        reset_token_obj = await self.reset_token_storage.get_by_hashed_token(
            session=self.session,
            hashed_token=hashed_token,
        )

        if not reset_token_obj or reset_token_obj.is_expired():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token",
            )

        user = await self.user_storage.get_user_by_id(
            session=self.session,
            user_id=reset_token_obj.user_id,  # noqa
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        new_hashed_password = hash_password(password=new_password)
        await self.user_storage.update_user(
            session=self.session,
            user=user,
            data={"hashed_password": new_hashed_password},
        )

        await self.jwt_service.logout_user(user=user)

        await self.reset_token_storage.delete_token(
            session=self.session,
            user_id=user.id,
        )

        await self.session.commit()
