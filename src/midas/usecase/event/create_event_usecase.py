from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.event import Event
from midas.query.event import EventRepository
from midas.query.user import UserRepository
from midas.usecase.abstract_usecase import AbstractUsecase
from midas.util.enums import EventFrequency, TransactionType


class CreateEventUsecase(AbstractUsecase[None]):
    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._user_repo = UserRepository(self._session)
        self._event_repo = EventRepository(self._session)

    @override
    async def execute(
        self,
        user_id: int,
        transaction_type: TransactionType,
        title: str,
        amount: Decimal,
        frequency: EventFrequency,
        description: Optional[str] = None,
    ) -> None:
        """
        Create a new recurring event.

        :param user_id: user's telegram id
        :type user_id: int
        :param transaction_type: transaction type
        :type transaction_type: TransactionType
        :param title: transaction title
        :type title: str
        :param amount: transaction amount
        :type amount: Decimal
        :param frequency: interval in days of how often
        the event should be repeated
        :type frequency: EventFrequency
        :param description: optional transaction description
        :type description: Optional[str]

        :raise ValueError: if no user with `user_id` exists
        """
        app_logger.debug(
            f"Started `CreateEventUsecase` execution: {user_id} - {transaction_type}"
        )

        async with self._session:
            user = await self._user_repo.get_by_id(user_id)
            if user is None:
                app_logger.debug(
                    "Finished `CreateEventUsecase` execution too soon because user does not exist"
                )
                raise ValueError(f"No user with {user_id} exists")

            today = date.today()
            delta = frequency
            # if delta is anything but monthly, leave it as it is.
            # if not, get the number of days of the month and use it as
            # delta (28, 30 and 31)
            if delta == EventFrequency.MONTHLY:
                delta = monthrange(today.year, today.month)[1]

            event = Event(
                user_id=user_id,
                transaction_type_id=transaction_type,
                title=title,
                description=description,
                amount=amount,
                last_run_on=today,  # even if it's not true
                interval=frequency,
                next_run_on=today + timedelta(days=delta),
            )
            self._event_repo.add(event)

            await self._session.commit()

        app_logger.debug(
            f"Successfully created an event: {user_id} - {transaction_type}"
        )
