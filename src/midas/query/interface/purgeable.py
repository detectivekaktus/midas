from abc import ABC, abstractmethod


class Purgeable(ABC):
    """
    Interface for `Repository` family classes. This interface defines
    method to purge all data related to user.
    """

    @abstractmethod
    async def purge_by_user_id(self, user_id: int) -> None:
        """
        Delete all rows bound to user with `user_id`.

        :param user_id: user's telegram id
        :type user_id: int
        """
        pass
