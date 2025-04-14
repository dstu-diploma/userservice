from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.user import (
    OptionalFullUserDataDto,
    get_user_controller,
    UserController,
    CreateUserDto,
    FullUserDto,
    RegisteredUserDto,
)
from app.controllers.user.auth import AccessJWTPayloadDto, get_user_dto
from fastapi import APIRouter, Depends, Query

from app.controllers.user.dto import MinimalUserDto

router = APIRouter(prefix="")


@router.post(
    "/",
    response_model=RegisteredUserDto,
    description="Создает нового пользователя",
)
async def create(
    user_dto: CreateUserDto,
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.create(user_dto.password, user_dto)


@router.post(
    "/login",
    response_model=RegisteredUserDto,
    description="Логинит пользователя, обновляет ревизию рефреш-токена и возвращает пару токенов",
)
async def login(
    input: OAuth2PasswordRequestForm = Depends(),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.login(input.username, input.password)


@router.patch(
    "/",
    response_model=FullUserDto,
    description="Обновляет некоторые данные о пользователе в СУБД",
)
async def update(
    update_dto: OptionalFullUserDataDto,
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.update_info(update_dto)


@router.delete("/", description="Удаляет пользователя из СУБД")
async def delete(
    user_id: int = Query(..., ge=0),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.delete(user_id)


@router.get(
    "/",
    description="Возвращает список всех зарегистрированных пользователей (с минимальным набором данных)",
)
async def get_all(
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.get_all()


@router.get(
    "/{id}",
    response_model=FullUserDto | MinimalUserDto,
    description="Возвращает данные о пользователе с заданным ID. Если запрошенный совпадает с ID залогиненного пользователя, то вернутся полные данные",
)
async def get_me(
    id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    user_controller: UserController = Depends(get_user_controller),
):
    if id == user_dto.user_id:
        return await user_controller.get_full_info(id)
    else:
        return await user_controller.get_minimal_info(id)
