from app.services.uploads.interface import IUserUploadService
from app.ports.event_publisher import IEventPublisherPort
from app.services.user.interface import IUserService
from app.services.auth import IAuthService
from app.acl.roles import UserRoles
from app.models import UserModel
from typing import Type
import bcrypt


from .dto import (
    ExternalUserDto,
    OptionalFullUserDataDto,
    RegisteredUserDto,
    MinimalUserDto,
    CreateUserDto,
    FullUserDto,
    UserDtoT,
)
from .exceptions import (
    UserWithThatEmailExistsException,
    InvalidLoginCredentialsException,
    NoUserWithSuchEmailException,
    UserIsBannedException,
    NoSuchUserException,
)


SALT = bcrypt.gensalt()


class UserService(IUserService):
    def __init__(
        self,
        auth_service: IAuthService,
        upload_service: IUserUploadService,
        event_publisher: IEventPublisherPort,
    ):
        self.auth_service = auth_service
        self.upload_service = upload_service
        self.event_publisher = event_publisher

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

        tokens = await self.auth_service.init_user(model.id, model.role)

        return RegisteredUserDto(
            user=FullUserDto.from_tortoise(model),
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    async def login(self, email: str, password: str) -> RegisteredUserDto:
        user = await UserModel.get_or_none(email=email)

        if user is None or not user.verify_password(password):
            raise InvalidLoginCredentialsException()

        if user.is_banned:
            raise UserIsBannedException()

        access_token, refresh_token = await self.auth_service.generate_key_pair(
            user.id, user.role
        )

        return RegisteredUserDto(
            user=FullUserDto.from_tortoise(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def get_info(
        self, user_id: int, dto_class: Type[UserDtoT]
    ) -> UserDtoT:
        user = await self.get_user_from_id(user_id)
        return dto_class.from_tortoise(
            user, await self.upload_service.get_uploads(user.id)
        )

    async def get_info_many(
        self,
        user_ids: list[int],
        dto_class: Type[UserDtoT],
        *,
        include_uploads: bool = False,
    ) -> list[UserDtoT]:
        users = await UserModel.filter(id__in=user_ids)
        if include_uploads:
            return [
                dto_class.from_tortoise(
                    user, await self.upload_service.get_uploads(user.id)
                )
                for user in users
            ]
        else:
            return [dto_class.from_tortoise(user) for user in users]

    async def get_info_all(
        self,
        dto_class: Type[UserDtoT],
        *,
        include_uploads: bool = False,
    ) -> list[UserDtoT]:
        users = await UserModel.all()
        if include_uploads:
            return [
                dto_class.from_tortoise(
                    user, await self.upload_service.get_uploads(user.id)
                )
                for user in users
            ]
        else:
            return [dto_class.from_tortoise(user) for user in users]

    async def update_info(
        self, user_id: int, dto: OptionalFullUserDataDto
    ) -> FullUserDto:
        user = await self.get_user_from_id(user_id)
        user.update_from_dict(dto.model_dump(exclude_none=True))

        await user.save()
        return FullUserDto.from_tortoise(
            user, await self.upload_service.get_uploads(user.id)
        )

    async def delete(self, user_id: int) -> None:
        user = await self.get_user_from_id(user_id)
        await user.delete()

        await self.event_publisher.publish(
            "user.deleted",
            ExternalUserDto.from_tortoise(user),
        )

    async def set_password(self, user_id: int, password: str) -> FullUserDto:
        user = await self.get_user_from_id(user_id)
        user.password_hash = bcrypt.hashpw(password.encode(), SALT).decode()
        await user.save()
        return FullUserDto.from_tortoise(
            user, await self.upload_service.get_uploads(user.id)
        )

    async def set_role(self, user_id: int, role: UserRoles) -> FullUserDto:
        user = await self.get_user_from_id(user_id)
        user.role = role
        await user.save()
        return FullUserDto.from_tortoise(
            user, await self.upload_service.get_uploads(user.id)
        )

    async def get_by_email(self, email: str) -> MinimalUserDto:
        user = await UserModel.get_or_none(email=email)
        if user:
            return MinimalUserDto.from_tortoise(
                user, await self.upload_service.get_uploads(user.id)
            )

        raise NoUserWithSuchEmailException()

    async def set_is_banned(self, user_id: int, is_banned: bool) -> FullUserDto:
        user = await self.get_user_from_id(user_id)
        user.is_banned = is_banned
        await user.save()

        # генерация рефреш токена нужна, чтобы поднять ревизию
        # все старые токены станут невалидными,
        # и забаненный пользователь не сможет даже зайти в аккаунт
        await self.auth_service.generate_refresh_token(user.id, user.role)

        await self.event_publisher.publish(
            "user.banned"
            ExternalUserDto.from_tortoise(user),
        )

        return FullUserDto.from_tortoise(
            user, await self.upload_service.get_uploads(user.id)
        )
