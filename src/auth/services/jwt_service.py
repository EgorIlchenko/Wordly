import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud.sqlalchemy_refresh import SQLAlchemyRefreshSessionStorage
from auth.schemas import RefreshSessionCreate
from core.config import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE_FIELD
from core.service import BaseService
from core.settings import get_settings
from users.models import User

settings = get_settings()


class JWTService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session=session)
        self.refresh_session_storage = SQLAlchemyRefreshSessionStorage()
        self.private_key = settings.auth_jwt.private_key_path.read_text()
        self.public_key = settings.auth_jwt.public_key_path.read_text()
        self.algorithm = settings.auth_jwt.algorithm

    @staticmethod
    def _generate_verifier_and_hash() -> tuple[str, str]:
        verifier = secrets.token_urlsafe(32)
        verifier_hash = hashlib.sha256(verifier.encode()).hexdigest()
        return verifier, verifier_hash

    def _create_jwt(
        self,
        token_type: str,
        token_data: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
    ) -> tuple[str, datetime]:
        jwt_payload = {TOKEN_TYPE_FIELD: token_type}
        jwt_payload.update(token_data)

        return self.encode_jwt(
            payload=jwt_payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
        )

    def create_access_token(self, user: User) -> tuple[str, datetime]:
        jwt_payload = {
            "sub": str(user.id),
            "username": user.full_name,
        }
        return self._create_jwt(
            token_type=ACCESS_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_minutes=settings.auth_jwt.access_token_expire_minutes,
        )

    def create_refresh_token(self, user: User) -> tuple[str, datetime]:
        jwt_payload = {
            "sub": str(user.id),
        }
        return self._create_jwt(
            token_type=REFRESH_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
        )

    def encode_jwt(
        self,
        payload: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
    ) -> tuple[str, datetime]:
        to_encode = payload.copy()
        now = datetime.now(timezone.utc)
        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=expire_minutes)
        to_encode.update(
            exp=expire,
            iat=now,
        )
        encoded = jwt.encode(
            payload=to_encode,
            key=self.private_key,
            algorithm=self.algorithm,
        )
        return encoded, expire

    def decode_jwt(
        self,
        token: str | bytes,
    ) -> Any:
        decoded_payload = jwt.decode(
            jwt=token,
            key=self.public_key,
            algorithms=[self.algorithm],
        )
        return decoded_payload

    async def record_refresh_token_in_db(
        self,
        user: User,
        refresh_token: str,
        session_id: UUID,
        expire: datetime,
        verifier_hash: str,
    ) -> None:
        refresh_token_data = RefreshSessionCreate(
            session_id=session_id,
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=expire,
            verifier_hash=verifier_hash,
        )

        await self.refresh_session_storage.save_token(
            session=self.session,
            refresh_token_data=refresh_token_data,
        )
        await self.session.commit()

    async def refresh_tokens(
        self,
        session_id: UUID,
        verifier: str,
    ) -> tuple[str, str]:
        if not verifier:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Verifier is missing",
            )

        refresh_session = await self.refresh_session_storage.get_token_by_session_id(
            session=self.session,
            session_id=session_id,
        )

        if not refresh_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
            )

        received_verifier_hash = hashlib.sha256(verifier.encode()).hexdigest()
        if received_verifier_hash != refresh_session.verifier_hash:
            await self.refresh_session_storage.revoke_all_user_sessions(
                session=self.session,
                user_id=refresh_session.user_id,
            )
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token reuse detected. All sessions revoked.",
            )

        user = refresh_session.user
        access_token, _ = self.create_access_token(user=user)
        refresh_token, expire = self.create_refresh_token(user=user)
        new_verifier, new_verifier_hash = self._generate_verifier_and_hash()

        await self.refresh_session_storage.update_token(
            session=self.session,
            session_id=session_id,
            new_data={
                "refresh_token": refresh_token,
                "expires_at": expire,
                "verifier_hash": new_verifier_hash,
            },
        )
        await self.session.commit()

        return access_token, new_verifier

    async def logout_user(self, user: User) -> None:
        await self.refresh_session_storage.revoke_all_user_sessions(
            session=self.session,
            user_id=user.id,
        )
        await self.session.commit()
