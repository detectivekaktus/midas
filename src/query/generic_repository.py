from typing import Iterable, Optional
from sqlalchemy.orm import Session

from src.db import Base


class GenericRepository[T: Base, ID]:
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
    >>> session = create_session()
    >>> repo = Repository[User, int](User, session)
    >>> with session:
    >>>     user = User(name="detectivekaktus", email="artiomastashonak@gmail.com")
    >>>     repo.add(user)
    """

    def __init__(self, model: type[T], session: Session) -> None:
        """
        Initialize the Repository class.

        :param model: the model managed by the repository.
        :type model: type[T]
        :param session: sqlalchemy session obtained via `create_session` method
        :type session: Session
        """
        self._model = model
        self._session = session

    def flush(self) -> None:
        """
        Trigger SQLAlchemy session flush
        """
        self._session.flush()

    def commit(self) -> None:
        """
        Commit changes to the database
        """
        self._session.commit()

    def add(self, value: T) -> None:
        """
        Add new database entity to the session.

        :param value: entity to be added.
        :type value: T
        """
        self._session.add(value)

    def add_many(self, values: Iterable[T]) -> None:
        """
        Add new database entities to the session.

        :param values: entities to be added.
        :type values: Iterable[T]
        """
        self._session.add_all(values)

    def get_by_id(self, id: ID) -> Optional[T]:
        """
        Get a database entity by its primary key.

        :param id: entity's primary key.
        :type id: ID
        :return: an entity associated with the id or `None` if no entity
        exists with the provided id.
        :rtype: Optional[T]
        """
        return self._session.get(self._model, id)

    def delete_by_id(self, id: ID) -> None:
        """
        Delete a database entity by its primary key.

        :param id: entity's primary key.
        :type id: ID
        :raise ValueError: if no entity with `id` exists.
        """
        entity = self._session.get(self._model, id)
        if not entity:
            raise ValueError(f"No entity with id {id} exists")

        self._session.delete(entity)
