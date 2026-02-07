from decimal import Decimal
from typing import Optional, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.storage import Storage
from midas.db.schemas.account import Account
from midas.db.schemas.transaction import Transaction
from midas.query.account import AccountRepository
from midas.query.storage import StorageRepository
from midas.query.transaction import TransactionRepository
from midas.query.user import UserRepository
from midas.usecase.abstract_usecase import AbstractUsecase
from midas.util.enums import TransactionType


class CreateTransactionUsecase(AbstractUsecase[None]):
    """
    Create transaction usecase class. This class is responsible for
    creating new transactions and their side effects, such as account
    and storage amounts.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._transaction_repo = TransactionRepository(self._session)
        self._user_repo = UserRepository(self._session)
        self._account_repo = AccountRepository(self._session)
        self._storage_repo = StorageRepository(self._session)

    @override
    async def execute(
        self,
        user_id: int,
        transaction_type: TransactionType,
        title: str,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> None:
        """
        Create a new transaction, update accounts debit and credit values and update
        user storage associated with the income account.

        :param user_id: user's telegram id
        :type user_id: int
        :param transaction_type: transaction type
        :type transaction_type: TransactionType
        :param title: transaction title
        :type title: str
        :param amount: transaction amount
        :type amount: float
        :param description: transaction description
        :type description: Optional[str]
        """
        app_logger.debug(
            f"Started `CreateTransactionUsecase` execution: {user_id} - {transaction_type}"
        )

        async with self._session:
            user = await self._user_repo.get_by_id(user_id)
            if user is None:
                app_logger.debug(
                    "Finished `CreateTransactionUsecase` execution too soon because user does not exist"
                )
                raise ValueError(f"No user with {user_id=} exists")

            # this is guaranteed to be an account instance because user exists.
            income_account: Account = (
                await self._account_repo.get_user_account_by_transaction_type(
                    user.id, TransactionType.INCOME, eager=True
                )
            )  # type: ignore
            if transaction_type == TransactionType.INCOME:
                debit_account = income_account
                credit_account = None
                storage: Storage = debit_account.storage

                # +-------------+--------+--------+
                # | Account     | Debit  | Credit |
                # +-------------+--------+--------+
                # | Income      | amount |        |
                # | Income debt |        | amount |
                # +-------------+--------+--------+
                debit_account.debit_amount += amount
                storage.amount += amount
            else:
                # same here
                debit_account: Account = (
                    await self._account_repo.get_user_account_by_transaction_type(
                        user.id, transaction_type, eager=True
                    )
                )  # type: ignore
                credit_account = income_account
                storage: Storage = credit_account.storage

                # +-------------+--------+--------+
                # | Account     | Debit  | Credit |
                # +-------------+--------+--------+
                # | Expense     | amount |        |
                # | Income      |        | amount |
                # +-------------+--------+--------+

                debit_account.debit_amount += amount
                credit_account.credit_amount += amount
                storage.amount -= amount

            transaction = Transaction(
                user_id=user_id,
                transaction_type_id=transaction_type,
                title=title,
                description=description,
                amount=amount,
                debit_account_id=debit_account.id,
                credit_account_id=(
                    credit_account.id if credit_account is not None else None
                ),
            )
            self._transaction_repo.add(transaction)

            await self._session.commit()

        app_logger.debug(
            f"Successfully created a transaction: {user_id} - {transaction_type}"
        )
