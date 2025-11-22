from typing import Optional, override
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.account import Account
from src.query.interface.eager_loadable import EagerLoadable
from src.query import GenericRepository
from src.util.enums import TransactionType


class AccountRepository(GenericRepository[Account, int], EagerLoadable[Account, int]):
    """
    Account repository class.

    This class inherits from `GenericRepository` class,
    thus provides the same functionality at its core.
    However, this class is specific to `accounts` table in
    the database and has methods that are specific to their
    manipulation.

    The class also implements interface `EagerLoadable`, so
    the fetch method can use eager loading mechanisms of
    sqlalchemy.
    """

    @override
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Account, session)

    @override
    async def get_by_id(self, id: int, eager: bool = False) -> Optional[Account]:
        """
        Get account by its id.

        If this method is used with eager loading, the associated
        storage is loaded upfront.

        :param id: account id.
        :type id: int
        :param eager: use eager loading.
        :type eager: bool
        :return: account associated with the id or `None` if no account
        exists with the provided id.
        :rtype: Optional[Account]
        """
        if eager:
            return (
                await self._session.scalars(
                    select(Account)
                    .where(Account.id == id)
                    .options(selectinload(Account.storage))
                )
            ).one_or_none()

        return await super().get_by_id(id)

    async def delete_all_by_user_id(self, user_id: int) -> None:
        """
        DELETE all rows where `accounts.user_id` = `user_id`.

        :param user_id: user's telegram id
        :type user_id: int
        """
        await self._session.execute(delete(Account).where(Account.user_id == user_id))

    async def get_user_account_by_transaction_type(
        self, user_id: int, transaction_type: TransactionType, eager: bool = False
    ) -> Optional[Account]:
        """
        SELECT account that's used for `transaction_type` that belongs
        to user with the `user_id`.

        When used with `eager` set to `True` the respective storage is
        loaded upfront.

        :param user_id: user's telegram id
        :type user_id: int
        :param transaction_type: transaction type that's being tracked
        by the account
        :param eager: use eager loading
        :type eager: bool
        :return: user's account or `None` if user doesn't exist
        :rtype: Optional[Account]
        """
        stmt = (
            select(Account)
            .where(Account.user_id == user_id)
            .where(Account.transaction_type_id == transaction_type)
        )
        if eager:
            stmt = stmt.options(selectinload(Account.storage))

        return (await self._session.scalars(stmt)).one_or_none()
