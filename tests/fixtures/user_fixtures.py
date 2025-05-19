from app.services.user.dto import CreateUserDto, RegisteredUserDto
from app.services.uploads.interface import IUserUploadService
from app.services.user.interface import IUserService
from fastapi.datastructures import Headers
from fastapi import UploadFile
from faker import Faker
import pytest_asyncio
import io


async def _create_user(faker: Faker, mock_user_service: IUserService, **params):
    password = params.get("password", faker.pystr(8, 16))
    user = await mock_user_service.create(
        password,
        CreateUserDto(
            email=params.get("email", faker.email()),
            first_name=params.get("first_name", faker.first_name()),
            last_name=params.get("last_name", faker.last_name()),
            patronymic=params.get("patronymic", faker.pystr(3, 5)),
            password=password,
        ),
    )

    if params.get("is_banned", False):
        await mock_user_service.set_is_banned(user.user.id, True)
        user.user.is_banned = True

    return user


@pytest_asyncio.fixture
async def user(
    request, faker: Faker, mock_user_service: IUserService
) -> RegisteredUserDto:
    params = getattr(request, "param", {})
    return await _create_user(faker, mock_user_service, **params)


@pytest_asyncio.fixture
async def user_with_avatar(
    request,
    faker: Faker,
    mock_user_service: IUserService,
    mock_upload_service: IUserUploadService,
):
    params = getattr(request, "param", {})
    user = await _create_user(faker, mock_user_service, **params)
    file = UploadFile(
        io.BytesIO(faker.image((256, 256), "png")),
        filename="avatar.png",
        headers=Headers(raw=[(b"content-type", b"image/png")]),
    )

    await mock_upload_service.upload_avatar(file, user.user.id)
    return user


@pytest_asyncio.fixture
async def users(
    request, faker: Faker, mock_user_service: IUserService
) -> list[RegisteredUserDto]:
    params = getattr(request, "param", {})
    count = params.get("count", 5)
    return [
        await _create_user(faker, mock_user_service, **params)
        for i in range(count)
    ]
