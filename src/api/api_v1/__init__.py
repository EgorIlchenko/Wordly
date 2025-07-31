from fastapi import APIRouter

from core.settings import get_settings

from .routes import api_router

settings = get_settings()

router = APIRouter()
router.include_router(
    api_router,
    prefix=settings.api.v1.prefix,
)
