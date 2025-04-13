from jose import ExpiredSignatureError, JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime
from fastapi import Depends, HTTPException
from os import environ


OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/login")
JWT_SECRET = environ.get("JWT_SECRET", "dstu")


class AccessJWTPayloadDto(BaseModel):
    user_id: int
    role: str
    exp: datetime


class RefreshJWTPayloadDto(AccessJWTPayloadDto):
    token_revision: int


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
