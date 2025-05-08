from app.controllers.user.dto import OptionalFullUserDataDto
from pydantic import StringConstraints
from app.acl.roles import UserRoles
from typing import Annotated


class OptionalAdminFullUserDataDto(OptionalFullUserDataDto):
    password: Annotated[str, StringConstraints(min_length=8)] | None = None
    role: UserRoles | None = None
