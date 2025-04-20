from .auth import get_token_from_header
from fastapi import APIRouter, Depends
from .dto import SearchUserDto
from app.controllers.user import (
    get_user_controller,
    UserController,
)

router = APIRouter(
    tags=["Internal"],
    prefix="/internal",
    include_in_schema=False,
    dependencies=(Depends(get_token_from_header),),
)


@router.get("/{id}")
async def get_user_by_id(
    id: int, controller: UserController = Depends(get_user_controller)
):
    return await controller.get_minimal_info(id)


@router.get("/search")
async def search_user(
    search_params: SearchUserDto,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.get_by_email_or_id(
        search_params.id, search_params.email
    )
