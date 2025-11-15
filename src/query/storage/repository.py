from typing import override
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.db.schemas.storage import Storage
from src.query import GenericRepository


class StorageRepository(GenericRepository):
    @override
    def __init__(self, session: Session) -> None:
        super().__init__(Storage, session)

    def delete_all_by_user_id(self, user_id: int) -> None:
        self._session.execute(delete(Storage).where(Storage.user_id == user_id))
