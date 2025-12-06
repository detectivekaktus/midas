from enum import IntEnum
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Command(IntEnum):
    EXIT = 0
    PREV = 1
    NEXT = 2
    DELETE = 3


class TransactionPaginationCommand(CallbackData, prefix="trans-pag"):
    command: Command


def get_transaction_pagination_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔙",
        callback_data=TransactionPaginationCommand(command=Command.EXIT),
    )
    builder.button(
        text="◀️",
        callback_data=TransactionPaginationCommand(command=Command.PREV),
    )
    builder.button(
        text="❌",
        callback_data=TransactionPaginationCommand(command=Command.DELETE),
    )
    builder.button(
        text="▶️",
        callback_data=TransactionPaginationCommand(command=Command.NEXT),
    )
    return builder.as_markup()
