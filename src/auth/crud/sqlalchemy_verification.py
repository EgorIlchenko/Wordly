from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from .verification_protocol import EmailVerificationStorageProtocol

from auth.models import EmailVerificationCode
from auth.schemas import EmailVerificationCodeCreate


class SQLAlchemyEmailVerificationStorage(EmailVerificationStorageProtocol):
    async def save_code(
        self,
        session: AsyncSession,
        code: EmailVerificationCodeCreate,
    ) -> None:
        new_code = EmailVerificationCode(
            email=str(code.email),
            code=code.code,
        )
        session.add(new_code)
        await session.commit()

    async def get_valid_code(
        self,
        session: AsyncSession,
        email: str,
    ) -> Optional[EmailVerificationCode]:
        stmt = select(EmailVerificationCode).where(
            EmailVerificationCode.email == email,
        )
        result = await session.execute(stmt)
        code_obj = result.scalar_one_or_none()

        if code_obj and not code_obj.is_expired():
            return code_obj
        return None

    async def delete_code(
        self,
        session: AsyncSession,
        email: str,
    ) -> None:
        stmt = delete(EmailVerificationCode).where(
            EmailVerificationCode.email == email,
        )
        await session.execute(stmt)
        await session.commit()
