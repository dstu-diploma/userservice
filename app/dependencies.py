from app.services.avatar import IUserAvatarService, UserAvatarService
from app.services.auth import AuthService, IAuthService
from app.services.user import IUserService, UserService
from app.ports.istorageport import IStoragePort
from app.adapters.s3adapter import S3Adapter
from functools import lru_cache
from fastapi import Depends


@lru_cache
def get_storage_adapter() -> IStoragePort:
    return S3Adapter()


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
