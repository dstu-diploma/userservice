from .dto import (
    FullUserDto,
    MinimalUserDto,
    OptionalFullUserData,
    CreateUserDto,
)
from fastapi import HTTPException
from app.models import UserModel
from os import environ
import bcrypt

SALT = bcrypt.gensalt()


async def get_user_from_id(user_id: int):
    user = await UserModel.get_or_none(id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="No user with such UserID!")

    return user


async def create(password: str, dto: CreateUserDto):
    model = await UserModel.create(
        password_hash=bcrypt.hashpw(password.encode(), SALT), **dto.model_dump()
    )

    return FullUserDto.from_tortoise(model)


async def update_info(dto: OptionalFullUserData):
    user = await get_user_from_id(dto.id)
    user.update_from_dict(dto.model_dump(exclude_none=True))

    await user.save()
    return FullUserDto.from_tortoise(user)


async def delete(user_id: int):
    user = await get_user_from_id(user_id)
    await user.delete()


async def get_all():
    users = await UserModel.all()
    return [MinimalUserDto.from_tortoise(user) for user in users]
