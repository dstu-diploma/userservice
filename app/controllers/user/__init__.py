from app.grpc.auth import IAuthServiceClient
from .dto import (
    FullUserDto,
    MinimalUserDto,
    OptionalFullUserData,
    CreateUserDto,
    RegisteredUserDto,
)
from fastapi import HTTPException, Depends
from app.grpc.auth import get_auth_client
from app.models import UserModel
import bcrypt

SALT = bcrypt.gensalt()


class UserController:
    def __init__(self, auth_service: IAuthServiceClient):
        self.auth_service = auth_service

    async def get_user_from_id(self, user_id: int):
        user = await UserModel.get_or_none(id=user_id)

        if user is None:
            raise HTTPException(
                status_code=404, detail="No user with such UserID!"
            )

        return user

    async def create(self, password: str, dto: CreateUserDto):
        model = await UserModel.create(
            password_hash=bcrypt.hashpw(password.encode(), SALT).decode(),
            **dto.model_dump(),
        )

        tokens = await self.auth_service.init_user(model.id, model.role)

        return RegisteredUserDto(
            user=FullUserDto.from_tortoise(model),
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    async def login(self, email: str, password: str):
        user = await UserModel.get_or_none(email=email)

        if user is None or not user.verify_password(password):
            raise HTTPException(
                status_code=403, detail="Invalid email or password!"
            )

        tokens = await self.auth_service.generate_key_pair(user.id, user.role)

        return RegisteredUserDto(
            user=FullUserDto.from_tortoise(user),
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    async def get_info(self, user_id: int):
        user = await self.get_user_from_id(user_id)
        return FullUserDto.from_tortoise(user)

    async def update_info(self, dto: OptionalFullUserData):
        user = await self.get_user_from_id(dto.id)
        user.update_from_dict(dto.model_dump(exclude_none=True))

        await user.save()
        return FullUserDto.from_tortoise(user)

    async def delete(self, user_id: int):
        user = await self.get_user_from_id(user_id)
        await user.delete()

    async def get_all(self):
        users = await UserModel.all()
        return [MinimalUserDto.from_tortoise(user) for user in users]


def get_user_controller(
    auth_client: IAuthServiceClient = Depends(get_auth_client),
) -> UserController:
    return UserController(auth_client)
