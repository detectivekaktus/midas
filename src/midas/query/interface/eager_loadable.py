from abc import ABC, abstractmethod
from typing import Optional

from midas.db import Base


class EagerLoadable[T: Base, ID](ABC):
    """
    Interface for `Repository` family classes. This interface defines
    methods to implement for repositories that support eager loading
    techniques of sqlalchemy.
    """

    @abstractmethod
    async def get_by_id(self, id: ID, eager: bool = False) -> Optional[T]:
        """
        Get a database entity by its primary key.

        :param id: entity's primary key.
        :type id: ID
        :param eager: use eager loading
        :type eager: bool
        :return: an entity associated with the id or `None` if no entity
        exists with the provided id.
        :rtype: Optional[T]
        """
        ...
