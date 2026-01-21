from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from src.loggers import app_logger

from src.query.account import AccountRepository
from src.query.storage import StorageRepository
from src.query.user import UserRepository
from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.db.schemas.user import User
from src.usecase.abstract_usecase import AbstractUsecase
from src.util.enums import Currency, TransactionType


class RegisterUserUsecase(AbstractUsecase[None]):
    """
    Register user usercase. This class performs all those necessary
    operations for creating a new user, described more deeply in
    `execute()` method.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        """
        Initialize a new `RegisterUserUsecase` object.

        See `AbstractUsecase` for more details.
        """
        super().__init__(session)
        self._user_repo = UserRepository(self._session)
        self._account_repo = AccountRepository(self._session)
        self._storage_repo = StorageRepository(self._session)

    @override
    async def execute(self, user_id: int, currency: Currency) -> None:
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
        app_logger.debug("Started `RegisterUserUsecase` execution")

        async with self._session:
            user = await self._user_repo.get_by_id(user_id)
            if user is not None:
                app_logger.debug(
                    "Finished `RegisterUserUsecase` execution too soon because user already exists"
                )
                raise KeyError("User already exists")

            user = User(id=user_id, currency_id=currency)
            self._user_repo.add(user)

            accounts = [
                Account(user_id=user_id, transaction_type_id=type_id)
                for type_id in TransactionType
            ]
            self._account_repo.add_many(accounts)
            await self._account_repo.flush()

            income_account = next(
                acc
                for acc in accounts
                if acc.transaction_type_id == TransactionType.INCOME
            )
            storage = Storage(user_id=user_id, account_id=income_account.id)
            self._storage_repo.add(storage)

            await self._session.commit()

        app_logger.debug("Successfully registered a user")
