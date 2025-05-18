from app.services.avatar.interface import IUserAvatarService
from app.services.avatar.service import UserAvatarService
from app.services.auth import AuthService, IAuthService
from app.services.user.interface import IUserService
from app.adapters.storage import S3StorageAdapter
from app.services.user.service import UserService
from app.ports.storage import IStoragePort
from functools import lru_cache
from fastapi import Depends


@lru_cache
def get_storage_adapter() -> IStoragePort:
    return S3StorageAdapter()


@lru_cache
def get_avatar_controller(
    storage: IStoragePort = Depends(get_storage_adapter),
) -> IUserAvatarService:
    return UserAvatarService(storage)


@lru_cache
def get_auth_controller() -> IAuthService:
    return AuthService()


@lru_cache
def get_user_controller(
    controller: IAuthService = Depends(get_auth_controller),
) -> IUserService:
    return UserService(controller)
