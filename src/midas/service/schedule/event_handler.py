from datetime import date, timedelta
from typing import Any, override

from midas.db.schemas.event import Event
from midas.service.schedule.abstract_handler import AbstractHandler
from midas.usecase.event import GetUpcomingEventsUsecase
from midas.usecase.event.util import determine_timedelta
from midas.usecase.transaction import CreateTransactionUsecase
from midas.util.enums import EventFrequency


class EventHandler(AbstractHandler):
    @override
    def __init__(self) -> None:
        self._get_events = GetUpcomingEventsUsecase()
        self._create_transaction = CreateTransactionUsecase()

    def _event_to_transaction_scheme(self, event: Event) -> dict[str, Any]:
        scheme = {
            "user_id": event.user_id,
            "transaction_type": event.transaction_type_id,
            "title": event.title,
            "amount": event.amount,
        }

        if event.description:
            scheme["description"] = event.description

        return scheme

    @override
    async def loop(self) -> None:
        events = await self._get_events.execute()
        if len(events) == 0:
            return

        for event in events:
            data = self._event_to_transaction_scheme(event)
            await self._create_transaction.execute(**data)

            # this is a very dirty implementation
            # i'm not supposed to access private member of a class
            async with self._get_events.get_session():
                today = date.today()
                delta = determine_timedelta(EventFrequency(event.interval))
                event.last_run_on = today
                event.next_run_on = today + timedelta(days=delta)
