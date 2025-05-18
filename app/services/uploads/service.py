from app.models.user import UserUploadsModel, UserUploadsType
from app.services.uploads.interface import IUserUploadService
from app.services.uploads.dto import UserUploadDto
from app.ports.storage import IStoragePort
from PIL import Image, ImageFile
from app.config import Settings
from fastapi import UploadFile
import urllib.parse
import uuid
import io

from .exceptions import (
    TooSmallImageException,
    TooBigImageException,
    WrongMagicsException,
    FileRemoveException,
    WrongMimeException,
    ImageReadException,
    ImageSaveException,
    NoFileException,
)


def validate_magics(file_bytes: bytes) -> bool:
    png_signature = b"\x89PNG\r\n\x1a\n"
    jpeg_signature = b"\xff\xd8"
    return file_bytes.startswith(png_signature) or file_bytes.startswith(
        jpeg_signature
    )


def prepare_image(
    image: ImageFile.ImageFile, size: tuple[int, int]
) -> Image.Image:
    return image.convert("PNG").resize(size, Image.Resampling.LANCZOS)


class UserUploadService(IUserUploadService):
    def __init__(self, storage: IStoragePort):
        self.storage = storage
        self.bucket_name = "avatars"

    async def _get_validated_image(
        self,
        file: UploadFile,
        *,
        size_mins: tuple[int, int] | None = None,
        size_maxs: tuple[int, int] | None = None,
    ) -> ImageFile.ImageFile:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise WrongMimeException()

        file_bytes = await file.read()
        if not validate_magics(file_bytes):
            raise WrongMagicsException()

        try:
            image = Image.open(io.BytesIO(file_bytes))
        except Exception:
            raise ImageReadException()

        if size_mins:
            if image.width < size_mins[0] or image.height < size_mins[1]:
                raise TooSmallImageException(
                    image.width, image.height, *size_mins
                )

        if size_maxs:
            if image.width < size_maxs[0] or image.height < size_maxs[1]:
                raise TooBigImageException(
                    image.width, image.height, *size_maxs
                )

        return image

    def _upload_file(self, file: Image.Image, key: str) -> None:
        try:
            image_buf = io.BytesIO()
            file.save(image_buf, "JPEG")
            image_buf.seek(0)
            self.storage.upload_jpeg(image_buf, self.bucket_name, key)
        except Exception as e:
            raise ImageSaveException()

    def _generate_key(self, user_id: int) -> str:
        return f"{uuid.uuid4()}-{user_id}"

    async def _save_upload(
        self, user_id: int, file: Image.Image, type: UserUploadsType
    ):
        await self.delete(user_id, type)
        key = self._generate_key(user_id)

        upload = await UserUploadsModel.create(
            user_id=user_id,
            type=type,
            s3_key=key,
            content_type="image/jpeg",
        )

        self._upload_file(file, key)

        return UserUploadDto.from_tortoise(
            upload, self._generate_upload_url(upload.s3_key)
        )

    async def upload_avatar(
        self, file: UploadFile, user_id: int
    ) -> UserUploadDto:
        image = await self._get_validated_image(file, size_mins=(128, 128))
        prepared = prepare_image(image, (256, 256))
        return await self._save_upload(
            user_id, prepared, UserUploadsType.Avatar
        )

    async def upload_cover(
        self, file: UploadFile, user_id: int
    ) -> UserUploadDto:
        image = await self._get_validated_image(
            file, size_mins=(1024, 512), size_maxs=(4096, 2048)
        )
        prepared = prepare_image(image, (2048, 1080))
        return await self._save_upload(user_id, prepared, UserUploadsType.Cover)

    async def _get_upload(
        self, user_id: int, type: UserUploadsType
    ) -> UserUploadsModel:
        upload = await UserUploadsModel.get_or_none(user_id=user_id, type=type)
        if upload is None:
            raise NoFileException()

        return upload

    def _generate_upload_url(self, s3_key: str) -> str:
        return urllib.parse.urljoin(
            Settings.PUBLIC_API_URL, f"download/uploads/{s3_key}"
        )

    async def get_upload(
        self, user_id: int, type: UserUploadsType
    ) -> UserUploadDto:
        upload = await self._get_upload(user_id, type)
        return UserUploadDto.from_tortoise(
            upload, self._generate_upload_url(upload.s3_key)
        )

    async def get_upload_by_key(self, s3_key: str) -> UserUploadDto:
        upload = await UserUploadsModel.get_or_none(s3_key=s3_key)
        if upload is None:
            raise NoFileException()

        return UserUploadDto.from_tortoise(
            upload, self._generate_upload_url(upload.s3_key)
        )

    async def get_uploads(self, user_id: int) -> list[UserUploadDto]:
        uploads = await UserUploadsModel.filter(user_id=user_id)
        return [
            UserUploadDto.from_tortoise(
                upload, self._generate_upload_url(upload.s3_key)
            )
            for upload in uploads
        ]

    async def delete(self, user_id: int, type: UserUploadsType) -> None:
        upload = await self._get_upload(user_id, type)
        await upload.delete()

        exists = self.storage.object_exists(self.bucket_name, upload.s3_key)
        if exists:
            try:
                self.storage.delete_object(self.bucket_name, upload.s3_key)
            except Exception:
                raise FileRemoveException()
        else:
            raise NoFileException()
