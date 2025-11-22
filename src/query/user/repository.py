from typing import Optional, override
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.user import User
from src.query.interface.eager_loadable import EagerLoadable
from src.query import GenericRepository


class UserRepository(GenericRepository[User, int], EagerLoadable[User, int]):
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

    @override
    async def get_by_id(self, id: int, eager: bool = False) -> Optional[User]:
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
        :rtype: Optional[T]
        """
        if eager:
            return (
                await self._session.scalars(
                    select(User)
                    .where(User.id == id)
                    .options(
                        selectinload(User.accounts),
                        selectinload(User.storages)
                    )
                )
            ).one_or_none()

        return await super().get_by_id(id)
