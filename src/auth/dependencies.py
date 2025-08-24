from uuid import UUID

from fastapi import Depends, Form, HTTPException, Request, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import ACCESS_TOKEN_TYPE, TOKEN_TYPE_FIELD
from core.models import db_helper
from users.crud import SQLAlchemyUserStorage
from users.models import User

from .crud import SQLAlchemyEmailVerificationStorage
from .services import JWTService, VerificationService
from .services.registration_service import RegistrationService
from .utils import check_active_user, validate_password


def get_registration_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> RegistrationService:
    user_storage = SQLAlchemyUserStorage()
    code_storage = SQLAlchemyEmailVerificationStorage()
    code_service = VerificationService(
        session=session,
        user_storage=user_storage,
        code_storage=code_storage,
    )

    return RegistrationService(
        session=session,
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


def get_jwt_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> JWTService:
    return JWTService(session=session)


async def authenticate_user(
    email: EmailStr = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    unauthed_exp = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )
    user_storage = SQLAlchemyUserStorage()

    user = await user_storage.get_user_by_email(
        session=session,
        email=email,  # noqa
    )
    if not user:
        raise unauthed_exp

    if not validate_password(
        password=password,
        hashed_password=user.hashed_password,  # noqa
    ):
        raise unauthed_exp

    if not check_active_user(user=user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def get_current_token_payload(
    request: Request,
    jwt_service: JWTService = Depends(get_jwt_service),
) -> dict:
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in",
        )

    try:
        payload = jwt_service.decode_jwt(token=token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    user_storage = SQLAlchemyUserStorage()

    token_type = payload.get(TOKEN_TYPE_FIELD)
    if token_type != ACCESS_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id: UUID | None = payload.get("sub")
    user = await user_storage.get_user_by_id(
        session=session,
        user_id=user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
        )

    return user


async def get_current_active_auth_user(
    user: User = Depends(get_current_auth_user),
) -> User:
    if not check_active_user(user=user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user
