from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import EmailVerificationStorageProtocol
from auth.schemas import EmailVerificationCodeCreate
from core.service import BaseService
from users.crud import UserStorageProtocol
from utils.utils import generate_code
from core.celery_tasks import send_verification_email


class VerificationService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        user_storage: UserStorageProtocol,
        code_storage: EmailVerificationStorageProtocol,
    ):
        super().__init__(session=session)
        self.user_storage = user_storage
        self.code_storage = code_storage

    async def send_code(self, email: str) -> None:
        await self.code_storage.delete_code(session=self.session, email=email)

        code = generate_code()

        code_raw = {
            "email": email,
            "code": code,
        }

        code_obj = EmailVerificationCodeCreate.model_validate(code_raw)

        await self.code_storage.save_code(session=self.session, code=code_obj)

        send_verification_email.delay(email=email, code=code)

    async def validate_code(self, email: str, code: str) -> bool:
        code_obj = await self.code_storage.get_valid_code(session=self.session, email=email)

        if not code_obj:
            raise HTTPException(status_code=404, detail="Код не найден")
        if code_obj.code != code or code_obj.is_expired():
            raise HTTPException(status_code=400, detail="Код недействителен или истёк")

        await self.code_storage.delete_code(session=self.session, email=email)

        return True

    async def verify_email(self, email: str, code: str) -> None:
        if not await self.validate_code(email=email, code=code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Код недействителен или истёк",
            )

        user = await self.user_storage.get_user_by_email(session=self.session, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        user.is_verified = True
        await self.session.commit()
