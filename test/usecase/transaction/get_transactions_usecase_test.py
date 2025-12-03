from decimal import Decimal
from aiogram.enums import Currency
from pytest import fixture, mark
from sqlalchemy.ext.asyncio import AsyncSession

from src.usecase.transaction import GetTransactionsUsecase
from src.util.enums import TransactionType


@fixture
def test_get_transactions(test_engine) -> GetTransactionsUsecase:
    session = AsyncSession(test_engine)
    usecase = GetTransactionsUsecase(session=session)
    return usecase


@mark.asyncio
async def test_create_income_transaction_and_get_it_back(
    test_register_usecase, test_create_transaction, test_get_transactions
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income transaction",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    transactions = await test_get_transactions.execute(user_id)
    for transaction in transactions:
        assert transaction.user_id == transaction_data["user_id"]
        assert transaction.transaction_type_id == transaction_data["transaction_type"]
        assert transaction.title == transaction_data["title"]
        assert transaction.amount == transaction_data["amount"]


@mark.asyncio
async def test_add_4_transactions_and_get_them_back(
    test_register_usecase, test_create_transaction, test_get_transactions
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = [
        {
            "user_id": user_id,
            "transaction_type": TransactionType.INCOME,
            "title": "Income transaction",
            "amount": Decimal("100"),
            "description": "Income transaction description",
        },
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

    for transaction in transaction_data:
        await test_create_transaction.execute(**transaction)

    transactions = await test_get_transactions.execute(user_id)
    transactions = reversed(transactions)
    for i, transaction in enumerate(transactions):
        assert transaction.user_id == transaction_data[i]["user_id"]
        assert (
            transaction.transaction_type_id == transaction_data[i]["transaction_type"]
        )
        assert transaction.title == transaction_data[i]["title"]
        assert transaction.amount == transaction_data[i]["amount"]
        assert transaction.description == transaction_data[i]["description"]
