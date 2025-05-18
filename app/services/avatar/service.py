from app.services.avatar.interface import IUserAvatarService
from app.ports.storage import IStoragePort
from PIL import Image, ImageFile
from fastapi import UploadFile
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


class UserAvatarService(IUserAvatarService):
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
        self.delete(key)

        try:
            image_buf = io.BytesIO()
            file.save(image_buf, "JPEG")
            image_buf.seek(0)
            self.storage.upload_jpeg(image_buf, self.bucket_name, key)
        except Exception as e:
            raise ImageSaveException()

    async def upload_avatar(self, file: UploadFile, user_id: int) -> None:
        image = await self._get_validated_image(file, size_mins=(128, 128))
        prepared = prepare_image(image, (256, 256))
        self._upload_file(prepared, self.generate_avatar_key(user_id))

    async def upload_cover(self, file: UploadFile, user_id: int) -> None:
        image = await self._get_validated_image(
            file, size_mins=(1024, 512), size_maxs=(4096, 2048)
        )
        prepared = prepare_image(image, (2048, 1080))
        self._upload_file(prepared, self.generate_upload_key(user_id))

    def generate_avatar_key(self, user_id: int) -> str:
        return f"avatar_{user_id}.jpg"

    def generate_upload_key(self, user_id: int) -> str:
        return f"cover_{user_id}.jpg"

    def delete(self, key: str) -> None:
        exists = self.storage.object_exists(self.bucket_name, key)
        if exists:
            try:
                self.storage.delete_object(self.bucket_name, key)
            except Exception:
                raise FileRemoveException()
        else:
            raise NoFileException()
