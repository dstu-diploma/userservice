from .exceptions import (
    AvatarRemoveException,
    WrongMagicsException,
    WrongMimeException,
    ImageReadException,
    ImageSaveException,
    NoAvatarException,
)
from os import environ, path, remove
from PIL import Image, ImageFile
from fastapi import UploadFile
from typing import Protocol
import io

AVATAR_PATH = environ.get("AVATAR_PATH", "/")


class IUserAvatarController(Protocol):
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


def get_avatar_path(user_id: int) -> str:
    return path.join(AVATAR_PATH, f"{user_id}.jpg")


class UserAvatarController(IUserAvatarController):
    def __init__(self):
        pass

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
            prepared.save(get_avatar_path(user_id), "JPEG")
        except Exception:
            raise ImageSaveException()

    def delete(self, user_id: int) -> None:
        if self.exists(user_id):
            try:
                remove(get_avatar_path(user_id))
            except Exception:
                raise AvatarRemoveException()
        else:
            raise NoAvatarException()

    def exists(self, user_id: int) -> bool:
        return path.exists(get_avatar_path(user_id))
