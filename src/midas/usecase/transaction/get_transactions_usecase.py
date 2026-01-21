from typing import Sequence, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.transaction import Transaction
from midas.query.transaction import TransactionRepository
from midas.usecase.abstract_usecase import AbstractUsecase


class GetTransactionsUsecase(AbstractUsecase[Sequence[Transaction]]):
    """
    Get transactions usecase class. The instantiated object provides a number of
    recent transactions of the requested user.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._transaction_repo = TransactionRepository(self._session)

    @override
    async def execute(self, user_id: int, count: int = 16) -> Sequence[Transaction]:
        """
        Get last `count` transactions of the `user_id` user.

        Note that the list of transactions will be empty if `user_id` is invalid.

        :param user_id: user's telegram id
        :type user_id: int
        :param count: number of transactions to retrieve
        :type count: int
        :return: list of recent transactions in descending order (from the newest to oldest)
        of the specified user
        :rtype: Sequence[Transaction]
        """
        app_logger.debug(
            f"Started `GetTransactionsUsecase` execution: {user_id} - {count}"
        )

        async with self._session:
            transactions = await self._transaction_repo.get_recent(user_id, count)
            app_logger.debug("Successfully returned transactions back")
            return transactions
