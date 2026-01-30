from typing import override

from midas.service.abstract_notifier import AbstractNotifier

from midas.platform.telegram import bot


class TelegramNotifier(AbstractNotifier):
    @override
    async def notify(self, user_id: int, msg: str) -> None:
        await bot.send_message(user_id, msg)
