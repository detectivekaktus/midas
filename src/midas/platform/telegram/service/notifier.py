from typing import override
from aiogram import Bot

from midas.service.abstract_notifier import AbstractNotifier


class TelegramNotifier(AbstractNotifier):
    @override
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @override
    async def notify(self, user_id: int, msg: str) -> None:
        await self.bot.send_message(user_id, msg)
