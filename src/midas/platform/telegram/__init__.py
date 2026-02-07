from .bot import bot
from .routers import dp


async def start_bot():
    """
    Start polling on the main dispatcher for the bot.

    This function uses global `Dispatcher` and `Bot` objects to
    start polling on the requests to the bot with the `TELEGRAM_TOKEN`
    specified in the `.env` file.
    """
    await dp.start_polling(bot)


__all__ = ("start_bot",)
