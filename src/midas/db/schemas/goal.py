from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from midas.db import Base


class Goal(Base):
    """
    Goal database table. Represents the user-defined financial goals.

    id:             serial primary key
    user_id:        int foreign key not null
    title:          varchar(64) not null
    description:    varchar(256)
    current_amount: Numeric(12, 2) default 0 not null
    total_amount:   Numeric(12, 2) not null
    """

    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    user = relationship("User", back_populates="goals")

    def __repr__(self) -> str:
        return f"Goal({self.id=!r}, {self.user_id=!r}, {self.title=!r}, {self.description=!r}, {self.current_amount=!r}, {self.total_amount=!r})"
