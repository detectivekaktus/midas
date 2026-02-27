from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from midas.db import Base


class User(Base):
    """
    User database table. Represents all the users using the application.
    The `id` column contains Telegram user id, while `currency_id` and
    `send_notifications` columns reference the currency that user's adopted
    and whether or not they want to receive notifications respectively.

    id:                 int primary key
    currency_id:        int not null
    send_notifications: bool not null default true
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id"), nullable=False
    )
    send_notifications: Mapped[bool] = mapped_column(nullable=False, default=True)

    currency = relationship("Currency", back_populates="users")
    accounts = relationship("Account", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    storages = relationship("Storage", back_populates="user")
    events = relationship("Event", back_populates="user")

    def __repr__(self) -> str:
        return f"User({self.id=!r}, {self.currency_id=!r})"
