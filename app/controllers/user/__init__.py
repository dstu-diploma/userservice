from app.controllers.auth import IAuthController, AuthController
from app.models import UserModel
from fastapi import Depends
from typing import Protocol
import bcrypt
from .dto import (
    OptionalFullUserDataDto,
    RegisteredUserDto,
    MinimalUserDto,
    CreateUserDto,
    FullUserDto,
)
from .exceptions import (
    NoUserWithSuchEmailException,
    UserWithThatEmailExistsException,
    InvalidLoginCredentialsException,
    NoSuchUserException,
)


SALT = bcrypt.gensalt()


class IUserController(Protocol):
    auth_controller: IAuthController

    async def create(
        self, password: str, dto: CreateUserDto
    ) -> RegisteredUserDto: ...
    async def login(self, email: str, password: str) -> RegisteredUserDto: ...
    async def get_minimal_info(self, user_id: int) -> MinimalUserDto: ...
    async def get_full_info(self, user_id: int) -> FullUserDto: ...
    async def update_info(self, user_id: int, dto: OptionalFullUserDataDto): ...
    async def delete(self, user_id: int) -> None: ...
    async def get_minimal_info_all(self) -> list[MinimalUserDto]: ...
    async def get_full_info_all(self) -> list[FullUserDto]: ...
    async def set_password(self, user_id: int, password: str) -> None: ...
    async def get_by_email(self, email: str) -> MinimalUserDto: ...


class UserController(IUserController):
    def __init__(self, auth_controller: IAuthController):
        self.auth_controller = auth_controller

    async def get_user_from_id(self, user_id: int) -> UserModel:
        user = await UserModel.get_or_none(id=user_id)

        if user is None:
            raise NoSuchUserException()

        return user

    async def create(
        self, password: str, dto: CreateUserDto
    ) -> RegisteredUserDto:
        if await UserModel.exists(email=dto.email):
            raise UserWithThatEmailExistsException()

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
            raise InvalidLoginCredentialsException()

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

    async def update_info(
        self, user_id: int, dto: OptionalFullUserDataDto
    ) -> FullUserDto:
        user = await self.get_user_from_id(user_id)
        user.update_from_dict(dto.model_dump(exclude_none=True))

        await user.save()
        return FullUserDto.from_tortoise(user)

    async def delete(self, user_id: int) -> None:
        user = await self.get_user_from_id(user_id)
        await user.delete()

    async def get_minimal_info_all(self) -> list[MinimalUserDto]:
        users = await UserModel.all()
        return [MinimalUserDto.from_tortoise(user) for user in users]

    async def get_full_info_all(self) -> list[FullUserDto]:
        users = await UserModel.all()
        return [FullUserDto.from_tortoise(user) for user in users]

    async def set_password(self, user_id: int, password: str) -> None:
        user = await self.get_user_from_id(user_id)
        user.password_hash = bcrypt.hashpw(password.encode(), SALT).decode()
        await user.save()

    async def get_by_email(self, email: str) -> MinimalUserDto:
        user = await UserModel.get_or_none(email=email)
        if user:
            return MinimalUserDto.from_tortoise(user)

        raise NoUserWithSuchEmailException()


# TODO: нормальный DI (Dishka)
# текущая реализация будет создавать по два объекта при каждом входе в эндпоинт, хотя эти зависимости должны быть на уровне приложения
def get_user_controller(
    controller: AuthController = Depends(),
) -> UserController:
    return UserController(controller)
