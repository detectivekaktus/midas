from abc import ABC, abstractmethod

from midas.service.abstract_notifier import AbstractNotifier


class AbstractHandler(ABC):
    """
    Handlers are supposed to be usecases of main loop.
    The handlers pack the code into a single testable
    unit.
    """

    def __init__(self, notifier: AbstractNotifier, update_interval: int = 600) -> None:
        """
        Create new event handler.

        :param notifier: concrete notifier implementation of where you want to
        send notifications.
        :type notifier: AbstractNotifier
        :param update_interval: seconds interval between updates
        :type update_interval: int
        """
        self._notifier = notifier
        self._UPDATE_INTERVAL = update_interval

    @abstractmethod
    async def loop(self) -> None:
        """
        Execute handler's block of code after sleeping.
        """
        ...
