from typing import Iterable, Optional, Self
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from src.db import Base, engine


class Repository[T: Base, ID]:
    """
    Repository class. This class is inspired by the clean architecture
    principles. The goal of this class is to abstract database queries
    in a Facade interface.
    
    The functionality of this class allows to perform simple CRUD operations
    on `model` object of type `T` which must inherit from `Base`, thus `model`
    must have column `id` of type `ID`.

    Repository is meant to be used as context manager to maintain the
    underlying SQLAlchemy session alive during all the operations to avoid
    detached state on objects.

    :example:
    >>> repo = Repository[User, int](User)
    >>> with repo:
    >>>     user = User(name="detectivekaktus", email="artiomastashonak@gmail.com")
    >>>     repo.add(user)
    """

    def __init__(self, model: type[T], custom_engine: Optional[Engine] = None) -> None:
        """
        Initialize the Repository class.

        Note that the `custom_engine` argument is meant for simplying unit-testing
        of this class and is not meant to be specified in production. The repository
        will use by default `src.db.engine` object to comunicate with the database.

        :param model: the model managed by the repository.
        :type model: type[T]
        :param custom_engine: custom engine that replaces the global `src.db.engine`
        object.
        :type custom_engine: Optional[Engine]
        """
        self._model = model
        self._engine = custom_engine or engine
        self._session: Optional[Session] = None

    def __enter__(self) -> Self:
        self._session = Session(self._engine)
        return self

    def __exit__(self, *args) -> None:
        if not self._session:
            raise SyntaxError("Session can't be closed when it hand't been opened")

        self._session.commit()
        self._session.close()

    @property
    def session(self) -> Session:
        if not self._session:
            raise SyntaxError(
                "Session hasn't been opened. Use Repository as context manager"
            )
        return self._session

    def flush(self) -> None:
        """
        Triggers SQLAlchemy session flush
        """
        self.session.flush()

    def add(self, value: T) -> None:
        """
        Add new database entity to the session.

        :param value: entity to be added.
        :type value: T
        """
        self.session.add(value)

    def add_many(self, values: Iterable[T]) -> None:
        """
        Add new database entities to the session.

        :param values: entities to be added.
        :type values: Iterable[T]
        """
        self.session.add_all(values)

    def get_by_id(self, id: ID) -> Optional[T]:
        """
        Get a database entity by its primary key.

        :param id: entity's primary key.
        :type id: ID
        :return: an entity associated with the id or `None` if no entity
        exists with the provided id.
        :rtype: Optional[T]
        """
        return self.session.get(self._model, id)

    def delete_by_id(self, id: ID) -> None:
        """
        Delete a database entity by its primary key.

        :param id: entity's primary key.
        :type id: ID
        :raise ValueError: if no entity with `id` exists.
        """
        entity = self.session.get(self._model, id)
        if not entity:
            raise ValueError(f"No entity with id {id} exists")

        self.session.delete(entity)
