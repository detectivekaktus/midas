from typing import Optional, override
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.account import Account
from src.query import GenericRepository
from src.util.enums import TransactionType


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

    async def get_user_account_by_transaction_type(
        self, user_id: int, transaction_type: TransactionType
    ) -> Optional[Account]:
        """
        SELECT account that's used for `transaction_type` that belongs
        to user with the `user_id`.

        :param user_id: user's telegram id
        :type user_id: int
        :param transaction_type: transaction type that's being tracked
        by the account
        :return: user's account or `None` if user doesn't exist
        :rtype: Optional[Account]
        """
        return (
            await self._session.scalars(
                select(Account)
                .where(Account.user_id == user_id)
                .where(Account.transaction_type_id == transaction_type)
            )
        ).one_or_none()
