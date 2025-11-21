#!/usr/bin/env python3
from typing import Optional
from uuid import uuid4
from sqlalchemy import TIMESTAMP, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class Transaction(Base):
    """
    Transaction database table. Represents the expense/income transactions
    made by application users. The credit account may be null in case of an
    income transaction:

    ```
    | Account name | Debit | Credit |
    +--------------+-------+--------+
    | Income       | X     |        |
    | Income debt  |       | X      |
    ```

    Since it would be useless to keep the income debit account, income
    transactions violate double-entry rules and apply changes only
    to Income account.

    id:                     uuid primary key
    user_id:                int foreign key not null
    transaction_type_id:    int foreign key not null
    created_at:             timestamp default now not null
    title:                  varchar(64) not null
    description:            varchar(256)
    amount:                 Numeric(12, 2) not null
    debit_account_id:       int foreign key not null
    credit_account_id:      int foreign key
    """

    __tablename__ = "transactions"

    id: Mapped[Uuid] = mapped_column(Uuid, default=uuid4, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    transaction_type_id: Mapped[int] = mapped_column(
        ForeignKey("transaction_types.id"), nullable=False
    )
    created_at = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    debit_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"), nullable=False
    )
    credit_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id"))

    user = relationship("User", back_populates="transactions")
    transaction_type = relationship("TransactionType", back_populates="transactions")
    debit_account = relationship(
        "Account", foreign_keys=[debit_account_id], back_populates="debit_transactions"
    )
    credit_account = relationship(
        "Account",
        foreign_keys=[credit_account_id],
        back_populates="credit_transactions",
    )

    def __repr__(self) -> str:
        return f"Transaction({self.id=!r}, {self.user_id=!r}, {self.transaction_type_id=!r}, {self.created_at=!r}, {self.title=!r}, {self.description=!r}, {self.amount=!r}, {self.debit_account_id=!r}, {self.credit_account_id=!r})"
