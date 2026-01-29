from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    """
    Handlers are supposed to be usecases of main loop.
    The handlers pack the code into a single testable
    unit.
    """

    @abstractmethod
    async def loop(self) -> None:
        """
        Execute handler's block of code after sleeping.
        """
        ...
