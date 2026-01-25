from typing import Optional, Sequence, override
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from midas.db.schemas.storage import Storage
from midas.query.interface.eager_loadable import EagerLoadable
from midas.query import GenericRepository
from midas.query.interface.purgeable import Purgeable
from midas.query.interface.retrievable_by_user_id import RetrievableByUserId


class StorageRepository(
    GenericRepository[Storage, int],
    EagerLoadable[Storage, int],
    Purgeable,
    RetrievableByUserId,
):
    """
    Storage repository class.

    This class inherits from `GenericRepository` class,
    thus provides the same functionality at its core.
    However, this class is specific to `storages` table in
    the database and has methods that are specific to their
    manipulation.

    The class also implements interface `EagerLoadable`, so
    the fetch method can use eager loading mechanisms of
    sqlalchemy.
    """

    @override
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Storage, session)

    @override
    async def get_by_id(self, id: int, eager: bool = False) -> Optional[Storage]:
        """
        Get storage by its id.

        If this method is used with eager loading, account associated
        with the storage is loaded upfront.

        :param id: storage id.
        :type id: int
        :param eager: use eager loading.
        :type eager: bool
        :return: storage associated with the id or `None` if no storage
        exists with the provided id.
        :rtype: Optional[Storage]
        """
        if eager:
            return (
                await self._session.scalars(
                    select(Storage)
                    .where(Storage.id == id)
                    .options(selectinload(Storage.account))
                )
            ).one_or_none()

        return await super().get_by_id(id)

    @override
    async def get_by_user_id(
        self, user_id: int, count: int, eager: bool = False
    ) -> Sequence[Storage]:
        """
        Get `count` accounts associated with `user_id` user.

        :param user_id: user's telegram id.
        :type user_id: int
        :param count: number of storages to get.
        :type count: int
        :param eager: use eager loading.
        :type eager: bool
        :return: list of storages associated with the `user_id` user. The list
        may be empty if `user_id` is invalid.
        :rtype: Sequence[Storage]
        """
        stmt = select(Storage).where(Storage.user_id == user_id).limit(count)
        if eager:
            stmt = stmt.options(selectinload(Storage.account))

        return (await self._session.scalars(stmt)).fetchall()

    @override
    async def purge_by_user_id(self, user_id: int) -> None:
        """
        DELETE all rows where `storages.user_id` = `user_id`.

        :param user_id: user's telegram id
        :type user_id: int
        """
        await self._session.execute(delete(Storage).where(Storage.user_id == user_id))
