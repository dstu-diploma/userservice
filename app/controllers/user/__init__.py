from app.controllers.auth import IAuthController, AuthController
from fastapi import HTTPException, Depends
from app.models import UserModel
from typing import Protocol
from .dto import (
    OptionalFullUserDataDto,
    RegisteredUserDto,
    MinimalUserDto,
    CreateUserDto,
    FullUserDto,
)
import bcrypt


SALT = bcrypt.gensalt()


class IUserController(Protocol):
    auth_controller: IAuthController

    async def create(
        self, password: str, dto: CreateUserDto
    ) -> RegisteredUserDto: ...
    async def login(self, email: str, password: str) -> RegisteredUserDto: ...
    async def get_minimal_info(self, user_id: int) -> MinimalUserDto: ...
    async def get_full_info(self, user_id: int) -> FullUserDto: ...
    async def update_info(self, dto: OptionalFullUserDataDto): ...
    async def delete(self, user_id: int) -> None: ...
    async def get_all(self) -> list[MinimalUserDto]: ...


class UserController(IUserController):
    def __init__(self, auth_controller: IAuthController):
        self.auth_controller = auth_controller

    async def get_user_from_id(self, user_id: int) -> UserModel:
        user = await UserModel.get_or_none(id=user_id)

        if user is None:
            raise HTTPException(
                status_code=404, detail="No user with such UserID!"
            )

        return user

    async def create(
        self, password: str, dto: CreateUserDto
    ) -> RegisteredUserDto:
        if UserModel.exists(email=dto.email):
            raise HTTPException(
                status_code=403, detail="User with such email already exists!"
            )

        model = await UserModel.create(
            password_hash=bcrypt.hashpw(password.encode(), SALT).decode(),
            **dto.model_dump(),
        )

        tokens = await self.auth_controller.init_user(model.id, model.role)

        return RegisteredUserDto(
            user=FullUserDto.from_tortoise(model),
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    async def login(self, email: str, password: str) -> RegisteredUserDto:
        user = await UserModel.get_or_none(email=email)

        if user is None or not user.verify_password(password):
            raise HTTPException(
                status_code=403, detail="Invalid email or password!"
            )

        access_token, refresh_token = (
            await self.auth_controller.generate_key_pair(user.id, user.role)
        )

        return RegisteredUserDto(
            user=FullUserDto.from_tortoise(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def get_minimal_info(self, user_id: int) -> MinimalUserDto:
        user = await self.get_user_from_id(user_id)
        return MinimalUserDto.from_tortoise(user)

    async def get_full_info(self, user_id: int) -> FullUserDto:
        user = await self.get_user_from_id(user_id)
        return FullUserDto.from_tortoise(user)

    async def update_info(self, dto: OptionalFullUserDataDto) -> FullUserDto:
        user = await self.get_user_from_id(dto.id)
        user.update_from_dict(dto.model_dump(exclude_none=True))

        await user.save()
        return FullUserDto.from_tortoise(user)

    async def delete(self, user_id: int) -> None:
        user = await self.get_user_from_id(user_id)
        await user.delete()

    async def get_all(self) -> list[MinimalUserDto]:
        users = await UserModel.all()
        return [MinimalUserDto.from_tortoise(user) for user in users]


# TODO: нормальный DI (Dishka)
# текущая реализация будет создавать по два объекта при каждом входе в эндпоинт, хотя эти зависимости должны быть на уровне приложения
def get_user_controller(
    controller: AuthController = Depends(),
) -> UserController:
    return UserController(controller)
