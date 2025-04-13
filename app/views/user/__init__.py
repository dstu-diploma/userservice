from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.user import (
    OptionalFullUserData,
    get_user_controller,
    UserController,
    CreateUserDto,
    FullUserDto,
    RegisteredUserDto,
)
from app.controllers.user.auth import AccessJWTPayloadDto, get_user_dto
from fastapi import APIRouter, Depends, Query

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
    update_dto: OptionalFullUserData,
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
    "/me",
    response_model=FullUserDto,
    description="Возвращает полные данные о текущем залогиненном пользователе",
)
async def get_me(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.get_info(user_dto.user_id)
