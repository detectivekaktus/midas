from asyncio import create_task

from midas.platform.telegram.bot import bot
from midas.platform.telegram.service.notifier import TelegramNotifier
from midas.service.schedule import EventHandler, ReportHandler


notifier = TelegramNotifier(bot)


async def start_event_handling() -> None:
    handler = EventHandler(notifier, 3600)
    create_task(handler.loop())


async def start_monthly_reporting() -> None:
    handler = ReportHandler(notifier, 3600 * 12)
    create_task(handler.loop())


__all__ = ("start_event_handling", "start_monthly_reporting")
