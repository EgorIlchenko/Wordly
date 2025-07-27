from fastapi import APIRouter

from users.routes import router as users_router

from core.config import get_settings

settings = get_settings()

api_router = APIRouter()
api_router.include_router(
    users_router,
    prefix=settings.api.v1.users,
    tags=["Users"],
)
