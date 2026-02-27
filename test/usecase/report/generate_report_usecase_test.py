from decimal import Decimal
from pytest import fixture, mark
from sqlalchemy.ext.asyncio import AsyncSession

from midas.db.schemas.account import Account
from midas.query.account import AccountRepository
from midas.usecase.report import GenerateReportUsecase
from midas.util.enums import Currency, TransactionType


@fixture
def test_generate_report(test_engine) -> GenerateReportUsecase:
    session = AsyncSession(test_engine)
    usecase = GenerateReportUsecase(session)
    return usecase


@mark.asyncio
async def test_add_only_expense_transactions_and_clear_accounts(
    test_engine, test_register_usecase, test_create_transaction, test_generate_report
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transactions = [
        {
            "user_id": user_id,
            "transaction_type": TransactionType.ENTERTAINMENT,
            "title": "Satisfactory",
            "amount": Decimal("49.99"),
            "description": "Bought Satisfactory on steam",
        },
        {
            "user_id": user_id,
            "transaction_type": TransactionType.GROCERIES,
            "title": "Lidl groceries",
            "amount": Decimal("150.46"),
            "description": "",
        },
        {
            "user_id": user_id,
            "transaction_type": TransactionType.BILLS_AND_FEES,
            "title": "Rent",
            "amount": Decimal("400"),
            "description": "Paid my rent",
        },
    ]

    balance = Decimal()
    for transaction in transactions:
        balance -= transaction["amount"]
        await test_create_transaction.execute(**transaction)

    report = await test_generate_report.execute(user_id)
    assert report["result"] == balance

    session = AsyncSession(test_engine)
    repo = AccountRepository(session)
    async with session:
        for transaction in transactions:
            ttype = transaction["transaction_type"]
            account: Account = await repo.get_user_account_by_transaction_type(
                user_id, ttype
            )  # type: ignore

            assert report["accounts"][ttype.name.lower()] == transaction["amount"]
            assert account.debit_amount == Decimal()
            assert account.credit_amount == Decimal()


@mark.asyncio
async def test_add_only_expense_transactions_and_dont_clear_accounts(
    test_engine, test_register_usecase, test_create_transaction, test_generate_report
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transactions = [
        {
            "user_id": user_id,
            "transaction_type": TransactionType.ENTERTAINMENT,
            "title": "Satisfactory",
            "amount": Decimal("49.99"),
            "description": "Bought Satisfactory on steam",
        },
        {
            "user_id": user_id,
            "transaction_type": TransactionType.GROCERIES,
            "title": "Lidl groceries",
            "amount": Decimal("150.46"),
            "description": "",
        },
        {
            "user_id": user_id,
            "transaction_type": TransactionType.BILLS_AND_FEES,
            "title": "Rent",
            "amount": Decimal("400"),
            "description": "Paid my rent",
        },
    ]

    balance = Decimal()
    for transaction in transactions:
        balance -= transaction["amount"]
        await test_create_transaction.execute(**transaction)

    report = await test_generate_report.execute(user_id, clear_accounts=False)
    assert report["result"] == balance

    session = AsyncSession(test_engine)
    repo = AccountRepository(session)
    async with session:
        for transaction in transactions:
            ttype = transaction["transaction_type"]
            account: Account = await repo.get_user_account_by_transaction_type(
                user_id, ttype
            )  # type: ignore
            assert (
                report["accounts"][ttype.name.lower()]
                == account.debit_amount - account.credit_amount
            )
