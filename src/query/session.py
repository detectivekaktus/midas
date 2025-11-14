from typing import Optional
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from src.db import engine


def create_session(custom_engine: Optional[Engine] = None) -> Session:
    """
    Create sqlalchemy session.

    This method obscures the sqlalchemy calls from the end
    user to provide a simpler interface for accessing session.

    Note that `custom_engine` argument is meant only for
    testing purposes and should remain `None` in production.

    :param custom_engine: custom testing `Engine` object.
    :type custom_engine: Engine
    :return: new sqlalchemy session
    :rtype: Session
    """
    session = Session(custom_engine or engine)
    return session
