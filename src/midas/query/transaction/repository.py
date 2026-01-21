from typing import Optional, Sequence, override
from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from midas.db.schemas.account import Account
from midas.db.schemas.transaction import Transaction
from midas.query.interface.eager_loadable import EagerLoadable
from midas.query import GenericRepository


class TransactionRepository(
    GenericRepository[Transaction, UUID], EagerLoadable[Transaction, UUID]
):
    """
    Transaction repository class.

    This class inherits from `GenericRepository` class,
    thus provides the same functionality at its core.
    However, this class is specific to `transaction` table in
    the database and has methods that are specific to their
    manipulation.

    The class also implements interface `EagerLoadable`, so
    the fetch method can use eager loading mechanisms of
    sqlalchemy.
    """

    @override
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Transaction, session)

    @override
    async def get_by_id(self, id: UUID, eager: bool = False) -> Optional[Transaction]:
        """
        Get transaction by its id.

        If this method is used with eager loading, credit and debit accounts
        used in the transaction are loaded upfront.

        :param id: transaction id.
        :type id: UUID
        :param eager: use eager loading.
        :type eager: bool
        :return: transaction associated with the id or `None` if no transaction
        exists with the provided id.
        :rtype: Optional[Transaction]
        """
        if eager:
            return (
                await self._session.scalars(
                    select(Transaction)
                    .where(Transaction.id == id)
                    .options(
                        selectinload(Transaction.debit_account).selectinload(
                            Account.storage
                        ),
                        selectinload(Transaction.credit_account).selectinload(
                            Account.storage
                        ),
                    )
                )
            ).one_or_none()

        return await super().get_by_id(id)

    async def delete_all_by_user_id(self, user_id: int) -> None:
        """
        DELETE all rows where `transactions.user_id` = `user_id`.

        :param user_id: user's telegram id
        :type user_id: int
        """
        await self._session.execute(
            delete(Transaction).where(Transaction.user_id == user_id)
        )

    async def get_recent(
        self, user_id: int, limit: int = 10, eager: bool = False
    ) -> Sequence[Transaction]:
        """
        Get recent user transactions.

        If used with eager loading, debit and credit accounts associated
        with the transaction are loaded.

        :param user_id: user's telegram id
        :type user_id: int
        :param limit: transactions count
        :type limit: int
        :param eager: use eager loading
        :type eager: bool
        :return: list of transactions
        :rtype: Sequence[Transaction]
        """
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        if eager:
            stmt = stmt.options(
                selectinload(Transaction.debit_account).selectinload(Account.storage),
                selectinload(Transaction.credit_account),
            )

        return (await self._session.scalars(stmt)).all()
