from typing import Union, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.db.schemas.event import Event
from midas.query.event import EventRepository
from midas.usecase.abstract_usecase import AbstractUsecase


class DeleteEventUsecase(AbstractUsecase[None]):
    """
    Delete event usecase. The objects of this class are responsible for
    deleting already existing user-generated events.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._event_repo = EventRepository(self._session)

    @override
    async def execute(self, arg: Union[int, Event]) -> None:
        """
        Delete an event. Note that this method does not delete any
        transactions created while this event was active.

        :param arg: event id or `Event` instance
        :type arg: Union[int, Event]
        :raises ValueError: if no event with `id` exists.
        """
        async with self._session:
            if isinstance(arg, Event):
                event = arg
                id = event.id
            else:
                id = arg
                event = await self._event_repo.get_by_id(id)

            if event is None:
                raise ValueError(f"No event with {id=} exists")

            await self._event_repo.delete_by_id(id)
            await self._session.commit()
