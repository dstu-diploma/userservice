from fastapi import APIRouter, Depends, Query, UploadFile
from app.controllers.avatar import UserAvatarController
from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.user.dto import MinimalUserDto
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

from .dto import AccessTokenDto

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
    """
    Создает нового пользователя.
    """
    return await user_controller.create(user_dto.password, user_dto)


@router.post(
    "/login",
    response_model=RegisteredUserDto,
    summary="Получение актуальной пары токенов",
)
async def login(
    input: OAuth2PasswordRequestForm = Depends(),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Логинит пользователя в системе. По факту "логином" является получение пары токенов. Рефреш токен обновляет свою ревизию, поэтому все предыдуще токены становятся невалидными.
    """
    return await user_controller.login(input.username, input.password)


@router.post(
    "/access_token",
    response_model=AccessTokenDto,
    summary="Получение Access-токена",
)
async def update_access_token(
    token: str = Depends(get_token_from_header),
    auth_controller: AuthController = Depends(),
):
    """
    Выпускает новый Access-токен для текущего пользователя. В заголовке Authorization должен находиться актуальный Refresh-токен.
    """
    return AccessTokenDto(
        access_token=await auth_controller.generate_access_token(token)
    )


@router.patch(
    "/", response_model=FullUserDto, summary="Обновление данных о пользователе"
)
async def update(
    update_dto: OptionalFullUserDataDto,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Позволяет изменить все или часть данных о текущем пользователе.
    """
    return await user_controller.update_info(user_dto.user_id, update_dto)


@router.get(
    "/info/{id}",
    response_model=FullUserDto | MinimalUserDto,
    summary="Получение данных о пользователе",
)
async def get_info(
    id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Возвращает данные о пользователе с заданным ID. Если запрошенный совпадает с ID залогиненного пользователя, то вернутся полные данные.
    """
    if id == user_dto.user_id:
        return await user_controller.get_full_info(id)
    else:
        return await user_controller.get_minimal_info(id)


@router.get(
    "/info-many",
    response_model=list[MinimalUserDto],
    summary="Получение данных о пользователях",
)
async def get_info_many(
    user_ids: list[int],
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    user_controller: UserController = Depends(get_user_controller),
):
    """
    Возвращает данные о пользователях с заданными ID. Если какого то из пользователей не существует, то он не попадет в список.
    """
    return user_controller.get_minimal_info_many(user_ids)


@router.get("/search-by-email", summary="Поиск пользователя")
async def search_user(
    email: str = Query(...),
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: UserController = Depends(get_user_controller),
):
    """
    Позволяет найти пользователя по его ID/Email.
    Если пользователя не существует, то вернет 404.
    """
    return await controller.get_by_email(email)


@router.put(
    "/avatar",
    summary="Установка/обновление аватарки",
)
async def upload_avatar(
    file: UploadFile,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    avatar_controller: UserAvatarController = Depends(),
):
    """
    Загружает аватарку пользователю. Если у него уже есть аватарка, то заменит существующую.
    """
    await avatar_controller.create(file, user_dto.user_id)


@router.delete("/avatar", summary="Удаление аватарки")
def delete_avatar(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    avatar_controller: UserAvatarController = Depends(),
):
    """
    Удаляет аватарку пользователя.
    """
    return avatar_controller.delete(user_dto.user_id)
