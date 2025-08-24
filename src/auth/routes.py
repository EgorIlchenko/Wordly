from uuid import UUID as UUID_TYPE
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from core.config import TIMEDELTA_SEC
from core.settings import get_settings, templates
from users.models import User

from .dependencies import (
    authenticate_user,
    get_current_active_auth_user,
    get_jwt_service,
    get_registration_service,
    get_verification_service,
)
from .schemas import UserCreate
from .services import JWTService, RegistrationService, VerificationService

settings = get_settings()

router = APIRouter(
    tags=["Auth"],
)


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@router.post("/register")
async def register_user(
    request: Request,
    registration_service: RegistrationService = Depends(
        get_registration_service,
    ),
):
    form = await request.form()

    raw_data = {
        "email": form.get("email"),
        "password": form.get("password"),
        "full_name": form.get("full_name"),
        "is_subscribed": form.get("is_subscribed") == "on",
    }

    try:
        user_data = UserCreate.model_validate(raw_data)
        await registration_service.register_user(
            user_data=user_data,
        )
        request.session["email"] = user_data.email

        return RedirectResponse(
            url="/api/v1/auth/verify-email",
            status_code=302,
        )

    except HTTPException as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": e.detail, **raw_data},
        )


@router.get("/verify-email", response_class=HTMLResponse)
async def get_verify_page(request: Request):
    email = request.session.get("email")

    if not email:
        return RedirectResponse(url="/api/v1/auth/register")

    return templates.TemplateResponse(
        "verify_email.html",
        {"request": request, "email": email},
    )


@router.post("/verify-email")
async def post_verify_email(
    request: Request,
    verification_service: VerificationService = Depends(
        get_verification_service,
    ),
):
    form = await request.form()
    email = form.get("email")
    code = form.get("code")

    try:
        await verification_service.verify_email(
            email=email,
            code=code,
        )
        request.session.pop("email", None)

        return RedirectResponse(
            url="/api/v1/auth/login",
            status_code=302,
        )

    except HTTPException as e:
        return templates.TemplateResponse(
            "verify_email.html",
            {"request": request, "email": email, "error": e.detail},
        )


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@router.post("/login", response_class=RedirectResponse)
async def login_user(
    user: User = Depends(authenticate_user),
    jwt_service: JWTService = Depends(get_jwt_service),
    next: str | None = Query(default="/"),
):
    access_token, expire = jwt_service.create_access_token(user=user)
    refresh_token, expire = jwt_service.create_refresh_token(user=user)

    session_id = uuid4()
    verifier, verifier_hash = jwt_service._generate_verifier_and_hash()

    await jwt_service.record_refresh_token_in_db(
        user=user,
        refresh_token=refresh_token,
        session_id=session_id,
        expire=expire,
        verifier_hash=verifier_hash,
    )

    redirect_url = next if next and next.startswith("/") else "/"
    redirect = RedirectResponse(url=redirect_url, status_code=302)

    redirect.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=(settings.auth_jwt.access_token_expire_minutes * 60) + TIMEDELTA_SEC,
        path="/",
    )
    redirect.set_cookie(
        key="session_id",
        value=str(session_id),
        httponly=True,
        max_age=(settings.auth_jwt.refresh_token_expire_days * 24 * 60 * 60) + TIMEDELTA_SEC,
        path="/",
    )
    redirect.set_cookie(
        key="verifier",
        value=verifier,
        httponly=True,
        max_age=(settings.auth_jwt.refresh_token_expire_days * 24 * 60 * 60) + TIMEDELTA_SEC,
        path="/",
    )

    return redirect


@router.get("/refresh", response_class=RedirectResponse)
async def auth_refresh_jwt(
    request: Request,
    jwt_service: JWTService = Depends(get_jwt_service),
    next: str | None = Query(default="/"),
):
    session_id_str = request.cookies.get("session_id")
    verifier = request.cookies.get("verifier")

    if not session_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session ID",
        )

    try:
        session_id = UUID_TYPE(session_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session ID format",
        )

    new_access_token, new_verifier = await jwt_service.refresh_tokens(
        session_id=session_id,
        verifier=verifier,
    )

    redirect_url = next if next and next.startswith("/") else "/"
    redirect = RedirectResponse(url=redirect_url, status_code=302)

    redirect.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=(settings.auth_jwt.access_token_expire_minutes * 60) + TIMEDELTA_SEC,
        path="/",
    )
    redirect.set_cookie(
        key="verifier",
        value=new_verifier,
        httponly=True,
        max_age=(settings.auth_jwt.refresh_token_expire_days * 24 * 60 * 60) + TIMEDELTA_SEC,
        path="/",
    )

    return redirect


@router.post("/logout", response_class=RedirectResponse)
async def logout_user_route(
    current_user: User = Depends(get_current_active_auth_user),
    jwt_service: JWTService = Depends(get_jwt_service),
):
    await jwt_service.logout_user(user=current_user)

    redirect = RedirectResponse(url="/api/v1/auth/login", status_code=302)
    redirect.delete_cookie(key="access_token", path="/")
    redirect.delete_cookie(key="session_id", path="/")
    redirect.delete_cookie(key="verifier", path="/")

    return redirect
