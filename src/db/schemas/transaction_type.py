#!/usr/bin/env python3
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class TransactionType(Base):
    """
    Transaction type database table. This table is meant to be seeded
    with data from `db/seed/data` and represents the transaction types
    for each transaction or event.

    id:     serial primary key
    name:   varchar(32) not null
    income: bool not null

    Example:
    ```
    | name         | is_income |
    +--------------+-----------+
    | Bills & Fees | false     |
    | Income       | true      |
    ```
    """

    __tablename__ = "transaction_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    income: Mapped[bool] = mapped_column(Boolean, nullable=False)

    accounts = relationship("Account", back_populates="transaction_type")
    transactions = relationship("Transaction", back_populates="transaction_type")
    events = relationship("Event", back_populates="transaction_type")

    def __repr__(self) -> str:
        return f"TransactionType({self.id=!r}, {self.name=!r}, {self.income=!r})"
