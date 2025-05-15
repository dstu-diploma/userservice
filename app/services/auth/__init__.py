from .dto import AccessJWTPayloadDto, RefreshJWTPayloadDto, UserJWTDto
from app.acl.permissions import PermissionAcl, perform_check
from jose import ExpiredSignatureError, JWTError, jwt
from datetime import datetime, timedelta
from app.models import UserTokensModel
from typing import Annotated, Protocol
from app.acl.roles import UserRoles
from os import environ, path

from fastapi import Depends

from fastapi.security import (
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
    HTTPBearer,
)
from .exceptions import (
    NoSuchTokenUserException,
    RestrictedPermissionException,
    JWTParseErrorException,
    InvalidTokenException,
    TokenExpiredException,
    InvalidTokenRevision,
)

JWT_SECRET = environ.get("JWT_SECRET", "zaza")
ROOT_PATH = environ.get("ROOT_PATH", "/")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl=path.join(ROOT_PATH, "login"))
SECURITY_SCHEME = HTTPBearer(auto_error=False)


class IAuthService(Protocol):
    async def init_user(self, user_id: int, role: UserRoles) -> UserJWTDto: ...
    async def generate_key_pair(
        self, user_id: int, role: UserRoles
    ) -> tuple[str, str]: ...
    async def generate_access_token(self, refresh_token: str) -> str: ...
    async def generate_refresh_token(
        self, user_id: int, role: UserRoles
    ) -> str: ...
    async def validate_refresh_token(
        self, token: str
    ) -> RefreshJWTPayloadDto: ...


class AuthService(IAuthService):
    def __init__(self):
        pass

    async def init_user(self, user_id: int, role: UserRoles) -> UserJWTDto:
        await UserTokensModel.create(user_id=user_id)
        access, refresh = await self.generate_key_pair(user_id, role)
        return UserJWTDto(access_token=access, refresh_token=refresh)

    async def generate_key_pair(
        self, user_id: int, role: UserRoles
    ) -> tuple[str, str]:
        refresh = await self.generate_refresh_token(user_id, role)
        access = await self.generate_access_token(refresh)

        return access, refresh

    async def generate_access_token(self, refresh_token: str) -> str:
        refresh_payload = await self.validate_refresh_token(refresh_token)
        payload = AccessJWTPayloadDto(
            user_id=refresh_payload.user_id,
            role=refresh_payload.role,
            exp=datetime.now() + timedelta(minutes=20),
        )

        return jwt.encode(
            payload.model_dump(),
            JWT_SECRET,
        )

    async def generate_refresh_token(
        self, user_id: int, role: UserRoles
    ) -> str:
        user = await self._get_user_by_id(user_id)
        await user.increase_revision()

        payload = RefreshJWTPayloadDto(
            user_id=user_id,
            role=role,
            token_revision=user.token_revision,
            exp=datetime.now() + timedelta(days=7),
        )

        await user.save()
        return jwt.encode(
            payload.model_dump(),
            JWT_SECRET,
        )

    async def validate_refresh_token(self, token: str) -> RefreshJWTPayloadDto:
        try:
            raw_payload = jwt.decode(token, JWT_SECRET)
            payload = RefreshJWTPayloadDto(**raw_payload)
            user = await self._get_user_by_id(payload.user_id)

            if not user.verify_revision(payload.token_revision):
                raise InvalidTokenRevision()

            return payload
        except ExpiredSignatureError:
            raise TokenExpiredException()
        except JWTError:
            raise JWTParseErrorException()

    async def _get_user_by_id(self, user_id: int):
        user = await UserTokensModel.get_or_none(user_id=user_id)

        if user is None:
            raise NoSuchTokenUserException()
        return user


def get_token_from_header(
    credentials: HTTPAuthorizationCredentials = Depends(SECURITY_SCHEME),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise InvalidTokenException()
    return credentials.credentials


async def get_user_dto(
    access_token: str = Depends(OAUTH2_SCHEME),
) -> AccessJWTPayloadDto:
    try:
        raw_payload = jwt.decode(access_token, JWT_SECRET)
        return AccessJWTPayloadDto(**raw_payload)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise JWTParseErrorException()


class PermittedAction:
    acl: PermissionAcl

    def __init__(self, acl: PermissionAcl):
        self.acl = acl

    def __call__(
        self, user_dto: Annotated[AccessJWTPayloadDto, Depends(get_user_dto)]
    ):
        if perform_check(self.acl, user_dto.role):
            return user_dto

        raise RestrictedPermissionException()
