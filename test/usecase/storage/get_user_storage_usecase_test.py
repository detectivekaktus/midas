from decimal import Decimal
from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from src.usecase.storage import GetUserStorageUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_get_storage(test_engine) -> GetUserStorageUsecase:
    session = AsyncSession(test_engine)
    usecase = GetUserStorageUsecase(session=session)
    return usecase


@mark.asyncio
async def test_get_empty_storage(test_register_usecase, test_get_storage):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    storage = await test_get_storage.execute(user_id)
    assert storage is not None
    assert storage.amount == Decimal()


@mark.asyncio
async def test_get_invalid_user_storage(test_get_storage):
    with raises(ValueError):
        await test_get_storage.execute(69420)


@mark.asyncio
async def test_get_invalid_storage(test_register_usecase, test_get_storage):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    with raises(IndexError):
        await test_get_storage.execute(user_id, index=1)


@mark.asyncio
async def test_get_storage_after_transactions(
    test_register_usecase, test_create_transaction, test_get_storage
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = [
        {
            "user_id": user_id,
            "transaction_type": TransactionType.INCOME,
            "title": "Income",
            "amount": Decimal(1000),
        },
        {
            "user_id": user_id,
            "transaction_type": TransactionType.ENTERTAINMENT,
            "title": "Dispatch",
            "amount": Decimal(30),
        },
    ]
    for transaction in transaction_data:
        await test_create_transaction.execute(**transaction)

    storage = await test_get_storage.execute(user_id)
    assert storage is not None
    assert storage.amount == Decimal(970)
