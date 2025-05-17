from datetime import datetime
from pydantic import BaseModel, StringConstraints
from app.models.user import UserModel
from typing import Annotated


class CreateUserDto(BaseModel):
    email: Annotated[str, StringConstraints(min_length=4)]
    first_name: Annotated[str, StringConstraints(min_length=3)]
    last_name: Annotated[str, StringConstraints(min_length=3)]
    patronymic: Annotated[str, StringConstraints(min_length=3)]
    password: Annotated[str, StringConstraints(min_length=8)]


class MinimalUserDto(BaseModel):
    id: int
    first_name: str
    last_name: str
    patronymic: str
    register_date: datetime
    is_banned: bool
    formatted_name: str

    @staticmethod
    def from_tortoise(user: UserModel):
        return MinimalUserDto(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            register_date=user.register_date,
            is_banned=user.is_banned,
            formatted_name=f"{user.last_name} {user.first_name} {user.patronymic}",
        )


class FullUserDto(MinimalUserDto):
    email: str
    role: str
    about: str | None
    birthday: datetime | None

    @staticmethod
    def from_tortoise(user: UserModel):
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
