from typing import override
from sqlalchemy.ext.asyncio import AsyncSession

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

    # TODO: add method overloading allowing to pass directly an `Event` object
    # instead of referencing its id and making a useless fetch
    @override
    async def execute(self, id: int) -> None:
        """
        Delete an event. Note that this method does not delete any
        transactions created while this event was active.

        :param id: event id
        :type id: int
        :raises ValueError: if no event with `id` exists.
        """
        async with self._session:
            event = self._event_repo.get_by_id(id)
            if event is None:
                raise ValueError(f"No event with {id=} exists")

            await self._event_repo.delete_by_id(id)
            await self._session.commit()
