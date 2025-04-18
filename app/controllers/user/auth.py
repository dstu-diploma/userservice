from app.controllers.auth.dto import AccessJWTPayloadDto
from jose import ExpiredSignatureError, JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
from os import environ, path

ROOT_PATH = environ.get('ROOT_PATH', '/')
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl=path.join(ROOT_PATH, "login"))
JWT_SECRET = environ.get("JWT_SECRET", "dstu")


class UserJWTDto(BaseModel):
    access_token: str
    refresh_token: str


async def get_user_dto(
    access_token: str = Depends(OAUTH2_SCHEME),
) -> AccessJWTPayloadDto:
    try:
        raw_payload = jwt.decode(access_token, JWT_SECRET)
        return AccessJWTPayloadDto(**raw_payload)
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired!")
    except JWTError:
        raise HTTPException(
            status_code=403, detail="An error occured during JWT parsing!"
        )


class UserWithRole:
    allowed_roles: tuple[str, ...]
    allowed_roles_str: str

    def __init__(self, *allowed_roles: str):
        self.allowed_roles = allowed_roles
        self.allowed_roles_str = ", ".join(allowed_roles)

    def __call__(
        self, user_dto: Annotated[AccessJWTPayloadDto, Depends(get_user_dto)]
    ) -> AccessJWTPayloadDto:
        if user_dto.role in self.allowed_roles:
            return user_dto
        else:
            raise HTTPException(
                status_code=403,
                detail=f"You dont have enough permissions. Allowed roles: {self.allowed_roles_str}",
            )
