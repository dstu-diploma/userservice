import os

os.environ["DATABASE_URL"] = "sqlite://:memory:"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost/"
os.environ["S3_ENDPOINT"] = "http://localhost:9000"
os.environ["S3_ACCESS_KEY"] = "testkey"
os.environ["S3_SECRET_KEY"] = "testsecret"

from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from tortoise import Tortoise
from tests.fixtures import *
import pytest_asyncio


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://localhost:8000"
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def initialize_db():
    await Tortoise.init(
        config={
            "connections": {
                "default": "sqlite://:memory:",
            },
            "apps": {
                "models": {
                    "models": ["app.models"],
                    "default_connection": "default",
                },
            },
        }
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise._drop_databases()
