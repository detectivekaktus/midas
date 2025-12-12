from decimal import Decimal
from typing import Any, Optional, override
from uuid import UUID
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.loggers import app_logger

from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.db.schemas.transaction import Transaction
from src.query.account import AccountRepository
from src.query.transaction import TransactionRepository
from src.usecase.abstract_usecase import AbstractUsecase
from src.util.enums import TransactionType


class EditTransactionUsecase(AbstractUsecase[None]):
    """
    Edit transaction usecase class. Use this class for editing info
    of currently exisiting transactions.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._transaction_repo = TransactionRepository(self._session)
        self._account_repo = AccountRepository(self._session)

    def _get_effective_updates(
        self,
        transaction: Transaction,
        transaction_type: Optional[TransactionType],
        title: Optional[str],
        amount: Optional[Decimal],
        description: Optional[str],
    ) -> dict[str, Any]:
        """
        Get effective updates against the transaction.

        Any `None` fields aren't counter as well as any identical fields.

        :raise ValueError: if all optional fields are `None` or if changes
        are identical to source transaction.
        """
        fields = {
            "transaction_type_id": transaction_type,
            "title": title,
            "amount": amount,
            "description": description,
        }

        updates = {
            k: v
            for k, v in fields.items()
            if v is not None and getattr(transaction, k, v) != v
        }
        if len(updates) == 0:
            raise ValueError("No valid updates found")

        return updates

    async def _change_income_to_expense(
        self, transaction: Transaction, new_transaction_type: TransactionType
    ) -> None:
        """
        Current state
        +----------+-------+--------+
        | Account  | Debit | Credit |
        +----------+-------+--------+
        | Income   | X     |        |
        |          |       |        |
        +----------+-------+--------+

        Desired state
        +----------+-------+--------+
        | Account  | Debit | Credit |
        +----------+-------+--------+
        | Expense  | X     |        |
        | Income   |       | X      |
        +----------+-------+--------+
        """
        transaction.transaction_type_id = new_transaction_type

        income_account: Account = transaction.debit_account
        income_account.debit_amount -= transaction.amount
        income_account.credit_amount += transaction.amount

        # 0 -> x -> -x
        storage: Storage = income_account.storage
        storage.amount -= transaction.amount * 2

        expense_account: Account = (
            await self._account_repo.get_user_account_by_transaction_type(
                transaction.user_id, new_transaction_type
            )
        )  # type: ignore
        expense_account.debit_amount += transaction.amount

        transaction.debit_account_id = expense_account.id
        transaction.credit_account_id = income_account.id

    async def _change_expense_to_expense(
        self, transaction: Transaction, new_transaction_type: TransactionType
    ) -> None:
        """
        Current state
        +-----------+-------+--------+
        | Account   | Debit | Credit |
        +-----------+-------+--------+
        | Expense A | X     |        |
        | Income    |       | X      |
        +-----------+-------+--------+

        Desired state
        +-----------+-------+--------+
        | Account   | Debit | Credit |
        +-----------+-------+--------+
        | Expense B | X     |        |
        | Income    |       | X      |
        +-----------+-------+--------+
        """
        transaction.transaction_type_id = new_transaction_type

        debit_account: Account = transaction.debit_account
        debit_account.debit_amount -= transaction.amount

        expense_account: Account = (
            await self._account_repo.get_user_account_by_transaction_type(
                transaction.user_id, new_transaction_type
            )
        )  # type: ignore
        expense_account.debit_amount += transaction.amount

        transaction.debit_account_id = expense_account.id

    def _change_expense_to_income(
        self, transaction: Transaction, new_transaction_type: TransactionType
    ) -> None:
        """
        Current state
        +----------+-------+--------+
        | Account  | Debit | Credit |
        +----------+-------+--------+
        | Expense  | X     |        |
        | Income   |       | X      |
        +----------+-------+--------+

        Desired state
        +---------+-------+--------+
        | Account | Debit | Credit |
        +---------+-------+--------+
        | Income  | X     |        |
        |         |       |        |
        +---------+-------+--------+
        """
        transaction.transaction_type_id = new_transaction_type

        expense_account: Account = transaction.debit_account
        expense_account.debit_amount -= transaction.amount

        income_account: Account = transaction.debit_account
        income_account.credit_amount -= transaction.amount
        income_account.debit_amount += transaction.amount

        # 0 -> -x -> x
        storage: Storage = income_account.storage
        storage.amount += transaction.amount * 2

        transaction.debit_account_id = income_account.id
        transaction.credit_account_id = None

    def _change_amount(self, transaction: Transaction, new_amount: Decimal) -> None:
        diff = transaction.amount - new_amount

        debit_account: Account = transaction.debit_account
        debit_account.debit_amount -= diff

        if transaction.transaction_type_id == TransactionType.INCOME:
            storage: Storage = debit_account.storage
            storage.amount -= diff
        else:
            credit_account: Account = transaction.credit_account
            credit_account.credit_amount -= diff

            storage: Storage = credit_account.storage
            storage.amount += diff

    @override
    async def execute(
        self,
        id: UUID,
        transaction_type: Optional[TransactionType] = None,
        title: Optional[str] = None,
        amount: Optional[Decimal] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Edit transaction by its `id`.

        This method requires at least one of optional fields to be
        specified.

        :param id: transaction id
        :type id: UUID
        :param transaction_type: transaction type enum value
        :type transaction_type: Optional[TransactionType]
        :param title: transaction title
        :type title: Optional[str]
        :param amount: transaction amount
        :type amount: Optional[Decimal]
        :param description: transaction description
        :type description: Optional[str]

        :raise ValueError: if all optional fields are `None`, identical to source
        transaction, or if no transaction is bound to `id`.
        """
        app_logger.debug(f"Started `EditTransactionUsecase` execution: {id}")

        async with self._session:
            transaction = await self._transaction_repo.get_by_id(id, eager=True)
            if transaction is None:
                raise ValueError(f"No transaction with {id} found")

            updates = self._get_effective_updates(
                transaction, transaction_type, title, amount, description
            )

            if "transaction_type_id" in updates:
                new_transaction_type = updates["transaction_type_id"]
                if transaction.transaction_type_id == TransactionType.INCOME:
                    await self._change_income_to_expense(
                        transaction, new_transaction_type
                    )
                elif new_transaction_type != TransactionType.INCOME:
                    await self._change_expense_to_expense(
                        transaction, new_transaction_type
                    )
                else:
                    self._change_expense_to_income(transaction, new_transaction_type)
                updates.pop("transaction_type_id")

            if "amount" in updates:
                new_amount = updates["amount"]
                self._change_amount(transaction, new_amount)
                updates.pop("amount")

            await self._session.execute(
                update(Transaction).where(Transaction.id == id).values(**updates)
            )
            await self._session.commit()

        app_logger.debug(f"Successfully edited the transaction: {id}")
