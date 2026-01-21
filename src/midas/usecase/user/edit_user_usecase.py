from typing import override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger
from midas.services import user_storage

from midas.query.user.repository import UserRepository
from midas.usecase.abstract_usecase import AbstractUsecase
from midas.util.enums import Currency
from midas.util.errors import NoChangesDetectedException


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

        :raise ValueError: if no user with `user_id` exists.
        :raise NoChangesDetectedException: if user initial data is identical to
        the update data.
        """
        app_logger.debug("Started `EditUserUsecase` execution")

        async with self._session:
            user = await self._user_repo.get_by_id(user_id)
            if user is None:
                raise ValueError(f"No user with {user_id} id was found")

            if user.currency_id == currency:
                raise NoChangesDetectedException("No changes were detected")

            user.currency_id = currency
            await user_storage.store(user)

            await self._session.commit()

        app_logger.debug("Successfully edited user")
