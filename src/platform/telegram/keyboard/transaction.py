from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.platform.telegram.util.transaction import get_transaction_type_list
from src.platform.telegram.validator import SkipAnswer


def get_transaction_type_keyboard(skippable: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for type_ in get_transaction_type_list():
        builder.button(text=type_)

    if skippable:
        builder.button(text=SkipAnswer.SKIP)

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
