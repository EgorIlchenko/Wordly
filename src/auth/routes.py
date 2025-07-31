from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_302_FOUND

from .schemas import UserCreate
from core.models import db_helper
from core.settings import templates
from users.crud import UserStorageProtocol, get_user_storage
from .services import UserService

router = APIRouter(
    tags=["Auth"],
)


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_user(
    request: Request,
    user_service: UserService = Depends(UserService),
):
    form = await request.form()

    raw_data = {
        "email": form.get("email"),
        "password": form.get("password"),
        "full_name": form.get("full_name"),
        "is_subscribed": form.get("is_subscribed") == "on",
    }
    user_data = UserCreate.model_validate(raw_data)

    try:
        await user_service.create_user(user_data=user_data)
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": str(e),
                "email": form.get("email"),
                "full_name": form.get("full_name"),
            },
        )
