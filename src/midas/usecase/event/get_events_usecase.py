from typing import Sequence, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.event import Event
from midas.query.event import EventRepository
from midas.usecase.abstract_usecase import AbstractUsecase


class GetEventsUsecase(AbstractUsecase[Sequence[Event]]):
    """
    Get events usecase class. The object created via this class provides
    a way to get events bound to a user.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._event_repo = EventRepository(self._session)

    @override
    async def execute(self, user_id: int, count: int = 16) -> Sequence[Event]:
        """
        Get first `count` events of the `user_id` user.

        The list will be empty if `user_id` is invalid.

        :param user_id: user's telegram id
        :type user_id: int
        :param count: number of events to get
        :type count: int
        :return: list of user-created events
        :rtype: Sequence[Event]
        """
        app_logger.debug(f"Started `GetEventsUsecase` execution: {user_id} - {count}")

        async with self._session:
            events = await self._event_repo.get_by_user_id(user_id, count)
            app_logger.debug("Successfully returned events back")
            return events
