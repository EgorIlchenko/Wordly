from sqlalchemy import delete, select

from core.service import BaseService
from auth.models import EmailVerificationCode
from utils.utils import generate_code
from core.celery_tasks import send_verification_email


class EmailVerificationService(BaseService):
    async def send_code(self, email: str) -> None:
        await self.session.execute(
            delete(EmailVerificationCode).where(EmailVerificationCode.email == email)
        )

        code = generate_code()

        self.session.add(EmailVerificationCode(
            email=email,
            code=code,
        ))
        await self.session.commit()

        send_verification_email.delay(email, code)

    async def validate_code(self, email: str, code: str) -> bool:
        result = await self.session.execute(
            select(EmailVerificationCode).where(
                EmailVerificationCode.email == email,
                EmailVerificationCode.code == code,
            )
        )
        record = result.scalar_one_or_none()

        if not record or record.is_expired():
            return False

        await self.session.delete(record)
        await self.session.commit()

        return True
