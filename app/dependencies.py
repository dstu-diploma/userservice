from app.services.uploads.interface import IUserUploadService
from app.services.uploads.service import UserUploadService
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
def get_upload_service(
    storage: IStoragePort = Depends(get_storage_adapter),
) -> IUserUploadService:
    return UserUploadService(storage)


@lru_cache
def get_auth_service() -> IAuthService:
    return AuthService()


@lru_cache
def get_user_service(
    auth_service: IAuthService = Depends(get_auth_service),
    upload_service: IUserUploadService = Depends(get_upload_service),
) -> IUserService:
    return UserService(auth_service, upload_service)
