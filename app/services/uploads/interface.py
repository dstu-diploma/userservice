from app.services.uploads.dto import UserUploadDto
from app.models.user import UserUploadsType
from app.ports.storage import IStoragePort
from fastapi import UploadFile
from typing import Protocol


class IUserUploadService(Protocol):
    storage: IStoragePort
    bucket_name: str

    async def upload_avatar(
        self, file: UploadFile, user_id: int
    ) -> UserUploadDto: ...
    async def upload_cover(
        self, file: UploadFile, user_id: int
    ) -> UserUploadDto: ...
    async def get_upload(
        self, user_id: int, type: UserUploadsType
    ) -> UserUploadDto: ...
    async def get_upload_by_key(self, s3_key: str) -> UserUploadDto: ...
    async def get_uploads(self, user_id: int) -> list[UserUploadDto]: ...
    async def delete(self, user_id: int, type: UserUploadsType) -> None: ...
