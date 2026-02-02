from decimal import Decimal
from typing import Any, Optional, override
from sqlalchemy.ext.asyncio import AsyncSession

from midas.loggers import app_logger

from midas.db.schemas.event import Event
from midas.query.event import EventRepository
from midas.usecase.abstract_usecase import AbstractUsecase
from midas.util.enums import EventFrequency, TransactionType
from midas.util.errors import NoChangesDetectedException


class EditEventUsecase(AbstractUsecase[None]):
    """
    Edit event usecase. This class is responsible for making changes
    to already existing events without making changes to the transactions
    created in the event handling phase.
    """

    @override
    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(session)
        self._event_repo = EventRepository(self._session)

    def _get_effective_updates(
        self,
        event: Event,
        transaction_type: Optional[TransactionType],
        title: Optional[str],
        amount: Optional[Decimal],
        description: Optional[str],
        frequency: Optional[EventFrequency],
    ) -> dict[str, Any]:
        """
        Get effective updates against the event.

        Any `None` fields aren't counter as well as any identical fields.

        :raise ValueError: if all optional fields are `None` or if changes
        are identical to source event.
        """
        fields = {
            "transaction_type_id": transaction_type,
            "title": title,
            "amount": amount,
            "description": description,
            "interval": frequency,
        }

        updates = {
            k: v
            for k, v in fields.items()
            if v is not None and getattr(event, k, v) != v
        }
        if len(updates) == 0:
            raise NoChangesDetectedException("No valid updates found")

        return updates

    @override
    async def execute(
        self,
        id: int,
        transaction_type: Optional[TransactionType] = None,
        title: Optional[str] = None,
        amount: Optional[Decimal] = None,
        description: Optional[str] = None,
        frequency: Optional[EventFrequency] = None,
    ) -> None:
        """
        Edit an existing event.

        :param id: event id
        :type id: int
        :param transaction_type: new trasnaction type
        :type transaction_type: Optional[TransactionType]
        :param title: new title
        :type title: Optional[str]
        :param amount: new amount
        :type amount: Optional[Decimal]
        :param description: new description
        :type description: Optional[str]
        :param frequency: new frequency
        :type frequency: Optional[EventFrequency]

        :raise ValueError: if no event with `id` exists.
        :raise NoChangesDetectedException: if the source event fields
        are identical to the new ones or the new ones are all `None`.
        """
        app_logger.debug(f"Started `EditEventUsecase` execution: {id}")

        async with self._session:
            event = await self._event_repo.get_by_id(id)
            if event is None:
                raise ValueError(f"No event with {id=} found")

            updates = self._get_effective_updates(
                event, transaction_type, title, amount, description, frequency
            )

            for k, v in updates.items():
                setattr(event, k, v)

            await self._session.commit()

        app_logger.debug(f"Successfully edited the event: {id}")
