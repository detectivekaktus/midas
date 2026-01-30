from typing import Sequence, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.event import Event
from midas.query.event import EventRepository
from midas.usecase.abstract_usecase import AbstractUsecase


class GetUpcomingEventsUsecase(AbstractUsecase[Sequence[Event]]):
    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._event_repo = EventRepository(self._session)

    @override
    async def execute(self) -> Sequence[Event]:
        app_logger.debug("Started `GetUpcomingEventsUsecase` execution")

        async with self._session:
            events = await self._event_repo.get_upcoming_events(eager=True)
            app_logger.debug("Successfully returned upcoming events back")
            return events
