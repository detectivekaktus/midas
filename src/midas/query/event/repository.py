from typing import Sequence, override
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from midas.db.schemas.event import Event
from midas.query import GenericRepository
from midas.query.interface.purgeable import Purgeable
from midas.query.interface.retrievable_by_user_id import RetrievableByUserId


class EventRepository(GenericRepository[Event, int], Purgeable, RetrievableByUserId):
    """
    Event repository class.

    This class inherits from `GenericRepository` thus has all
    the features it provides by default. This class is more specific
    to `events` database table and provides extra method to work
    with them.
    """

    @override
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Event, session)

    @override
    async def get_by_user_id(self, user_id: int, count: int = 16) -> Sequence[Event]:
        """
        Get `count` events associated with `user_id` user.

        :param user_id: user's telegram id.
        :type user_id: int
        :param count: number of events to get.
        :type count: int
        :return: list of events. Can be empty if `user_id` is invalid.
        :rtype: Sequence[Event]
        """
        return (
            await self._session.scalars(
                select(Event).where(Event.user_id == user_id).order_by(Event.id)
            )
        ).fetchmany(count)

    @override
    async def purge_by_user_id(self, user_id: int) -> None:
        await self._session.execute(delete(Event).where(Event.user_id == user_id))
