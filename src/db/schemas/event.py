#!/usr/bin/env python3
from decimal import Decimal
from sqlalchemy import TIMESTAMP, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class Event(Base):
    """
    Event database table. Represents user-generated recurring events
    that provoke transactions. Use `interval` column that contains an integer
    number of seconds from `last_run_at` until `next_run_at`.

    id:                     serial primary key
    user_id:                int foreign key not null
    transaction_type_id:    int foreign key not null
    title:                  varchar(64) not null
    description:            varchar(256)
    amount:                 Numeric(12, 2) not null
    last_run_at:            timestamp (without tz) not null
    interval:               int not null
    next_run_at:            timestamp (without tz) not null
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    transaction_type_id: Mapped[int] = mapped_column(
        ForeignKey("transaction_types.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    last_run_at = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    interval: Mapped[int] = mapped_column(Integer, nullable=False)
    next_run_at = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    user = relationship("User", back_populates="events")
    transaction_type = relationship("TransactionType", back_populates="events")

    def __repr__(self) -> str:
        return f"Event({self.id=!r}, {self.user_id=!r}, {self.transaction_type_id=!r}, {self.title=!r}, {self.description=!r}, {self.amount=!r}, {self.last_run_at=!r}, {self.interval=!r}, {self.next_run_at=!r})"
