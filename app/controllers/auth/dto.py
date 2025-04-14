from pydantic import BaseModel
from datetime import datetime


class AccessJWTPayloadDto(BaseModel):
    user_id: int
    role: str
    exp: datetime


class RefreshJWTPayloadDto(AccessJWTPayloadDto):
    token_revision: int


class UserJWTDto(BaseModel):
    access_token: str
    refresh_token: str
