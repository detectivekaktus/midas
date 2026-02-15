from asyncio import sleep
from time import perf_counter
from typing import Any, override

from midas.loggers import app_logger

from midas.db.schemas.event import Event
from midas.service.abstract_notifier import AbstractNotifier
from midas.service.schedule.abstract_handler import AbstractHandler
from midas.usecase.event import GetUpcomingEventsUsecase, UpdateEventAfterRunUsecase
from midas.usecase.transaction import CreateTransactionUsecase


class EventHandler(AbstractHandler):
    @override
    def __init__(self, notifier: AbstractNotifier, update_interval: int = 3600) -> None:
        super().__init__(notifier, update_interval)
        self._get_events = GetUpcomingEventsUsecase()
        self._update_event = UpdateEventAfterRunUsecase()
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
        while True:
            app_logger.info("Started execution of event updates")
            start = perf_counter()

            events = await self._get_events.execute()
            for event in events:
                data = self._event_to_transaction_scheme(event)
                await self._create_transaction.execute(**data)

                if event.user.send_notifications:
                    await self._notifier.notify(
                        event.user_id, f"New event: {event.title}"
                    )

                await self._update_event.execute(event)

            app_logger.info(
                f"Finished updating {len(events)} events in {round(perf_counter() - start, 3)} seconds"
            )
            await sleep(self._UPDATE_INTERVAL)
