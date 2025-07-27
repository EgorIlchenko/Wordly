from fastapi import APIRouter

router = APIRouter(tags=["main"])


@router.get("")
async def get_all_users():
    pass
