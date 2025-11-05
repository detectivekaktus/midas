#!/usr/bin/env python3
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class Account(Base):
    """
    Account database table. Represents double-entry accounts each user
    has for different expenses and one for income.

    id:             serial primary key
    user_id:        int foreign key not null
    debit_amount:   double precision not null default 0
    credit_amount:  double precision not null default 0
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    debit_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )
    credit_amount: Mapped[float] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )

    user = relationship("User", back_populates="accounts")
    debit_transactions = relationship(
        "Transaction",
        foreign_keys="[Transaction.debit_account_id]",
        back_populates="debit_account",
    )
    credit_transactions = relationship(
        "Transaction",
        foreign_keys="[Transaction.credit_account_id]",
        back_populates="credit_account",
    )
    storage = relationship("Storage", back_populates="account")

    def __repr__(self) -> str:
        return f"Account({self.id=!r}, {self.user_id=!r}, {self.debit_amount=!r}, {self.credit_amount=!r})"
