from app.controllers.user.dto import FullUserDto, OptionalFullUserDataDto
from app.controllers.user import UserController, get_user_controller
from fastapi import APIRouter, Depends, HTTPException, Query
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.user.auth import UserWithRole
from .dto import PasswordDto


router = APIRouter(
    tags=["Админка"],
    prefix="/admin",
    dependencies=(Depends(UserWithRole("admin")),),
)


@router.get("/")
async def get_all(
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.get_full_info_all()


@router.get("/{id}", response_model=FullUserDto)
async def get_user_by_id(
    user_id: int = Query(..., gt=0),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.get_full_info(user_id)


@router.patch(
    "/{id}",
    response_model=FullUserDto,
)
async def update(
    update_dto: OptionalFullUserDataDto,
    user_id: int = Query(..., gt=0),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.update_info(user_id, update_dto)


@router.patch("/{id}/password")
async def update_password(
    dto: PasswordDto,
    user_id: int = Query(..., gt=0),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.set_password(user_id, dto.password)


@router.delete("/", description="Удаляет пользователя из СУБД")
async def delete(
    user_id: int = Query(..., gt=0),
    admin: AccessJWTPayloadDto = Depends(UserWithRole("admin")),
    user_controller: UserController = Depends(get_user_controller),
):
    if admin.user_id == user_id:
        raise HTTPException(status_code=403, detail="You cant delete yourself!")
    return await user_controller.delete(user_id)
