from typing import override
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.db.schemas.account import Account
from src.query import GenericRepository


class AccountRepository(GenericRepository):
    @override
    def __init__(self, session: Session) -> None:
        super().__init__(Account, session)

    def delete_all_by_user_id(self, user_id: int) -> None:
        self._session.execute(delete(Account).where(Account.user_id == user_id))
