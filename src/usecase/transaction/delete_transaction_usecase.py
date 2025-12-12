from typing import override
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.loggers import app_logger

from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.query.transaction import TransactionRepository
from src.usecase.abstract_usecase import AbstractUsecase
from src.util.enums import TransactionType


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

        This method affects debit and credit accounts as well as storages
        associated with them.

        :param id: transaction id
        :type id: UUID
        """
        app_logger.debug(f"Started `DeleteTransactionUsecase` execution: {id}")

        async with self._session:
            transaction = await self._transaction_repo.get_by_id(id, eager=True)
            if transaction is None:
                raise ValueError(f"No transaction with {id} is found")

            debit_account: Account = transaction.debit_account
            credit_account: Account = transaction.credit_account
            storage: Storage = (
                debit_account.storage
                if transaction.transaction_type_id == TransactionType.INCOME
                else credit_account.storage
            )

            if transaction.transaction_type_id == TransactionType.INCOME:
                debit_account.debit_amount -= transaction.amount
                storage.amount -= transaction.amount
            else:
                debit_account.debit_amount -= transaction.amount
                credit_account.credit_amount -= transaction.amount
                storage.amount += transaction.amount

            await self._transaction_repo.delete_by_id(id)
            await self._session.commit()

        app_logger.debug(f"Successfully deleted the transaction: {id}")
