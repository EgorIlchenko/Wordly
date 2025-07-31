from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from core.settings import templates

from .dependencies import get_registration_service, get_verification_service
from .schemas import UserCreate
from .services import RegistrationService, VerificationService

router = APIRouter(
    tags=["Auth"],
)


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
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
