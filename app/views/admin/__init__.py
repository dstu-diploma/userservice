from app.controllers.user.dto import FullUserDto, OptionalFullUserDataDto
from app.controllers.user import UserController, get_user_controller
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.auth import PermittedAction
from app.acl.permissions import Permissions
from fastapi import APIRouter, Depends
from .dto import PasswordDto, RoleDto

from app.views.admin.exceptions import (
    CantChangeSelfRoleException,
    CantDeleteSelfException,
)

router = APIRouter(tags=["Админка"], prefix="/admin")


@router.get("/", summary="Список пользователей")
async def get_all(
    _=Depends(PermittedAction(Permissions.GetUserFullInfo)),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Возвращает список всех зарегистрированных пользователей.
    """
    return await user_controller.get_full_info_all()


@router.get(
    "/{user_id}",
    response_model=FullUserDto,
    summary="Информация о пользователе",
)
async def get_user_by_id(
    user_id: int,
    _=Depends(PermittedAction(Permissions.GetUserFullInfo)),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Возвращает информацию о конкретном пользователе.
    """
    return await user_controller.get_full_info(user_id)


@router.patch(
    "/{user_id}",
    response_model=FullUserDto,
    summary="Изменение данных о пользователе",
)
async def update(
    user_id: int,
    update_dto: OptionalFullUserDataDto,
    _=Depends(PermittedAction(Permissions.UpdateAnyUser)),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Позволяет изменить часть (или все) данных о пользователе.
    """
    return await user_controller.update_info(user_id, update_dto)


@router.put(
    "/{user_id}/password",
    response_model=FullUserDto,
    summary="Изменение пароля",
)
async def update_password(
    user_id: int,
    dto: PasswordDto,
    _=Depends(PermittedAction(Permissions.UpdateAnyUser)),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Позволяет изменить пароль пользователю.
    """
    return await user_controller.set_password(user_id, dto.password)


@router.put(
    "/{user_id}/role", response_model=FullUserDto, summary="Изменение роли"
)
async def update_role(
    user_id: int,
    dto: RoleDto,
    admin: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateRole)
    ),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Позволяет изменить роль пользователю. Самому себе менять роль нельзя.
    """
    if admin.user_id == user_id:
        raise CantChangeSelfRoleException()

    return await user_controller.set_role(user_id, dto.role)


@router.delete("/{user_id}", summary="Удаление пользователя")
async def delete(
    user_id: int,
    admin: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.DeleteUser)
    ),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Полностью удаляет пользователя из системы. Самого себя удалять нельзя.
    """
    if admin.user_id == user_id:
        raise CantDeleteSelfException()

    return await user_controller.delete(user_id)
