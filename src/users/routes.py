from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_302_FOUND

from core.models import db_helper
from .schemas import UserCreate
from .services import create_user
from .crud import SQLAlchemyUserStorage, UserStorageProtocol

router = APIRouter(
    tags=["Users"],
)
templates = Jinja2Templates(directory="templates")


def get_user_storage() -> UserStorageProtocol:
    return SQLAlchemyUserStorage()


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    session: AsyncSession = Depends(db_helper.session_getter),
    storage: UserStorageProtocol = Depends(get_user_storage),
):
    raw_data = {
        "email": email,
        "password": password,
        "full_name": full_name,
    }
    user_data = UserCreate.model_validate(raw_data)

    try:
        await create_user(session=session, user_data=user_data, storage=storage)
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": str(e),
                "email": email,
                "full_name": full_name
            }
        )
