from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from api import router as api_router
from auth.dependencies import get_current_active_auth_user
from core.models import db_helper
from core.settings import get_settings, templates
from users.models import User

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


@main_app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        if "text/html" in request.headers.get("Accept", ""):
            if exc.detail and exc.detail.startswith("Token expired"):
                next_url = f"?next={request.url.path}"
                return RedirectResponse(url=f"/api/v1/auth/refresh{next_url}")

            next_url = f"?next={request.url.path}"
            return RedirectResponse(url=f"/api/v1/auth/login{next_url}")

    return exc


@main_app.get("/")
async def get_main_page(
    request: Request,
    user: User = Depends(get_current_active_auth_user),
):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user},
    )
