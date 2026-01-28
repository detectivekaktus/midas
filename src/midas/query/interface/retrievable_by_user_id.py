from abc import ABC, abstractmethod
from typing import Sequence


class RetrievableByUserId(ABC):
    """
    Interface for repository family classes. By implementing this interface
    the repository can fetch entities, given the owner (user) id.
    """

    @abstractmethod
    async def get_by_user_id(
        self, user_id: int, count: int = 16, *args, **kwargs
    ) -> Sequence:
        """
        Get `count` rows with `user_id`.

        NOTE: This method must return empty list when no user with `user_id`
        exists.

        :param user_id: user's telegram id
        :type user_id: int
        :param count: number of rows to get
        :type count: int
        :return: list of rows owned by `user_id`
        :rtype: Sequence[Any]
        """
        pass
