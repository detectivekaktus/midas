from enum import StrEnum
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from src.loggers import aiogram_logger

from src.usecase.user import GetUserUsecase


class AllowedCommand(StrEnum):
    START = "/start"
    CANCEL = "/cancel"


class AuthMiddleware(BaseMiddleware):
    """
    Auth middleware implementation class.

    The middleware component fails if:
        * no telegram user is associated with the event.
        * no text is sent with the event.
        * unregistered user runs unallowed command.
        * registered user runs `/start` command.
    """

    def __init__(self) -> None:
        super().__init__()
        self._usecase = GetUserUsecase()

    async def __call__(  # type: ignore
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        telegram_user = event.from_user
        if telegram_user is None:
            await event.answer(
                "You must register to use commands.\n" "Register with /start command."
            )
            return

        text = event.text
        if not text:
            aiogram_logger.warning(
                "Auth middleware found an event without `message.text` attribute."
            )
            return

        user = await self._usecase.execute(telegram_user.id)
        # If user is not registered and has sent a command and that command is not allowed.
        if user is None and (text.startswith("/") and (text not in AllowedCommand)):
            await event.answer(
                "You must register to use commands.\n" "Register with /start command."
            )
            return

        if user is not None and text == AllowedCommand.START:
            await event.answer(
                "You are already registered.\n"
                "If you want to delete your profile, use /delete_profile command."
            )
            return

        return await handler(event, data)
