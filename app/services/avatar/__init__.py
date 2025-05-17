from app.ports.storage import IStoragePort
from PIL import Image, ImageFile
from fastapi import UploadFile
from typing import Protocol
from os import environ
import io

from .exceptions import (
    AvatarRemoveException,
    WrongMagicsException,
    WrongMimeException,
    ImageReadException,
    ImageSaveException,
    NoAvatarException,
)

AVATAR_PATH = environ.get("AVATAR_PATH", "/")


class IUserAvatarService(Protocol):
    storage: IStoragePort
    bucket_name: str

    async def create(self, file: UploadFile, user_id: int) -> None: ...
    def delete(self, user_id: int) -> None: ...
    def exists(self, user_id: int) -> bool: ...


def validate_magics(file_bytes: bytes) -> bool:
    png_signature = b"\x89PNG\r\n\x1a\n"
    jpeg_signature = b"\xff\xd8"
    return file_bytes.startswith(png_signature) or file_bytes.startswith(
        jpeg_signature
    )


def prepare_image(image: ImageFile.ImageFile) -> Image.Image:
    return image.convert("RGB").resize((256, 256), Image.Resampling.LANCZOS)


class UserAvatarService(IUserAvatarService):
    def __init__(self, storage: IStoragePort):
        self.storage = storage
        self.bucket_name = "avatars"

    async def create(self, file: UploadFile, user_id: int) -> None:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise WrongMimeException()

        file_bytes = await file.read()
        if not validate_magics(file_bytes):
            raise WrongMagicsException()

        try:
            image = Image.open(io.BytesIO(file_bytes))
        except Exception:
            raise ImageReadException()

        prepared = prepare_image(image)

        if self.exists(user_id):
            self.delete(user_id)

        try:
            image_buf = io.BytesIO()
            prepared.save(image_buf, "JPEG")
            image_buf.seek(0)
            self.storage.upload_jpeg(
                image_buf, self.bucket_name, self.generate_key_name(user_id)
            )
        except Exception as e:
            raise ImageSaveException()

    def generate_key_name(self, user_id: int) -> str:
        return f"{user_id}.jpg"

    def delete(self, user_id: int) -> None:
        if self.exists(user_id):
            try:
                self.storage.delete_object(
                    self.bucket_name, self.generate_key_name(user_id)
                )
            except Exception:
                raise AvatarRemoveException()
        else:
            raise NoAvatarException()

    def exists(self, user_id: int) -> bool:
        return self.storage.object_exists(
            self.bucket_name, self.generate_key_name(user_id)
        )
