from datetime import date, timedelta
from typing import Union, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.event import Event
from midas.query.event import EventRepository
from midas.usecase.abstract_usecase import AbstractUsecase
from midas.usecase.event.util import determine_timedelta
from midas.util.enums import EventFrequency


class UpdateEventAfterRunUsecase(AbstractUsecase[None]):
    """
    Update event after run usecase. This usecase has exactly one use, which
    is in the event scheduler. Do not use it anywhere else.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._event_repo = EventRepository(self._session)

    @override
    async def execute(self, arg: Union[int, Event]) -> None:
        """
        Set event's `last_run_on` field to today and increment `next_run_on`
        based on the `interval`.

        :param arg: event id or `Event` instance.
        :type arg: Union[int, Event]
        :raise ValueError: if `arg` is a non-existing event id.
        """
        app_logger.debug("Started `UpdateEventAfterRunUsecase` execution")

        async with self._session:
            if isinstance(arg, Event):
                event = arg
                id = event.id
            else:
                event = await self._event_repo.get_by_id(arg)
                id = arg

            if event is None:
                raise ValueError(f"No event with {id=} exists")

            today = date.today()
            delta = determine_timedelta(EventFrequency(event.interval))
            event.last_run_on = today
            event.next_run_on = today + timedelta(days=delta)

            self._session.add(event)
            await self._session.commit()

        app_logger.debug("Successfully updated event")
