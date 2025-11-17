from typing import override
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.account import Account
from src.query import GenericRepository


class AccountRepository(GenericRepository):
    """
    Account repository class.

    This class inherits from `GenericRepository` class,
    thus provides the same functionality at its core.
    However, this class is specific to `accounts` table in
    the database and has methods that are specific to their
    manipulation.
    """

    @override
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Account, session)

    async def delete_all_by_user_id(self, user_id: int) -> None:
        """
        DELETE all rows where `accounts.user_id` = `user_id`.

        :param user_id: user's telegram id
        :type user_id: int
        """
        await self._session.execute(delete(Account).where(Account.user_id == user_id))
