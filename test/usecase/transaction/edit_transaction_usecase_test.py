from decimal import Decimal
from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from src.usecase.transaction import EditTransactionUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_edit_transaction(test_engine) -> EditTransactionUsecase:
    session = AsyncSession(test_engine)
    usecase = EditTransactionUsecase(session=session)
    return usecase


@mark.asyncio
async def test_add_one_transaction_and_edit_it(
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
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

    old_transaction = (await test_get_transactions.execute(user_id))[0]
    await test_edit_transaction.execute(
        old_transaction.id, description="December 2025", amount=Decimal("1000")
    )
    new_transaction = (await test_get_transactions.execute(user_id))[0]

    assert old_transaction.id == new_transaction.id
    assert old_transaction.transaction_type_id == new_transaction.transaction_type_id
    assert old_transaction.title == new_transaction.title
    assert old_transaction.amount == Decimal(
        "100"
    ) and new_transaction.amount == Decimal("1000")
    assert (
        old_transaction.description is None
        and new_transaction.description == "December 2025"
    )


@mark.asyncio
@mark.asyncio
async def test_add_4_transactions_and_edit_them(
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
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
        await test_edit_transaction.execute(
            transaction.id, title=str(i), description=""
        )

    transactions = await test_get_transactions.execute(user_id)
    transactions = reversed(transactions)
    for i, transaction in enumerate(transactions):
        assert transaction.user_id == transaction_data[i]["user_id"]
        assert transaction.title == str(i)
        assert (
            transaction.transaction_type_id == transaction_data[i]["transaction_type"]
        )
        assert transaction.amount == transaction_data[i]["amount"]
        assert transaction.description == ""


@mark.asyncio
async def test_pass_invalid_arguments(
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
) -> None:
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

    transaction = (await test_get_transactions.execute(user_id))[0]

    with raises(ValueError):
        await test_edit_transaction.execute(transaction.id)
