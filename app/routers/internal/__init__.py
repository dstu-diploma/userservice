from app.services.user.exceptions import UserIsBannedException
from app.dependencies import get_user_controller
from .auth import get_token_from_header
from fastapi import APIRouter, Depends

from app.services.user import (
    IUserService,
)

router = APIRouter(
    tags=["Internal"], prefix="/internal", include_in_schema=False
)


@router.get("/{id}")
async def get_user_by_id(
    id: int,
    _token: str = Depends(get_token_from_header),
    controller: IUserService = Depends(get_user_controller),
):
    info = await controller.get_minimal_info(id)
    if info.is_banned:
        raise UserIsBannedException()

    return info
