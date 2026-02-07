from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from midas.platform.telegram.util.currency import get_currency_list
from midas.platform.telegram.validator import SkipAnswer


def get_currency_keyboard(skippable: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for currency in get_currency_list():
        builder.button(text=currency)

    if skippable:
        builder.button(text=SkipAnswer.SKIP)

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
