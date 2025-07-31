from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from api import router as api_router
from core.models import db_helper
from core.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(
    api_router,
)

main_app.add_middleware(
    SessionMiddleware,  # noqa
    secret_key=settings.middleware.session_secret_key,
    session_cookie="wordly_session",
    max_age=600,
    same_site="lax",
    https_only=False,
)

main_app.mount("/assets", StaticFiles(directory="templates/assets"), name="assets")
