from app.ports.event_consumer import IEventConsumerPort
from typing import Callable, Awaitable
import asyncio


class MockEventConsumerAdapter(IEventConsumerPort):
    def __init__(
        self,
        connection_url: str,
        exchange_name: str = "events",
        queue_name: str = "",
    ):
        return

    async def connect(self):
        return

    async def create_consuming_loop(
        self,
        routing_keys: list[str],
        handler: Callable[[dict], Awaitable[None]],
    ) -> asyncio.Task:
        async def consume():
            await asyncio.sleep(1)

        return asyncio.create_task(consume())
