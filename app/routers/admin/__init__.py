from app.services.auth.exceptions import RestrictedPermissionException
from .dto import OptionalAdminFullUserDataDto, SetUserBannedDto
from app.acl.permissions import Permissions, perform_check
from app.services.auth.dto import AccessJWTPayloadDto
from app.services.user.interface import IUserService
from app.dependencies import get_user_service
from app.services.auth import PermittedAction
from app.services.user.dto import FullUserDto
from fastapi import APIRouter, Depends

from .exceptions import (
    CantChangeSelfRoleException,
    CantDeleteSelfException,
    CantBanSelfException,
)

router = APIRouter(tags=["Админка"], prefix="/admin")


@router.get(
    "/", response_model=list[FullUserDto], summary="Список пользователей"
)
async def get_all(
    _=Depends(PermittedAction(Permissions.GetUserFullInfo)),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Возвращает список всех зарегистрированных пользователей.
    """
    return await user_service.get_info_all(FullUserDto)


@router.get(
    "/{user_id}",
    response_model=FullUserDto,
    summary="Информация о пользователе",
)
async def get_user_by_id(
    user_id: int,
    _=Depends(PermittedAction(Permissions.GetUserFullInfo)),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Возвращает информацию о конкретном пользователе.
    """
    return await user_service.get_info(user_id, FullUserDto)


@router.patch(
    "/{user_id}",
    response_model=FullUserDto,
    summary="Изменение данных о пользователе",
)
async def update(
    user_id: int,
    dto: OptionalAdminFullUserDataDto,
    admin: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateAnyUser)
    ),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Позволяет изменить часть (или все) данных о пользователе.
    Самому себе менять роль нельзя.
    """

    if dto.role is not None:
        if not perform_check(Permissions.UpdateRole, admin.role):
            raise RestrictedPermissionException()

        if admin.user_id == user_id:
            raise CantChangeSelfRoleException()

        await user_service.set_role(user_id, dto.role)
        dto.role = None

    if dto.password is not None:
        await user_service.set_password(user_id, dto.password)
        dto.password = None

    return await user_service.update_info(user_id, dto)


@router.post("/{user_id}/ban", summary="Блокировка пользователя")
async def set_banned(
    user_id: int,
    dto: SetUserBannedDto,
    admin: AccessJWTPayloadDto = Depends(PermittedAction(Permissions.BanUser)),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Устанавливает статус блокировки пользователя. Забаненный пользователь после истечения Access-токена не сможет войти в систему
    (до тех пор, пока не разбанят).
    Все остальные сервисы не разрешают работать с забаненными пользователями.
    Самого себя забанить нельзя.
    """
    if admin.user_id == user_id:
        raise CantBanSelfException()

    return await user_service.set_is_banned(user_id, dto.is_banned)


@router.delete("/{user_id}", summary="Удаление пользователя")
async def delete(
    user_id: int,
    admin: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.DeleteUser)
    ),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Полностью удаляет пользователя из системы. Самого себя удалять нельзя.
    """
    if admin.user_id == user_id:
        raise CantDeleteSelfException()

    return await user_service.delete(user_id)
