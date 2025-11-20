from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.user import User
from src.query import GenericRepository
from src.query.account import AccountRepository
from src.query.storage import StorageRepository
from src.usecase.user import DeleteUserUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_delete_usecase(test_engine) -> DeleteUserUsecase:
    session = AsyncSession(test_engine)
    usecase = DeleteUserUsecase(session=session)
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
    user_repo = GenericRepository[User, int](User, session)
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
