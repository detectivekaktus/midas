from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from midas.db import engine


def create_session(custom_engine: Optional[AsyncEngine] = None) -> AsyncSession:
    """
    Create async sqlalchemy session.

    This method obscures the sqlalchemy calls from the end
    user to provide a simpler interface for accessing session.

    Note that `custom_engine` argument is meant only for
    testing purposes and should remain `None` in production.

    :param custom_engine: custom testing `AsyncEngine` object.
    :type custom_engine: AsyncEngine
    :return: new sqlalchemy session
    :rtype: AsyncSession
    """
    session = AsyncSession(custom_engine or engine)
    return session
