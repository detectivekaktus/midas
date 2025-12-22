from typing import override
from sqlalchemy.ext.asyncio import AsyncSession

from src.loggers import app_logger
from src.services import user_storage

from src.query.user.repository import UserRepository
from src.usecase.abstract_usecase import AbstractUsecase
from src.util.enums import Currency


class EditUserUsecase(AbstractUsecase[None]):
    """
    Edit user usecase. Instanciate this class when in need of changing
    user's display currency.
    """

    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._user_repo = UserRepository(self._session)

    @override
    async def execute(self, user_id: int, currency: Currency) -> None:
        """
        Edit user's currency.

        This method updates cache to include new instance of `CachedUser` object.

        :param user_id: user's telegram id
        :type user_id: int
        :param currency: new currency
        :type currency: Currency

        :raise ValueError: if no user with `user_id` exists or if user is
        already using `currency` currency.
        """
        app_logger.debug("Started `EditUserUsecase` execution")

        async with self._session:
            user = await self._user_repo.get_by_id(user_id)
            if user is None:
                raise ValueError(f"No user with {user_id} id was found")

            if user.currency_id == currency:
                raise ValueError("No changes were detected")

            user.currency_id = currency
            await user_storage.store(user)

            await self._session.commit()

        app_logger.debug("Successfully edited user")
