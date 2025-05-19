from app.acl.permissions import PublicAccess, Group
from app.services.auth import PermittedAction
from app.acl.roles import UserRoles
from datetime import datetime
from ctypes import cast
import pytest

from app.services.auth.dto import AccessJWTPayloadDto
from app.services.auth.exceptions import RestrictedPermissionException
from app.services.user.dto import (
    RegisteredUserDto,
)


def generate_access_dto(user: RegisteredUserDto) -> AccessJWTPayloadDto:
    return AccessJWTPayloadDto(
        user_id=user.user.id,
        role=user.user.role,  # type:ignore
        exp=datetime.now(),
    )


@pytest.mark.asyncio
async def test_permissions_user_public_access(user: RegisteredUserDto):
    assert PermittedAction(PublicAccess())(generate_access_dto(user))


@pytest.mark.asyncio
async def test_permissions_user_can_user_group(user: RegisteredUserDto):
    assert PermittedAction(Group(UserRoles.User, UserRoles.Admin))(
        generate_access_dto(user)
    )


@pytest.mark.asyncio
async def test_permissions_user_not_admin(user: RegisteredUserDto):
    with pytest.raises(RestrictedPermissionException):
        PermittedAction(UserRoles.Admin)(generate_access_dto(user))
