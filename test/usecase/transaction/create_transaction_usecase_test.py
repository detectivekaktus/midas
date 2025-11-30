from decimal import Decimal
from pytest import fixture, mark
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.storage import Storage
from src.db.schemas.account import Account
from src.query.user import UserRepository
from src.query.transaction import TransactionRepository
from src.usecase.transaction import CreateTransactionUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_create_transaction(test_engine) -> CreateTransactionUsecase:
    session = AsyncSession(test_engine)
    usecase = CreateTransactionUsecase(session=session)
    return usecase


@mark.asyncio
async def test_create_income_transaction_without_description(
    test_engine, test_register_usecase, test_create_transaction
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

    session = AsyncSession(test_engine)
    user_repo = UserRepository(session)
    transaction_repo = TransactionRepository(session)
    async with session:
        user = await user_repo.get_by_id(user_id)
        assert user is not None

        transactions = await transaction_repo.get_recent(user.id, eager=True)
        transaction = transactions[0]
        assert transaction.user_id == transaction_data["user_id"]
        assert transaction.transaction_type_id == transaction_data["transaction_type"]
        assert transaction.title == transaction_data["title"]
        assert transaction.amount == transaction_data["amount"]

        debit_account: Account = transaction.debit_account
        assert debit_account is not None
        assert debit_account.debit_amount == transaction_data["amount"]

        credit_account = transaction.credit_account
        assert credit_account is None

        storage: Storage = debit_account.storage
        assert storage is not None
        assert storage.amount == transaction_data["amount"]


@mark.asyncio
async def test_create_income_transaction_with_description(
    test_engine, test_register_usecase, test_create_transaction
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income transaction",
        "amount": Decimal("100"),
        "description": "Income transaction description",
    }
    await test_create_transaction.execute(**transaction_data)

    session = AsyncSession(test_engine)
    user_repo = UserRepository(session)
    transaction_repo = TransactionRepository(session)
    async with session:
        user = await user_repo.get_by_id(user_id)
        assert user is not None

        transactions = await transaction_repo.get_recent(user.id, eager=True)
        transaction = transactions[0]
        assert transaction.user_id == transaction_data["user_id"]
        assert transaction.transaction_type_id == transaction_data["transaction_type"]
        assert transaction.title == transaction_data["title"]
        assert transaction.amount == transaction_data["amount"]
        assert transaction.description == transaction_data["description"]

        debit_account: Account = transaction.debit_account
        assert debit_account is not None
        assert debit_account.debit_amount == transaction_data["amount"]

        credit_account = transaction.credit_account
        assert credit_account is None

        storage: Storage = debit_account.storage
        assert storage is not None
        assert storage.amount == transaction_data["amount"]


@mark.asyncio
async def test_create_multiple_transactions(
    test_engine, test_register_usecase, test_create_transaction
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transactions = [
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

    for transaction in transactions:
        await test_create_transaction.execute(**transaction)

    session = AsyncSession(test_engine)
    user_repo = UserRepository(session)
    transaction_repo = TransactionRepository(session)
    async with session:
        user = await user_repo.get_by_id(user_id, eager=True)
        assert user is not None

        income_account_amount = Decimal("0")
        user_transactions = await transaction_repo.get_recent(user.id, eager=True)
        # it needs to be reversed, because the `transactions` array contains
        # the transactions in order from old to new ones.
        user_transactions = reversed(user_transactions)
        for i, transaction in enumerate(user_transactions):
            assert transaction.user_id == transactions[i]["user_id"]
            assert (
                transaction.transaction_type_id == transactions[i]["transaction_type"]
            )
            assert transaction.title == transactions[i]["title"]
            assert transaction.amount == transactions[i]["amount"]
            assert transaction.description == transactions[i]["description"]

            debit_account = transaction.debit_account
            credit_account = transaction.credit_account
            if transaction.transaction_type_id == TransactionType.INCOME:
                income_account_amount += transaction.amount

                assert debit_account is not None
                assert credit_account is None
            else:
                income_account_amount -= transaction.amount

                assert debit_account is not None
                assert debit_account.debit_amount == transactions[i]["amount"]
                assert credit_account is not None

        storage = user.storages[0]
        assert storage is not None
        assert storage.amount == income_account_amount
