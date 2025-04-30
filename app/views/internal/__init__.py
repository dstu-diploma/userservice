from .auth import get_token_from_header
from fastapi import APIRouter, Depends
from app.controllers.user import (
    get_user_controller,
    UserController,
)

router = APIRouter(
    tags=["Internal"], prefix="/internal", include_in_schema=False
)


@router.get("/{id}")
async def get_user_by_id(
    id: int,
    _token: str = Depends(get_token_from_header),
    controller: UserController = Depends(get_user_controller),
):
    return await controller.get_minimal_info(id)
