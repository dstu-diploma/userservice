from app.services.user.dto import OptionalFullUserDataDto
from pydantic import BaseModel, StringConstraints
from app.acl.roles import UserRoles
from typing import Annotated


class SetUserBannedDto(BaseModel):
    is_banned: bool


class OptionalAdminFullUserDataDto(OptionalFullUserDataDto):
    password: Annotated[str, StringConstraints(min_length=8)] | None = None
    role: UserRoles | None = None
