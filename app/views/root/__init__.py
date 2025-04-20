from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.avatar import UserAvatarController
from app.controllers.user.dto import MinimalUserDto
from fastapi import APIRouter, Depends, UploadFile
from app.controllers.user import (
    OptionalFullUserDataDto,
    get_user_controller,
    RegisteredUserDto,
    UserController,
    CreateUserDto,
    FullUserDto,
)
from app.controllers.auth import (
    get_token_from_header,
    AccessJWTPayloadDto,
    AuthController,
    get_user_dto,
)

router = APIRouter(tags=["Основное"], prefix="")


@router.post(
    "/",
    response_model=RegisteredUserDto,
    summary="Регистрация пользователя",
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


@router.post(
    "/access_token",
    response_model=str,
    description="Возвращает новый AccessToken по переданному RefreshToken",
)
async def update_access_token(
    token: str = Depends(get_token_from_header),
    auth_controller: AuthController = Depends(),
):
    return await auth_controller.generate_access_token(token)


@router.patch(
    "/",
    response_model=FullUserDto,
    description="Обновляет некоторые данные о текущем пользователе в СУБД",
)
async def update(
    update_dto: OptionalFullUserDataDto,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.update_info(user_dto.user_id, update_dto)


@router.get(
    "/",
    description="Возвращает список всех зарегистрированных пользователей (с минимальным набором данных)",
)
async def get_minimal_info_all(
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.get_minimal_info_all()


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


@router.post(
    "/avatar",
    description="Загружает аватарку пользователю. Если у него уже есть аватарка, то заменит существующую",
)
async def upload_avatar(
    file: UploadFile,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    avatar_controller: UserAvatarController = Depends(),
):
    await avatar_controller.create(file, user_dto.user_id)


@router.delete("/avatar", description="Удаляет аватарку пользователя.")
def delete_avatar(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    avatar_controller: UserAvatarController = Depends(),
):
    return avatar_controller.delete(user_dto.user_id)
