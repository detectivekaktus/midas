from dataclasses import dataclass
from src.db.schemas.user import User


@dataclass
class CachedUser:
    id: int
    currency_id: int


class UserCacheStorage:
    """
    User cache storage. This object is used to provide an interface that
    speeds up the `AuthMiddleware` frontend component.
    """

    def __init__(self) -> None:
        self._cache: dict[int, CachedUser] = {}

    async def store(self, user: User) -> CachedUser:
        """
        Cache user.

        :param user: user sqlalchemy instance
        :type user: User
        :return: Cached version of user
        :rtype: CachedUser
        """
        cached_user = CachedUser(user.id, user.currency_id)
        self._cache[cached_user.id] = cached_user
        return cached_user

    async def get(self, id: int) -> CachedUser:
        """
        Get cached user.

        :param id: user's telegram id
        :type id: int
        :return: cached user instance
        :rtype: CachedUser
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
