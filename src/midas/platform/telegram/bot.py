from os import getenv
from sys import stderr
from typing import Optional
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN: Optional[str] = getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print(
        "FATAL: No `TELEGRAM_TOKEN` environment variable was found or it is blank. Aborting...",
        file=stderr,
    )
    exit(1)

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

__all__ = ("bot",)
