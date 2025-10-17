import asyncio
from json import JSONDecodeError
from typing import Optional

import httpx
from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.schemas import UserCreateFromOAuth
from core.config import GOOGLE_TOKEN_URL
from core.settings import get_settings
from users.crud import UserStorageProtocol
from users.models import User

settings = get_settings()


class GoogleAuthService:
    def __init__(self, session: AsyncSession, user_storage: UserStorageProtocol):
        self.session = session
        self.user_storage = user_storage
        self.google_settings = settings.google_auth

    async def _get_google_tokens(self, code: str) -> dict:
        data = {
            "client_id": self.google_settings.client_id,
            "client_secret": self.google_settings.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.google_settings.redirect_uri,
            "code": code,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=GOOGLE_TOKEN_URL, data=data, timeout=5)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPStatusError, JSONDecodeError):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials with Google",
                )

    async def _decode_google_id_token(self, user_id_token: str) -> dict:
        try:
            id_info = await asyncio.to_thread(
                id_token.verify_oauth2_token,
                id_token=user_id_token,
                request=requests.Request(),
                audience=self.google_settings.client_id,
                clock_skew_in_seconds=0,
            )
            return id_info

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    async def _get_or_create_user(self, user_info: dict) -> User | None:
        user_email = user_info.get("email")

        user: Optional[User] = await self.user_storage.get_user_by_email(
            session=self.session,
            email=user_email,
        )

        if user:
            if user.is_google_account:
                return user

            user.is_google_account = True
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

            return user

        user_to_create = UserCreateFromOAuth(
            email=user_info["email"],
            full_name=user_info.get("name"),
            avatar_url=user_info.get("picture"),
        )
        db_user_data = user_to_create.model_dump()

        user = await self.user_storage.create_user(
            session=self.session,
            **db_user_data,
        )

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_user_from_google(self, code: str) -> User:
        google_tokens_data = await self._get_google_tokens(code=code)

        user_id_token = google_tokens_data.get("id_token")
        if not user_id_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        user_info = await self._decode_google_id_token(user_id_token=user_id_token)

        user = await self._get_or_create_user(user_info=user_info)

        return user
