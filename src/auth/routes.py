import secrets
from uuid import UUID as UUID_TYPE
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import TIMEDELTA_SEC
from core.models import db_helper
from core.settings import get_settings, templates
from users.models import User

from .dependencies import (
    authenticate_user,
    generate_google_oauth_redirect_uri,
    get_current_active_auth_user,
    get_google_auth_service,
    get_jwt_service,
    get_password_reset_service,
    get_registration_service,
    get_verification_service,
)
from .schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserCreateWithPassword,
)
from .services import JWTService, RegistrationService, VerificationService
from .services.google_auth_service import GoogleAuthService
from .services.password_reset_service import PasswordResetService

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

    if not form.get("privacy_agree"):
        raw_data = {
            "email": form.get("email"),
            "full_name": form.get("full_name"),
        }
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Необходимо согласиться на обработку персональных данных",
                **raw_data,
            },
        )

    raw_data = {
        "email": form.get("email"),
        "password": form.get("password"),
        "full_name": form.get("full_name"),
        "is_subscribed": form.get("is_subscribed") == "on",
    }

    try:
        user_data = UserCreateWithPassword.model_validate(raw_data)
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
async def get_login_page(
    request: Request,
    message: str | None = None,
):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "message": message,
        },
    )


@router.post("/login", response_class=RedirectResponse)
async def login_user(
    request: Request,
    # user: User = Depends(authenticate_user),
    jwt_service: JWTService = Depends(get_jwt_service),
    next: str | None = Query(default="/"),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")

    try:
        user = await authenticate_user(
            email=email,  # noqa
            password=password,
            session=session,
        )

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

    except HTTPException as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": e.detail,
                "email": email,
            },
            status_code=e.status_code,
        )


@router.get("/google-login/redirect")
def get_google_oauth_uri(
    request: Request,
):
    state = secrets.token_urlsafe(nbytes=16)
    request.session["oauth_state"] = state
    redirect_uri = generate_google_oauth_redirect_uri(state=state)

    return RedirectResponse(url=redirect_uri, status_code=302)


@router.get("/google", response_class=RedirectResponse)
async def get_google_oauth_code(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    error: str = Query(None),
    next: str | None = Query(default="/"),
    google_service: GoogleAuthService = Depends(get_google_auth_service),
    jwt_service: JWTService = Depends(get_jwt_service),
):
    session_state = request.session.pop("oauth_state", None)
    if session_state is None or state != session_state:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid state parameter. CSRF attack detected.",
        )

    if error or not code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied by Google",
        )

    user = await google_service.get_user_from_google(code=code)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive or not found",
        )

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


@router.get("/forgot-password", response_class=HTMLResponse)
async def get_forgot_password_page(request: Request):
    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request},
    )


@router.post("/forgot-password")
async def handle_forgot_password_form(
    request: Request,
    reset_service: PasswordResetService = Depends(get_password_reset_service),
):
    form = await request.form()
    raw_data = {"email": form.get("email")}

    forgot_password_form = ForgotPasswordRequest.model_validate(raw_data)

    await reset_service.request_password_reset(email=str(forgot_password_form.email))
    return templates.TemplateResponse(
        "forgot_password_success.html",
        {"request": request},
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def get_reset_password_page(
    request: Request,
    token: str = Query(...),
):
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "token": token},
    )


@router.post("/reset-password")
async def handle_reset_password_form(
    request: Request,
    reset_service: PasswordResetService = Depends(get_password_reset_service),
):
    form = await request.form()

    raw_data = {
        "token": form.get("email"),
        "password": form.get("password"),
    }

    reset_password_form = ResetPasswordRequest.model_validate(raw_data)

    await reset_service.reset_password(
        token=reset_password_form.token,
        new_password=reset_password_form.password,
    )
    return RedirectResponse(
        url="/api/v1/auth/login?message=Password+has+been+reset+successfully",
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/logout", response_class=RedirectResponse)
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
