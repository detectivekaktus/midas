from typing import Optional, override
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.storage import Storage
from src.query.interface.eager_loadable import EagerLoadable
from src.query import GenericRepository


class StorageRepository(GenericRepository[Storage, int], EagerLoadable[Storage, int]):
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

    async def delete_all_by_user_id(self, user_id: int) -> None:
        """
        DELETE all rows where `storages.user_id` = `user_id`.

        :param user_id: user's telegram id
        :type user_id: int
        """
        await self._session.execute(delete(Storage).where(Storage.user_id == user_id))
