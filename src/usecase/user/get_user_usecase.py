from typing import Optional, override
from sqlalchemy.ext.asyncio import AsyncSession

from src.loggers import app_logger

from src.db.schemas.user import User
from src.query.user import UserRepository
from src.usecase.abstract_usecase import AbstractUsecase


class GetUserUsecase(AbstractUsecase[Optional[User]]):
    """
    Get user usecase. This class is meant to retrieve `User` database
    row associated with the id provided and used in the auth middleware.
    """

    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self.user_repo = UserRepository(self._session)

    @override
    async def execute(self, user_id: int) -> Optional[User]:
        """
        Get a user with the `user_id` provided.

        :param user_id: user's telegram id.
        :type user_id: int
        :return: `User` database row or `None` if no user was found.
        :rtype: Optional[User]
        """
        app_logger.debug("Started `GetUserUsecase` execution")

        async with self._session:
            user = await self.user_repo.get_by_id(user_id)
            app_logger.debug("Successfully returned user back")
            return user
