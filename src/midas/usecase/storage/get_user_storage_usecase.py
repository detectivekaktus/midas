from typing import override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.db.schemas.storage import Storage
from midas.query.storage import StorageRepository
from midas.usecase.abstract_usecase import AbstractUsecase


class GetUserStorageUsecase(AbstractUsecase[Storage]):
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._storage_repo = StorageRepository(self._session)

    @override
    async def execute(self, user_id: int, index: int = 0) -> Storage:
        """
        Get `user_id` storage at `index` position.

        Currently `index` position can't be any value but 0. Maybe later
        when I allow user to have multiple storages it will find its use.

        :param user_id: user's telegram id.
        :type user_id: int
        :param index: 0-indexed position of the storage.
        :type index: int
        :return: the `index`th storage associated with `user_id`.
        :rtype: Storage
        :raise IndexError: if index is out of bound.
        :raise ValueError: if there's no user with `user_id`.
        """
        async with self._session:
            storages = await self._storage_repo.get_by_user_id(user_id)

            if len(storages) == 0:
                raise ValueError(f"No user with {user_id} id found")

            return storages[index]
