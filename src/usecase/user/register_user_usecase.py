from typing import override

from sqlalchemy.orm import Session

from src.query import GenericRepository
from src.query.account import AccountRepository
from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.db.schemas.user import User
from src.usecase.abstract_usecase import AbstractUsecase
from src.util.enums import Currency, TransactionType


class RegisterUserUsecase(AbstractUsecase):
    """
    Register user usercase. This class performs all those necessary
    operations for creating a new user, described more deeply in
    `execute()` method.
    """

    @override
    def __init__(self, session: Session | None = None) -> None:
        """
        Initialize a new `RegisterUserUsecase` object.

        See `AbstractUsecase` for more details.
        """
        super().__init__(session)
        self._user_repo = GenericRepository[User, int](User, self._session)
        self._account_repo = AccountRepository(self._session)
        self._storage_repo = GenericRepository[Storage, int](Storage, self._session)

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
        with self._session:
            user = self._user_repo.get_by_id(user_id)
            if user is not None:
                raise KeyError("User already exists")

            user = User(id=user_id, currency_id=currency)
            self._user_repo.add(user)

            accounts = [
                Account(user_id=user_id, transaction_type_id=type_id)
                for type_id in TransactionType
            ]
            self._account_repo.add_many(accounts)
            self._account_repo.flush()

            income_account = next(
                acc
                for acc in accounts
                if acc.transaction_type_id == TransactionType.INCOME
            )
            storage = Storage(user_id=user_id, account_id=income_account.id)
            self._storage_repo.add(storage)

            self._session.commit()
