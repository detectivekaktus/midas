from typing import Optional, Sequence, override
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from midas.db.schemas.user import User
from midas.query import GenericRepository


class UserRepository(GenericRepository[User, int]):
    """
    User repository class.

    This class inherits from `GenericRepository` class,
    thus provides the same functionality at its core.
    However, this class is specific to `users` table in
    the database and has methods that are specific to their
    manipulation.

    The class also implements interface `EagerLoadable`, so
    the fetch method can use eager loading mechanisms of
    sqlalchemy.
    """

    @override
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_id(self, id: int) -> Optional[User]:
        """
        Get user by its id.

        If this method is used with eager loading, all user accounts and
        user storages are loaded upfront.

        :param id: user id.
        :type id: int
        :param eager: use eager loading.
        :type eager: bool
        :return: user associated with the id or `None` if no user
        exists with the provided id.
        :rtype: Optional[User]
        """
        return await super().get_by_id(id)

    async def get_all(self) -> Sequence[User]:
        return (await self._session.scalars(select(User))).fetchall()
