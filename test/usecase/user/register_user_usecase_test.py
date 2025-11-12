from pytest import fixture, raises

from src.db.schemas.storage import Storage
from src.db.schemas.account import Account
from src.db.schemas.user import User
from src.query.repository import Repository
from src.usecase.user import RegisterUserUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_user_repo(test_engine) -> Repository[User, int]:
    repo = Repository[User, int](User, custom_engine=test_engine)
    return repo


@fixture
def test_account_repo(test_engine) -> Repository[Account, int]:
    repo = Repository[Account, int](Account, custom_engine=test_engine)
    return repo


@fixture
def test_storage_repo(test_engine) -> Repository[Storage, int]:
    repo = Repository[Storage, int](Storage, custom_engine=test_engine)
    return repo


@fixture
def test_usecase(
    test_user_repo, test_account_repo, test_storage_repo
) -> RegisterUserUsecase:
    usecase = RegisterUserUsecase(test_user_repo, test_account_repo, test_storage_repo)
    return usecase


def test_register_user(
    test_user_repo, test_account_repo, test_storage_repo, test_usecase
):
    user_id = 123456789
    currency = Currency.EUR
    test_usecase.execute(user_id, currency)

    with test_user_repo:
        user = test_user_repo.get_by_id(user_id)

        assert user
        assert user.id == user_id
        assert user.currency_id == currency

    with test_account_repo:
        for i in TransactionType:
            account = test_account_repo.get_by_id(i)

            assert account
            assert account.user_id == user_id
            assert account.transaction_type_id == i
            assert account.credit_amount == 0
            assert account.debit_amount == 0

        with test_storage_repo:
            storage = test_storage_repo.get_by_id(1)

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
