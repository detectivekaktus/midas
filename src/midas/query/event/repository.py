from typing import Sequence, override
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from midas.db.schemas.event import Event
from midas.query import GenericRepository
from midas.query.interface.purgeable import Purgeable


class EventRepository(GenericRepository[Event, int], Purgeable):
    @override
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Event, session)

    async def get_by_user_id(self, user_id: int, count: int = 16) -> Sequence[Event]:
        return (
            await self._session.scalars(select(Event).where(Event.user_id == user_id))
        ).fetchmany(count)

    @override
    async def purge_by_user_id(self, user_id: int) -> None:
        await self._session.execute(delete(Event).where(Event.user_id == user_id))
