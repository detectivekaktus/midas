#!/usr/bin/env python3
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class Storage(Base):
    """
    Storage database table. Represents a monetary storage a user can have
    whether it's a bank or cash storage. The storage is associated with an
    income account the user has.

    id:         serial primary key
    user_id:    int foreign key not null
    account_id: int foreign key not null
    amount:     Numeric(12, 2) not null default 0
    """

    __tablename__ = "storages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    user = relationship("User", back_populates="storages")
    account = relationship("Account", back_populates="storage")

    def __repr__(self) -> str:
        return f"Storage({self.id=!r}, {self.user_id=!r}, {self.account_id=!r}, {self.amount=!r})"
