from fastapi import APIRouter

from auth.routes import router as auth_router
from core.settings import get_settings

# from users.routes import router as users_router

settings = get_settings()

api_router = APIRouter()
api_router.include_router(
    auth_router,
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)
