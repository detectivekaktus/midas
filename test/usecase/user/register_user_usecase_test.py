from pytest import mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from src.query.account import AccountRepository
from src.query.storage import StorageRepository
from src.query.user import UserRepository
from src.util.enums import Currency, TransactionType



@mark.asyncio
async def test_register_user(test_engine, test_register_usecase):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    session = AsyncSession(test_engine)
    user_repo = UserRepository(session)
    account_repo = AccountRepository(session)
    storage_repo = StorageRepository(session)

    async with session:
        user = await user_repo.get_by_id(user_id)
        assert user
        assert user.id == user_id
        assert user.currency_id == currency

        for i in TransactionType:
            account = await account_repo.get_by_id(i)
            assert account
            assert account.user_id == user_id
            assert account.transaction_type_id == i
            assert account.credit_amount == 0
            assert account.debit_amount == 0

        storage = await storage_repo.get_by_id(1)
        assert storage
        assert storage.id == 1
        assert storage.user_id == user_id
        assert storage.account_id == 1
        assert storage.amount == 0


@mark.asyncio
async def test_register_the_same_user_twice(test_register_usecase):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    with raises(KeyError):
        await test_register_usecase.execute(user_id, currency)
