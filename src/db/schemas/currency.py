#!/usr/bin/env python3
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class Currency(Base):
    """
    Currency database table. This table is meant to be seeded with
    values from `db/seed/data` and represents the currencies available
    in the application.

    id:     serial primary key
    name:   varchar(32) not null
    code:   varchar(4) not null
    symbol: varchar(4) not null

    Example:
    ```
    | name                 | code | symbol |
    +----------------------+------|--------|
    | United States Dollar | USD  | $      |
    ```
    """
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    code: Mapped[str] = mapped_column(String(4), nullable=False)
    symbol: Mapped[str] = mapped_column(String(4), nullable=False)

    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship
    # The first argument is the class name (can be both class reference or a string)
    # the `back_populates` argument is the class attribute to relate
    users = relationship("User", back_populates="currency")

    def __repr__(self) -> str:
        return f"Currency({self.id=!r}, {self.name=!r}, {self.code=!r}, {self.symbol=!r})"
