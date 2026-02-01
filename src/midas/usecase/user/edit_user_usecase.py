from typing import Any, Optional, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger
from midas.services import user_storage

from midas.db.schemas.user import User
from midas.query.user import UserRepository
from midas.usecase.abstract_usecase import AbstractUsecase
from midas.util.enums import Currency
from midas.util.errors import NoChangesDetectedException


class EditUserUsecase(AbstractUsecase[None]):
    """
    Edit user usecase. Instanciate this class when in need of changing
    user's display currency and notification agreement.
    """

    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._user_repo = UserRepository(self._session)

    def _get_effective_updates(
        self,
        user: User,
        currency: Optional[Currency],
        send_notifications: Optional[bool],
    ) -> dict[str, Any]:
        """
        Get effective updates against the user.

        Any `None` fields aren't counter as well as any identical fields.

        :raise NoChangesDetectedException: if all optional fields are `None`
        or if changes are identical to source user.
        """
        fields = {"currency_id": currency, "send_notifications": send_notifications}

        updates = {
            k: v
            for k, v in fields.items()
            if v is not None and getattr(user, k, v) != v
        }
        if len(updates) == 0:
            raise NoChangesDetectedException("No valid updates found")

        return updates

    @override
    async def execute(
        self,
        user_id: int,
        currency: Optional[Currency] = None,
        send_notifications: Optional[bool] = None,
    ) -> None:
        """
        Edit user's currency.

        This method updates cache to include new instance of `CachedUser` object.

        :param user_id: user's telegram id
        :type user_id: int
        :param currency: new currency
        :type currency: Optional[Currency]
        :param send_notifications: send user notifications about events
        :type send_notifications: Optional[bool]

        :raise ValueError: if no user with `user_id` exists.
        :raise NoChangesDetectedException: if user initial data is identical to
        the update data.
        """
        app_logger.debug("Started `EditUserUsecase` execution")

        async with self._session:
            user = await self._user_repo.get_by_id(user_id)
            if user is None:
                raise ValueError(f"No user with {user_id} id was found")

            updates = self._get_effective_updates(user, currency, send_notifications)
            for k, v in updates.items():
                setattr(user, k, v)
            await user_storage.store(user)

            await self._session.commit()

        app_logger.debug("Successfully edited user")
