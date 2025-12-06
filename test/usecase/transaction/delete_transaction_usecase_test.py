from decimal import Decimal
from pytest import fixture, mark
from sqlalchemy.ext.asyncio import AsyncSession

from src.usecase.transaction import DeleteTransactionUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_delete_transaction(test_engine) -> DeleteTransactionUsecase:
    session = AsyncSession(test_engine)
    usecase = DeleteTransactionUsecase(session=session)
    return usecase


@mark.asyncio
async def test_create_income_transaction_and_delete_it(
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_delete_transaction,
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
    await test_delete_transaction.execute(transactions[0].id)

    transactions = await test_get_transactions.execute(user_id)
    assert len(transactions) == 0


@mark.asyncio
async def test_add_4_transactions_and_delete_them(
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_delete_transaction,
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
    for transaction in transactions:
        await test_delete_transaction.execute(transaction.id)

    transactions = await test_get_transactions.execute(user_id)
    assert len(transactions) == 0
