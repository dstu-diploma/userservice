from app.services.auth import IAuthService
from app.acl.roles import UserRoles
from typing import Protocol, Type
from app.models import UserModel

from .dto import (
    OptionalFullUserDataDto,
    RegisteredUserDto,
    MinimalUserDto,
    CreateUserDto,
    FullUserDto,
    UserDtoT,
)


class IUserService(Protocol):
    auth_controller: IAuthService

    async def get_user_from_id(self, user_id: int) -> UserModel: ...
    async def create(
        self, password: str, dto: CreateUserDto
    ) -> RegisteredUserDto: ...
    async def login(self, email: str, password: str) -> RegisteredUserDto: ...
    async def get_info(
        self, user_id: int, dto_class: Type[UserDtoT]
    ) -> UserDtoT: ...
    async def get_info_many(
        self, user_ids: list[int], dto_class: Type[UserDtoT]
    ) -> list[UserDtoT]: ...
    async def get_info_all(
        self, dto_class: Type[UserDtoT]
    ) -> list[UserDtoT]: ...
    async def update_info(
        self, user_id: int, dto: OptionalFullUserDataDto
    ) -> FullUserDto: ...
    async def delete(self, user_id: int) -> None: ...
    async def set_password(
        self, user_id: int, password: str
    ) -> FullUserDto: ...
    async def set_role(self, user_id: int, role: UserRoles) -> FullUserDto: ...
    async def get_by_email(self, email: str) -> MinimalUserDto: ...
    async def set_is_banned(
        self, user_id: int, is_banned: bool
    ) -> FullUserDto: ...
