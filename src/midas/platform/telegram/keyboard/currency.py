from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from midas.platform.telegram.util.currency import get_currency_list


def get_currency_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for currency in get_currency_list():
        builder.button(text=currency)

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
