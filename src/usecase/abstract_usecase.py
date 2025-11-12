from abc import ABC, abstractmethod


class AbstractUsecase(ABC):
    """
    Abstract usecase class. All concrete usecases must inherit
    from this class and implement its `execute()` method which
    implements the business logic of the usecase itself.

    The usecase has no predefined initializer, as it may vary
    depending on the operations computed in the usecase. In
    most cases you would need to specify at least one repository
    in the initializer.

    :example:
    >>> repo = Repository(User)
    >>> usecase = RegisterUserUsecase(repo)
    >>> usecase.execute()
    """

    @abstractmethod
    def execute(self, *args, **kwargs) -> None:
        """
        Execute the usecase business logic.
        """
        ...
