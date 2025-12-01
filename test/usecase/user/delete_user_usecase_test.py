from decimal import Decimal
from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from src.query.account import AccountRepository
from src.query.storage import StorageRepository
from src.query.transaction import TransactionRepository
from src.query.user import UserRepository
from src.usecase.transaction import CreateTransactionUsecase
from src.usecase.user import DeleteUserUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_delete_usecase(test_engine) -> DeleteUserUsecase:
    session = AsyncSession(test_engine)
    usecase = DeleteUserUsecase(session=session)
    return usecase


@fixture
def test_create_transaction(test_engine) -> CreateTransactionUsecase:
    session = AsyncSession(test_engine)
    usecase = CreateTransactionUsecase(session=session)
    return usecase


@mark.asyncio
async def test_register_user_and_delete_their_profile_and_data(
    test_engine, test_register_usecase, test_delete_usecase
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)
    await test_delete_usecase.execute(user_id)

    session = AsyncSession(test_engine)
    user_repo = UserRepository(session)
    account_repo = AccountRepository(session)
    storage_repo = StorageRepository(session)

    async with session:
        user = await user_repo.get_by_id(user_id)
        assert user is None

        for i in TransactionType:
            account = await account_repo.get_by_id(i)
            assert account is None

        storage = await storage_repo.get_by_id(1)
        assert storage is None


@mark.asyncio
async def test_register_user_and_double_delete_their_profile_and_data(
    test_register_usecase, test_delete_usecase
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)
    await test_delete_usecase.execute(user_id)

    with raises(ValueError):
        await test_delete_usecase.execute(user_id)


@mark.asyncio
async def test_delete_invalid_user(test_delete_usecase):
    with raises(ValueError):
        await test_delete_usecase.execute(1)


@mark.asyncio
async def test_delete_user_with_transactions(
    test_engine, test_register_usecase, test_create_transaction, test_delete_usecase
):
    user_id = 123456789
    currency = Currency.UAH
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

    await test_delete_usecase.execute(user_id)

    session = AsyncSession(test_engine)
    user_repo = UserRepository(session)
    account_repo = AccountRepository(session)
    storage_repo = StorageRepository(session)
    transaction_repo = TransactionRepository(session)
    async with session:
        user = await user_repo.get_by_id(user_id)
        assert user is None

        for i in TransactionType:
            account = await account_repo.get_by_id(i)
            assert account is None

        storage = await storage_repo.get_by_id(1)
        assert storage is None

        transactions = await transaction_repo.get_recent(user_id, eager=True)
        assert len(transactions) == 0
