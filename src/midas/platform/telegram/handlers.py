from asyncio import create_task

from midas.platform.telegram.bot import bot
from midas.platform.telegram.service.notifier import TelegramNotifier
from midas.service.schedule import EventHandler


async def start_event_handling() -> None:
    notifier = TelegramNotifier(bot)
    handler = EventHandler(notifier)
    create_task(handler.loop())


__all__ = ("start_event_handling",)
