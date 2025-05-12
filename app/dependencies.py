from app.controllers.avatar import IUserAvatarController, UserAvatarController
from app.controllers.auth import AuthController, IAuthController
from app.controllers.user import IUserController, UserController
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
) -> IUserAvatarController:
    return UserAvatarController(storage)


@lru_cache
def get_auth_controller() -> IAuthController:
    return AuthController()


@lru_cache
def get_user_controller(
    controller: IAuthController = Depends(get_auth_controller),
) -> IUserController:
    return UserController(controller)
