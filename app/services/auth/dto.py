from app.acl.roles import UserRoles
from pydantic import BaseModel
from datetime import datetime


class AccessJWTPayloadDto(BaseModel):
    user_id: int
    role: UserRoles
    exp: datetime


class RefreshJWTPayloadDto(AccessJWTPayloadDto):
    token_revision: int


class UserJWTDto(BaseModel):
    access_token: str
    refresh_token: str
