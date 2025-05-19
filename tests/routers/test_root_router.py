from app.services.uploads.interface import IUserUploadService
from app.routers.root.dto import AccessTokenDto
from app.models.user import UserUploadsType
from httpx import AsyncClient
from faker import Faker
import pytest
import random

from app.services.user.dto import (
    OptionalFullUserDataDto,
    RegisteredUserDto,
)


@pytest.mark.asyncio
async def test_200_root_register(faker: Faker, client: AsyncClient):
    payload = {
        "email": faker.email(),
        "password": faker.password(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "patronymic": faker.pystr(3, 5),
    }
    response = await client.post("/", json=payload)
    assert response.status_code == 200
    data = response.json()
    dto = RegisteredUserDto(**data)
    assert dto.user.email == payload["email"]


@pytest.mark.asyncio
async def test_400_root_register_user_email(
    faker: Faker, client: AsyncClient, user: RegisteredUserDto
):
    payload = {
        "email": user.user.email,
        "password": faker.password(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "patronymic": faker.pystr(3, 5),
    }
    response = await client.post("/", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("user", [{"password": "123456789"}], indirect=True)
async def test_200_root_login(client: AsyncClient, user: RegisteredUserDto):
    response = await client.post(
        "/login",
        data={"username": user.user.email, "password": "123456789"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = response.json()
    dto = RegisteredUserDto(**data)
    assert dto.user.email == user.user.email


@pytest.mark.asyncio
async def test_400_root_login_no_user(faker: Faker, client: AsyncClient):
    response = await client.post(
        "/login",
        data={"username": faker.email(), "password": faker.pystr(8, 16)},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_403_root_login_wrong_password(
    faker: Faker, client: AsyncClient, user: RegisteredUserDto
):
    response = await client.post(
        "/login",
        data={"username": user.user.email, "password": faker.pystr(8, 16)},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize("user", [{"is_banned": True}], indirect=True)
async def test_403_root_login_banned(
    faker: Faker, client: AsyncClient, user: RegisteredUserDto
):
    response = await client.post(
        "/login",
        data={"username": user.user.email, "password": faker.pystr(8, 16)},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_200_root_update_access_token(
    client: AsyncClient, user: RegisteredUserDto
):
    response = await client.post(
        "/access_token",
        headers={"Authorization": f"Bearer {user.refresh_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    dto = AccessTokenDto(**data)
    assert dto.access_token


@pytest.mark.asyncio
async def test_400_root_update_access_token_not_refresh(
    client: AsyncClient, user: RegisteredUserDto
):
    response = await client.post(
        "/access_token",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("user", [{"is_banned": True}], indirect=True)
async def test_400_root_update_access_token_banned(
    client: AsyncClient, user: RegisteredUserDto
):
    response = await client.post(
        "/access_token",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_200_root_patch_user(
    faker: Faker, client: AsyncClient, user: RegisteredUserDto
):
    def try_inject(value):
        if random.random() > 0.5:
            return value
        return None

    dto = OptionalFullUserDataDto(
        email=try_inject(faker.email()),
        first_name=try_inject(faker.first_name()),
        last_name=try_inject(faker.last_name()),
        patronymic=try_inject(faker.pystr()),
        about=try_inject(faker.pystr(10, 20)),
    )

    response = await client.patch(
        "/",
        json=dto.model_dump(),
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    for k, v in dto.model_dump(exclude_none=True).items():
        assert data[k] == v


@pytest.mark.asyncio
async def test_200_root_info_user_id_self(
    client: AsyncClient, user: RegisteredUserDto
):
    response = await client.get(
        f"/info/{user.user.id}",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 200
    assert "email" in response.json()


@pytest.mark.asyncio
async def test_200_root_info_user_id_someone(
    client: AsyncClient, user: RegisteredUserDto, users: list[RegisteredUserDto]
):
    response = await client.get(
        f"/info/{random.choice(users).user.id}",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 200
    assert "email" not in response.json()


@pytest.mark.asyncio
async def test_404_root_info_user_id_not_exists(
    faker: Faker, client: AsyncClient, user: RegisteredUserDto
):
    response = await client.get(
        f"/info/{faker.pyint()}",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_200_root_info_many_all(
    client: AsyncClient, users: list[RegisteredUserDto]
):
    response = await client.post(
        f"/info-many",
        json=list(range(1, len(users) + 1)),
        headers={"Authorization": f"Bearer {users[0].access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(users)


@pytest.mark.asyncio
async def test_200_root_info_many_all_not_exists(
    faker: Faker, client: AsyncClient, users: list[RegisteredUserDto]
):
    response = await client.post(
        f"/info-many",
        json=list(range(1, len(users) + 1)) + [faker.pyint()],
        headers={"Authorization": f"Bearer {users[0].access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(users)


@pytest.mark.asyncio
async def test_200_root_info_many_empty(
    client: AsyncClient, users: list[RegisteredUserDto]
):
    response = await client.post(
        f"/info-many",
        json=[],
        headers={"Authorization": f"Bearer {users[0].access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_200_root_search_by_email(
    client: AsyncClient, user: RegisteredUserDto
):
    response = await client.get(
        f"/search-by-email?email={user.user.email}",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.user.id


@pytest.mark.asyncio
async def test_404_root_search_by_email_not_exists(
    faker: Faker, client: AsyncClient, user: RegisteredUserDto
):
    response = await client.get(
        f"/search-by-email?email={faker.email()}",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_200_root_upload_avatar(
    faker: Faker,
    client: AsyncClient,
    user: RegisteredUserDto,
    mock_upload_service: IUserUploadService,
):
    response = await client.put(
        "/avatar",
        files={
            "file": ("avatar.png", faker.image((256, 256), "png"), "image/png")
        },
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 200
    assert await mock_upload_service.get_upload(
        user.user.id, UserUploadsType.Avatar
    )


@pytest.mark.asyncio
async def test_400_root_upload_avatar_small(
    faker: Faker,
    client: AsyncClient,
    user: RegisteredUserDto,
):
    response = await client.put(
        "/avatar",
        files={
            "file": ("avatar.png", faker.image((16, 16), "png"), "image/png")
        },
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_200_root_upload_avatar_replace(
    faker: Faker,
    client: AsyncClient,
    user_with_avatar: RegisteredUserDto,
    mock_upload_service: IUserUploadService,
):
    files = {
        "file": ("avatar.png", faker.image((256, 256), "png"), "image/png")
    }

    response = await client.put(
        "/avatar",
        files=files,
        headers={"Authorization": f"Bearer {user_with_avatar.access_token}"},
    )

    assert response.status_code == 200
    uploads = await mock_upload_service.get_uploads(user_with_avatar.user.id)
    assert len(uploads) == 1
    assert uploads[0].type == UserUploadsType.Avatar


@pytest.mark.asyncio
async def test_200_root_upload_cover(
    faker: Faker,
    client: AsyncClient,
    user: RegisteredUserDto,
    mock_upload_service: IUserUploadService,
):
    response = await client.put(
        "/cover",
        files={
            "file": ("cover.png", faker.image((2048, 1080), "png"), "image/png")
        },
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 200
    assert await mock_upload_service.get_upload(
        user.user.id, UserUploadsType.Cover
    )


@pytest.mark.asyncio
async def test_400_root_upload_cover_small(
    faker: Faker,
    client: AsyncClient,
    user: RegisteredUserDto,
):
    response = await client.put(
        "/avatar",
        files={
            "file": ("cover.png", faker.image((16, 16), "png"), "image/png")
        },
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_400_root_upload_cover_big(
    faker: Faker,
    client: AsyncClient,
    user: RegisteredUserDto,
):
    response = await client.put(
        "/avatar",
        files={
            "file": ("cover.png", faker.image((10000, 1), "png"), "image/png")
        },
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_200_root_upload_cover_replace(
    faker: Faker,
    client: AsyncClient,
    user: RegisteredUserDto,
    mock_upload_service: IUserUploadService,
):
    files = {
        "file": ("cover.png", faker.image((2048, 1080), "png"), "image/png")
    }

    await client.put(
        "/cover",
        files=files,
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    response = await client.put(
        "/cover",
        files=files,
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 200
    uploads = await mock_upload_service.get_uploads(user.user.id)
    assert len(uploads) == 1
    assert uploads[0].type == UserUploadsType.Cover


@pytest.mark.asyncio
async def test_200_root_delete_avatar(
    client: AsyncClient,
    user_with_avatar: RegisteredUserDto,
    mock_upload_service: IUserUploadService,
):
    response = await client.delete(
        "/avatar",
        headers={"Authorization": f"Bearer {user_with_avatar.access_token}"},
    )

    assert response.status_code == 200
    assert (
        len(await mock_upload_service.get_uploads(user_with_avatar.user.id))
        == 0
    )


@pytest.mark.asyncio
async def test_200_root_delete_avatar_not_exists(
    client: AsyncClient,
    user: RegisteredUserDto,
):
    response = await client.delete(
        "/avatar",
        headers={"Authorization": f"Bearer {user.access_token}"},
    )

    assert response.status_code == 400


# @pytest.mark.asyncio
# async def test_upload_avatar(client: AsyncClient, user_with_token):
#     user, token = user_with_token
#     headers = {"Authorization": "Bearer MOCK_ACCESS_TOKEN"}
#     files = {"file": ("avatar.png", b"fake image content", "image/png")}
#     response = await client.put("/avatar", files=files, headers=headers)
#     assert response.status_code in (200, 401, 403)


# @pytest.mark.asyncio
# async def test_upload_cover(client: AsyncClient, user_with_token):
#     user, token = user_with_token
#     headers = {"Authorization": "Bearer MOCK_ACCESS_TOKEN"}
#     files = {"file": ("cover.jpg", b"fake image content", "image/jpeg")}
#     response = await client.put("/cover", files=files, headers=headers)
#     assert response.status_code in (200, 401, 403)


# @pytest.mark.asyncio
# async def test_delete_avatar(client: AsyncClient, user_with_token):
#     user, token = user_with_token
#     headers = {"Authorization": "Bearer MOCK_ACCESS_TOKEN"}
#     response = await client.delete("/avatar", headers=headers)
#     assert response.status_code in (200, 401, 403)


# @pytest.mark.asyncio
# async def test_delete_cover(client: AsyncClient, user_with_token):
#     user, token = user_with_token
#     headers = {"Authorization": "Bearer MOCK_ACCESS_TOKEN"}
#     response = await client.delete("/cover", headers=headers)
#     assert response.status_code in (200, 401, 403)
