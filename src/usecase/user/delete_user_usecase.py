from typing import override
from sqlalchemy.orm import Session

from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.db.schemas.user import User
from src.query import GenericRepository
from src.usecase.abstract_usecase import AbstractUsecase


class DeleteUserUsecase(AbstractUsecase):
    """
    Delete user usecase. This class deletes all user-generated
    data produced by the user as well as their profile.
    """

    @override
    def __init__(self, session: Session | None = None) -> None:
        super().__init__(session)
        self._user_repo = GenericRepository[User, int](User, self._session)
        self._account_repo = GenericRepository[Account, int](Account, self._session)
        self._storage_repo = GenericRepository[Storage, int](Storage, self._session)

    @override
    def execute(self, user_id: int) -> None:
        """
        Delete all user-generated content and their profile.

        First, this method deletes all storages associated with
        the user profile. In the second place, all user accounts
        are destroyed. Finally, the user row inside `users` table
        is purged.

        NOTE: Changes done with this method are irreversible!

        :param user_id: user's telegram id.
        :type user_id: int

        :raise ValueError: if no user with the provided id exists.
        """
        with self._session:
            user = self._user_repo.get_by_id(user_id)
            if user is None:
                raise ValueError(f"No user with {user_id} exists")
            
            storages: list[Storage] = user.storages
            for storage in storages:
                self._storage_repo.delete_by_id(storage.id)
            self._storage_repo.flush()

            accounts: list[Account] = user.accounts
            for account in accounts:
                self._account_repo.delete_by_id(account.id)
            self._account_repo.flush()

            self._user_repo.delete_by_id(user.id)
            self._session.commit()
