from typing import override
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.loggers import app_logger

from src.query.transaction import TransactionRepository
from src.usecase.abstract_usecase import AbstractUsecase


class DeleteTransactionUsecase(AbstractUsecase[None]):
    """
    Delete transaction usecase class. Use this class to delete transactions
    by their primary key.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._transaction_repo = TransactionRepository(self._session)

    @override
    async def execute(self, id: UUID) -> None:
        """
        Delete transaction by its id.

        :param id: transaction id
        :type id: UUID
        """
        app_logger.debug(f"Started `DeleteTransactionUsecase` execution: {id}")

        async with self._session:
            await self._transaction_repo.delete_by_id(id)
            await self._session.commit()

        app_logger.debug(f"Successfully deleted the transaction: {id}")
