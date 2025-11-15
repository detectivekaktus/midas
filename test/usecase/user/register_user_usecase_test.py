from pytest import fixture, raises
from sqlalchemy.orm import Session

from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.query import GenericRepository
from src.db.schemas.user import User
from src.usecase.user import RegisterUserUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_usecase(test_engine):
    session = Session(test_engine)
    usecase = RegisterUserUsecase(session=session)
    return usecase


def test_register_user(test_engine, test_usecase):
    user_id = 123456789
    currency = Currency.EUR
    test_usecase.execute(user_id, currency)

    session = Session(test_engine)
    user_repo = GenericRepository[User, int](User, session)
    account_repo = GenericRepository[Account, int](Account, session)
    storage_repo = GenericRepository[Storage, int](Storage, session)

    with session:
        user = user_repo.get_by_id(user_id)
        assert user
        assert user.id == user_id
        assert user.currency_id == currency

        for i in TransactionType:
            account = account_repo.get_by_id(i)
            assert account
            assert account.user_id == user_id
            assert account.transaction_type_id == i
            assert account.credit_amount == 0
            assert account.debit_amount == 0

        storage = storage_repo.get_by_id(1)
        assert storage
        assert storage.id == 1
        assert storage.user_id == user_id
        assert storage.account_id == 1
        assert storage.amount == 0


def test_register_the_same_user_twice(test_usecase):
    user_id = 123456789
    currency = Currency.EUR
    test_usecase.execute(user_id, currency)

    with raises(KeyError):
        test_usecase.execute(user_id, currency)
