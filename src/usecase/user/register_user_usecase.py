from typing import override

from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.db.schemas.user import User
from src.query.repository import Repository
from src.usecase.abstract_usecase import AbstractUsecase
from src.util.enums import Currency, TransactionType


class RegisterUserUsecase(AbstractUsecase):
    """
    Register user usercase. This class performs all those necessary
    operations for creating a new user, described more deeply in
    `execute()` method.
    """
    
    def __init__(
        self,
        user_repo: Repository[User, int],
        account_repo: Repository[Account, int],
        storage_repo: Repository[Storage, int],
    ) -> None:
        """
        Initialize a new `RegisterUserUsecase` object.

        :param user_repo: repository instance for adding a new user.
        :type user_repo: Repository[User, int]
        :param account_repo: repository instance for adding new accounts.
        :type account_repo: Repository[Account, int]
        :param storage_repo: repository instance for adding a new storage.
        :type storage_repo: Repository[Storage, int]
        """
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.storage_repo = storage_repo

    @override
    def execute(self, user_id: int, currency: Currency) -> None:
        """
        Register a new user and data relative to them in the database.

        This method creates a new row inside `users` table for the current
        user. Also, all users have one associated account per each
        `TransactionType`. In the end, `TransactionType.INCOME` account is
        related to a new storage for the newly created user.

        :param user_id: user's telegram id.
        :type user_id: int
        :param currency: user's preferred currency.
        :type currency: Currency

        :raise KeyError: if user with `user_id` already exists.
        """
        with self.user_repo:
            user = self.user_repo.get_by_id(user_id)
            if user is not None:
                raise KeyError("User already exists")

            user = User(id=user_id, currency_id=currency.value)
            self.user_repo.add(user)

        income_account_id = None
        with self.account_repo:
            accounts = [
                Account(user_id=user_id, transaction_type_id=type_id)
                for type_id in TransactionType
            ]

            self.account_repo.add_many(accounts)
            self.account_repo.flush()

            income_account = [
                acc
                for acc in accounts
                if acc.transaction_type_id == TransactionType.INCOME
            ][0]
            income_account_id = income_account.id

        with self.storage_repo:
            storage = Storage(user_id=user_id, account_id=income_account_id)
            self.storage_repo.add(storage)
