from app.models.user import UserUploadsType
from app.services.uploads.dto import UserUploadDto
from app.services.uploads.interface import IUserUploadService
from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from app.services.user.interface import IUserService
from app.acl.permissions import Permissions
from .dto import AccessTokenDto

from app.services.user.dto import (
    OptionalFullUserDataDto,
    RegisteredUserDto,
    CreateUserDto,
    MinimalUserDto,
    FullUserDto,
)

from app.dependencies import (
    get_upload_service,
    get_auth_service,
    get_user_service,
)

from app.services.auth import (
    get_token_from_header,
    AccessJWTPayloadDto,
    PermittedAction,
    IAuthService,
)

router = APIRouter(tags=["Основное"], prefix="")


@router.post(
    "/",
    response_model=RegisteredUserDto,
    summary="Регистрация пользователя",
)
async def create(
    user_dto: CreateUserDto,
    user_service: IUserService = Depends(get_user_service),
):
    """
    Создает нового пользователя.
    """
    return await user_service.create(user_dto.password, user_dto)


@router.post(
    "/login",
    response_model=RegisteredUserDto,
    summary="Получение актуальной пары токенов",
)
async def login(
    input: OAuth2PasswordRequestForm = Depends(),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Логинит пользователя в системе. По факту "логином" является получение пары токенов. Рефреш токен обновляет свою ревизию, поэтому все предыдуще токены становятся невалидными.
    """
    return await user_service.login(input.username, input.password)


@router.post(
    "/access_token",
    response_model=AccessTokenDto,
    summary="Получение Access-токена",
)
async def update_access_token(
    token: str = Depends(get_token_from_header),
    auth_service: IAuthService = Depends(get_auth_service),
):
    """
    Выпускает новый Access-токен для текущего пользователя. В заголовке Authorization должен находиться актуальный Refresh-токен.
    """
    return AccessTokenDto(
        access_token=await auth_service.generate_access_token(token)
    )


@router.patch(
    "/", response_model=FullUserDto, summary="Обновление данных о пользователе"
)
async def update(
    update_dto: OptionalFullUserDataDto,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateSelf)
    ),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Позволяет изменить все или часть данных о текущем пользователе.
    """
    return await user_service.update_info(user_dto.user_id, update_dto)


@router.get(
    "/info/{user_id}",
    response_model=FullUserDto | MinimalUserDto,
    summary="Получение данных о пользователе",
)
async def get_info(
    user_id: int,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.GetUserMinimalInfo)
    ),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Возвращает данные о пользователе с заданным ID. Если запрошенный совпадает с ID залогиненного пользователя, то вернутся полные данные.
    """
    if user_id == user_dto.user_id:
        return await user_service.get_info(user_id, FullUserDto)
    else:
        return await user_service.get_info(user_id, MinimalUserDto)


@router.post(
    "/info-many",
    response_model=list[MinimalUserDto],
    summary="Получение данных о пользователях",
)
async def get_info_many(
    user_ids: list[int],
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.GetUserMinimalInfo)
    ),
    user_service: IUserService = Depends(get_user_service),
):
    """
    Возвращает данные о пользователях с заданными ID. Если какого то из пользователей не существует, то он не попадет в список.
    """
    return await user_service.get_info_many(user_ids, MinimalUserDto)


@router.get("/search-by-email", summary="Поиск пользователя")
async def search_user(
    email: str = Query(...),
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.SearchUserMinimalInfo)
    ),
    service: IUserService = Depends(get_user_service),
):
    """
    Позволяет найти пользователя по его ID/Email.
    Если пользователя не существует, то вернет 404.
    """
    return await service.get_by_email(email)


@router.put(
    "/avatar",
    response_model=UserUploadDto,
    summary="Установка/обновление аватарки",
)
async def upload_avatar(
    file: UploadFile,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateSelf)
    ),
    upload_service: IUserUploadService = Depends(get_upload_service),
):
    """
    Загружает аватарку пользователю. Если у него уже есть аватарка, то заменит существующую.
    """
    return await upload_service.upload_cover(file, user_dto.user_id)


@router.delete("/avatar", summary="Удаление аватарки")
async def delete_avatar(
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateSelf)
    ),
    upload_service: IUserUploadService = Depends(get_upload_service),
):
    """
    Удаляет аватарку пользователя.
    """
    return await upload_service.delete(user_dto.user_id, UserUploadsType.Avatar)
