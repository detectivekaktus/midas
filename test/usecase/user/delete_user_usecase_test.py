from pytest import fixture, raises
from sqlalchemy.orm import Session

from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.db.schemas.user import User
from src.query import GenericRepository
from src.usecase.user import DeleteUserUsecase, RegisterUserUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_register_usecase(test_engine):
    session = Session(test_engine)
    usecase = RegisterUserUsecase(session=session)
    return usecase


@fixture
def test_delete_usecase(test_engine):
    session = Session(test_engine)
    usecase = DeleteUserUsecase(session=session)
    return usecase


def test_register_user_and_delete_their_profile_and_data(
    test_engine, test_register_usecase, test_delete_usecase
):
    user_id = 123456789
    currency = Currency.EUR
    test_register_usecase.execute(user_id, currency)
    test_delete_usecase.execute(user_id)

    session = Session(test_engine)
    user_repo = GenericRepository[User, int](User, session)
    account_repo = GenericRepository[Account, int](Account, session)
    storage_repo = GenericRepository[Storage, int](Storage, session)

    with session:
        user = user_repo.get_by_id(user_id)
        assert user is None

        for i in TransactionType:
            account = account_repo.get_by_id(i)
            assert account is None

        storage = storage_repo.get_by_id(1)
        assert storage is None


def test_register_user_and_double_delete_their_profile_and_data(
    test_register_usecase, test_delete_usecase
):
    user_id = 123456789
    currency = Currency.EUR
    test_register_usecase.execute(user_id, currency)
    test_delete_usecase.execute(user_id)

    with raises(ValueError):
        test_delete_usecase.execute(user_id)


def test_delete_invalid_user(test_delete_usecase):
    with raises(ValueError):
        test_delete_usecase.execute(1)
