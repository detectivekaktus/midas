from abc import ABC, abstractmethod


class AbstractNotifier(ABC):
    """
    Base class for all Notifier classes. A notifier is a class
    responsible for sending notifications on the supported platforms.
    """

    @abstractmethod
    async def notify(self, user_id: int) -> None:
        """
        Send a notification to user by their id.

        :param user_id: user's id.
        :type user_id: int
        """
        ...
