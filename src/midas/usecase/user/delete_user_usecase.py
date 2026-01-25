from typing import override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.query.account import AccountRepository
from midas.query.event import EventRepository
from midas.query.storage import StorageRepository
from midas.query.transaction import TransactionRepository
from midas.query.user import UserRepository
from midas.usecase.abstract_usecase import AbstractUsecase


class DeleteUserUsecase(AbstractUsecase[None]):
    """
    Delete user usecase. This class deletes all user-generated
    data produced by the user as well as their profile.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._user_repo = UserRepository(self._session)
        self._account_repo = AccountRepository(self._session)
        self._storage_repo = StorageRepository(self._session)
        self._transaction_repo = TransactionRepository(self._session)
        self._event_repo = EventRepository(self._session)

    @override
    async def execute(self, user_id: int) -> None:
        """
        Delete all user-generated content and their profile.

        What's the subject of being purged:
        * Transactions
        * Storages
        * Accounts
        * Events

        NOTE: Changes done with this method are irreversible!

        :param user_id: user's telegram id.
        :type user_id: int

        :raise ValueError: if no user with the provided id exists.
        """
        app_logger.debug(f"Started `DeleteUserUsecase` execution: {user_id}")

        async with self._session:
            user = await self._user_repo.get_by_id(user_id)
            if user is None:
                app_logger.debug(
                    "Finished `DeleteUserUsecase` execution too soon because user does not exist"
                )
                raise ValueError(f"No user with {user_id} exists")

            await self._transaction_repo.purge_by_user_id(user_id)
            await self._storage_repo.purge_by_user_id(user_id)
            await self._account_repo.purge_by_user_id(user_id)
            await self._event_repo.purge_by_user_id(user_id)
            await self._user_repo.delete_by_id(user_id)
            await self._session.commit()

        app_logger.debug(f"Successfully deleted the user: {user_id}")
