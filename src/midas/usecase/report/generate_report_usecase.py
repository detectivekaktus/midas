from decimal import Decimal
from typing import Any, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.account import Account
from midas.query.account import AccountRepository
from midas.usecase.abstract_usecase import AbstractUsecase
from midas.util.enums import TransactionType


class GenerateReportUsecase(AbstractUsecase[dict[str, Any]]):
    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self.account_repo = AccountRepository(self._session)

    @override
    async def execute(
        self, user_id: int, clear_accounts: bool = True
    ) -> dict[str, Any]:
        """
        Generate personalized report for user.

        :param user_id: user's telegram id.
        :type user_id: int
        :param clear_accounts: if `True` the debit and credit values
        of accounts get cleared.
        :type clear_accounts: bool
        :return: dictionary with all entries to be displayed
        to the end user.
        :rtype: dict[str, Any]
        """
        app_logger.debug(f"Started `GenerateReportUsecase` execution: {user_id}")

        async with self._session:
            report: dict[str, Any] = {}
            report["accounts"] = {}

            accounts: list[Account] = [
                await self.account_repo.get_user_account_by_transaction_type(
                    user_id, ttype
                )
                for ttype in TransactionType
            ]  # type: ignore

            for account in accounts:
                ttype = TransactionType(account.transaction_type_id)
                balance = account.debit_amount - account.credit_amount

                if ttype == TransactionType.INCOME:
                    report["result"] = balance
                report["accounts"][ttype.name.lower()] = balance

                if clear_accounts:
                    account.debit_amount = Decimal()
                    account.credit_amount = Decimal()

            await self._session.commit()

        app_logger.debug(f"Successfully generated report for: {user_id}")
        return report
