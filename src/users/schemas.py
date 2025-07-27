from uuid import UUID
from pydantic import BaseModel, EmailStr, constr, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=20)
    full_name: Optional[str] = None


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserRead):
    hashed_password: str
