from pytest import fixture, mark, raises

from midas.db.schemas.user import User
from midas.query import GenericRepository, create_session
from midas.util.enums import Currency


@fixture
def test_repo(test_engine) -> GenericRepository:
    session = create_session(test_engine)
    repo = GenericRepository[User, int](User, session)
    return repo


@mark.asyncio
async def test_add_one_and_get_it_back(test_repo):
    async with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        fetched_user = await test_repo.get_by_id(123456789)

        assert fetched_user
        assert user is fetched_user
        assert fetched_user.id == 123456789
        assert fetched_user.currency_id == Currency.EUR


@mark.asyncio
async def test_add_one_and_get_invalid(test_repo):
    async with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        fetched_user = await test_repo.get_by_id(1)

        assert not fetched_user
        assert fetched_user is not user


@mark.asyncio
async def test_add_many_and_get_first_one(test_repo):
    async with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.EUR.value),
        ]
        test_repo.add_many(users)

        fetched_user = await test_repo.get_by_id(123456789)

        assert fetched_user
        assert fetched_user.id == 123456789
        assert fetched_user.currency_id == Currency.EUR


@mark.asyncio
async def test_add_many_and_get_last_one(test_repo):
    async with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.EUR.value),
        ]
        test_repo.add_many(users)

        fetched_user = await test_repo.get_by_id(123456786)

        assert fetched_user
        assert fetched_user.id == 123456786
        assert fetched_user.currency_id == Currency.EUR


@mark.asyncio
async def test_add_many_and_get_all(test_repo):
    async with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.EUR.value),
        ]
        test_repo.add_many(users)

        for user in users:
            fetched_user = await test_repo.get_by_id(user.id)
            assert fetched_user.id == user.id
            assert fetched_user.currency_id == user.currency_id


@mark.asyncio
async def test_add_one_and_update_one(test_repo):
    async with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        fetched_user = await test_repo.get_by_id(123456789)
        fetched_user.currency_id = Currency.USD.value
        # test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 123456789
        assert fetched_user.currency_id == Currency.USD


@mark.asyncio
async def test_add_many_and_update_first_one(test_repo):
    async with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.EUR.value),
        ]
        test_repo.add_many(users)

        fetched_user = await test_repo.get_by_id(123456789)
        fetched_user.currency_id = Currency.USD.value
        # test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 123456789
        assert fetched_user.currency_id == Currency.USD


@mark.asyncio
async def test_add_many_and_update_last_one(test_repo):
    async with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.EUR.value),
        ]
        test_repo.add_many(users)

        fetched_user = await test_repo.get_by_id(123456786)
        fetched_user.currency_id = Currency.EUR.value
        # test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 123456786
        assert fetched_user.currency_id == Currency.EUR


@mark.asyncio
async def test_add_one_and_delete_one(test_repo):
    async with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        await test_repo.delete_by_id(123456789)
        await test_repo.flush()

        fetched_user = await test_repo.get_by_id(123456789)

        assert not fetched_user


@mark.asyncio
async def test_add_one_and_delete_invalid_one(test_repo):
    async with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        with raises(ValueError):
            await test_repo.delete_by_id(2)


@mark.asyncio
async def test_add_many_and_delete_first_one(test_repo):
    async with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.EUR.value),
        ]
        test_repo.add_many(users)

        await test_repo.delete_by_id(123456789)
        await test_repo.flush()

        fetched_user = await test_repo.get_by_id(123456789)

        assert not fetched_user


@mark.asyncio
async def test_add_many_and_delete_last_one(test_repo):
    async with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.EUR.value),
        ]
        test_repo.add_many(users)

        await test_repo.delete_by_id(123456786)
        await test_repo.flush()

        fetched_user = await test_repo.get_by_id(123456786)

        assert not fetched_user


@mark.asyncio
async def test_add_many_and_delete_all(test_repo):
    async with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.EUR.value),
        ]
        test_repo.add_many(users)

        for i in range(123456786, 123456790):
            await test_repo.delete_by_id(i)
            await test_repo.flush()
            fetched_user = await test_repo.get_by_id(i)
            assert not fetched_user
