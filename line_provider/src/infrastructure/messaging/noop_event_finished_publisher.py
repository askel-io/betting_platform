from line_provider.src.application.ports.event_finished_publisher import (
    EventFinishedPublisher,
)


class NoOpEventFinishedPublisher(EventFinishedPublisher):
    "Заглушка для локальных тестов"

    async def publish(self, event_id: str, state: str) -> None:
        return
