from app.ports.event_publisher import IEventPublisherPort
from pydantic import BaseModel


class MockEventPublisherAdapter(IEventPublisherPort):
    def __init__(self, connection_url: str = "", exchange_name: str = "events"):
        return

    async def connect(self):
        return

    async def publish(self, event_name: str, data: BaseModel) -> None:
        return
