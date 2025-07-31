from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from users.crud import SQLAlchemyUserStorage

from .crud import SQLAlchemyEmailVerificationStorage
from .services import UserService, VerificationService
from .services.registration_service import RegistrationService


def get_registration_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> RegistrationService:
    user_storage = SQLAlchemyUserStorage()
    user_service = UserService(
        session=session,
        storage=user_storage,
    )
    code_storage = SQLAlchemyEmailVerificationStorage()
    code_service = VerificationService(
        session=session,
        user_storage=user_storage,
        code_storage=code_storage,
    )

    return RegistrationService(
        session=session,
        user_service=user_service,
        user_storage=user_storage,
        code_service=code_service,
    )


def get_verification_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> VerificationService:
    user_storage = SQLAlchemyUserStorage()
    code_storage = SQLAlchemyEmailVerificationStorage()

    return VerificationService(
        session=session,
        user_storage=user_storage,
        code_storage=code_storage,
    )
