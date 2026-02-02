from enum import IntEnum
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Command(IntEnum):
    EXIT = 0
    PREV = 1
    NEXT = 2
    DELETE = 3
    EDIT = 4


class EventPaginationCommand(CallbackData, prefix="event-pag"):
    command: Command


def get_event_pagination_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔙",
        callback_data=EventPaginationCommand(command=Command.EXIT),
    )
    builder.button(
        text="◀️",
        callback_data=EventPaginationCommand(command=Command.PREV),
    )
    builder.button(
        text="❌",
        callback_data=EventPaginationCommand(command=Command.DELETE),
    )
    builder.button(
        text="▶️",
        callback_data=EventPaginationCommand(command=Command.NEXT),
    )
    return builder.as_markup()
