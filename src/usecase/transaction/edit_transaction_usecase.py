from decimal import Decimal
from typing import Optional, override
from uuid import UUID
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.loggers import app_logger

from src.db.schemas.transaction import Transaction
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

        :raise ValueError: if all optional fields are `None`.
        """
        app_logger.debug(f"Started `EditTransactionUsecase` execution: {id}")

        fields = {
            "transaction_type_id": transaction_type,
            "title": title,
            "amount": amount,
            "description": description,
        }

        updates = {k: v for k, v in fields.items() if v is not None}
        if len(updates) == 0:
            raise ValueError("Expected at least one optional field")

        async with self._session:
            await self._session.execute(
                update(Transaction).where(Transaction.id == id).values(**updates)
            )
            await self._session.commit()

        app_logger.debug(f"Successfully edited the transaction: {id}")
