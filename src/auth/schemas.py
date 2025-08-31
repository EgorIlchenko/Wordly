from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, constr


class UserCreateWithPassword(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=20)
    full_name: str
    is_subscribed: bool = False


class UserCreateFromOAuth(BaseModel):
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None
    is_google_account: bool = True
    is_verified: bool = True
    is_subscribed: bool = True


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailVerificationCodeCreate(BaseModel):
    email: EmailStr
    code: str


class RefreshSessionCreate(BaseModel):
    session_id: UUID
    user_id: UUID
    refresh_token: str
    expires_at: datetime
    verifier_hash: str
