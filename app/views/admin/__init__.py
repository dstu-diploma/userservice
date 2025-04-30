from app.controllers.user.dto import FullUserDto, OptionalFullUserDataDto
from app.controllers.user import UserController, get_user_controller
from fastapi import APIRouter, Depends, HTTPException, Query
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.auth import UserWithRole
from .dto import PasswordDto


router = APIRouter(tags=["Админка"], prefix="/admin")


@router.get("/", summary="Список пользователей")
async def get_all(
    _=Depends(UserWithRole("admin")),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Возвращает список всех зарегистрированных пользователей.
    """
    return await user_controller.get_full_info_all()


@router.get(
    "/{id}", response_model=FullUserDto, summary="Информация о пользователе"
)
async def get_user_by_id(
    id: int,
    _=Depends(UserWithRole("admin")),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Возвращает информацию о конкретном пользователе.
    """
    return await user_controller.get_full_info(id)


@router.patch(
    "/{id}",
    response_model=FullUserDto,
    summary="Изменение данных о пользователе",
)
async def update(
    id: int,
    update_dto: OptionalFullUserDataDto,
    _=Depends(UserWithRole("admin")),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Позволяет изменить часть (или все) данных о пользователе.
    """
    return await user_controller.update_info(id, update_dto)


@router.patch("/{id}/password", summary="Изменение пароля")
async def update_password(
    id: int,
    dto: PasswordDto,
    _=Depends(UserWithRole("admin")),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Позволяет изменить пароль пользователю.
    """
    return await user_controller.set_password(id, dto.password)


@router.delete("/{id}", summary="Удаление пользователя")
async def delete(
    id: int,
    admin: AccessJWTPayloadDto = Depends(UserWithRole("admin")),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Полностью удаляет пользователя из системы.
    """
    if admin.user_id == id:
        raise HTTPException(
            status_code=403, detail="Вы не можете удалить самого себя!"
        )
    return await user_controller.delete(id)
