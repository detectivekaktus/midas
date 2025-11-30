from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.platform.telegram.util.transaction import get_transaction_type_list


def get_transaction_type_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for type_ in get_transaction_type_list():
        builder.button(text=type_)

    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)
