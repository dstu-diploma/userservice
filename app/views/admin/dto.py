from pydantic import BaseModel, StringConstraints
from app.acl.roles import UserRoles
from typing import Annotated


class PasswordDto(BaseModel):
    password: Annotated[str, StringConstraints(min_length=8)]


class RoleDto(BaseModel):
    role: UserRoles
