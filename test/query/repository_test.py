from pytest import fixture, raises

from src.query.session import create_session
from src.db.schemas.user import User
from src.query.repository import Repository
from src.util.enums import Currency


@fixture
def test_repo(test_engine) -> Repository:
    session = create_session(test_engine)
    repo = Repository[User, int](User, session)
    return repo


def test_add_one_and_get_it_back(test_repo):
    with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        fetched_user = test_repo.get_by_id(123456789)

        assert fetched_user
        assert user is fetched_user
        assert fetched_user.id == 123456789
        assert fetched_user.currency_id == Currency.EUR


def test_add_one_and_get_invalid(test_repo):
    with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        fetched_user = test_repo.get_by_id(1)

        assert not fetched_user
        assert fetched_user is not user


def test_add_many_and_get_first_one(test_repo):
    with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.BTC.value),
        ]
        test_repo.add_many(users)

        fetched_user = test_repo.get_by_id(123456789)

        assert fetched_user
        assert fetched_user.id == 123456789
        assert fetched_user.currency_id == Currency.EUR


def test_add_many_and_get_last_one(test_repo):
    with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.BTC.value),
        ]
        test_repo.add_many(users)

        fetched_user = test_repo.get_by_id(123456786)

        assert fetched_user
        assert fetched_user.id == 123456786
        assert fetched_user.currency_id == Currency.BTC


def test_add_many_and_get_all(test_repo):
    with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.BTC.value),
        ]
        test_repo.add_many(users)

        for user in users:
            fetched_user = test_repo.get_by_id(user.id)
            assert fetched_user.id == user.id
            assert fetched_user.currency_id == user.currency_id


def test_add_one_and_update_one(test_repo):
    with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        fetched_user = test_repo.get_by_id(123456789)
        fetched_user.currency_id = Currency.USD.value
        # test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 123456789
        assert fetched_user.currency_id == Currency.USD


def test_add_many_and_update_first_one(test_repo):
    with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.BTC.value),
        ]
        test_repo.add_many(users)

        fetched_user = test_repo.get_by_id(123456789)
        fetched_user.currency_id = Currency.USD.value
        # test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 123456789
        assert fetched_user.currency_id == Currency.USD


def test_add_many_and_update_last_one(test_repo):
    with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.BTC.value),
        ]
        test_repo.add_many(users)

        fetched_user = test_repo.get_by_id(123456786)
        fetched_user.currency_id = Currency.EUR.value
        # test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 123456786
        assert fetched_user.currency_id == Currency.EUR


def test_add_one_and_delete_one(test_repo):
    with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        test_repo.delete_by_id(123456789)
        test_repo.flush()

        fetched_user = test_repo.get_by_id(123456789)

        assert not fetched_user


def test_add_one_and_delete_invalid_one(test_repo):
    with test_repo._session:
        user = User(id=123456789, currency_id=Currency.EUR.value)
        test_repo.add(user)

        with raises(ValueError):
            test_repo.delete_by_id(2)


def test_add_many_and_delete_first_one(test_repo):
    with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.BTC.value),
        ]
        test_repo.add_many(users)

        test_repo.delete_by_id(123456789)
        test_repo.flush()
        
        fetched_user = test_repo.get_by_id(123456789)

        assert not fetched_user


def test_add_many_and_delete_last_one(test_repo):
    with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.BTC.value),
        ]
        test_repo.add_many(users)

        test_repo.delete_by_id(123456786)
        test_repo.flush()
        
        fetched_user = test_repo.get_by_id(123456786)

        assert not fetched_user


def test_add_many_and_delete_all(test_repo):
    with test_repo._session:
        users = [
            User(id=123456789, currency_id=Currency.EUR.value),
            User(id=123456788, currency_id=Currency.USD.value),
            User(id=123456787, currency_id=Currency.UAH.value),
            User(id=123456786, currency_id=Currency.BTC.value),
        ]
        test_repo.add_many(users)

        for i in range(123456786, 123456790):
            test_repo.delete_by_id(i)
            test_repo.flush()
            assert not test_repo.get_by_id(i)
