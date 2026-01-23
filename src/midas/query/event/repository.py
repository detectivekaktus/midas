from typing import override
from sqlalchemy import delete

from midas.db.schemas.event import Event
from midas.query import GenericRepository
from midas.query.interface.purgeable import Purgeable


class EventRepository(GenericRepository[Event, int], Purgeable):
    @override
    async def purge_by_user_id(self, user_id: int) -> None:
        await self._session.execute(delete(Event).where(Event.user_id == user_id))
