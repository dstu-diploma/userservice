from tests.mocks.adapters.event_publisher import MockEventPublisherAdapter
from app.services.uploads.service import UserUploadService
from tests.mocks.adapters.storage import MockS3Storage
from app.services.user.service import UserService
from app.services.auth import AuthService
from app.main import app
import pytest

from app.dependencies import (
    get_auth_service,
    get_event_publisher,
    get_storage_adapter,
    get_upload_service,
    get_user_service,
)


@pytest.fixture(autouse=True)
def mock_storage_adapter():
    storage = MockS3Storage()
    app.dependency_overrides[get_storage_adapter] = lambda: storage
    yield storage
    app.dependency_overrides.pop(get_storage_adapter, None)


@pytest.fixture(autouse=True)
def mock_event_publisher():
    event_publisher = MockEventPublisherAdapter()
    app.dependency_overrides[get_event_publisher] = lambda: event_publisher
    yield event_publisher
    app.dependency_overrides.pop(get_event_publisher, None)


@pytest.fixture(autouse=True)
def mock_upload_service(mock_storage_adapter):
    service = UserUploadService(mock_storage_adapter)
    app.dependency_overrides[get_upload_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_event_publisher, None)


@pytest.fixture(autouse=True)
def mock_auth_service():
    service = AuthService()
    app.dependency_overrides[get_auth_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_auth_service, None)


@pytest.fixture(autouse=True)
def mock_user_service(
    mock_auth_service,
    mock_upload_service,
    mock_event_publisher,
):
    service = UserService(
        mock_auth_service, mock_upload_service, mock_event_publisher
    )
    app.dependency_overrides[get_user_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_user_service, None)
