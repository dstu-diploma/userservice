import random
from httpx import AsyncClient
from faker import Faker
import pytest

from app.acl.roles import UserRoles
from app.routers.admin.dto import OptionalAdminFullUserDataDto
from app.services.user.dto import (
    FullUserDto,
    RegisteredUserDto,
)


@pytest.mark.asyncio
async def test_200_admin_get_all(
    client: AsyncClient,
    admin_user: RegisteredUserDto,
    users: list[RegisteredUserDto],
):
    response = await client.get(
        "/admin/",
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(users) + 1


@pytest.mark.asyncio
async def test_200_admin_get_user(
    client: AsyncClient,
    admin_user: RegisteredUserDto,
    user: RegisteredUserDto,
):
    response = await client.get(
        f"/admin/{user.user.id}",
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    user_data = user.user.model_dump()
    del user_data["uploads"]
    del user_data["register_date"]

    assert response.status_code == 200
    data = response.json()
    del data["uploads"]
    del data["register_date"]
    assert data == user_data


@pytest.mark.asyncio
async def test_404_admin_get_user_not_exists(
    faker: Faker,
    client: AsyncClient,
    admin_user: RegisteredUserDto,
):
    response = await client.get(
        f"/admin/{faker.pyint()}",
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_200_admin_patch_change_role(
    faker: Faker,
    client: AsyncClient,
    admin_user: RegisteredUserDto,
    user: RegisteredUserDto,
):
    new_role = faker.enum(UserRoles)

    response = await client.patch(
        f"/admin/{user.user.id}",
        json=OptionalAdminFullUserDataDto(
            role=new_role,
        ).model_dump(),
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 200
    dto = FullUserDto(**response.json())
    assert dto.role == new_role


@pytest.mark.asyncio
async def test_400_admin_patch_change_role_self(
    faker: Faker,
    client: AsyncClient,
    admin_user: RegisteredUserDto,
):
    response = await client.patch(
        f"/admin/{admin_user.user.id}",
        json=OptionalAdminFullUserDataDto(
            role=faker.enum(UserRoles),
        ).model_dump(),
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_200_admin_patch_change_password(
    faker: Faker,
    client: AsyncClient,
    admin_user: RegisteredUserDto,
):
    response = await client.patch(
        f"/admin/{admin_user.user.id}",
        json=OptionalAdminFullUserDataDto(
            password=faker.pystr(8, 16),
        ).model_dump(),
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_200_admin_patch_change_something(
    faker: Faker,
    client: AsyncClient,
    admin_user: RegisteredUserDto,
):
    def try_inject(value):
        if random.random() > 0.5:
            return value
        return None

    dto = OptionalAdminFullUserDataDto(
        email=try_inject(faker.email()),
        first_name=try_inject(faker.first_name()),
        last_name=try_inject(faker.last_name()),
        patronymic=try_inject(faker.pystr()),
        about=try_inject(faker.pystr(10, 20)),
    )

    response = await client.patch(
        f"/admin/{admin_user.user.id}",
        json=dto.model_dump(),
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    for k, v in dto.model_dump(exclude_none=True).items():
        assert data[k] == v


@pytest.mark.asyncio
async def test_200_admin_ban_user(
    client: AsyncClient, admin_user: RegisteredUserDto, user: RegisteredUserDto
):
    response = await client.post(
        f"/admin/{user.user.id}/ban",
        json={
            "is_banned": True,
        },
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_banned"] is True


@pytest.mark.asyncio
async def test_200_admin_delete(
    client: AsyncClient, admin_user: RegisteredUserDto, user: RegisteredUserDto
):
    response = await client.delete(
        f"/admin/{user.user.id}",
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_404_admin_delete_not_exists(
    faker: Faker, client: AsyncClient, admin_user: RegisteredUserDto
):
    response = await client.delete(
        f"/admin/{faker.pyint()}",
        headers={"Authorization": f"Bearer {admin_user.access_token}"},
    )

    assert response.status_code == 404
