from typing import Annotated, Protocol, Type, TypeVar
from pydantic import BaseModel, StringConstraints
from app.models.user import UserModel
from datetime import datetime

from app.services.uploads.dto import UserUploadDto


class CreateUserDto(BaseModel):
    email: Annotated[str, StringConstraints(min_length=4)]
    first_name: Annotated[str, StringConstraints(min_length=3)]
    last_name: Annotated[str, StringConstraints(min_length=3)]
    patronymic: Annotated[str, StringConstraints(min_length=3)]
    password: Annotated[str, StringConstraints(min_length=8)]


UserDtoT = TypeVar("UserDtoT", bound="IUserDto")


class IUserDto(Protocol):
    @classmethod
    def from_tortoise(
        cls: Type[UserDtoT],
        user: UserModel,
        uploads: list[UserUploadDto] | None = None,
    ) -> UserDtoT: ...


class MinimalUserDto(BaseModel):
    id: int
    first_name: str
    last_name: str
    patronymic: str
    register_date: datetime
    is_banned: bool
    formatted_name: str
    role: str
    about: str | None
    birthday: datetime | None
    uploads: list[UserUploadDto] | None = None

    @classmethod
    def from_tortoise(
        cls, user: UserModel, uploads: list[UserUploadDto] | None = None
    ) -> "MinimalUserDto":
        return MinimalUserDto(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            register_date=user.register_date,
            is_banned=user.is_banned,
            role=user.role,
            about=user.about,
            birthday=user.birthday,
            formatted_name=f"{user.last_name} {user.first_name} {user.patronymic}",
            uploads=uploads,
        )


class FullUserDto(MinimalUserDto):
    email: str

    @classmethod
    def from_tortoise(
        cls, user: UserModel, uploads: list[UserUploadDto] | None = None
    ) -> "FullUserDto":
        return FullUserDto(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            register_date=user.register_date,
            email=user.email,
            role=user.role,
            about=user.about,
            birthday=user.birthday,
            is_banned=user.is_banned,
            formatted_name=f"{user.last_name} {user.first_name} {user.patronymic}",
            uploads=uploads,
        )


class ExternalUserDto(BaseModel):
    id: int
    is_banned: bool
    formatted_name: str
    role: str
    uploads: list[UserUploadDto] | None = None

    @classmethod
    def from_tortoise(
        cls, user: UserModel, uploads: list[UserUploadDto] | None = None
    ) -> "ExternalUserDto":
        return ExternalUserDto(
            id=user.id,
            is_banned=user.is_banned,
            role=user.role,
            formatted_name=f"{user.last_name} {user.first_name} {user.patronymic}",
            uploads=uploads,
        )


class OptionalFullUserDataDto(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    about: str | None = None
    birthday: datetime | None = None


class RegisteredUserDto(BaseModel):
    user: FullUserDto
    access_token: str
    refresh_token: str
