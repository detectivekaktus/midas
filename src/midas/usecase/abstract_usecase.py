from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from midas.query.session import create_session


class AbstractUsecase[T](ABC):
    """
    Abstract usecase class. All concrete usecases must inherit
    from this class and implement its `execute()` method which
    implements the business logic of the usecase itself.

    The usecase has no predefined initializer, as it may vary
    depending on the operations computed in the usecase. In
    most cases you would need to specify at least one repository
    in the initializer.

    The generic `T` type represents the return type of `exeucte()`
    method and in most of the cases is equal to `None`.

    :example:
    >>> usecase = RegisterUserUsecase()
    >>> usecase.execute()
    """

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        """
        Initialize a new Usecase object.

        Note that `session` argument is here only for testing
        purposes and must be left blank when this class is used
        in production.

        :param session: testing session.
        :type session: Optional[AsyncSession]
        """
        self._session = session or create_session()

    def get_session(self) -> AsyncSession:
        """
        Getter for AsyncSession used under the hood.

        :return: usecase database session
        :rtype: AsyncSession
        """
        return self._session

    @abstractmethod
    async def execute(self, *args, **kwargs) -> T:
        """
        Execute the usecase business logic.
        """
        ...
