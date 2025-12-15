from src.db.schemas.user import User


class UserCacheStorage:
    """
    User cache storage. This object is used to provide an interface that
    speeds up the `AuthMiddleware` frontend component.
    """

    def __init__(self) -> None:
        self._cache: dict[int, User] = {}

    async def store(self, user: User) -> None:
        """
        Cache user.

        :param user: user sqlalchemy instance
        :type user: User
        """
        self._cache[user.id] = user

    async def get(self, id: int) -> User:
        """
        Get cached user.

        :param id: user's telegram id
        :type id: int
        :return: user sqlalchemy instance
        :rtype: User
        :raise KeyError: if no user with `id` is cached.
        """
        return self._cache[id]

    async def exists(self, id: int) -> bool:
        """
        Check if user is already cached.

        :param id: user's telegram id
        :type id: int
        :return: `True` if user is already cached, `False` otherwise.
        :rtype: bool
        """
        return id in self._cache

    async def delete(self, id: int) -> None:
        """
        Delete cached user by its id.

        :param id: user's telegram id
        :type id: int
        :raise KeyError: if no user with `id` is cached.
        """
        self._cache.pop(id)
