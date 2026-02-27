from typing import Sequence, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.user import User
from midas.query.user.repository import UserRepository
from midas.usecase.abstract_usecase import AbstractUsecase


class GetAllUsersUsecase(AbstractUsecase[Sequence[User]]):
    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._user_repo = UserRepository(self._session)

    @override
    async def execute(self) -> Sequence[User]:
        app_logger.debug("Started `GetAllUsersUsecase` execution")

        async with self._session:
            users = await self._user_repo.get_all()
            app_logger.debug("Successfully returned all users")
            return users
