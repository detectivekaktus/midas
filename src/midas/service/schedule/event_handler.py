from asyncio import create_task, sleep
from datetime import date, timedelta
from time import perf_counter
from typing import Any, override

from midas.loggers import app_logger

from midas.db.schemas.event import Event
from midas.service.schedule.abstract_handler import AbstractHandler
from midas.usecase.event import GetUpcomingEventsUsecase
from midas.usecase.event.util import determine_timedelta
from midas.usecase.transaction import CreateTransactionUsecase
from midas.util.enums import EventFrequency

from midas.platform.telegram.service.notifier import TelegramNotifier


class EventHandler(AbstractHandler):
    @override
    def __init__(self, update_interval: int = 600) -> None:
        """
        Create new event handler.

        :param update_interval: seconds interval between updates
        :type update_interval: int
        """
        self._get_events = GetUpcomingEventsUsecase()
        self._create_transaction = CreateTransactionUsecase()
        self._UPDATE_INTERVAL = update_interval
        self._notifier = TelegramNotifier()

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
        while True:
            app_logger.info("Started execution of event updates")
            start = perf_counter()

            events = await self._get_events.execute()
            for event in events:
                data = self._event_to_transaction_scheme(event)
                await self._create_transaction.execute(**data)

                # this is a very dirty implementation
                # i'm not supposed to access private member of a class
                session = self._get_events.get_session()
                async with session:
                    today = date.today()
                    delta = determine_timedelta(EventFrequency(event.interval))
                    event.last_run_on = today
                    event.next_run_on = today + timedelta(days=delta)
                    await session.commit()

                if event.user.send_notifications:
                    await self._notifier.notify(
                        event.user_id, f"New event: {event.title}"
                    )

            app_logger.info(
                f"Finished updating {len(events)} events in {round(perf_counter() - start, 3)} seconds"
            )
            await sleep(self._UPDATE_INTERVAL)


async def start_event_handling() -> None:
    handler = EventHandler()
    create_task(handler.loop())
