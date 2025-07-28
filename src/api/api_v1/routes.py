from fastapi import APIRouter

from core.config import get_settings
from users.routes import router as users_router

settings = get_settings()

api_router = APIRouter()
api_router.include_router(
    users_router,
    prefix=settings.api.v1.users,
    tags=["Users"],
)
